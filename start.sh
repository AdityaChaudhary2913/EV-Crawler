#!/usr/bin/env bash
set -euo pipefail

# Large crawl script for 1200+ items
PY=python

echo "=== Starting Large Scale Crawl for 1200+ Items ==="
echo "Target: 200 HN + 1000 Reddit = 1200 total items"
echo

echo "[1/5] Cleaning previous data..."
rm -rf data/processed/*
mkdir -p data/processed/tables data/processed/labels data/processed/figs

echo "[2/5] Running HN crawler (200 items)..."
$PY -m crawler.crawl --platform "hn" --max_items "200" --hours "168"

echo "[3/5] Running Reddit crawler (1000 items)..."
$PY -m crawler.crawl --platform "reddit" --max_items "1000" --hours "168"

echo "[4/5] Running analysis suite..."
echo "  - Link graph analysis..."
$PY -m analysis.link_graph || true

echo "  - Relevance distribution analysis..."
$PY -m analysis.relevance_eval --analyze_distribution || true

echo "  - Efficiency metrics..."
$PY -m analysis.efficiency_eval || true

echo "[5/5] Checking final count..."
TOTAL_ITEMS=$(wc -l data/processed/posts.jsonl 2>/dev/null | awk '{print $1}' || echo "0")
echo "Total items collected: $TOTAL_ITEMS"

if [ "$TOTAL_ITEMS" -ge 1100 ]; then
    echo "✅ SUCCESS: Collected $TOTAL_ITEMS items (target: 1100+)"
else
    echo "⚠️  WARNING: Only collected $TOTAL_ITEMS items (target: 1100+)"
    echo "   You may need to run additional crawls or adjust thresholds"
fi

echo
echo "All done! Check data/processed/ for results"
echo "Report can now be updated with these new metrics"