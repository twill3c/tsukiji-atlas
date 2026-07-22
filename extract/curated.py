"""Bronze: 手動キュレーション CSV(F-03)。

verified=false の座標は Gold に流さない(Q-05)。ここで仕分けて両方返し、
件数は品質レポート(counts.json、P3)に計上する。欠損は黙ってスキップしない。
"""
from __future__ import annotations

import csv
from pathlib import Path

REQUIRED_COLUMNS = (
    "site_id", "name", "era", "category", "year", "lat", "lon",
    "summary", "qid", "license", "verified", "area",
)


def _parse_row(row: dict, lineno: int) -> dict:
    flag = (row["verified"] or "").strip().lower()
    if flag not in ("true", "false"):
        raise ValueError(f"curated CSV {lineno} 行目: verified は true/false のみ(実際: {row['verified']!r})")
    return {
        "source": "curated",
        "license": row["license"],
        "area": row["area"],
        "qid": row["qid"] or None,
        "site_id": row["site_id"],
        "name": row["name"],
        "era": row["era"],
        "category": row["category"],
        "year": int(row["year"]) if row["year"] else None,
        "lat": float(row["lat"]) if row["lat"] else None,
        "lon": float(row["lon"]) if row["lon"] else None,
        "summary": row["summary"],
        "verified": flag == "true",
    }


def load(path: str | Path) -> tuple[list[dict], list[dict]]:
    """(verified, unverified) の 2 リストを返す(T-014)。必須列欠落は明示的エラー(T-015)。"""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"curated CSV 必須列欠落: {missing}(ファイル: {path})")
        verified: list[dict] = []
        unverified: list[dict] = []
        for lineno, row in enumerate(reader, start=2):
            rec = _parse_row(row, lineno)
            (verified if rec["verified"] else unverified).append(rec)
    return verified, unverified
