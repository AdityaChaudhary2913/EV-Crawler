# Content-Weighted PageRank Implementation

This directory contains the Python implementation of Content-Weighted PageRank (CW-PR) and baseline comparison methods.

## Files

- `content_weighted_pagerank.py` - Main CW-PR implementation
- `baselines.py` - Baseline methods (Standard PR, HITS, Degree Centrality)
- `evaluation.py` - Evaluation metrics and utilities
- `visualization.py` - Plotting and visualization functions
- `run_experiments.py` - Script to run all experiments

## Installation

```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install numpy pandas networkx matplotlib seaborn scipy
```

## Usage

### Basic Usage

```python
from content_weighted_pagerank import ContentWeightedPageRank

# Initialize
cwpr = ContentWeightedPageRank(
    nodes_file='../../data/processed/nodes.csv',
    edges_file='../../data/processed/edges.csv',
    posts_file='../../data/processed/posts.jsonl'
)

# Compute scores
scores = cwpr.compute_pagerank(use_content_weights=True)

# Get top-10 authors
top_authors = cwpr.get_top_k(scores, k=10, node_type='author')
```

### Run All Experiments

```bash
python content_weighted_pagerank.py
```

This will:
1. Load the EV dataset
2. Compute CW-PR scores
3. Compare with baseline methods
4. Generate comparison tables
5. Create visualizations

## Output

Results are saved to:
- `results/method_comparison.csv` - Method comparison table
- `../figures/score_distribution.pdf` - Score distribution plot
- `../figures/convergence_plot.pdf` - Convergence analysis

## Evaluation Metrics

The implementation supports the following metrics:

- **Kendall's Tau**: Rank correlation coefficient
- **Spearman's Rho**: Monotonic correlation
- **Precision@k**: Fraction of relevant items in top-k
- **nDCG@k**: Normalized Discounted Cumulative Gain
- **Convergence Rate**: Iterations to converge

## Algorithm Details

### Content-Weighted PageRank

The core algorithm:

```
CW-PR(u) = (1-d) * w(u) + d * Σ[v→u] (CW-PR(v) * t(v,u) / out_degree(v))
```

Where:
- `d` = damping factor (0.85)
- `w(u)` = normalized content weight
- `t(v,u)` = edge type weight
- `out_degree(v)` = out-degree of node v

### Edge Type Weights

- AUTHORED_BY: 1.0 (full authority transfer)
- REPLY_TO: 0.8 (engagement signal)
- MENTIONS_BRAND/POLICY: 0.6 (domain relevance)
- IN_CONTAINER: 0.5 (community membership)
- LINKS_TO_DOMAIN: 0.3 (external reference)

## Extending the Implementation

### Add Custom Edge Weights

```python
cwpr.edge_type_weights['NEW_EDGE_TYPE'] = 0.7
```

### Implement Personalized Ranking

```python
personalization = {
    'user1': 0.5,
    'user2': 0.3,
    # ...
}
scores = cwpr.compute_pagerank(personalization=personalization)
```

### Add Temporal Decay

Modify the content weights to include time decay:

```python
import datetime

def time_decay_weight(post):
    now = datetime.datetime.now()
    post_time = datetime.datetime.fromisoformat(post['created_iso'])
    hours_diff = (now - post_time).total_seconds() / 3600
    decay = 2 ** (-hours_diff / 72)  # 72-hour half-life
    return post['relevance_score'] * decay
```

## Performance

On the EV dataset (2,191 nodes, 2,105 edges):
- Convergence: ~20-30 iterations
- Runtime: < 1 second
- Memory: < 100 MB

## Citation

If you use this implementation, please cite:

```
@misc{ev_crawler_cwpr,
  author = {Chaudhary, Aditya and Deshmukh, Aayush and Agrawal, Utkarsh},
  title = {Content-Weighted PageRank for Social Network Analysis},
  year = {2025},
  course = {Introduction to Knowledge Graphs (IKG)}
}
```
