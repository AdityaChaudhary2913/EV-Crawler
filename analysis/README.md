# EV Discussion Analysis Pipeline

This directory contains a comprehensive analysis pipeline for Electric Vehicle (EV) discussion data. The pipeline analyzes Reddit discussions to extract insights about author behavior, brand mentions, topics, and network structure.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Data files** in the correct location:
   - `data/processed/nodes.csv`
   - `data/processed/edges.csv`

### Installation

1. Install required packages:
```bash
pip install -r analysis/requirements.txt
```

2. Run the complete analysis pipeline:
```bash
cd analysis
python run_complete_analysis.py
```

## 📊 Analysis Modules

### 1. Author Activity Analysis (`author_activity.py`)
Analyzes user engagement patterns and contribution behaviors.

**Key Metrics:**
- Author participation rates
- Post vs comment distributions  
- Engagement ratios
- Top contributors identification
- Activity level categorization

**Run individually:**
```bash
python author_activity.py
```

### 2. Brand & Topic Analysis (`brand_topic_analysis.py`) 
Examines brand mentions, external links, and topical patterns.

**Key Metrics:**
- Brand mention frequency and distribution
- Most discussed brands and topics
- External domain linking patterns
- Subreddit-specific brand activity
- Discussion thread popularity

**Run individually:**
```bash
python brand_topic_analysis.py
```

### 3. Network Structure Analysis (`network_analysis.py`)
Analyzes the graph structure of discussions and user interactions.

**Key Metrics:**
- Network topology (nodes, edges, density)
- Connected components analysis
- Centrality measures (degree, betweenness, closeness)
- Community structure detection
- Discussion thread depth analysis
- User interaction patterns

**Run individually:**
```bash
python network_analysis.py
```

### 4. Complete Pipeline (`run_complete_analysis.py`)
Runs all analyses in sequence and generates comprehensive reports.

**Features:**
- Automated pipeline execution
- Error handling and logging
- Comprehensive summary report generation
- Organized output structure

## 📁 Output Structure

After running the analysis, you'll find results in:

```
analysis/
├── plots/                          # Generated visualizations
│   ├── author_activity_analysis.png
│   ├── brand_topic_analysis.png
│   └── network_analysis.png
├── results/                        # Analysis results and data
│   ├── author_activity_results.csv
│   ├── brand_topic_results.json
│   ├── network_analysis_results.json
│   └── complete_analysis_summary.txt
```

## 🎯 Key Insights Generated

### Author Behavior
- **Participation Rate**: Percentage of registered users who actively contribute
- **Content Creator Types**: Distribution of posters vs commenters vs balanced contributors
- **Power User Identification**: Top contributors by activity volume
- **Engagement Patterns**: Comment-to-post ratios and interaction styles

### Brand & Topic Trends
- **Brand Mention Analysis**: Which EV brands are most discussed
- **Topic Evolution**: Trending discussion themes
- **External Information Sources**: Most linked domains and information sources
- **Community Focus Areas**: Subreddit-specific interests and brand preferences

### Community Structure
- **Network Connectivity**: How users and content are interconnected
- **Influence Patterns**: Identification of key opinion leaders
- **Discussion Depth**: Analysis of conversation thread complexity
- **Community Clusters**: Detection of specialized discussion groups

## 🔧 Customization

### Modifying Analysis Parameters

Each analysis module can be customized by modifying parameters:

```python
# Example: Customize author activity analysis
results = analyze_author_activity(
    nodes_file='custom_nodes.csv',
    edges_file='custom_edges.csv'
)

# Example: Customize network analysis edge types
graph = create_discussion_network(
    edge_types=['AUTHORED_BY', 'REPLY_TO']  # Only include specific relationships
)
```

### Adding New Analysis Functions

1. Create a new Python file in the `analysis/` directory
2. Follow the existing module structure:
   - Main analysis function returning structured results
   - Visualization function for plots
   - Insights printing function
   - Main execution block
3. Import and integrate into `run_complete_analysis.py`

## 📊 Data Requirements

### Expected Data Format

**nodes.csv:**
```csv
node_id,node_type,attrs_json
reddit:post:abc123,post,{"subreddit": "ElectricVehicles"}
reddit:author:username,author,{}
reddit:container:subreddit,container,{}
```

**edges.csv:**
```csv
src_id,dst_id,edge_type,weight,attrs_json
reddit:post:abc123,reddit:author:username,AUTHORED_BY,1.0,{}
reddit:comment:def456,reddit:post:abc123,REPLY_TO,1.0,{}
```

### Supported Edge Types
- `AUTHORED_BY`: Content authorship relationships
- `REPLY_TO`: Comment-to-post reply relationships  
- `IN_CONTAINER`: Content-to-subreddit containment
- `LINKS_TO_DOMAIN`: External domain references
- `MENTIONS_BRAND`: Brand mention annotations

## 🐛 Troubleshooting

### Common Issues

1. **"Data files not found" error**:
   - Ensure `data/processed/nodes.csv` and `data/processed/edges.csv` exist
   - Check file paths and current working directory

2. **Memory errors on large datasets**:
   - Reduce sample sizes in network centrality calculations
   - Process data in chunks for very large graphs
   - Consider using a machine with more RAM

3. **Missing dependencies**:
   ```bash
   pip install --upgrade -r analysis/requirements.txt
   ```

4. **Visualization issues**:
   - Ensure matplotlib backend is properly configured
   - For headless environments, add: `matplotlib.use('Agg')`

### Performance Optimization

For large datasets (>100k nodes):

1. **Sampling for centrality measures**: Network analysis automatically samples large graphs
2. **Chunk processing**: Modify analysis functions to process data in batches
3. **Memory management**: Use generators instead of loading full datasets

## 🤝 Contributing

To extend the analysis pipeline:

1. Fork the repository
2. Create new analysis modules following existing patterns
3. Add comprehensive docstrings and type hints
4. Include visualization and insight generation functions
5. Update this README with new module documentation
6. Submit a pull request

## 📄 License

This analysis pipeline is part of the EV-Crawler project. Please refer to the main repository for licensing information.

---

**Generated by**: EV Discussion Analysis Pipeline  
**Last Updated**: October 2025  
**Python Version**: 3.8+