"""
Create visualizations for the KG report.
Generates charts and graphs showing system performance and KG structure.
"""

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from pathlib import Path
import sys
import networkx as nx

sys.path.insert(0, str(Path(__file__).parent.parent))


def plot_entity_distribution(kg_data: dict, output_file: Path):
    """Plot distribution of entity types in the KG."""
    stats = kg_data['statistics']
    entity_types = stats['nodes_by_type']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    types = list(entity_types.keys())
    counts = list(entity_types.values())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    bars = ax.bar(types, counts, color=colors, edgecolor='black', linewidth=1.2)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('Entity Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title('Entity Type Distribution in Knowledge Graph', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved entity distribution plot to {output_file}")


def plot_relation_distribution(kg_data: dict, output_file: Path):
    """Plot distribution of relation types in the KG."""
    stats = kg_data['statistics']
    relation_types = stats['edges_by_relation']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Sort by count
    sorted_relations = sorted(relation_types.items(), key=lambda x: x[1], reverse=True)
    types = [r[0] for r in sorted_relations]
    counts = [r[1] for r in sorted_relations]
    
    colors = plt.cm.viridis(range(len(types)))
    bars = ax.bar(types, counts, color=colors, edgecolor='black', linewidth=1.2)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Relation Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title('Relation Type Distribution in Knowledge Graph', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved relation distribution plot to {output_file}")


def plot_ner_performance(eval_data: dict, output_file: Path):
    """Plot NER performance by entity type."""
    ner_by_type = eval_data['ner_re_evaluation']['by_entity_type']
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    entity_types = list(ner_by_type.keys())
    precisions = [ner_by_type[t]['precision'] for t in entity_types]
    recalls = [ner_by_type[t]['recall'] for t in entity_types]
    f1_scores = [ner_by_type[t]['f1_score'] for t in entity_types]
    
    x = range(len(entity_types))
    width = 0.25
    
    bars1 = ax.bar([i - width for i in x], precisions, width, label='Precision', 
                    color='#FF6B6B', edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x, recalls, width, label='Recall',
                    color='#4ECDC4', edgecolor='black', linewidth=1.2)
    bars3 = ax.bar([i + width for i in x], f1_scores, width, label='F1-Score',
                    color='#45B7D1', edgecolor='black', linewidth=1.2)
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=8)
    
    ax.set_xlabel('Entity Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('NER Performance by Entity Type', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(entity_types)
    ax.legend(loc='lower right', fontsize=10)
    ax.set_ylim([0, 1.1])
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved NER performance plot to {output_file}")


def plot_re_performance(eval_data: dict, output_file: Path):
    """Plot RE performance by relation type."""
    re_by_type = eval_data['ner_re_evaluation']['by_relation_type']
    
    # Filter out types with no data
    re_by_type = {k: v for k, v in re_by_type.items() 
                  if v['true_positives'] + v['false_positives'] + v['false_negatives'] > 0}
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    relation_types = list(re_by_type.keys())
    precisions = [re_by_type[t]['precision'] for t in relation_types]
    recalls = [re_by_type[t]['recall'] for t in relation_types]
    f1_scores = [re_by_type[t]['f1_score'] for t in relation_types]
    
    x = range(len(relation_types))
    width = 0.25
    
    bars1 = ax.bar([i - width for i in x], precisions, width, label='Precision',
                    color='#FF6B6B', edgecolor='black', linewidth=1.2)
    bars2 = ax.bar(x, recalls, width, label='Recall',
                    color='#4ECDC4', edgecolor='black', linewidth=1.2)
    bars3 = ax.bar([i + width for i in x], f1_scores, width, label='F1-Score',
                    color='#45B7D1', edgecolor='black', linewidth=1.2)
    
    # Add value labels
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}',
                        ha='center', va='bottom', fontsize=7)
    
    ax.set_xlabel('Relation Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Relation Extraction Performance by Type', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(relation_types, rotation=45, ha='right')
    ax.legend(loc='upper right', fontsize=10)
    ax.set_ylim([0, 1.1])
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved RE performance plot to {output_file}")


def plot_overall_comparison(eval_data: dict, output_file: Path):
    """Plot overall NER vs RE performance comparison."""
    ner_overall = eval_data['ner_re_evaluation']['overall']['ner']
    re_overall = eval_data['ner_re_evaluation']['overall']['re']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    metrics = ['Precision', 'Recall', 'F1-Score']
    ner_values = [ner_overall['precision'], ner_overall['recall'], ner_overall['f1_score']]
    re_values = [re_overall['precision'], re_overall['recall'], re_overall['f1_score']]
    
    x = range(len(metrics))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], ner_values, width, label='NER',
                    color='#4ECDC4', edgecolor='black', linewidth=1.2)
    bars2 = ax.bar([i + width/2 for i in x], re_values, width, label='RE',
                    color='#FF6B6B', edgecolor='black', linewidth=1.2)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Metric', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Overall NER vs RE Performance', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend(fontsize=11)
    ax.set_ylim([0, 1.1])
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved overall comparison plot to {output_file}")


def plot_kg_network_sample(kg_data: dict, output_file: Path, top_n: int = 20):
    """Plot a sample of the knowledge graph showing top entities."""
    nodes = kg_data['nodes']
    edges = kg_data['edges']
    
    # Get top N entities by degree
    node_degrees = {}
    for node in nodes:
        node_id = node['id']
        out_degree = sum(1 for e in edges if e['source'] == node_id)
        in_degree = sum(1 for e in edges if e['target'] == node_id)
        node_degrees[node_id] = out_degree + in_degree
    
    top_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_node_ids = set(n[0] for n in top_nodes)
    
    # Create subgraph
    G = nx.MultiDiGraph()
    
    # Add nodes
    node_info = {n['id']: n for n in nodes}
    for node_id in top_node_ids:
        info = node_info[node_id]
        G.add_node(node_id, **info)
    
    # Add edges between top nodes
    for edge in edges:
        if edge['source'] in top_node_ids and edge['target'] in top_node_ids:
            G.add_edge(edge['source'], edge['target'], **edge)
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Node colors by type
    type_colors = {
        'ORGANIZATION': '#FF6B6B',
        'PRODUCT': '#4ECDC4',
        'TECHNOLOGY': '#45B7D1',
        'LOCATION': '#FFA07A',
        'POLICY': '#98D8C8'
    }
    
    node_colors = [type_colors.get(G.nodes[n]['entity_type'], '#CCCCCC') for n in G.nodes()]
    
    # Node sizes by degree
    node_sizes = [node_degrees.get(n, 1) * 100 for n in G.nodes()]
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                           alpha=0.9, edgecolors='black', linewidths=2, ax=ax)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.3, 
                           arrows=True, arrowsize=10, width=0.5, ax=ax)
    
    # Draw labels
    labels = {n: G.nodes[n]['text'][:15] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold', ax=ax)
    
    # Legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                  markerfacecolor=color, markersize=10, label=etype)
                      for etype, color in type_colors.items()]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    ax.set_title(f'Knowledge Graph Sample (Top {top_n} Entities)', fontsize=14, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved KG network sample to {output_file}")


def main():
    """Generate all visualizations."""
    
    print("=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)
    print()
    
    # Setup paths
    crawler_root = Path(__file__).parent.parent
    kg_file = crawler_root / 'kg' / 'output' / 'knowledge_graph.json'
    eval_file = crawler_root / 'evaluation' / 'results' / 'comprehensive_evaluation.json'
    output_dir = crawler_root / 'kg_report' / 'figures'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("Loading data...")
    with open(kg_file, 'r', encoding='utf-8') as f:
        kg_data = json.load(f)
    
    with open(eval_file, 'r', encoding='utf-8') as f:
        eval_data = json.load(f)
    
    print()
    
    # Generate plots
    plot_entity_distribution(kg_data, output_dir / 'entity_distribution.pdf')
    plot_relation_distribution(kg_data, output_dir / 'relation_distribution.pdf')
    plot_ner_performance(eval_data, output_dir / 'ner_performance.pdf')
    plot_re_performance(eval_data, output_dir / 're_performance.pdf')
    plot_overall_comparison(eval_data, output_dir / 'overall_comparison.pdf')
    plot_kg_network_sample(kg_data, output_dir / 'kg_network_sample.pdf', top_n=20)
    
    print()
    print("=" * 80)
    print("VISUALIZATION COMPLETE")
    print("=" * 80)
    print(f"\nAll figures saved to {output_dir}")


if __name__ == '__main__':
    main()
