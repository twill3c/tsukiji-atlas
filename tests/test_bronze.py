"""Bronze 層テスト(T-011〜T-015)。全ケースフィクスチャ駆動、ネットワーク不要(N-01)。"""
import json
import socket
from pathlib import Path

import pytest

from extract import curated, tokyo_od, wikidata
from extract.common import DataSourceError

FIXTURES = Path(__file__).resolve().parent.parent / "data" / "fixtures"
AREA = "tsukiji-akashicho"

pytestmark = pytest.mark.unit


# T-011(F-01): SPARQL 応答フィクスチャの解析
def test_parse_sparql_to_common_form():
    payload = json.loads((FIXTURES / "wikidata_sites_base.json").read_text(encoding="utf-8"))
    records = wikidata.parse_sparql_json(payload, area=AREA)

    assert len(records) == 3  # 勝鬨橋の P31 2 行は 1 レコードに集約
    by_qid = {r["qid"]: r for r in records}
    katsudoki = by_qid["Q4844361"]
    assert isinstance(katsudoki["lat"], float) and isinstance(katsudoki["lon"], float)
    assert (katsudoki["lat"], katsudoki["lon"]) == (35.661944, 139.775)
    assert {i["qid"] for i in katsudoki["instance_of"]} == {"Q537127", "Q911663"}
    assert all(r["source"] == "wikidata" and r["license"] == "CC0" for r in records)
    assert all(r["area"] == AREA for r in records)


# T-012(F-01/N-02): タイムアウト応答 → リトライ 3 回後に DATA-SRC 相当の例外、部分結果なし
def test_fetch_sparql_timeout_retries_then_raises():
    calls = []

    def timeout_opener(req, timeout=None):
        calls.append(req.full_url)
        raise socket.timeout("simulated timeout")

    with pytest.raises(DataSourceError):
        wikidata.fetch_sparql(
            "SELECT * WHERE { ?s ?p ?o } LIMIT 1",
            opener=timeout_opener,
            sleep_fn=lambda s: None,
        )
    assert len(calls) == 3  # リトライ上限まで試行
    # 例外送出 = 部分結果を返す経路が存在しない(戻り値なし)


# T-013(F-02): 都 OD CSV フィクスチャ — 中央区行のみ抽出、想定列の存在検証
def test_tokyo_od_filters_chuo_rows():
    text = (FIXTURES / "tokyo_od_cultural_property.csv").read_text(encoding="utf-8")
    records = tokyo_od.parse_csv_text(text, area=AREA)

    assert len(records) == 1  # 台東区行は除外
    rec = records[0]
    assert rec["name"] == "一石橋迷子しらせ石標"
    assert isinstance(rec["lat"], float) and isinstance(rec["lon"], float)
    assert rec["source"] == "tokyo_od" and rec["license"] == "CC BY 4.0"


def test_tokyo_od_missing_column_fails():
    text = (FIXTURES / "tokyo_od_missing_column.csv").read_text(encoding="utf-8")
    with pytest.raises(DataSourceError, match="住所"):
        tokyo_od.parse_csv_text(text, area=AREA)


# T-014(F-03): curated CSV 読込 — verified=false が仕分けされ件数が返る
def test_curated_splits_by_verified():
    verified, unverified = curated.load(FIXTURES / "curated_ok.csv")

    assert len(verified) == 2 and len(unverified) == 1
    assert unverified[0]["name"] == "軍艦操練所跡"
    assert isinstance(verified[0]["lat"], float)
    assert all(r["source"] == "curated" for r in verified + unverified)
    assert verified[0]["year"] == 1657  # year は int 化


# T-015(F-03): 必須列欠落は明示的エラー(黙って欠損行スキップしない)
def test_curated_missing_column_raises():
    with pytest.raises(ValueError, match="verified"):
        curated.load(FIXTURES / "curated_missing_column.csv")
