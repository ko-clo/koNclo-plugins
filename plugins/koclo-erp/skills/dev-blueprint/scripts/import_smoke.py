#!/usr/bin/env python3
"""라우터·서비스 모듈을 실제로 import 해 스모크 판정한다. FAIL 이면 exit 1.

`py_compile` 통과는 이 검사를 대체하지 못한다 — import 시점에만 드러나는 오류가 있다.
외부 의존(fastapi·sqlalchemy·asyncpg)이 없는 로컬에서는 SKIP(exit 2)을 내므로
그때는 컨테이너에서 돌리거나 배포 후 `Application startup complete` + `/docs` 200 으로 대체한다.

사용법: python3 import_smoke.py <모듈명...> [--pkg app.routers] [--root backend]
"""
import argparse
import importlib
import sys
import time
from pathlib import Path

# 컨테이너에만 설치된 외부 의존 — 이게 없어서 실패하면 코드 결함이 아니라 환경 문제다
CONTAINER_ONLY_DEPS = {"fastapi", "sqlalchemy", "sqlmodel", "asyncpg", "pydantic", "starlette", "uvicorn"}

EXIT_PASS, EXIT_FAIL, EXIT_SKIP = 0, 1, 2


def _missing_dep(exc: BaseException) -> str | None:
    """ModuleNotFoundError 가 컨테이너 전용 의존 때문인지 판별한다."""
    while exc is not None:
        if isinstance(exc, ModuleNotFoundError) and exc.name:
            top = exc.name.split(".")[0]
            if top in CONTAINER_ONLY_DEPS:
                return top
        exc = exc.__cause__ or exc.__context__
    return None


def import_modules(names: list[str], pkg: str, root: Path) -> int:
    sys.path.insert(0, str(root))
    failed, skipped = [], []
    started = time.perf_counter()
    for name in names:
        target = name if "." in name else f"{pkg}.{name}"
        try:
            importlib.import_module(target)
        except BaseException as exc:  # SystemExit 를 내는 모듈도 실패로 본다
            dep = _missing_dep(exc)
            (skipped if dep else failed).append((target, dep or f"{type(exc).__name__}: {exc}"))
    elapsed = time.perf_counter() - started

    for target, reason in failed:
        print(f"FAIL {target} — {reason}")
    for target, dep in skipped:
        print(f"SKIP {target} — 컨테이너 전용 의존 `{dep}` 미설치")
    ok = len(names) - len(failed) - len(skipped)
    print(f"{ok}/{len(names)} imported ({elapsed:.1f}s)")

    if failed:
        return EXIT_FAIL
    if skipped:
        print("→ 이 환경에서는 판정 불가. 컨테이너에서 실행하거나 배포 후 /docs 200 으로 대체한다.")
        return EXIT_SKIP
    print("PASS")
    return EXIT_PASS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modules", nargs="+", help="모듈명 (점이 없으면 --pkg 아래로 해석)")
    parser.add_argument("--pkg", default="app.routers", help="기본 패키지 (기본값: app.routers)")
    parser.add_argument("--root", default="backend", help="sys.path 에 넣을 루트 (기본값: backend)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"FAIL 루트 없음: {root}")
        return EXIT_FAIL
    return import_modules(args.modules, args.pkg, root)


if __name__ == "__main__":
    sys.exit(main())
