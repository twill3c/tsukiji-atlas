"""Gold: sites.geojson + counts.json の生成(F-05)。

出力は SPEC §5 の 1 ファイル契約。counts.json は品質レポート兼
地図 UI のサマリ表示用(件数・時代別・分野別・除外件数)。
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from gold.contract import OPTIONAL_PROPS, REQUIRED_PROPS


def split_unverified(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """verified=False を Gold から除外する(Q-05)。除外分は件数計上用に返す。"""
    kept = [r for r in records if r.get("verified") is not False]
    dropped = [r for r in records if r.get("verified") is False]
    return kept, dropped


def to_feature(rec: dict) -> dict:
    props = {k: rec[k] for k in REQUIRED_PROPS}
    for k in OPTIONAL_PROPS:
        if rec.get(k) is not None:  # year 不明・qid 未判明は省略(SPEC §5)
            props[k] = rec[k]
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [rec["lon"], rec["lat"]]},
        "properties": props,
    }


def build(records: list[dict], *, excluded: int) -> tuple[dict, dict]:
    """(FeatureCollection, counts) を返す。書き出しは write() が担う。"""
    features = [to_feature(r) for r in records]
    counts = {
        "total": len(features),
        "by_era": dict(Counter(r["era"] for r in records)),
        "by_category": dict(Counter(r["category"] for r in records)),
        "excluded": excluded,
    }
    return {"type": "FeatureCollection", "features": features}, counts


def write(fc: dict, counts: dict, out_dir: str | Path = "public/data") -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "sites.geojson").write_text(
        json.dumps(fc, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    (out / "counts.json").write_text(
        json.dumps(counts, ensure_ascii=False, indent=1), encoding="utf-8"
    )
