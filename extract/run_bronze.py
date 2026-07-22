"""Bronze 取得 CLI: python -m extract.run_bronze [--area tsukiji-akashicho]

実 Wikidata / 都 OD への疎通は本 CLI の手動実行のみ(TEST_SPEC 実行規約)。
結果は data/bronze/(gitignore)に保存し、実行はループログに test_run として記録する。
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from extract import tokyo_od, wikidata
from extract.common import load_area

BRONZE_DIR = Path("data/bronze")
QUERIES = ("sites_base", "sites_heritage", "sites_dates")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--area", default="tsukiji-akashicho")
    args = p.parse_args()
    load_area(args.area)  # 存在確認(エリアキー起点の規律)

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    for name in QUERIES:
        payload = wikidata.fetch_sparql(wikidata.load_query(name))
        n = len(payload["results"]["bindings"])
        (BRONZE_DIR / f"wikidata_{name}.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )
        print(f"wikidata_{name}: {n} 行")
        time.sleep(2)  # リクエスト間隔(N-02)

    od_text = tokyo_od.fetch_csv()
    (BRONZE_DIR / "tokyo_od.csv").write_text(od_text, encoding="utf-8")
    print(f"tokyo_od: {len(od_text.splitlines()) - 1} 行")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
