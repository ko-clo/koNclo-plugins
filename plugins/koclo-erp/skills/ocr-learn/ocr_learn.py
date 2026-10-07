# -*- coding: utf-8 -*-
"""자동판정 PaddleOCR 학습 루프 — koclo-vm 에서 워커 venv 로 실행한다(/ocr-learn 스킬이 올려서 부른다).

  collect(기본): 그날 메인(Claude) erp<날짜>_* ↔ 테스트(PaddleOCR) test_erp<날짜>_* 결과를 매장별로 짝지어
                 회귀 세트(dataset/)에 쌓고 일치율·오답 보고서를 낸다. 결과가 없으면 에러 없이 상황만 알린다.
                 판독은 DB auto_judge.ocr_batches, 원시 OCR 은 auto_judge.ocr_raw_batches 에서 읽는다.
  reparse     : 수정한 auto_judge_paddle.py 로 회귀 세트 전체의 원시 OCR 을 다시 파싱해 재채점한다(재OCR 없음).

사용:
  python ocr_learn.py collect [--date YYYY-MM-DD]
  python ocr_learn.py reparse --code <auto_judge_paddle.py 가 있는 폴더>
"""
import argparse
import datetime
import glob
import importlib
import json
import os
import re
import sys

MAIN_BASE = os.environ.get('OCR_LEARN_MAIN', '/home/konclo/autojudge')
TEST_BASE = os.environ.get('OCR_LEARN_TEST', '/home/konclo/autojudge-test')
WORK = os.path.expanduser(os.environ.get('OCR_LEARN_WORK', '~/paddle_dev/ocr_learn'))
DATASET = os.path.join(WORK, 'dataset')
REPORTS = os.path.join(WORK, 'reports')
TEST_PREFIX = 'test_'
PART_MARK = '__rc'               # 여러 장 분리 조각 표식(auto_judge_layout.MARK)
RAW_TABLE = 'auto_judge.ocr_raw_batches'   # 테스트 워커(auto_judge_ocr_store.save_raw)가 쓰는 원시 OCR 표
SUMMARY_FIELDS = ('전잔', '당일합계', '당잔', '매입전잔', '매입잔액', '부가세', '최종잔', '반입액', '입금')
SUPPLIER_PREFIX_LENGTH = 2       # 상호 앞 두 글자 같거나 포함관계면 같은 사입처
MIN_LATIN_NAME = 4               # 병기 영문 상호 일치로 판정할 최소 길이
MISMATCH_EXAMPLES = 15           # 보고서에 항목별로 보여줄 오답 예시 수


# ─────────────────────────── 비교 ───────────────────────────

def normalize_name(text):
    return re.sub(r'[^0-9a-z가-힣]', '', str(text or '').lower())


def is_same_supplier(a, b):
    latin_a = re.sub(r'[^a-z]', '', str(a or '').lower())
    latin_b = re.sub(r'[^a-z]', '', str(b or '').lower())
    if len(latin_a) >= MIN_LATIN_NAME and latin_a == latin_b:
        return True
    a, b = normalize_name(a), normalize_name(b)
    if not a or not b:
        return False
    return a in b or b in a or a[:SUPPLIER_PREFIX_LENGTH] == b[:SUPPLIER_PREFIX_LENGTH]


def item_total(record):
    return sum(int(i.get('amount') or 0) for i in record.get('items') or [])


def compare_records(truth, other):
    truth_summary, other_summary = truth.get('summary') or {}, other.get('summary') or {}
    scored = [f for f in SUMMARY_FIELDS if truth_summary.get(f) is not None]
    matched = [f for f in scored if other_summary.get(f) == truth_summary.get(f)]
    return {
        'supplier_truth': truth.get('supplier_raw'), 'supplier_paddle': other.get('supplier_raw'),
        'supplier_ok': is_same_supplier(truth.get('supplier_raw'), other.get('supplier_raw')),
        'date_truth': truth.get('rcpt_date'), 'date_paddle': other.get('rcpt_date'),
        'date_ok': truth.get('rcpt_date') == other.get('rcpt_date'),
        'txn_ok': truth.get('txn_type') == other.get('txn_type'),
        'summary_matched': len(matched), 'summary_scored': len(scored),
        'summary_miss': [f for f in scored if f not in matched],
        'amount_truth': item_total(truth), 'amount_paddle': item_total(other),
        'amount_ok': item_total(truth) == item_total(other),
    }


def _score(row):
    return 4 * row['supplier_ok'] + 2 * row['amount_ok'] + row['date_ok'] + row['summary_matched']


def original_of(name):
    return name.split(PART_MARK)[0]


def compare_sets(truth, paddle):
    """원본 사진별로 조각을 내용 기준으로 짝짓는다(두 엔진의 조각 번호 순서가 달라도 된다)."""
    groups = {}
    for name in truth:
        groups.setdefault(original_of(name), [[], []])[0].append(name)
    for name in paddle:
        groups.setdefault(original_of(name), [[], []])[1].append(name)
    rows, split_diff = [], []
    for original, (truth_names, paddle_names) in sorted(groups.items()):
        if len(truth_names) != len(paddle_names):
            split_diff.append({'original': original, 'claude': len(truth_names), 'paddle': len(paddle_names)})
        candidates = sorted(((compare_records(truth[t], paddle[p]), t, p) for t in truth_names for p in paddle_names),
                            key=lambda c: -_score(c[0]))
        used_t, used_p = set(), set()
        for row, t, p in candidates:
            if t in used_t or p in used_p:
                continue
            used_t.add(t)
            used_p.add(p)
            rows.append({'file': t, 'paddle_file': p, **row})
    return rows, split_diff


def summarize(rows, split_diff):
    total = len(rows)
    if not total:
        return {'pairs': 0}
    scored = sum(r['summary_scored'] for r in rows)
    return {
        'pairs': total,
        'supplier': round(100 * sum(r['supplier_ok'] for r in rows) / total, 1),
        'date': round(100 * sum(r['date_ok'] for r in rows) / total, 1),
        'txn': round(100 * sum(r['txn_ok'] for r in rows) / total, 1),
        'summary': round(100 * sum(r['summary_matched'] for r in rows) / scored, 1) if scored else None,
        'amount': round(100 * sum(r['amount_ok'] for r in rows) / total, 1),
        'split_diff': len(split_diff),
    }


def format_summary(label, stats):
    if not stats.get('pairs'):
        return f'{label}: 비교 가능한 영수증 없음'
    return (f"{label}: {stats['pairs']}건 | 품목금액 {stats['amount']}% · 발행처 {stats['supplier']}% · "
            f"날짜 {stats['date']}% · 유형 {stats['txn']}% · 요약 {stats['summary']}% · 분리 차이 {stats['split_diff']}장")


# ─────────────────────────── 수집 ───────────────────────────

def import_main_module(name):
    """메인 워커 모듈을 가져온다 — DB 설정(auto_judge_env · $MAIN_BASE/_db.env)과 판독 저장소를 그대로 쓴다."""
    if MAIN_BASE not in sys.path:
        sys.path.insert(0, MAIN_BASE)
    return importlib.import_module(name)


def connect_db():
    import psycopg2

    return psycopg2.connect(**import_main_module('auto_judge_env').pg_kwargs())


def describe_error(error):
    """예외 → '이름: 첫 줄'. psycopg2 메시지의 LINE·^ 줄이 로그를 여러 줄로 깨지 않게 한다."""
    first_line = (str(error).strip().splitlines() or [''])[0]
    return f'{type(error).__name__}: {first_line}'


def load_records(job_key):
    """판독(auto_judge.ocr_batches)을 배치 이름순으로 펼친다 — 키는 file, 여러 장 조각은 file#partN."""
    _manifest, _site, batches = import_main_module('auto_judge_ocr_store').load(job_key)
    records = {}
    for _batch_name, rows in sorted(batches.items()):
        for record in rows or []:
            name = str(record.get('file') or '')
            if record.get('part'):
                name += f"#part{record['part']}"
            records[name] = record
    return records


def load_engine_records(job_key):
    """load_records + 0건 사유 출력. 조회 실패도 원인을 찍고 빈 결과로 돌린다(그 매장만 건너뛴다)."""
    try:
        records = load_records(job_key)
    except Exception as error:
        print(f'- {job_key}: 판독 0건 — auto_judge.ocr_batches 조회 실패({describe_error(error)})')
        return {}
    if not records:
        print(f'- {job_key}: 판독 0건 — auto_judge.ocr_batches 에 {job_key} 없음')
    return records


def load_raw(job_key):
    """테스트 실행의 원시 OCR(auto_judge.ocr_raw_batches) — {'detect': {...}, 'read': {...}} 병합."""
    merged = {'detect': {}, 'read': {}}
    try:
        connection = connect_db()
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'SELECT payload FROM {RAW_TABLE} WHERE job_key = %s ORDER BY batch_name', (job_key,))
                payloads = [payload for (payload,) in cursor.fetchall()]
        finally:
            connection.close()
    except Exception as error:   # 재채점용 보조 자료 — 없으면 그 날짜만 reparse 에서 빠진다
        print(f'  ⚠ {RAW_TABLE} 조회 실패(건너뜀): {describe_error(error)}')
        return merged
    for raw in payloads:
        merged['detect'].update(raw.get('detect') or {})
        merged['read'].update(raw.get('read') or {})
    return merged


def run_keys(base, prefix, d8):
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(base, '_runs', f'{prefix}erp{d8}_*'))
                  if os.path.isdir(p))


def queue_jobs(date):
    """그날 판정 잡의 큐 상태(auto_judge.queue_jobs) — 결과가 없을 때 왜 없는지 설명하는 재료. DB 를 못 읽으면 빈 목록."""
    try:
        connection = connect_db()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT target_worker, job_key, store, status,
                                         to_char(queued_at AT TIME ZONE 'Asia/Seoul', 'YYYY-MM-DD HH24:MI:SS')
                                    FROM auto_judge.queue_jobs
                                   WHERE work_date = %s AND job_type = 'judge' ORDER BY queued_at""", (date,))
                rows = cursor.fetchall()
        finally:
            connection.close()
    except Exception as error:   # 설명용 보조 정보 — 실패해도 수집 결과 보고는 계속한다
        print(f'  ⚠ 큐 상태 조회 실패(건너뜀): {describe_error(error)}')
        return []
    return [{'queue': worker, 'key': key, 'store': store, 'status': status, 'queued_at': queued_at}
            for worker, key, store, status, queued_at in rows]


def explain_missing(date, main_keys, test_keys):
    print(f'{date} 학습 대상 없음 (메인·테스트 둘 다 있는 매장이 없다)')
    suffixes = sorted({k.split('_', 1)[1] for k in main_keys} | {k.split('_', 2)[2] for k in test_keys})
    for suffix in suffixes:
        has_main = f'erp{date.replace("-", "")}_{suffix}' in main_keys
        has_test = f'{TEST_PREFIX}erp{date.replace("-", "")}_{suffix}' in test_keys
        print(f"- {suffix}: 메인 {'있음' if has_main else '없음'} / 테스트 {'있음' if has_test else '없음'}")
    jobs = queue_jobs(date)
    for job in jobs:
        print(f"  큐[{job['queue']}] {job['store']} {job['key']} — {job['status']} (접수 {job['queued_at']})")
    if not suffixes and not jobs:
        print('- 이 날짜로 실행된 잡이 없다')
    print('→ 같은 날짜·매장을 메인서버와 테스트서버로 모두 실행한 뒤 /ocr-learn 을 다시 실행하세요')


def collect(date):
    d8 = date.replace('-', '')
    main_keys = run_keys(MAIN_BASE, '', d8)
    test_keys = run_keys(TEST_BASE, TEST_PREFIX, d8)
    pairs = [(k, TEST_PREFIX + k) for k in main_keys if TEST_PREFIX + k in test_keys]
    if not pairs:
        explain_missing(date, main_keys, test_keys)
        return 0
    os.makedirs(REPORTS, exist_ok=True)
    report = {'date': date, 'pairs': []}
    for main_key, test_key in pairs:
        truth = load_engine_records(main_key)
        paddle = load_engine_records(test_key)
        if not truth or not paddle:
            continue
        engines = {r.get('ocr_engine', 'claude') for r in paddle.values()}
        if 'paddle' not in engines:
            print(f'- {test_key}: 테스트 결과가 PaddleOCR 이 아니다(엔진 전환 전 Claude 실행) — 건너뜀')
            continue
        raw = load_raw(test_key)
        save_dataset(date, main_key, test_key, truth, paddle, raw)
        rows, split_diff = compare_sets(truth, paddle)
        stats = summarize(rows, split_diff)
        print(format_summary(main_key, stats))
        if not raw['read']:
            print(f'  ⚠ 원시 OCR 없음({RAW_TABLE} 에 {test_key} 없음) — 이 날짜는 reparse 재채점에서 빠진다')
        report['pairs'].append({'main': main_key, 'test': test_key, 'stats': stats,
                                'split_diff': split_diff, 'mismatches': mismatch_examples(rows)})
    if not report['pairs']:
        print(f'{date} 학습 대상 없음 — PaddleOCR 로 돈 테스트 결과가 없다. '
              f'테스트서버로 다시 실행한 뒤 /ocr-learn 을 다시 실행하세요')
        return 0
    path = os.path.join(REPORTS, f'{date}.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print(f'보고서: {path}')
    print(format_summary('회귀 세트 전체(현재 파서 결과 기준)', score_dataset(None)))
    return 0


def mismatch_examples(rows):
    def pick(condition, fields):
        return [{k: r[k] for k in ('file', *fields)} for r in rows if condition(r)][:MISMATCH_EXAMPLES]
    return {
        'supplier': pick(lambda r: not r['supplier_ok'], ('supplier_truth', 'supplier_paddle')),
        'amount': pick(lambda r: not r['amount_ok'], ('amount_truth', 'amount_paddle')),
        'summary': pick(lambda r: r['summary_miss'], ('summary_miss',)),
        'date': pick(lambda r: not r['date_ok'], ('date_truth', 'date_paddle')),
    }


def save_dataset(date, main_key, test_key, truth, paddle, raw):
    folder = os.path.join(DATASET, f'{date}_{main_key.split("_", 1)[1]}')
    os.makedirs(folder, exist_ok=True)
    for name, data in (('truth.json', truth), ('paddle.json', paddle), ('raw.json', raw),
                       ('meta.json', {'date': date, 'main_key': main_key, 'test_key': test_key})):
        with open(os.path.join(folder, name), 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False)


# ─────────────────────────── 재채점 ───────────────────────────

def reparse_records(raw, parser):
    records = {}
    for name, result in (raw.get('read') or {}).items():
        if 'lines' in result:
            records[name] = parser.parse_receipt(result['lines'], name, result['height'], result['width'])
    return records


def score_dataset(parser):
    """회귀 세트 전체 채점. parser 가 None 이면 저장된 paddle 결과, 있으면 원시 OCR 을 다시 파싱."""
    all_rows, all_split = [], []
    for folder in sorted(glob.glob(os.path.join(DATASET, '*'))):
        try:
            with open(os.path.join(folder, 'truth.json'), encoding='utf-8') as fh:
                truth = json.load(fh)
            if parser is None:
                with open(os.path.join(folder, 'paddle.json'), encoding='utf-8') as fh:
                    paddle = json.load(fh)
            else:
                with open(os.path.join(folder, 'raw.json'), encoding='utf-8') as fh:
                    paddle = reparse_records(json.load(fh), parser)
                if not paddle:
                    print(f'  - {os.path.basename(folder)}: 원시 OCR 없음 — 재채점 제외')
                    continue
        except (OSError, ValueError) as error:
            print(f'  ⚠ {folder} 읽기 실패(건너뜀): {error}')
            continue
        rows, split_diff = compare_sets(truth, paddle)
        if parser is not None:
            print('  ' + format_summary(os.path.basename(folder), summarize(rows, split_diff)))
        all_rows += rows
        all_split += split_diff
    return summarize(all_rows, all_split)


def reparse(code_dir):
    if not glob.glob(os.path.join(DATASET, '*')):
        print('회귀 세트가 비어 있다 — 먼저 /ocr-learn 으로 결과를 수집하세요')
        return 0
    sys.path.insert(0, code_dir)
    parser = importlib.import_module('auto_judge_paddle')
    print(f'파서: {parser.__file__}')
    print(format_summary('저장된 결과(수정 전)', score_dataset(None)))
    print(format_summary('재파싱(수정 후)', score_dataset(parser)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('command', nargs='?', default='collect', choices=('collect', 'reparse'))
    ap.add_argument('--date', default=datetime.date.today().isoformat())
    ap.add_argument('--code', default=TEST_BASE, help='reparse 에 쓸 auto_judge_paddle.py 폴더')
    a = ap.parse_args()
    try:
        datetime.date.fromisoformat(a.date)
    except ValueError:
        print(f'날짜 형식이 아니다: {a.date} (YYYY-MM-DD)')
        return 0
    if a.command == 'reparse':
        return reparse(a.code)
    return collect(a.date)


if __name__ == '__main__':
    sys.exit(main())
