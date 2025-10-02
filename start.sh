#!/usr/bin/env bash
set -euo pipefail

# Ensure venv active or use system python
PY=python

echo "[1/6] Running unit tests..."
$PY -m unittest tests/test_relevance.py || true

echo "[2/6] Running crawler: platform=hackernews max_items=50 hours=186"
$PY -m crawler.crawl --platform "hn" --max_items "50" --hours "168"

echo "[3/6] Running crawler: platform=reddit max_items=200 hours=72"
$PY -m crawler.crawl --platform "reddit" --max_items "200" --hours "72"

echo "[4/6] Link-structure analysis..."
$PY -m analysis.link_graph || true

echo "[5/6] Relevance analysis..."
$PY -m analysis.relevance_eval --analyze_distribution || true

echo "[6/6] Efficiency metrics..."
$PY -m analysis.efficiency_eval || true

echo "All done. Outputs in data/processed"
