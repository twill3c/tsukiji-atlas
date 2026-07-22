"""Gold 層テスト(T-031〜T-036)。固定データ駆動、ネットワーク不要(N-01)。"""
import pytest

from extract.common import load_area
from gold import export_geojson, validate

pytestmark = pytest.mark.unit

AREA = "tsukiji-akashicho"
AREA_CFG = load_area(AREA)  # Q-02: bbox は config/areas から読む(ハードコード禁止)

_ERAS = ["edo_early", "edo_late", "bakumatsu", "meiji", "taisho", "showa", "heisei_reiwa"]
_CATS = ["shrine_temple_church", "samurai_site", "monument_origin", "edu_medical",
         "naval_military", "market_food", "bridge_civil", "literature_arts"]


def make_record(i: int, **over) -> dict:
    """bbox 内の決定的な完全レコードを生成(フィクスチャ相当)。"""
    rec = {
        "source": "curated", "license": "self", "area": AREA,
        "site_id": f"{AREA}-{i:03d}", "name": f"史跡{i:03d}",
        "era": _ERAS[i % len(_ERAS)], "category": _CATS[i % len(_CATS)],
        "year": 1868 + i, "qid": None, "summary": f"史跡{i:03d}の自前要約。",
        "lat": 35.660 + (i % 10) * 0.001, "lon": 139.766 + (i % 10) * 0.001,
        "verified": True,
    }
    rec.update(over)
    return rec


def make_records(n: int) -> list[dict]:
    return [make_record(i + 1) for i in range(n)]


# T-031(F-05/Q-03): GeoJSON 契約 — 必須 properties 充足、era/category が定義キーのみ
def test_geojson_contract():
    records = [make_record(1, qid="Q943255"), make_record(2, year=None)]
    fc, counts = export_geojson.build(records, excluded=0)

    assert fc["type"] == "FeatureCollection"
    assert len(fc["features"]) == 2
    f1 = fc["features"][0]
    assert f1["geometry"]["type"] == "Point"
    lon, lat = f1["geometry"]["coordinates"]  # GeoJSON は [経度, 緯度]
    assert (lat, lon) == (records[0]["lat"], records[0]["lon"])
    props = f1["properties"]
    for key in ("site_id", "name", "era", "category", "summary", "source", "license", "area"):
        assert props[key]
    assert props["qid"] == "Q943255"
    assert "year" not in fc["features"][1]["properties"]  # 不明なら省略(SPEC §5)
    assert "verified" not in props                        # Gold 契約外の列は落とす
    assert validate.run(fc, counts, area_cfg=AREA_CFG, min_features=2) == []


# T-032(Q-02): bbox 検証 — 域外座標が FAIL(bbox は config/areas から読む)
def test_bbox_violation_fails():
    records = make_records(2)
    records[1]["lat"], records[1]["lon"] = 35.683948, 139.77088  # 一石橋(八重洲)= bbox 外
    fc, counts = export_geojson.build(records, excluded=0)

    errors = validate.run(fc, counts, area_cfg=AREA_CFG, min_features=2)
    assert any("Q-02" in e for e in errors)


# T-033(Q-04): site_id / qid 一意性 — 重複注入で FAIL
def test_duplicate_site_id_and_qid_fail():
    dup_site = make_records(3)
    dup_site[2]["site_id"] = dup_site[0]["site_id"]
    fc, counts = export_geojson.build(dup_site, excluded=0)
    assert any("Q-04" in e and "site_id" in e for e in validate.run(fc, counts, area_cfg=AREA_CFG, min_features=3))

    dup_qid = make_records(3)
    dup_qid[0]["qid"] = dup_qid[1]["qid"] = "Q943255"  # 名寄せ後の二重登録を模擬
    fc, counts = export_geojson.build(dup_qid, excluded=0)
    assert any("Q-04" in e and "qid" in e for e in validate.run(fc, counts, area_cfg=AREA_CFG, min_features=3))


# T-034(Q-05): verified=false は Gold に含まれず、counts.json の excluded に計上
def test_unverified_excluded_and_counted():
    records = make_records(3) + [make_record(99, verified=False, name="未検証地物")]
    kept, dropped = export_geojson.split_unverified(records)
    fc, counts = export_geojson.build(kept, excluded=len(dropped))

    assert len(fc["features"]) == 3
    assert all(f["properties"]["name"] != "未検証地物" for f in fc["features"])
    assert counts["excluded"] == 1
    assert validate.run(fc, counts, area_cfg=AREA_CFG, min_features=3) == []


# T-035(Q-01): 件数下限 — 39 件で FAIL、40 件で PASS
def test_min_count_boundary():
    fc39, c39 = export_geojson.build(make_records(39), excluded=0)
    assert any("Q-01" in e for e in validate.run(fc39, c39, area_cfg=AREA_CFG))

    fc40, c40 = export_geojson.build(make_records(40), excluded=0)
    assert validate.run(fc40, c40, area_cfg=AREA_CFG) == []


# T-036(F-05): 独立再計算(三角測量)— 時代別合計 = 総件数 = Feature 数を別経路で照合
def test_counts_triangulation():
    fc, counts = export_geojson.build(make_records(40), excluded=0)
    assert validate.run(fc, counts, area_cfg=AREA_CFG) == []

    tampered = dict(counts)
    tampered["by_era"] = dict(counts["by_era"])
    first_era = next(iter(tampered["by_era"]))
    tampered["by_era"][first_era] += 1  # 集計改竄 → 三角測量で検出
    errors = validate.run(fc, tampered, area_cfg=AREA_CFG)
    assert any("T-036" in e or "再計算" in e for e in errors)

    tampered2 = dict(counts)
    tampered2["total"] = counts["total"] - 1
    errors2 = validate.run(fc, tampered2, area_cfg=AREA_CFG)
    assert any("再計算" in e for e in errors2)
