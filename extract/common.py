"""Bronze 共通基盤: HTTP 取得(リトライ・タイムアウト・スリープ、N-02)とエリア設定。

Python 3.12 標準ライブラリのみ。
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

USER_AGENT = "tsukiji-atlas/0.1 (contact: twill3c@gmail.com)"
DEFAULT_TIMEOUT_S = 60
DEFAULT_RETRIES = 3
DEFAULT_SLEEP_S = 2.0


class DataSourceError(RuntimeError):
    """外部データソース起因の失敗(FAILURE_TAXONOMY: DATA-SRC 相当)。"""


def http_get(
    url: str,
    *,
    headers: dict | None = None,
    timeout: float = DEFAULT_TIMEOUT_S,
    retries: int = DEFAULT_RETRIES,
    sleep_s: float = DEFAULT_SLEEP_S,
    opener=urllib.request.urlopen,
    sleep_fn=time.sleep,
) -> bytes:
    """GET して全バイト列を返す。全リトライ失敗時は DataSourceError(部分結果は返さない)。"""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            with opener(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as e:  # timeout / HTTPError / URLError
            last_err = e
            if attempt < retries - 1:
                sleep_fn(sleep_s)
    raise DataSourceError(f"{retries} 回リトライ後も取得失敗: {url}: {last_err}") from last_err


def load_area(area: str, root: str | Path = ".") -> dict:
    """config/areas/{area}.json を読む。エリア固有値はすべてここに集約(AGENTS §1)。"""
    path = Path(root) / "config" / "areas" / f"{area}.json"
    return json.loads(path.read_text(encoding="utf-8"))
