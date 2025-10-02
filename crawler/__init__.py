"""Focused crawler package for Reddit/Hacker News.

Modules:
- crawl: CLI orchestrator
- fetch_reddit: PRAW-based fetchers
- fetch_hn: Hacker News Firebase fetchers
- parse: normalization and KG-ready fields
- relevance: lexical relevance scoring model
- frontier: priority frontier with dedup
- persist: writers for dataset and graph
- seeds: config loading and seed generation
- utils: helpers (lang detect, urls, hashing, time)
"""
