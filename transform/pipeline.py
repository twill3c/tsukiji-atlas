"""Silver 組み立てと Gold 選別(F-04/F-05 の結線)。

CLI(extract.run_bronze / transform.run_silver / gold.run_gold)から呼ぶ純粋ロジック。
テストはフィクスチャで全層再現する(N-01、T-051)。
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from extract import curated as curated_mod
from extract import tokyo_od, wikidata
from transform import dims, merge, normalize

_YEAR_RE = re.compile(r"^[+-]?(\d{1,4})")


def year_from_inception(value: str) -> int | None:
    """Wikidata の時刻値(+1868-01-01T00:00:00Z 等)→ 西暦。"""
    m = _YEAR_RE.match(value or "")
    return int(m.group(1)) if m else None


def parse_heritage_bindings(payload: dict) -> list[dict]:
    """sites_heritage.rq の応答 → [{qid, heritage}]。"""
    rows = []
    for b in payload["results"]["bindings"]:
        rows.append({
            "qid": b["item"]["value"].rsplit("/", 1)[-1],
            "heritage": b.get("heritageLabel", {}).get("value"),
        })
    return rows


def parse_dates_bindings(payload: dict) -> list[dict]:
    """sites_dates.rq の応答 → [{qid, year}]。"""
    rows = []
    for b in payload["results"]["bindings"]:
        rows.append({
            "qid": b["item"]["value"].rsplit("/", 1)[-1],
            "year": year_from_inception(b.get("inception", {}).get("value")),
        })
    return rows


def build_silver(
    *,
    base_payload: dict,
    heritage_rows: list[dict],
    dates_rows: list[dict],
    od_text: str | None,
    curated_path: str | Path,
    area: str,
) -> tuple[list[dict], list[dict]]:
    """(silver_records, needs_review) を返す。"""
    wd = wikidata.parse_sparql_json(base_payload, area=area)
    heritage_by_qid: dict[str, list[str]] = {}
    for row in heritage_rows:
        if row.get("heritage"):
            heritage_by_qid.setdefault(row["qid"], []).append(row["heritage"])
    year_by_qid = {r["qid"]: r["year"] for r in dates_rows if r.get("year")}
    for rec in wd:
        if rec["qid"] in heritage_by_qid:
            rec["heritage"] = heritage_by_qid[rec["qid"]]
        if rec["qid"] in year_by_qid:
            rec["year"] = year_by_qid[rec["qid"]]

    verified, unverified = curated_mod.load(curated_path)
    records = merge.merge_curated_wikidata(verified + unverified, wd)
    if od_text:
        records.extend(tokyo_od.parse_csv_text(od_text, area=area))

    normalize.add_name_norm(records)
    records, needs_review = dims.assign_era(records)
    return records, needs_review


def select_gold_records(silver_records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Gold 契約(SPEC §5)を満たしうるのは curated 由来(site_id あり)のみ。
    verified=false は除外リストへ(Q-05)。wikidata/tokyo_od 単独レコードは
    curated 化(qid 指定名寄せ)されるまで Gold に入れない。"""
    curated_derived = [r for r in silver_records if r.get("site_id")]
    gold_ready = [r for r in curated_derived if r.get("verified")]
    excluded = [r for r in curated_derived if not r.get("verified")]
    return gold_ready, excluded


def write_needs_review(needs_review: list[dict], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["qid", "site_id", "name", "year", "source"])
        for r in needs_review:
            w.writerow([r.get("qid") or "", r.get("site_id") or "", r["name"], r.get("year") or "", r["source"]])
