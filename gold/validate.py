"""Gold: 品質基準 Q-01〜Q-05 の機械検査(F-05)。

エラーは「Q-xx: 説明」形式の文字列リストで返す(空 = 合格)。
T-036: counts.json を信用せず、Feature 列から時代別分布・総件数を別経路で
再計算して照合する(独立再計算 = 三角測量)。
"""
from __future__ import annotations

from collections import Counter

from gold.contract import (
    CATEGORY_KEYS, ERA_KEYS, LICENSES, MIN_FEATURES, REQUIRED_PROPS,
    SOURCES, SUMMARY_MAX_CHARS,
)


def run(fc: dict, counts: dict, *, area_cfg: dict, min_features: int = MIN_FEATURES) -> list[str]:
    errors: list[str] = []
    features = fc.get("features", [])
    bbox = area_cfg["bbox"]

    # Q-01: 件数下限
    if len(features) < min_features:
        errors.append(f"Q-01: Feature 数 {len(features)} が下限 {min_features} 未満")

    site_ids: list[str] = []
    qids: list[str] = []
    for i, f in enumerate(features):
        props = f.get("properties", {})
        label = props.get("site_id") or f"features[{i}]"

        # Q-02: bbox 内(config/areas の値のみを使う)
        lon, lat = f["geometry"]["coordinates"]
        if not (bbox["min_lat"] <= lat <= bbox["max_lat"] and bbox["min_lon"] <= lon <= bbox["max_lon"]):
            errors.append(f"Q-02: {label} の座標 ({lat}, {lon}) が bbox 外")

        # Q-03: 必須列の充足と定義済みキー
        for key in REQUIRED_PROPS:
            if not props.get(key):
                errors.append(f"Q-03: {label} の必須列 {key} が欠落")
        if props.get("era") not in ERA_KEYS:
            errors.append(f"Q-03: {label} の era {props.get('era')!r} が未定義キー")
        if props.get("category") not in CATEGORY_KEYS:
            errors.append(f"Q-03: {label} の category {props.get('category')!r} が未定義キー")
        if props.get("source") not in SOURCES:
            errors.append(f"Q-03: {label} の source {props.get('source')!r} が未定義キー")
        if props.get("license") not in LICENSES:
            errors.append(f"Q-03: {label} の license {props.get('license')!r} が未定義キー")
        if len(props.get("summary") or "") > SUMMARY_MAX_CHARS:
            errors.append(f"Q-03: {label} の summary が {SUMMARY_MAX_CHARS} 字超")

        site_ids.append(props.get("site_id"))
        if props.get("qid"):
            qids.append(props["qid"])

    # Q-04: 一意性(名寄せ後の二重登録検出)
    for name, values in (("site_id", site_ids), ("qid", qids)):
        dupes = [v for v, n in Counter(values).items() if n > 1]
        if dupes:
            errors.append(f"Q-04: {name} が重複: {dupes}")

    # Q-05: 除外件数が品質レポートに記録されていること
    if not isinstance(counts.get("excluded"), int) or counts.get("excluded") < 0:
        errors.append("Q-05: counts.excluded が非負整数で記録されていない")

    # T-036: 独立再計算 — counts.json を Feature 列から検算
    recomputed_era = dict(Counter(f["properties"].get("era") for f in features))
    if counts.get("by_era") != recomputed_era:
        errors.append("T-036: counts.by_era が Feature 列からの再計算と不一致")
    if counts.get("total") != len(features):
        errors.append("T-036: counts.total が Feature 数の再計算と不一致")
    if sum(counts.get("by_era", {}).values()) != len(features):
        errors.append("T-036: by_era 合計が Feature 数の再計算と不一致")

    return errors
