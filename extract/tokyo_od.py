"""Bronze: 東京都オープンデータ 文化財一覧 CSV(F-02)。

loop_001 確認: 推奨データセット準拠・cp932・緯度/経度列あり(ジオコーディング不要)。
中央区該当は現状 1 件(八重洲)のみで、tsukiji-akashicho では 0 件でも正常。
"""
from __future__ import annotations

import csv
import io

from extract.common import DataSourceError, http_get

DEFAULT_URL = "https://www.opendata.metro.tokyo.lg.jp/suisyoudataset/130001_cultural_property.csv"
LICENSE = "CC BY 4.0"
# 列構成変更の検知対象(欠落は DATA-SRC として失敗させる)
REQUIRED_COLUMNS = ("名称", "文化財分類", "種類", "住所", "緯度", "経度", "文化財指定日")


def _float_or_none(value: str | None) -> float | None:
    return float(value) if value not in (None, "") else None


def parse_csv_text(text: str, *, area: str, address_filter: str = "中央区") -> list[dict]:
    """CSV 本文を共通中間形へ。住所に address_filter を含む行のみ。列欠落は明示的に失敗。"""
    reader = csv.DictReader(io.StringIO(text))
    missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise DataSourceError(f"都 OD CSV の想定列が欠落(列構成変更の疑い): {missing}")
    records = []
    for row in reader:
        if address_filter not in (row["住所"] or ""):
            continue
        records.append({
            "source": "tokyo_od",
            "license": LICENSE,
            "area": area,
            "qid": None,
            "name": row["名称"],
            "lat": _float_or_none(row["緯度"]),
            "lon": _float_or_none(row["経度"]),
            "designation": row["文化財分類"],
            "kind": row["種類"],
            "address": row["住所"],
            "designated_on": row["文化財指定日"],
        })
    return records


def decode_csv_bytes(raw: bytes) -> str:
    """実ファイルは cp932(loop_001 確認)。将来の UTF-8 化にも耐える。"""
    for enc in ("utf-8-sig", "cp932"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise DataSourceError("都 OD CSV のエンコーディングを解釈できない(utf-8-sig / cp932 とも失敗)")


def fetch_csv(url: str = DEFAULT_URL, **http_kw) -> str:
    return decode_csv_bytes(http_get(url, **http_kw))
