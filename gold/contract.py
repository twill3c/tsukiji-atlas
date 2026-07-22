"""Gold 契約の定義(SPEC §5・§6 が正)。era キーは transform.dims と単一ソース。"""
from __future__ import annotations

from transform.dims import ERA_RANGES

ERA_KEYS = tuple(key for key, _, _ in ERA_RANGES)
CATEGORY_KEYS = (
    "shrine_temple_church", "samurai_site", "monument_origin", "edu_medical",
    "naval_military", "market_food", "bridge_civil", "literature_arts",
)
SOURCES = ("wikidata", "tokyo_od", "curated")
LICENSES = ("CC0", "CC BY 4.0", "self")

REQUIRED_PROPS = ("site_id", "name", "era", "category", "summary", "source", "license", "area")
OPTIONAL_PROPS = ("year", "qid")
SUMMARY_MAX_CHARS = 120
MIN_FEATURES = 40  # Q-01: エリア初期リリース時の件数下限
