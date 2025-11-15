# EV Crawler - Electric Vehicles Knowledge Graph Project

A comprehensive focused web crawler and link analysis system for the Electric Vehicles (EV) domain in India. This project includes data collection from social platforms (Reddit/Hacker News), network analysis, and state-of-the-art graph ranking implementations.

**Course:** Introduction to Knowledge Graphs (IKG) - Semester 7  
**Team:** Aditya Chaudhary (22DCS002), Aayush Deshmukh (22DCS001), Utkarsh Agrawal (22UCS222)

## Project Overview

### Phase 1: Focused Web Crawler ✅ Complete
- Collected 1,032 items from Reddit and Hacker News
- Built network graph with 2,191 nodes and 2,105 edges
- Implemented relevance scoring and link analysis
- Generated comprehensive reports and visualizations

### Phase 2: Link Analysis Survey & Implementation 🚀 Current
- Surveyed 12+ state-of-the-art graph ranking papers
- Implemented Content-Weighted PageRank (CW-PR)
- Comprehensive comparison with baseline methods
- Professional LaTeX term paper with full analysis

## Repository Structure

```
Crawler/
├── crawler/              # Phase 1: Web crawler implementation
├── analysis/            # Network and relevance analysis
├── data/processed/      # Collected dataset and graph exports
├── reports/            # Phase 1 reports and documentation
├── term_paper/         # Phase 2: LaTeX term paper (NEW!)
│   ├── main.tex           # Complete survey paper
│   ├── implementation/    # Content-Weighted PageRank code
│   └── figures/          # Plots and visualizations
└── tests/              # Unit tests
```

## Quickstart - Phase 1 (Data Collection)

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

## Phase 2: Term Paper & Implementation

### Quick Start

```bash
# Navigate to term paper directory
cd term_paper

# Compile LaTeX paper
./compile.sh

# Run Content-Weighted PageRank implementation
cd implementation
pip install -r requirements.txt
python content_weighted_pagerank.py
```

### What's Included

**LaTeX Term Paper (main.tex):**
- Survey of 12+ link analysis papers
- Comprehensive comparison tables
- Content-Weighted PageRank algorithm description
- Complete implementation and evaluation section
- 60+ pages of professional academic content

**Python Implementation:**
- `content_weighted_pagerank.py` - Main CW-PR algorithm (450+ lines)
- `baselines.py` - Comparison methods (Standard PR, HITS, Degree)
- Complete evaluation framework
- Visualization tools

**Documentation:**
- `term_paper/SUMMARY.md` - Complete package overview
- `term_paper/QUICK_START.md` - Quick start guide
- `term_paper/README.md` - Detailed documentation
- `implementation/README.md` - Code documentation

### Selected Method: Content-Weighted PageRank

Combines structural authority (PageRank) with content relevance scores for superior ranking in domain-specific social networks.

**Algorithm:**
```
CW-PR(u) = (1-d) * w(u) + d * Σ[v→u] (CW-PR(v) * t(v,u) / out_degree(v))
```

**Key Features:**
- Handles heterogeneous graphs (multiple node/edge types)
- Incorporates content quality signals
- Edge type-specific weights
- Interpretable results
- Proven effectiveness

## Dataset Statistics (Phase 1)

| Metric | Value |
|--------|-------|
| Total Items | 1,032 |
| Network Nodes | 2,191 |
| Network Edges | 2,105 |
| Unique Authors | 420 |
| Posts | 107 |
| Comments | 899 |
| Domains | 28 |
| Relevant Items | 133 (12.9%) |

## Reports and Documentation

### Phase 1
- `reports/Part1_Report.md` - Complete Phase 1 implementation report
- `reports/README_data.md` - Dataset schema documentation

### Phase 2
- `term_paper/main.tex` - Complete survey paper
- `term_paper/SUMMARY.md` - Comprehensive overview
- `term_paper/QUICK_START.md` - Getting started guide

## KG-readiness
- Records include sentence offsets, outbound domains, mentions (brand/policy), and provenance.
- Graph exports include AUTHOR/CONTAINER/DOMAIN edges and mention edges.
- Ready for knowledge graph construction in future phases.

## Technologies Used

**Phase 1 (Crawler):**
- Python 3.9+
- PRAW (Reddit API)
- NetworkX (Graph analysis)
- Pandas (Data processing)

**Phase 2 (Term Paper):**
- LaTeX (Document preparation)
- Python (Implementation)
- NumPy, SciPy (Numerical computing)
- Matplotlib (Visualization)

## Citation

If you use this work, please cite:

```bibtex
@misc{ev_crawler_2025,
  author = {Chaudhary, Aditya and Deshmukh, Aayush and Agrawal, Utkarsh},
  title = {EV Crawler: Focused Web Crawling and Link Analysis for Electric Vehicles Domain},
  year = {2025},
  course = {Introduction to Knowledge Graphs (IKG)},
  institution = {[Your Institution]}
}
```

## License

This project is created for academic purposes as part of the IKG course.
