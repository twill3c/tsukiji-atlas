"""統合テスト(T-051)。フィクスチャから全層再現、ネットワーク不要(N-01)。"""
import json
from pathlib import Path

import pytest

from extract.common import load_area
from gold import export_geojson, validate
from transform import pipeline

FIXTURES = Path(__file__).resolve().parent.parent / "data" / "fixtures"
AREA = "tsukiji-akashicho"

pytestmark = pytest.mark.integration


# T-051(N-01/F-04/F-05): bronze 解析 → silver → gold をフィクスチャのみで通す
def test_full_pipeline_from_fixtures(tmp_path):
    base_payload = json.loads((FIXTURES / "wikidata_sites_base.json").read_text(encoding="utf-8"))
    od_text = (FIXTURES / "tokyo_od_cultural_property.csv").read_text(encoding="utf-8")

    silver_records, needs_review = pipeline.build_silver(
        base_payload=base_payload,
        heritage_rows=[{"qid": "Q4844361", "heritage": "重要文化財"}],
        dates_rows=[{"qid": "Q943255", "year": 1657}],
        od_text=od_text,
        curated_path=FIXTURES / "curated_ok.csv",
        area=AREA,
    )

    by_name = {r["name"]: r for r in silver_records}
    merged = by_name["築地本願寺"]  # curated_ok.csv の qid=Q943255 と統合される
    assert merged["source"] == "curated" and merged["qid"] == "Q943255"
    assert merged["name_norm"] == "築地本願寺"
    assert (merged["lat"], merged["lon"]) == (35.666389, 139.772222)  # curated(verified) 優先
    assert by_name["波除稲荷神社"]["era"] is None  # wikidata 単独・年不明 → needs_review
    assert any(r["name"] == "波除稲荷神社" for r in needs_review)

    gold_ready, excluded = pipeline.select_gold_records(silver_records)
    assert all(r.get("site_id") and r.get("verified") for r in gold_ready)
    assert any(r["name"] == "軍艦操練所跡" for r in excluded)  # verified=false は除外(Q-05)

    fc, counts = export_geojson.build(gold_ready, excluded=len(excluded))
    errors = validate.run(fc, counts, area_cfg=load_area(AREA), min_features=2)
    assert errors == []
    assert counts["excluded"] == 1

    out_dir = tmp_path / "data"
    export_geojson.write(fc, counts, out_dir=out_dir)
    assert json.loads((out_dir / "sites.geojson").read_text(encoding="utf-8"))["features"]
