#!/usr/bin/env python3
"""dev-blueprint §6 게이트 중 기계로 판정되는 항목을 검사한다. FAIL 이 있으면 exit 1.

사용법: python3 check_blueprint.py <feature> [--preserve-ui] [--css P] [--view P ...] [--widget P ...] [--router P] [--service P]
"""
import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_VIEW_LINES = 300  # §1 컴포넌트 분리 — View 가 이보다 길면 쪼갠다
NARROW_MAX_WIDTH_PX = 600  # 이보다 좁은 max-width 는 고정 폭 의심. 모달일 수 있어 WARN 에 그친다
SPINNER_WINDOW_LINES = 5  # loading 분기에서 이 줄 수 안에 .spinner 가 있어야 한다 (실측 분포 0~3줄)
LOADING_BRANCH_RE = re.compile(r'v-(?:if|else-if|show)="([^"]*[lL]oading[^"]*)"')
GENERIC_FONTS = {"sans-serif", "serif", "monospace", "system-ui", "cursive", "fantasy", "inherit", "initial", "unset"}
# OS 에 깔려 있어 로드가 필요 없는 글꼴 — '미로드'가 아니라 '토큰 밖'으로 센다 (frontend/css 실사용 이름)
SYSTEM_FONTS = {
    "-apple-system", "blinkmacsystemfont", "apple sd gothic neo", "sf mono", "sfmono-regular", "menlo",
    "segoe ui", "malgun gothic", "맑은 고딕", "consolas", "ui-monospace",
}
FORBIDDEN_BACKEND = {
    "session.exec(": "AsyncSession 에는 exec 가 없다 — execute 후 scalars 를 쓴다 (§3-2b)",
    "build_master_data": "공유 monolith 로더 금지 — 탭 전용 경량 loader 를 쓴다 (§1)",
    "psycopg2": "별도 DB 접근 경로 금지 — 앱 async 엔진을 쓴다 (§1)",
}
HEX_RE = re.compile(r"#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")


@dataclass
class Finding:
    check: str
    status: str  # PASS | FAIL | WARN | SKIP
    detail: str = ""


@dataclass
class Targets:
    feature: str
    css: Path | None
    views: list[Path]
    widgets: list[Path]
    router: Path | None
    service: Path | None


def find_project_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".claude").is_dir():
            return candidate
    raise SystemExit(f"프로젝트 루트(.claude 포함)를 찾지 못했습니다 — 기준 경로: {start}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="dev-blueprint 기계 판정 게이트")
    parser.add_argument("feature", help="탭 식별자 (예: payrate, sample-return)")
    parser.add_argument("--root", type=Path, help="프로젝트 루트 (기본: 이 파일에서 위로 탐색)")
    parser.add_argument("--css", type=Path, help="피처 CSS 경로")
    parser.add_argument("--view", type=Path, action="append", help="View 경로 (여러 번 지정 가능)")
    parser.add_argument("--widget", type=Path, action="append", help="위젯 경로 (여러 번 지정 가능)")
    parser.add_argument("--router", type=Path, help="라우터 경로")
    parser.add_argument("--service", type=Path, help="서비스 경로")
    parser.add_argument("--preserve-ui", action="store_true", help="정본 UI 를 보존한 이관 탭(§4-8) — 정본 값 검사를 WARN 으로 낮춘다")
    return parser.parse_args(argv)


def first_existing(candidates: list[Path]) -> Path | None:
    return next((path for path in candidates if path.is_file()), None)


def resolve_targets(root: Path, feature: str, args: argparse.Namespace) -> Targets:
    """파일명 규칙(§2)으로 대상 파일을 찾는다. 옵션으로 넘긴 경로가 우선한다."""
    snake, kebab = feature.replace("-", "_"), feature.replace("_", "-")
    pascal = "".join(part.capitalize() for part in re.split(r"[-_]", feature))
    css_dir, js_dir, app_dir = root / "frontend" / "css", root / "frontend" / "js", root / "backend" / "app"
    return Targets(
        feature=feature,
        css=args.css or first_existing([css_dir / f"{kebab}.css", css_dir / f"{snake}.css"]),
        views=args.view or sorted((js_dir / "views").glob(f"{pascal}*View.js")),
        widgets=args.widget or sorted((js_dir / "widgets").glob(f"{pascal}*.js")),
        router=args.router or first_existing([app_dir / "routers" / f"{snake}_router.py"]),
        service=args.service or first_existing([app_dir / "services" / f"{snake}_service.py"]),
    )


def report(check: str, problems: list[str], status: str = "FAIL") -> list[Finding]:
    if not problems:
        return [Finding(check, "PASS")]
    return [Finding(check, status, problem) for problem in problems]


def numbered_lines(path: Path, strip_css_comments: bool = False) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    if strip_css_comments:
        # 줄 번호가 밀리지 않게 주석을 같은 수의 개행으로 바꾼다
        text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.DOTALL)
    return list(enumerate(text.splitlines(), start=1))


def normalize_hex(raw: str) -> str:
    raw = raw.upper()
    return "#" + ("".join(char * 2 for char in raw) if len(raw) == 3 else raw)


def load_token_hexes(theme_css: Path) -> set[str]:
    text = theme_css.read_text(encoding="utf-8")
    return {normalize_hex(m.group(1)) for m in re.finditer(r"--koclo-[\w-]+\s*:\s*#([0-9A-Fa-f]{3,6})\b", text)}


def load_loaded_fonts(index_html: Path) -> set[str]:
    text = index_html.read_text(encoding="utf-8")
    return {m.group(1).replace("+", " ").lower() for m in re.finditer(r"family=([^:&\"']+)", text)}


def load_token_fonts(theme_css: Path) -> set[str]:
    """`--koclo-font-*` 토큰의 첫 글꼴 이름. 신규 탭이 쓸 수 있는 글꼴의 정본이다."""
    text = theme_css.read_text(encoding="utf-8")
    return {m.group(1).strip().strip("'\"").lower() for m in re.finditer(r"--koclo-font-[\w-]+\s*:\s*([^,;]+)", text)}


def check_css(root: Path, css: Path, preserve_ui: bool) -> list[Finding]:
    theme_css = root / "frontend" / "css" / "theme.css"
    tokens, token_fonts = load_token_hexes(theme_css), load_token_fonts(theme_css)
    loaded_fonts = load_loaded_fonts(root / "frontend" / "index.html")
    where = css.relative_to(root).as_posix() if css.is_relative_to(root) else str(css)
    hexes, unloaded, off_token_fonts, dark, fixed, narrow = [], [], [], [], [], []
    for number, line in numbered_lines(css, strip_css_comments=True):
        value_part = line.partition(":")[2]  # 선택자(#id)가 아니라 선언 값만 본다
        for match in HEX_RE.finditer(value_part):
            if normalize_hex(match.group(1)) not in tokens:
                hexes.append(f"{where}:{number} {normalize_hex(match.group(1))}")
        for match in re.finditer(r"font-family\s*:\s*([^;}]+)", line):
            for name in (part.strip().strip("'\"") for part in match.group(1).split(",")):
                if not name or name.startswith("var(") or name.lower() in GENERIC_FONTS | token_fonts:
                    continue
                bucket = off_token_fonts if name.lower() in loaded_fonts | SYSTEM_FONTS else unloaded
                bucket.append(f"{where}:{number} {name}")
        if "prefers-color-scheme" in line:
            dark.append(f"{where}:{number}")
        if re.search(r"position\s*:\s*fixed", line):
            fixed.append(f"{where}:{number}")
        for match in re.finditer(r"max-width\s*:\s*(\d+)px", line):
            if int(match.group(1)) < NARROW_MAX_WIDTH_PX:
                narrow.append(f"{where}:{number} max-width:{match.group(1)}px")
    # 정본 UI 를 보존한 탭은 정본 값을 그대로 쓰므로 막지 않고 대조 대상으로만 알린다 (§4-8)
    canon_status = "WARN" if preserve_ui else "FAIL"
    return (
        report("토큰 밖 hex", hexes, status=canon_status)
        + report("토큰 밖 글꼴", off_token_fonts, status=canon_status)
        + report("미로드 글꼴", unloaded)
        + report("다크모드 블록", dark)
        + report("position:fixed", fixed, status=canon_status)
        + report("좁은 고정 폭", narrow, status="WARN")
    )


def check_css_link(root: Path, css: Path) -> list[Finding]:
    index = (root / "frontend" / "index.html").read_text(encoding="utf-8")
    linked = re.search(rf"css/{re.escape(css.name)}\?v=", index)
    return report("CSS 링크", [] if linked else [f"index.html 에 css/{css.name}?v= link 없음"])


def spinnerless_loading_branches(lines: list[tuple[int, str]]) -> list[int]:
    """v-if/v-else-if/v-show="...loading..." 분기마다 근처 줄에 .spinner 가 있는지 본다."""
    texts = {number: text for number, text in lines}
    result = []
    for number, line in lines:
        match = LOADING_BRANCH_RE.search(line)
        if not match or match.group(1).strip().startswith("!"):
            continue
        window = [texts.get(n, "") for n in range(number, number + SPINNER_WINDOW_LINES)]
        if not any("spinner" in text for text in window):
            result.append(number)
    return result


def check_frontend(root: Path, targets: Targets) -> list[Finding]:
    iframes, oversized, no_spinner = [], [], []
    for path in [*targets.views, *targets.widgets]:
        where = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
        lines = numbered_lines(path)
        iframes += [f"{where}:{number}" for number, line in lines if "<iframe" in line]
        if path in targets.views and len(lines) > MAX_VIEW_LINES:
            oversized.append(f"{where} {len(lines)}줄 (기준 {MAX_VIEW_LINES})")
        no_spinner += [f"{where}:{number} loading 분기에 .spinner 없음" for number in spinnerless_loading_branches(lines)]
    return report("iframe", iframes) + report("View 비대", oversized) + report("스피너", no_spinner)


def imported_model_names(source: Path) -> list[tuple[int, str]]:
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    return [
        (node.lineno, alias.name)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "app.db.models"
        for alias in node.names
    ]


def defined_model_names(models_py: Path) -> set[str]:
    tree = ast.parse(models_py.read_text(encoding="utf-8"), filename=str(models_py))
    names = {node.name for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef))}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names |= {target.id for target in node.targets if isinstance(target, ast.Name)}
    return names


def check_backend(root: Path, targets: Targets) -> list[Finding]:
    defined = defined_model_names(root / "backend" / "app" / "db" / "models.py")
    missing, forbidden = [], []
    for path in [p for p in (targets.router, targets.service) if p]:
        where = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
        missing += [f"{where}:{line} {name} 이 models.py 에 없다" for line, name in imported_model_names(path) if name not in defined]
        for number, line in numbered_lines(path):
            code = line.split("#", 1)[0]  # 주석은 검사하지 않는다
            forbidden += [f"{where}:{number} {needle} — {why}" for needle, why in FORBIDDEN_BACKEND.items() if needle in code]
    findings = report("모델 심볼 실존", missing) + report("금지 API", forbidden)
    if targets.router:
        main_py = (root / "backend" / "app" / "main.py").read_text(encoding="utf-8")
        registered = re.search(rf"include_router\(\s*{re.escape(targets.router.stem)}\.router", main_py)
        findings += report("라우터 등록", [] if registered else [f"main.py 에 {targets.router.stem}.router 등록 없음"])
    return findings


def check_buildless(root: Path) -> list[Finding]:
    found = [name for name in ("package.json", "node_modules") if (root / "frontend" / name).exists()]
    return report("빌드리스", [f"frontend/{name} 존재" for name in found])


def run_checks(root: Path, targets: Targets, preserve_ui: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    if targets.css:
        findings += check_css(root, targets.css, preserve_ui) + check_css_link(root, targets.css)
    else:
        findings.append(Finding("피처 CSS", "SKIP", "대상 없음 — --css 로 지정"))
    if targets.views or targets.widgets:
        findings += check_frontend(root, targets)
    else:
        findings.append(Finding("View·위젯", "SKIP", "대상 없음 — --view / --widget 로 지정"))
    if targets.router or targets.service:
        findings += check_backend(root, targets)
    else:
        findings.append(Finding("라우터·서비스", "SKIP", "대상 없음 — --router / --service 로 지정"))
    return findings + check_buildless(root)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = (args.root or find_project_root(Path(__file__).resolve().parent)).resolve()
    targets = resolve_targets(root, args.feature, args)
    if not any([targets.css, targets.views, targets.widgets, targets.router, targets.service]):
        print(f"'{args.feature}' 에 해당하는 파일을 찾지 못했습니다. --help 의 경로 옵션으로 지정하라.", file=sys.stderr)
        return 2
    try:
        findings = run_checks(root, targets, args.preserve_ui)
    except (OSError, SyntaxError) as exc:
        print(f"검사 대상 파일을 읽거나 파싱하지 못했습니다: {exc}", file=sys.stderr)
        return 2
    for finding in findings:
        print(f"[{finding.status}] {finding.check}" + (f" — {finding.detail}" if finding.detail else ""))
    failed = sum(1 for finding in findings if finding.status == "FAIL")
    print(f"FAIL {failed}건")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
