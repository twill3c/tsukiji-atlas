"""Bronze: Wikidata SPARQL 抽出(F-01)。

クエリは extract/queries/*.rq に分割(sites_base / sites_heritage / sites_dates)。
中央区 = Q212704、P131 は推移的に辿る(loop_001 確定、docs/loop_001_exploration.md)。
"""
from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path

from extract.common import DataSourceError, http_get

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
_POINT_RE = re.compile(r"Point\(([-0-9.]+) ([-0-9.]+)\)")  # WKT は「経度 緯度」順


def parse_point(wkt: str) -> tuple[float, float]:
    """WKT Point → (lat, lon)。"""
    m = _POINT_RE.fullmatch(wkt.strip())
    if not m:
        raise DataSourceError(f"P625 の WKT を解釈できない: {wkt!r}")
    lon, lat = float(m.group(1)), float(m.group(2))
    return lat, lon


def parse_sparql_json(payload: dict, *, area: str) -> list[dict]:
    """SPARQL JSON 応答を共通中間形へ。同一 QID の複数行(P31 複数)は 1 レコードに集約。"""
    by_qid: dict[str, dict] = {}
    for b in payload["results"]["bindings"]:
        qid = b["item"]["value"].rsplit("/", 1)[-1]
        rec = by_qid.get(qid)
        if rec is None:
            lat, lon = parse_point(b["coord"]["value"]) if "coord" in b else (None, None)
            rec = by_qid[qid] = {
                "source": "wikidata",
                "license": "CC0",
                "area": area,
                "qid": qid,
                "name": b.get("itemLabel", {}).get("value"),
                "lat": lat,
                "lon": lon,
                "instance_of": [],
            }
        if "instanceOf" in b:
            io_qid = b["instanceOf"]["value"].rsplit("/", 1)[-1]
            if io_qid not in {i["qid"] for i in rec["instance_of"]}:
                rec["instance_of"].append(
                    {"qid": io_qid, "label": b.get("instanceOfLabel", {}).get("value")}
                )
    return list(by_qid.values())


def load_query(name: str, root: str | Path = ".") -> str:
    return (Path(root) / "extract" / "queries" / f"{name}.rq").read_text(encoding="utf-8")


def fetch_sparql(query: str, *, endpoint: str = SPARQL_ENDPOINT, **http_kw) -> dict:
    """SPARQL を実行し JSON 応答を返す。失敗は DataSourceError(部分結果を残さない)。"""
    url = endpoint + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    raw = http_get(url, headers={"Accept": "application/sparql-results+json"}, **http_kw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise DataSourceError(f"SPARQL 応答が JSON でない: {e}") from e
