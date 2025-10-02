"""Utility functions for the focused crawler.

Includes language detection, URL extraction, hashing, timestamps, and
simple sentence span detection.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import langid
import tldextract
from dateutil import parser as dateparser


ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def now_iso() -> str:
    """Return current UTC time in ISO 8601 with Z suffix."""
    return datetime.now(timezone.utc).strftime(ISO_FORMAT)


def to_iso(ts: float | int | str) -> str:
    """Convert epoch seconds or parseable string to ISO UTC string.

    Accepts:
    - epoch seconds (float/int)
    - ISO/parseable string
    """
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime(ISO_FORMAT)
    if isinstance(ts, str):
        dt = dateparser.parse(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime(ISO_FORMAT)
    raise TypeError("Unsupported timestamp type")


def detect_lang(text: str) -> str:
    """Detect language code using langid; return 'en' fallback on errors."""
    if not text:
        return ""
    try:
        code, _ = langid.classify(text)
        return code
    except Exception:
        return ""


_URL_RE = re.compile(r"https?://[^\s)\]}>'\"]+")


def extract_urls(text: str) -> List[str]:
    """Extract outbound URLs using a simple regex.

    This does not validate; it's okay for lightweight crawling.
    """
    if not text:
        return []
    return _URL_RE.findall(text)


def url_to_domain(url: str) -> Optional[str]:
    """Extract registrable domain using tldextract; returns None if unavailable."""
    if not url:
        return None
    try:
        ext = tldextract.extract(url)
        if not ext.domain:
            return None
        domain = ".".join(p for p in [ext.domain, ext.suffix] if p)
        return domain or None
    except Exception:
        return None


def sha1_hash(*parts: str) -> str:
    """Stable SHA1 hash from provided string parts."""
    h = hashlib.sha1()
    for p in parts:
        if p is None:
            continue
        h.update(p.encode("utf-8", errors="ignore"))
        h.update(b"|")
    return h.hexdigest()


def sleep_for_qps(qps: float, last_time: Optional[float]) -> float:
    """Politeness: sleep to respect QPS. Returns current time after sleep."""
    now = time.time()
    if qps <= 0:
        return now
    min_interval = 1.0 / qps
    if last_time is not None:
        elapsed = now - last_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
    return time.time()


def sentence_spans(text: str) -> List[Tuple[int, int]]:
    """Very simple sentence segmentation returning (start, end) offsets.

    Splits on '.', '!', '?'. Trims whitespace. Returns non-empty spans.
    """
    spans: List[Tuple[int, int]] = []
    if not text:
        return spans
    start = 0
    for m in re.finditer(r"[.!?]", text):
        end = m.end()
        seg = text[start:end]
        if seg.strip():
            # Trim leading/trailing whitespace to compute exact offsets
            ltrim = len(seg) - len(seg.lstrip())
            rtrim = len(seg) - len(seg.rstrip())
            spans.append((start + ltrim, end - rtrim))
        start = end
    if start < len(text):
        seg = text[start:]
        if seg.strip():
            ltrim = len(seg) - len(seg.lstrip())
            rtrim = len(seg) - len(seg.rstrip())
            spans.append((start + ltrim, len(text) - rtrim))
    return spans


def json_dumps(data: dict) -> str:
    """Stable JSON dumps for attributes in graph CSVs."""
    return json.dumps(data, ensure_ascii=False, sort_keys=True)
