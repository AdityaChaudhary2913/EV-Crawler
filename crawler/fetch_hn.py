"""Hacker News Firebase API helpers (fallback platform)."""
from __future__ import annotations

import time
from typing import Iterable, List, Optional, cast

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from .utils import sleep_for_qps

BASE = "https://hacker-news.firebaseio.com/v0"


@retry(wait=wait_exponential(multiplier=0.2, min=0.2, max=5), stop=stop_after_attempt(3))
def _get_json(url: str) -> dict:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_new_story_ids(qps: float) -> List[int]:
    """Fetch newstories ids list."""
    try:
        ids = _get_json(f"{BASE}/newstories.json") or []
        ids = cast(List[int], ids)
        sleep_for_qps(qps, time.time())
        return ids
    except Exception:
        return []
    ids = cast(List[int], ids)
    sleep_for_qps(qps, time.time())
    return ids


def fetch_item(item_id: int, qps: float) -> Optional[dict]:
    try:
        data = _get_json(f"{BASE}/item/{item_id}.json")
        sleep_for_qps(qps, time.time())
        return data
    except Exception:
        return None


def iter_recent_stories(limit: int, qps: float) -> Iterable[dict]:
    """Yield recent story items (type=story) up to limit."""
    count = 0
    for iid in fetch_new_story_ids(qps):
        if count >= limit:
            break
        item = fetch_item(iid, qps)
        if not item or item.get("type") != "story":
            continue
        yield item
        count += 1
