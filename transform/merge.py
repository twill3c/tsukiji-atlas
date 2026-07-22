"""Silver: 名寄せ(F-04)。

curated の qid 明示指定のみで Wikidata レコードと統合する(AGENTS §3。
同名別地物が多い土地柄のため、名称の曖昧一致による自動統合は行わない)。
統合優先順位(GUIDE §3): 座標 = curated(verified) > wikidata、summary = curated。
"""
from __future__ import annotations

# 統合時に wikidata 側から引き継ぐ属性(curated に無いもの)
_WIKIDATA_CARRY = ("instance_of", "heritage", "inception")


def _merge_pair(cur: dict, wd: dict) -> dict:
    rec = dict(cur)  # summary・era・category 等は curated が正
    if not (cur.get("verified") and cur.get("lat") is not None and cur.get("lon") is not None):
        rec["lat"], rec["lon"] = wd.get("lat"), wd.get("lon")  # curated 座標が未検証/欠損なら wikidata
    for key in _WIKIDATA_CARRY:
        if key in wd:
            rec[key] = wd[key]
    return rec


def merge_curated_wikidata(curated: list[dict], wikidata: list[dict]) -> list[dict]:
    """qid 一致ペアを 1 レコードに統合し、残りはそのまま返す。"""
    wd_by_qid = {r["qid"]: r for r in wikidata if r.get("qid")}
    merged: list[dict] = []
    consumed: set[str] = set()
    for cur in curated:
        qid = cur.get("qid")
        if qid and qid in wd_by_qid:
            merged.append(_merge_pair(cur, wd_by_qid[qid]))
            consumed.add(qid)
        else:
            merged.append(dict(cur))
    merged.extend(r for r in wikidata if r.get("qid") not in consumed)
    return merged
