"""Gold 生成 CLI: python -m gold.run_gold [--area tsukiji-akashicho]

validate(Q-01〜05)に合格した場合のみ web/public/data/ へ書き込む。
不合格時はエラーを表示して終了コード 1(壊れたデータで 1 ファイル契約を上書きしない)。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from extract.common import load_area
from gold import export_geojson, validate
from transform import pipeline

SILVER_PATH = Path("data/silver/sites.json")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--area", default="tsukiji-akashicho")
    p.add_argument("--out", default="web/public/data")
    args = p.parse_args()
    cfg = load_area(args.area)

    silver_records = json.loads(SILVER_PATH.read_text(encoding="utf-8"))
    gold_ready, excluded = pipeline.select_gold_records(silver_records)
    fc, counts = export_geojson.build(gold_ready, excluded=len(excluded))

    errors = validate.run(fc, counts, area_cfg=cfg)
    if errors:
        print(f"validate 不合格({len(errors)} 件)— 出力しません:")
        for e in errors[:20]:
            print(f"  - {e}")
        if len(errors) > 20:
            print(f"  … ほか {len(errors) - 20} 件")
        return 1

    export_geojson.write(fc, counts, out_dir=args.out)
    print(f"gold: {counts['total']} 件(除外 {counts['excluded']})→ {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
