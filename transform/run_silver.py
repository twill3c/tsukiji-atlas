"""Silver 生成 CLI: python -m transform.run_silver [--area tsukiji-akashicho]

data/bronze/ を読み、data/silver/sites.json と needs_review.csv を出力する。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from extract.common import load_area
from transform import pipeline

BRONZE_DIR = Path("data/bronze")
SILVER_DIR = Path("data/silver")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--area", default="tsukiji-akashicho")
    args = p.parse_args()
    cfg = load_area(args.area)

    read = lambda name: json.loads((BRONZE_DIR / name).read_text(encoding="utf-8"))
    od_path = BRONZE_DIR / "tokyo_od.csv"
    records, needs_review = pipeline.build_silver(
        base_payload=read("wikidata_sites_base.json"),
        heritage_rows=pipeline.parse_heritage_bindings(read("wikidata_sites_heritage.json")),
        dates_rows=pipeline.parse_dates_bindings(read("wikidata_sites_dates.json")),
        od_text=od_path.read_text(encoding="utf-8") if od_path.exists() else None,
        curated_path=cfg["curated_csv"],
        area=args.area,
    )

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    (SILVER_DIR / "sites.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    pipeline.write_needs_review(needs_review, SILVER_DIR / "needs_review.csv")
    print(f"silver: {len(records)} 件 / needs_review: {len(needs_review)} 件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
