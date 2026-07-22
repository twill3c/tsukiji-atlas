"""Silver 層テスト(T-021〜T-025)。固定データ駆動、ネットワーク不要(N-01)。"""
import pytest

from transform import dims, merge, normalize

pytestmark = pytest.mark.unit

AREA = "tsukiji-akashicho"


def _curated(name, qid=None, verified=True, lat=35.666389, lon=139.772222, era="edo_early"):
    return {
        "source": "curated", "license": "self", "area": AREA, "qid": qid,
        "site_id": "tsukiji-akashicho-001", "name": name, "era": era,
        "category": "shrine_temple_church", "year": 1657,
        "lat": lat, "lon": lon, "summary": "自前執筆の要約。", "verified": verified,
    }


def _wikidata(name, qid, lat=35.6663, lon=139.7721):
    return {
        "source": "wikidata", "license": "CC0", "area": AREA, "qid": qid,
        "name": name, "lat": lat, "lon": lon,
        "instance_of": [{"qid": "Q5393308", "label": "仏教寺院"}],
    }


# T-021(F-04): qid 指定ありの名寄せ — 1 レコードに統合、座標は curated 優先
def test_merge_with_explicit_qid():
    curated = [_curated("築地本願寺", qid="Q943255")]
    wikidata = [_wikidata("築地本願寺", "Q943255"), _wikidata("波除稲荷神社", "Q3335477")]

    merged = merge.merge_curated_wikidata(curated, wikidata)

    assert len(merged) == 2  # 統合 1 + 未対応 wikidata 1
    rec = next(r for r in merged if r["qid"] == "Q943255")
    assert (rec["lat"], rec["lon"]) == (35.666389, 139.772222)  # curated(verified) > wikidata
    assert rec["summary"] == "自前執筆の要約。"                  # summary = curated
    assert rec["source"] == "curated"
    assert rec["instance_of"][0]["qid"] == "Q5393308"           # wikidata 側の属性は保持


# T-022(F-04): qid 指定なし・同名 — 統合されない(名称の曖昧一致で自動統合しない)
def test_no_merge_without_qid_even_if_same_name():
    curated = [_curated("住吉神社", qid=None)]
    wikidata = [_wikidata("住吉神社", "Q11381869")]

    merged = merge.merge_curated_wikidata(curated, wikidata)

    assert len(merged) == 2
    assert {r["source"] for r in merged} == {"curated", "wikidata"}


# T-023(F-04): era 機械判定 — P571 の年から SPEC §4 の範囲で判定
@pytest.mark.parametrize(
    ("year", "expected"),
    [(1869, "meiji"), (1657, "edo_early"), (1868, "meiji"),  # 境界年は meiji
     (1700, "edo_early"), (1701, "edo_late"), (1853, "bakumatsu"),
     (1926, "showa"), (1989, "heisei_reiwa"), (2018, "heisei_reiwa")],
)
def test_era_from_year(year, expected):
    assert dims.era_from_year(year) == expected


# T-024(F-04): era 判定不能 — needs_review に出力、Silver 本体から除外されない
def test_unjudgeable_era_goes_to_needs_review_but_stays():
    records = [
        {"source": "wikidata", "qid": "Q1", "name": "年不明の地物", "year": None},
        {"source": "wikidata", "qid": "Q2", "name": "中世の地物", "year": 1500},  # 範囲外(1603 未満)
        {"source": "curated", "qid": None, "name": "手入力済み", "era": "bakumatsu", "year": 1857},
    ]
    result, needs_review = dims.assign_era(records)

    assert len(result) == 3                                   # 除外されない
    assert {r["name"] for r in needs_review} == {"年不明の地物", "中世の地物"}
    by_name = {r["name"]: r for r in result}
    assert by_name["年不明の地物"]["era"] is None              # era=null で保持
    assert by_name["中世の地物"]["era"] is None
    assert by_name["手入力済み"]["era"] == "bakumatsu"         # curated の手入力は変更しない


# T-025(F-04): NFKC 正規化 — 全角英数・互換文字が正規化された name_norm を持つ
def test_nfkc_name_norm():
    records = [
        {"name": "ＧＩＮＺＡ ＳＩＸ"},
        {"name": "㈱珠屋小林商店"},
        {"name": "鐵砲洲稲荷神社"},  # 異体字は NFKC では変わらない → そのまま
    ]
    out = normalize.add_name_norm(records)

    assert out[0]["name_norm"] == "GINZA SIX"
    assert out[1]["name_norm"] == "(株)珠屋小林商店"
    assert out[2]["name_norm"] == "鐵砲洲稲荷神社"
    assert out[2]["name"] == "鐵砲洲稲荷神社"  # 元の name は保持
