# Focused Crawler (Reddit / Hacker News)

A minimal, assignment-ready focused crawler that collects posts/comments for a domain, ranks by simple lexical relevance, exports normalized data and a typed link graph, and provides basic analysis/evaluation scripts.

## Quickstart

- Python 3.9+
- macOS/Linux/Windows

```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

cp config.example.toml config.toml
# Edit config.toml with your domain subreddits/keywords; add Reddit API keys if using Reddit.

# Hacker News (works without keys)
python -m crawler.crawl --platform hn --max_items 50 --hours 168

# Reddit (requires keys in config.toml)
python -m crawler.crawl --platform reddit --max_items 200 --hours 72
```

Outputs go to `data/processed` by default (configurable via `run.out_dir`):
- posts.jsonl: normalized records (posts and comments)
- nodes.csv, edges.csv: typed graph
- metrics.csv: crawl progress metrics over time

See `reports/README_data.md` for schema details.

## Analysis and Evaluation

```
# Link structure (writes CSVs to processed/tables/ and figs to processed/figs/)
python -m analysis.link_graph

# Prepare labels for manual relevance annotation (~400 rows)
python -m analysis.relevance_eval --prepare_labels

# Score labels after annotating the 'label' column (1 relevant, 0 not)
python -m analysis.relevance_eval --score_labels --k 100

# Efficiency metrics from metrics.csv
python -m analysis.efficiency_eval
```

## KG-readiness
- Records include sentence offsets, outbound domains, mentions (brand/policy), and provenance.
- Graph exports include AUTHOR/CONTAINER/DOMAIN edges and mention edges, making Part 2 KG construction straightforward.
