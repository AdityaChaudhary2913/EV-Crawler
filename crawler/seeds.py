"""Config loading and seed generation."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import toml


@dataclass
class Config:
    run: Dict
    crawler: Dict
    relevance: Dict
    reddit: Dict
    domain: Dict


def load_config(path: str = "config.toml") -> Config:
    """Load TOML config; falls back to defaults if missing sections."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    cfg = toml.load(path)
    # Provide defaults if not present
    cfg.setdefault("run", {})
    cfg.setdefault("crawler", {})
    cfg.setdefault("relevance", {})
    cfg.setdefault("reddit", {})
    cfg.setdefault("domain", {})
    return Config(
        run=cfg["run"],
        crawler=cfg["crawler"],
        relevance=cfg["relevance"],
        reddit=cfg["reddit"],
        domain=cfg["domain"],
    )


def get_seeds(cfg: Config) -> List[Tuple[str, str]]:
    """Generate (subreddit, keyword) seed pairs for Reddit search."""
    subs = cfg.domain.get("subreddits", [])
    keywords = cfg.domain.get("keywords", [])
    pairs: List[Tuple[str, str]] = []
    for s in subs:
        for k in keywords:
            pairs.append((s, k))
    return pairs
