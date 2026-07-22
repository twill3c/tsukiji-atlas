"""Silver: 時代ディメンション付与(F-04)。

era の年代範囲は SPEC §4 が正。curated の手入力 era は変更せず、
wikidata 由来は year(P571)から機械判定。判定不能は era=None のまま本体に保持し、
needs_review として返す(T-024。curated 側で確定させる運用)。
"""
from __future__ import annotations

# SPEC §4 dim_時代(開始年, 終了年)。heisei_reiwa は開経区間
ERA_RANGES: list[tuple[str, int, int | None]] = [
    ("edo_early", 1603, 1700),
    ("edo_late", 1701, 1852),
    ("bakumatsu", 1853, 1867),
    ("meiji", 1868, 1911),
    ("taisho", 1912, 1925),
    ("showa", 1926, 1988),
    ("heisei_reiwa", 1989, None),
]


def era_from_year(year: int | None) -> str | None:
    """西暦 → era キー。範囲外(1603 未満)・不明は None(needs_review 行き)。"""
    if year is None:
        return None
    for key, start, end in ERA_RANGES:
        if year >= start and (end is None or year <= end):
            return key
    return None


def assign_era(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """(全レコード, needs_review) を返す。needs_review も本体から除外しない(T-024)。"""
    needs_review: list[dict] = []
    for rec in records:
        if rec.get("era"):  # curated の手入力は変更しない
            continue
        rec["era"] = era_from_year(rec.get("year"))
        if rec["era"] is None:
            needs_review.append(rec)
    return records, needs_review
