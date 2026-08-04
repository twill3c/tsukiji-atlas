#!/usr/bin/env python3
"""looplog.py — 構造化ループログの記録・検証・要約・エクスポート。

Python 標準ライブラリのみで動作する(LL-00e)。

使い方:
  python scripts/looplog.py append  --loop loop_003 --event loop_start \
      --data goal="Silver層の結合実装" spec_refs='["F-03"]' \
             scaffold_version=1.2.0 agent=claude-code
  python scripts/looplog.py append  --loop loop_003 --event failure \
      --data code=GEN-REGRESS severity=S2 detected_stage=5 \
             summary="T-032がデグレード" resolution=rollback
  python scripts/looplog.py validate
  python scripts/looplog.py summary --loop loop_003
  python scripts/looplog.py export  --out out/
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

SCHEMA_VERSION = "1.0"
JST = dt.timezone(dt.timedelta(hours=9))

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR_DEFAULT = "logs/loops"
TAXONOMY_PATH = REPO_ROOT / "schema" / "taxonomy.json"

ENVELOPE_REQUIRED = ("v", "ts", "project", "loop_id", "event", "data")

EVENT_SPECS: dict[str, dict[str, tuple[type, ...]]] = {
    # event: {field: (types...)} — 必須フィールドのみ列挙(LOOP_LOG_SPEC §2)
    "loop_start": {
        "goal": (str,),
        "spec_refs": (list,),
        "scaffold_version": (str,),
        "agent": (str,),
    },
    "stage_end": {
        "stage": (int,),
        "stage_name": (str,),
        "result": (str,),
    },
    "test_run": {
        "command": (str,),
        "passed": (int,),
        "failed": (int,),
    },
    "failure": {
        "code": (str,),
        "severity": (str,),
        "detected_stage": (int,),
        "summary": (str,),
        "resolution": (str,),
    },
    "escalation": {
        "reason": (str,),
        "question": (str,),
    },
    "commit": {
        "sha": (str,),
        "kind": (str,),
    },
    "loop_end": {
        "outcome": (str,),
        "failure_count": (int,),
        "summary": (str,),
    },
}

ENUMS = {
    ("stage_end", "result"): {"pass", "fail", "skip"},
    ("loop_end", "outcome"): {"success", "partial", "aborted"},
    # data / spec はプロジェクト規約のコミット種別(HC-003: data 専用コミット、
    # スペック駆動プロジェクトの spec: コミット)を写像なしで記録するための拡張
    ("commit", "kind"): {"feat", "fix", "test", "docs", "refactor", "chore", "data", "spec"},
}


def load_taxonomy() -> dict:
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        return json.load(f)


def now_ts() -> str:
    return dt.datetime.now(JST).isoformat(timespec="seconds")


def detect_project() -> str:
    """プロジェクト名はリポジトリのディレクトリ名から推定(--project で上書き可)。"""
    return Path.cwd().name


# ---------------------------------------------------------------- validate

def validate_record(rec: dict, taxonomy: dict, lineno: int, fname: str) -> list[str]:
    errs: list[str] = []
    loc = f"{fname}:{lineno}"

    for field in ENVELOPE_REQUIRED:
        if field not in rec:
            errs.append(f"{loc}: エンベロープ必須フィールド欠落: {field}")
    if errs:
        return errs

    event = rec["event"]
    if event not in EVENT_SPECS:
        return [f"{loc}: 未知のイベント種別: {event}"]

    data = rec["data"]
    if not isinstance(data, dict):
        return [f"{loc}: data はオブジェクトであること"]

    for field, types in EVENT_SPECS[event].items():
        if field not in data:
            errs.append(f"{loc}: {event}.data 必須フィールド欠落: {field}")
        elif not isinstance(data[field], types):
            errs.append(f"{loc}: {event}.data.{field} の型が不正")

    for (ev, field), allowed in ENUMS.items():
        if event == ev and field in data and data[field] not in allowed:
            errs.append(f"{loc}: {event}.data.{field}={data[field]!r} は {sorted(allowed)} のいずれかであること")

    if event == "failure":
        code = data.get("code")
        if code is not None and code not in taxonomy["codes"]:
            errs.append(f"{loc}: 失敗コード {code!r} は taxonomy.json に存在しない")
        sev = data.get("severity")
        if sev is not None and sev not in taxonomy["severities"]:
            errs.append(f"{loc}: severity {sev!r} は {sorted(taxonomy['severities'])} のいずれかであること")
        res = data.get("resolution")
        if res is not None and res not in taxonomy["resolutions"]:
            errs.append(f"{loc}: resolution {res!r} は taxonomy.json の resolutions に存在しない")
        if res == "harness_fix" and not data.get("harness_ref"):
            errs.append(f"{loc}: resolution=harness_fix には harness_ref(HC-xxx)が必須(LL-04)")

    return errs


def validate_file(path: Path, taxonomy: dict) -> list[str]:
    errs: list[str] = []
    records: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                errs.append(f"{path.name}:{lineno}: JSON 解析エラー: {e}")
                continue
            errs.extend(validate_record(rec, taxonomy, lineno, path.name))
            records.append(rec)

    if not records:
        return errs or [f"{path.name}: レコードがありません"]

    expected_loop = path.stem
    for i, rec in enumerate(records, 1):
        if rec.get("loop_id") and rec["loop_id"] != expected_loop:
            errs.append(f"{path.name}:{i}: loop_id={rec['loop_id']!r} がファイル名と不一致(LL-00b)")

    ts_list = [r.get("ts", "") for r in records]
    if ts_list != sorted(ts_list):
        errs.append(f"{path.name}: ts が時系列順でない(LL-00a)")

    if records[0].get("event") != "loop_start":
        errs.append(f"{path.name}: 先頭イベントが loop_start でない(LL-01)")

    ends = [r for r in records if r.get("event") == "loop_end"]
    if len(ends) > 1:
        errs.append(f"{path.name}: loop_end が複数ある")
    if ends:
        if records[-1].get("event") != "loop_end":
            errs.append(f"{path.name}: loop_end の後にレコードがある(LL-07)")
        actual = sum(1 for r in records if r.get("event") == "failure")
        declared = ends[0].get("data", {}).get("failure_count")
        if declared is not None and declared != actual:
            errs.append(
                f"{path.name}: loop_end.failure_count={declared} だが failure レコードは {actual} 件(LL-07)"
            )
    return errs


def iter_log_files(log_dir: Path):
    yield from sorted(log_dir.glob("*.jsonl"))


def cmd_validate(args) -> int:
    taxonomy = load_taxonomy()
    log_dir = Path(args.log_dir)
    if not log_dir.is_dir():
        print(f"ログディレクトリがありません: {log_dir}(記録がなければ合格扱い)")
        return 0
    all_errs: list[str] = []
    n = 0
    for path in iter_log_files(log_dir):
        n += 1
        all_errs.extend(validate_file(path, taxonomy))
    if all_errs:
        print(f"NG — {n} ファイル中 {len(all_errs)} 件の違反:")
        for e in all_errs:
            print(f"  - {e}")
        return 1
    print(f"OK — {n} ファイル、違反なし")
    return 0


# ---------------------------------------------------------------- append

def parse_kv(pairs: list[str], str_fields: frozenset[str] = frozenset()) -> dict:
    """key=value 列を data オブジェクトに変換。値は JSON として解釈を試み、失敗時は文字列。

    str_fields に挙がったキーは JSON 解釈をせず常に文字列として扱う。
    指数表記に見える git 短縮 sha(72817e6 等)が float 化して記録拒否される
    問題への恒久対処(HC-005)。
    """
    data: dict = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"--data は key=value 形式で指定してください: {pair!r}")
        key, _, raw = pair.partition("=")
        if key in str_fields:
            data[key] = raw
            continue
        try:
            data[key] = json.loads(raw)
        except json.JSONDecodeError:
            data[key] = raw
    return data


def cmd_append(args) -> int:
    taxonomy = load_taxonomy()
    # スキーマ上 str 固定のフィールドは生文字列のまま受け取る(HC-005)
    str_fields = frozenset(
        f for f, types in EVENT_SPECS.get(args.event, {}).items() if types == (str,)
    )
    rec = {
        "v": SCHEMA_VERSION,
        "ts": args.ts or now_ts(),
        "project": args.project or detect_project(),
        "loop_id": args.loop,
        "event": args.event,
        "data": parse_kv(args.data or [], str_fields),
    }
    errs = validate_record(rec, taxonomy, 0, "(new)")
    if errs:
        print("記録拒否 — スキーマ違反:")
        for e in errs:
            print(f"  - {e}")
        return 1

    # ツーストライク規則(LL-10)の警告: 同一コードの既存件数を数える
    if args.event == "failure":
        code = rec["data"]["code"]
        prior = 0
        log_dir = Path(args.log_dir)
        if log_dir.is_dir():
            for path in iter_log_files(log_dir):
                with open(path, encoding="utf-8") as f:
                    for line in f:
                        try:
                            r = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if r.get("event") == "failure" and r.get("data", {}).get("code") == code:
                            prior += 1
        total = prior + 1
        if rec["data"].get("severity") == "S1" and not rec["data"].get("harness_ref"):
            print(f"⚠ LL-12: S1 失敗です。HARNESS_CHANGELOG への起票と harness_ref の追記が必要です。")
        elif total == 2:
            print(f"⚠ LL-10: 失敗コード {code} が累計 {total} 回目です。HARNESS_CHANGELOG への起票が必要です。")
        elif total > 2 and not rec["data"].get("harness_ref"):
            print(f"⚠ LL-10: {code} は累計 {total} 回目。起票済み HC への harness_ref を付けてください。")

    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"{args.loop}.jsonl"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"記録 → {path}({args.event})")
    return 0


# ---------------------------------------------------------------- summary

def cmd_summary(args) -> int:
    log_dir = Path(args.log_dir)
    paths = [log_dir / f"{args.loop}.jsonl"] if args.loop else list(iter_log_files(log_dir))
    taxonomy = load_taxonomy()
    for path in paths:
        if not path.exists():
            print(f"見つかりません: {path}")
            continue
        records = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        start = next((r for r in records if r["event"] == "loop_start"), None)
        end = next((r for r in records if r["event"] == "loop_end"), None)
        failures = [r for r in records if r["event"] == "failure"]
        tests = [r for r in records if r["event"] == "test_run"]
        commits = [r for r in records if r["event"] == "commit"]

        print(f"── {path.stem}" + (f"({start['project']})" if start else ""))
        if start:
            print(f"   目標: {start['data']['goal']}  [{', '.join(start['data']['spec_refs'])}]"
                  f"  scaffold v{start['data']['scaffold_version']}")
        if end:
            print(f"   結果: {end['data']['outcome']} — {end['data']['summary']}")
        else:
            print("   結果: (進行中 — loop_end 未記録)")
        if tests:
            last = tests[-1]["data"]
            print(f"   テスト: {len(tests)} 回実行、最終 {last['passed']} 合格 / {last['failed']} 不合格")
        print(f"   コミット: {len(commits)} 件 / 失敗: {len(failures)} 件")
        for f_ in failures:
            d = f_["data"]
            name = taxonomy["codes"].get(d["code"], {}).get("name", "?")
            ref = f" → {d['harness_ref']}" if d.get("harness_ref") else ""
            print(f"     [{d['severity']}] {d['code']}({name}): {d['summary']} → {d['resolution']}{ref}")
    return 0


# ---------------------------------------------------------------- export

def flatten(rec: dict) -> dict:
    row = {k: rec[k] for k in ("v", "ts", "project", "loop_id", "event")}
    for k, v in rec["data"].items():
        row[f"data_{k}"] = json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
    return row


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # BOM 付き: Power BI/Excel の日本語対策
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"出力 → {path}({len(rows)} 行)")


def cmd_export(args) -> int:
    taxonomy = load_taxonomy()
    log_dir = Path(args.log_dir)
    out = Path(args.out)

    events: list[dict] = []
    for path in iter_log_files(log_dir) if log_dir.is_dir() else []:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))

    # fact_events: 全イベント(明細粒度)
    write_csv(out / "fact_events.csv", [flatten(r) for r in events])

    # fact_loops: ループ粒度
    loops: dict[tuple, dict] = {}
    for r in events:
        key = (r["project"], r["loop_id"])
        row = loops.setdefault(key, {
            "project": r["project"], "loop_id": r["loop_id"],
            "started_at": None, "ended_at": None, "goal": None,
            "scaffold_version": None, "agent": None, "outcome": None,
            "n_failures": 0, "n_commits": 0, "n_test_runs": 0,
            "last_tests_passed": None, "last_tests_failed": None,
        })
        d = r["data"]
        if r["event"] == "loop_start":
            row.update(started_at=r["ts"], goal=d["goal"],
                       scaffold_version=d["scaffold_version"], agent=d["agent"])
        elif r["event"] == "loop_end":
            row.update(ended_at=r["ts"], outcome=d["outcome"])
        elif r["event"] == "failure":
            row["n_failures"] += 1
        elif r["event"] == "commit":
            row["n_commits"] += 1
        elif r["event"] == "test_run":
            row["n_test_runs"] += 1
            row["last_tests_passed"] = d["passed"]
            row["last_tests_failed"] = d["failed"]
    write_csv(out / "fact_loops.csv", list(loops.values()))

    # fact_failures: 失敗粒度
    frows = []
    for r in events:
        if r["event"] != "failure":
            continue
        d = r["data"]
        frows.append({
            "ts": r["ts"], "project": r["project"], "loop_id": r["loop_id"],
            "code": d["code"], "severity": d["severity"],
            "detected_stage": d["detected_stage"],
            "introduced_stage": d.get("introduced_stage"),
            "summary": d["summary"], "resolution": d["resolution"],
            "harness_ref": d.get("harness_ref"),
        })
    write_csv(out / "fact_failures.csv", frows)

    # dim_failure_taxonomy: taxonomy.json から生成
    drows = [
        {"code": code, "category": info["category"],
         "category_name": taxonomy["categories"][info["category"]],
         "name": info["name"], "definition": info["definition"]}
        for code, info in taxonomy["codes"].items()
    ]
    write_csv(out / "dim_failure_taxonomy.csv", drows)

    # ツーストライク監視ビュー: コード別累計と起票状況
    counts = Counter(f["code"] for f in frows)
    trows = [
        {"code": code, "total": n,
         "needs_hc": n >= 2,
         "has_hc_ref": any(f["harness_ref"] for f in frows if f["code"] == code)}
        for code, n in sorted(counts.items(), key=lambda x: -x[1])
    ]
    write_csv(out / "view_two_strike.csv", trows)
    return 0


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="構造化ループログ CLI")
    p.add_argument("--log-dir", default=LOG_DIR_DEFAULT, help=f"ログ置き場(既定: {LOG_DIR_DEFAULT})")
    sub = p.add_subparsers(dest="cmd", required=True)

    ap = sub.add_parser("append", help="イベントを 1 件記録する")
    ap.add_argument("--loop", required=True)
    ap.add_argument("--event", required=True, choices=sorted(EVENT_SPECS))
    ap.add_argument("--project", help="省略時はカレントディレクトリ名")
    ap.add_argument("--ts", help="省略時は現在時刻(JST)")
    ap.add_argument("--data", nargs="*", metavar="key=value")
    ap.set_defaults(func=cmd_append)

    vp = sub.add_parser("validate", help="全ログをスキーマ・規則検証する(CI 用)")
    vp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("summary", help="人間向け要約を表示する")
    sp.add_argument("--loop", help="省略時は全ループ")
    sp.set_defaults(func=cmd_summary)

    ep = sub.add_parser("export", help="Power BI 取込用 CSV 群を出力する")
    ep.add_argument("--out", default="out")
    ep.set_defaults(func=cmd_export)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
