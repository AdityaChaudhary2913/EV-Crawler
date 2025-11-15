# Term Paper - Phase 2: Link Analysis Survey

## Overview
This directory contains the LaTeX source files for the Phase 2 term paper on "Link Analysis and Graph Ranking Algorithms for Social Network Analysis".

## Topic Selected
**Link Analysis and Graph Ranking Algorithms**

This topic is highly relevant to our Phase 1 crawler project as:
- We collected 1,032 items forming a network with 2,191 nodes and 2,105 edges
- Our dataset includes authors, posts, comments, containers, and domains
- We already implemented basic PageRank and HITS in Phase 1
- This survey will help us understand and implement more advanced ranking methods

## Papers Surveyed (12+ papers)

1. **PageRank** - Page et al., 1999
2. **HITS** - Kleinberg, 1999
3. **Topic-Sensitive PageRank** - Haveliwala, 2002
4. **Personalized PageRank** - Jeh & Widom, 2003
5. **Temporal PageRank** - Rozenshtein & Gionis, 2016
6. **DynamicBC** - Kas et al., 2013
7. **ExpertRank** - Zhang et al., 2007
8. **TwitterRank** - Weng et al., 2010
9. **CommunityRank** - Chen et al., 2012
10. **Hierarchical PageRank** - Becchetti et al., 2008
11. **GraphSAGE** - Hamilton et al., 2017
12. **GAT (Graph Attention Networks)** - Veličković et al., 2018

## Structure

### Files
- `main.tex` - Main LaTeX document with complete survey
- `README.md` - This file
- `compile.sh` - Script to compile LaTeX to PDF
- `figures/` - Directory for figures and plots (to be created)

### Sections
1. **Introduction** - Motivation, problem statement, contributions
2. **Background** - Graph theory, key concepts, evaluation metrics
3. **Literature Survey** - Detailed description of 12+ papers
4. **Comparative Analysis** - Taxonomy, comparison tables, discussion
5. **Implementation** - Best method selection, algorithm, results
6. **Conclusions** - Summary, future directions

## Selected Method for Implementation

**Content-Weighted PageRank (CW-PR)**

### Why this method?
- Combines structural analysis (PageRank) with content signals (relevance scores)
- Handles heterogeneous graphs (multiple node/edge types)
- Interpretable and explainable results
- Efficient for moderate-scale networks
- Easy to extend with temporal or personalization features

### Implementation Plan
1. Load graph from existing CSV files (nodes.csv, edges.csv)
2. Extract relevance scores from posts.jsonl
3. Implement CW-PR algorithm in Python
4. Compare with baselines (standard PageRank, HITS, Degree Centrality)
5. Evaluate using Precision@k, nDCG@k, Kendall's Tau
6. Generate visualizations and analysis

## How to Compile

### Using pdflatex (recommended)
```bash
# Install LaTeX distribution first
# macOS: brew install mactex
# Ubuntu: sudo apt-get install texlive-full

# Compile the document
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Using the provided script
```bash
chmod +x compile.sh
./compile.sh
```

### Using Overleaf
1. Create new project on Overleaf
2. Upload main.tex
3. Set compiler to pdfLaTeX
4. Compile online

## Next Steps

### 1. Implement the Algorithm (Python)
Create `implementation/content_weighted_pagerank.py`:
- Load dataset from Phase 1
- Implement CW-PR algorithm
- Run experiments with baselines
- Generate results tables and figures

### 2. Create Figures
Generate plots in `figures/`:
- `convergence_plot.pdf` - Convergence comparison
- `score_distribution.pdf` - Rank score distributions
- `network_visualization.pdf` - Top authors network
- `comparison_bar_chart.pdf` - Method comparison

### 3. Update Results Section
- Fill in actual experimental results
- Add top-10 authors table
- Include performance metrics
- Add qualitative analysis

### 4. Finalize Bibliography
- Add missing citations
- Verify citation format
- Add recent papers if needed

## Requirements

### LaTeX Packages
All required packages are included in the preamble:
- Standard: amsmath, graphicx, hyperref
- Tables: booktabs, multirow, longtable
- Code: listings, algorithm, algorithmic
- Formatting: geometry, fancyhdr, caption

### Python Libraries (for implementation)
```bash
pip install numpy networkx pandas matplotlib seaborn scipy
```

## Timeline

- **Week 1**: Complete implementation of CW-PR
- **Week 2**: Run experiments and collect results
- **Week 3**: Generate figures and finalize results section
- **Week 4**: Review, proofreading, final compilation

## Grading Criteria

Based on typical academic term paper requirements:
- [ ] Survey quality (description of 10+ papers) - 30%
- [ ] Comparison and analysis - 20%
- [ ] Implementation of best method - 25%
- [ ] Experimental results and evaluation - 20%
- [ ] Writing quality and presentation - 5%

## Contact

For questions or clarifications, contact course instructor:
- Mr. Nirmal Sivaraman
- Course: Introduction to Knowledge Graphs (IKG)
- Semester 7

---

**Authors:**
- Aditya Chaudhary (22DCS002)
- Aayush Deshmukh (22DCS001)
- Utkarsh Agrawal (22UCS222)

**Last Updated:** November 15, 2025
