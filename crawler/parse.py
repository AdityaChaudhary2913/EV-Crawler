"""Normalization of platform-specific items to the dataset schema."""
from __future__ import annotations

from typing import Dict

from .utils import detect_lang, extract_urls, now_iso, sentence_spans, sha1_hash, to_iso, url_to_domain


def normalize_record(
    *,
    platform: str,
    kind: str,
    id: str,
    author_id: str | None,
    author_name: str | None,
    container_id: str | None,
    container_name: str | None,
    created_utc: float,
    title: str | None,
    body: str | None,
    url: str | None,
    score_upvotes: int | None,
    num_comments: int | None = None,
    parent_id: str | None = None,
    root_post_id: str | None = None,
    depth: int = 0,
    relevance_score: float = 0.0,
    relevance_features: dict | None = None,
    provenance: dict | None = None,
) -> dict:
    """Create a normalized JSONL record with KG-ready fields.

    Required schema fields are filled; optional ones can be None.
    """
    title = title or ""
    body = body or ""
    text = (title + "\n" + body).strip() if title and body else (title or body)
    lang = detect_lang(text)
    sentences = [{"start": s, "end": e} for s, e in sentence_spans(text)]
    fetched_iso = now_iso()
    created_iso = to_iso(created_utc)
    outbound_urls = extract_urls(text)
    outbound_domains = [d for d in (url_to_domain(u) for u in outbound_urls) if d]
    hash_sha1 = sha1_hash(platform, id, text or "")

    record = {
        "id": id,
        "platform": platform,
        "kind": kind,
        "author_id": author_id or "",
        "author_name": author_name or "",
        "container_id": container_id or "",
        "container_name": container_name or "",
        "created_utc": float(created_utc),
        "created_iso": created_iso,
        "fetched_iso": fetched_iso,
        "title": title,
        "body": body,
        "text": text,
        "lang": lang,
        "sentences": sentences,
        "url": url or "",
        "outbound_urls": outbound_urls,
        "outbound_domains": outbound_domains,
        "score_upvotes": int(score_upvotes or 0),
        "num_comments": int(num_comments) if num_comments is not None else None,
        "parent_id": parent_id,
        "root_post_id": root_post_id or id,
        "depth": int(depth),
        "relevance_score": float(relevance_score or 0.0),
        "relevance_features": relevance_features or {},
        "provenance": provenance or {},
        "hash_sha1": hash_sha1,
    }
    return record
