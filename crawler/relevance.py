"""Relevance scoring utilities.

Provides:
- content_score: lexical hits + phrase/brand/policy bonuses
- recency_boost: exponential decay based on half-life (hours)
- final_priority: combine scores into a single priority value
"""
from __future__ import annotations

import math
import re
from typing import Iterable, List


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9_+-]+", text.lower()) if text else []


def _phrase_hits(text: str, phrases: Iterable[str]) -> int:
    if not text:
        return 0
    tl = text.lower()
    c = 0
    for ph in phrases:
        phl = ph.lower().strip()
        if not phl:
            continue
        c += tl.count(phl)
    return c


def content_score(
    text: str,
    keywords: Iterable[str],
    brand_terms: Iterable[str],
    policy_terms: Iterable[str],
    brand_bonus: float = 0.7,
    policy_bonus: float = 0.4,
) -> float:
    """Compute content relevance score.

    - Base score: unique token hits vs keywords (+0.2 each), phrase hits (+0.6 each)
    - Brand/policy bonuses: +brand_bonus per brand hit, +policy_bonus per policy hit
    """
    if not text:
        return 0.0
    toks = _tokenize(text)
    tokset = set(toks)
    key_tokens = set()
    for kw in keywords:
        key_tokens.update(_tokenize(kw))
    base = 0.2 * len(tokset & key_tokens)
    base += 0.6 * _phrase_hits(text, keywords)

    brand_hits = _phrase_hits(text, brand_terms)
    policy_hits = _phrase_hits(text, policy_terms)
    bonus = brand_hits * brand_bonus + policy_hits * policy_bonus
    return base + bonus


def recency_boost(hours_since: float, half_life_hours: float = 72.0) -> float:
    """Exponential half-life decay boost. Returns in (0, 1]."""
    if hours_since <= 0:
        return 1.0
    if half_life_hours <= 0:
        return 1.0
    return math.pow(2.0, -hours_since / half_life_hours)


def final_priority(
    content: float,
    recency: float,
    author_auth: float = 0.0,
    url_auth: float = 0.0,
    off_topic_penalty: float = 0.0,
) -> float:
    """Combine signals into final priority.

    Simple multiplicative combination with additive authority and penalty:
    priority = content * recency * (1.0 + author_auth + url_auth) * (1.0 - off_topic_penalty)
    """
    content = max(content, 0.0)
    recency = max(min(recency, 1.0), 0.0)
    mult = (1.0 + max(author_auth, 0.0) + max(url_auth, 0.0)) * (1.0 - max(off_topic_penalty, 0.0))
    return content * recency * max(mult, 0.0)
