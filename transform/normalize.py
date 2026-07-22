"""Silver: 文字正規化(F-04)。

NFKC で name_norm を別途持ち、元の name(異体字含む)はそのまま保持する(GUIDE §3)。
name_norm は突き合わせ・検索用であり、名寄せの根拠には使わない(名寄せは qid 明示のみ)。
"""
from __future__ import annotations

import unicodedata


def add_name_norm(records: list[dict]) -> list[dict]:
    for rec in records:
        rec["name_norm"] = unicodedata.normalize("NFKC", rec["name"]) if rec.get("name") else None
    return records
