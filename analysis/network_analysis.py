"""Network analysis of the EV discussion graph structure."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

def create_discussion_network(nodes_file: str = 'data/processed/nodes.csv',
                            edges_file: str = 'data/processed/edges.csv',
                            edge_types: List[str] = None) -> nx.Graph:
    """
    Create a NetworkX graph from the EV discussion data.
    
    Args:
        nodes_file: Path to nodes CSV file
        edges_file: Path to edges CSV file
        edge_types: List of edge types to include (default: all except MENTIONS_BRAND)
        
    Returns:
        NetworkX graph object
    """
    
    # Load data
    nodes_df = pd.read_csv(nodes_file)
    edges_df = pd.read_csv(edges_file)
    
    # Default edge types to include (exclude MENTIONS_BRAND for network structure)
    if edge_types is None:
        edge_types = ['AUTHORED_BY', 'REPLY_TO', 'IN_CONTAINER', 'LINKS_TO_DOMAIN']
    
    # Filter edges
    filtered_edges = edges_df[edges_df['edge_type'].isin(edge_types)].copy()
    
    # Create graph
    G = nx.Graph()
    
    # Add nodes with attributes
    for _, node in nodes_df.iterrows():
        G.add_node(node['node_id'], 
                  node_type=node['node_type'],
                  attrs=node['attrs_json'])
    
    # Add edges
    for _, edge in filtered_edges.iterrows():
        G.add_edge(edge['src_id'], edge['dst_id'],
                  edge_type=edge['edge_type'],
                  weight=edge['weight'])
    
    return G

def analyze_network_structure(graph: nx.Graph) -> Dict:
    """
    Analyze the structure and properties of the discussion network.
    
    Args:
        graph: NetworkX graph to analyze
        
    Returns:
        Dictionary containing network analysis results
    """
    
    print("Analyzing network structure...")
    
    # Basic network statistics
    basic_stats = {
        'num_nodes': graph.number_of_nodes(),
        'num_edges': graph.number_of_edges(),
        'density': nx.density(graph),
        'is_connected': nx.is_connected(graph)
    }
    
    # Connected components analysis
    components = list(nx.connected_components(graph))
    component_sizes = [len(comp) for comp in components]
    
    components_info = {
        'num_components': len(components),
        'largest_component_size': max(component_sizes) if component_sizes else 0,
        'component_size_distribution': Counter(component_sizes)
    }
    
    # Degree analysis
    degrees = dict(graph.degree())
    degree_values = list(degrees.values())
    
    degree_stats = {
        'avg_degree': np.mean(degree_values),
        'max_degree': max(degree_values) if degree_values else 0,
        'min_degree': min(degree_values) if degree_values else 0,
        'degree_distribution': Counter(degree_values)
    }
    
    # Find high-degree nodes (hubs)
    degree_threshold = np.percentile(degree_values, 95) if degree_values else 0
    hub_nodes = [(node, deg) for node, deg in degrees.items() if deg >= degree_threshold]
    hub_nodes.sort(key=lambda x: x[1], reverse=True)
    
    # Analyze node types
    node_types = nx.get_node_attributes(graph, 'node_type')
    node_type_counts = Counter(node_types.values())
    
    # Analyze edge types
    edge_types = nx.get_edge_attributes(graph, 'edge_type')
    edge_type_counts = Counter(edge_types.values())
    
    # Network centrality measures (on largest component to avoid disconnected issues)
    largest_component = max(components, key=len) if components else set()
    largest_subgraph = graph.subgraph(largest_component)
    
    centrality_measures = {}
    if len(largest_component) > 1:
        print(f"Computing centrality measures on largest component ({len(largest_component)} nodes)...")
        
        # Degree centrality
        degree_centrality = nx.degree_centrality(largest_subgraph)
        top_degree_central = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Betweenness centrality (sample for large graphs)
        if len(largest_component) > 1000:
            # Sample for computational efficiency
            sample_nodes = np.random.choice(list(largest_component), size=min(500, len(largest_component)), replace=False)
            betweenness_centrality = nx.betweenness_centrality(largest_subgraph, k=len(sample_nodes))
        else:
            betweenness_centrality = nx.betweenness_centrality(largest_subgraph)
        
        top_betweenness_central = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Closeness centrality
        closeness_centrality = nx.closeness_centrality(largest_subgraph)
        top_closeness_central = sorted(closeness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        centrality_measures = {
            'top_degree_central': top_degree_central,
            'top_betweenness_central': top_betweenness_central,
            'top_closeness_central': top_closeness_central
        }
    
    # Clustering analysis
    clustering_coeffs = nx.clustering(graph)
    clustering_stats = {
        'avg_clustering': np.mean(list(clustering_coeffs.values())),
        'global_clustering': nx.transitivity(graph)
    }
    
    results = {
        'basic_stats': basic_stats,
        'components': components_info,
        'degree_analysis': degree_stats,
        'hub_nodes': hub_nodes[:20],  # Top 20 hub nodes
        'node_types': dict(node_type_counts),
        'edge_types': dict(edge_type_counts),
        'centrality': centrality_measures,
        'clustering': clustering_stats,
        'largest_component_nodes': len(largest_component)
    }
    
    return results

def analyze_discussion_patterns(graph: nx.Graph, nodes_df: pd.DataFrame, edges_df: pd.DataFrame) -> Dict:
    """
    Analyze specific discussion patterns in the EV forum data.
    
    Args:
        graph: NetworkX graph
        nodes_df: Nodes dataframe
        edges_df: Edges dataframe
        
    Returns:
        Dictionary containing discussion pattern analysis
    """
    
    print("Analyzing discussion patterns...")
    
    # Author interaction patterns
    authors = nodes_df[nodes_df['node_type'] == 'author']['node_id'].tolist()
    author_subgraph = graph.subgraph(authors)
    
    # Posts and comments analysis
    posts = nodes_df[nodes_df['node_type'] == 'post']['node_id'].tolist()
    comments = nodes_df[nodes_df['node_type'] == 'comment']['node_id'].tolist()
    
    # Reply chain analysis
    reply_edges = edges_df[edges_df['edge_type'] == 'REPLY_TO']
    
    # Build reply graph to find conversation threads
    reply_graph = nx.DiGraph()
    for _, edge in reply_edges.iterrows():
        reply_graph.add_edge(edge['src_id'], edge['dst_id'])
    
    # Find discussion thread depths
    thread_depths = []
    for post in posts:
        if post in reply_graph:
            # Find all paths from comments to this post
            depths = []
            for comment in comments:
                if comment in reply_graph:
                    try:
                        if nx.has_path(reply_graph, comment, post):
                            path_length = nx.shortest_path_length(reply_graph, comment, post)
                            depths.append(path_length)
                    except:
                        continue
            if depths:
                thread_depths.extend(depths)
    
    # Cross-platform linking patterns
    domain_edges = edges_df[edges_df['edge_type'] == 'LINKS_TO_DOMAIN']
    domain_patterns = {
        'total_external_links': len(domain_edges),
        'unique_domains': domain_edges['dst_id'].nunique(),
        'posts_with_links': domain_edges['src_id'].nunique(),
        'avg_links_per_post': len(domain_edges) / domain_edges['src_id'].nunique() if domain_edges['src_id'].nunique() > 0 else 0
    }
    
    # User engagement patterns
    authorship_edges = edges_df[edges_df['edge_type'] == 'AUTHORED_BY']
    author_activity = authorship_edges['dst_id'].value_counts()
    
    engagement_patterns = {
        'active_authors': len(author_activity),
        'lurker_authors': len(authors) - len(author_activity),
        'participation_rate': len(author_activity) / len(authors) * 100 if len(authors) > 0 else 0,
        'content_creators': len(author_activity[author_activity > 1]),  # Authors with >1 post/comment
        'power_users': len(author_activity[author_activity > author_activity.quantile(0.9)])  # Top 10% most active
    }
    
    results = {
        'thread_analysis': {
            'avg_thread_depth': np.mean(thread_depths) if thread_depths else 0,
            'max_thread_depth': max(thread_depths) if thread_depths else 0,
            'total_reply_chains': len(reply_edges)
        },
        'domain_patterns': domain_patterns,
        'engagement_patterns': engagement_patterns,
        'author_network': {
            'connected_authors': len(author_subgraph),
            'author_connections': author_subgraph.number_of_edges()
        }
    }
    
    return results

def plot_network_analysis(network_results: Dict, discussion_results: Dict, save_path: str = None) -> None:
    """
    Create visualizations for network analysis results.
    
    Args:
        network_results: Results from analyze_network_structure
        discussion_results: Results from analyze_discussion_patterns
        save_path: Optional path to save the plot
    """
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Network Structure Analysis - EV Discussions', fontsize=16, fontweight='bold')
    
    # 1. Node type distribution
    ax1 = axes[0, 0]
    node_types = network_results['node_types']
    colors = ['skyblue', 'lightcoral', 'lightgreen', 'gold', 'plum']
    
    wedges, texts, autotexts = ax1.pie(node_types.values(), labels=node_types.keys(), 
                                      autopct='%1.1f%%', colors=colors[:len(node_types)],
                                      startangle=90)
    ax1.set_title('Network Node Types Distribution', fontweight='bold')
    
    # 2. Degree distribution
    ax2 = axes[0, 1]
    degree_dist = network_results['degree_analysis']['degree_distribution']
    # Limit to reasonable range for visualization
    max_degree_shown = min(50, max(degree_dist.keys()) if degree_dist else 0)
    filtered_dist = {k: v for k, v in degree_dist.items() if k <= max_degree_shown}
    
    if filtered_dist:
        degrees, counts = zip(*sorted(filtered_dist.items()))
        ax2.bar(degrees, counts, color='steelblue', alpha=0.7, width=0.8)
    
    ax2.set_title('Node Degree Distribution', fontweight='bold')
    ax2.set_xlabel('Degree')
    ax2.set_ylabel('Number of Nodes')
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Component size distribution
    ax3 = axes[1, 0]
    comp_dist = network_results['components']['component_size_distribution']
    # Show distribution of component sizes
    if comp_dist:
        sizes, counts = zip(*sorted(comp_dist.items()))
        # Use log scale for x-axis if there's a wide range
        bars = ax3.bar(range(len(sizes)), counts, color='orange', alpha=0.7)
        ax3.set_xticks(range(len(sizes)))
        ax3.set_xticklabels([str(s) for s in sizes], rotation=45)
    
    ax3.set_title('Connected Component Sizes', fontweight='bold')
    ax3.set_xlabel('Component Size')
    ax3.set_ylabel('Number of Components')
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Engagement patterns
    ax4 = axes[1, 1]
    engage_data = discussion_results['engagement_patterns']
    
    categories = ['Active\nAuthors', 'Content\nCreators', 'Power\nUsers']
    values = [
        engage_data['active_authors'],
        engage_data['content_creators'],
        engage_data['power_users']
    ]
    colors_bar = ['lightblue', 'lightgreen', 'gold']
    
    bars = ax4.bar(categories, values, color=colors_bar, alpha=0.8)
    ax4.set_title('User Engagement Categories', fontweight='bold')
    ax4.set_ylabel('Number of Users')
    ax4.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    plt.show()

def print_network_insights(network_results: Dict, discussion_results: Dict) -> None:
    """
    Print key insights from network analysis.
    
    Args:
        network_results: Results from analyze_network_structure
        discussion_results: Results from analyze_discussion_patterns
    """
    
    print("=" * 60)
    print("🕸️  NETWORK STRUCTURE ANALYSIS - EV DISCUSSIONS")
    print("=" * 60)
    
    # Basic network statistics
    basic = network_results['basic_stats']
    print(f"\n🌐 NETWORK OVERVIEW:")
    print(f"  • Total nodes: {basic['num_nodes']:,}")
    print(f"  • Total edges: {basic['num_edges']:,}")
    print(f"  • Network density: {basic['density']:.6f}")
    print(f"  • Is connected: {basic['is_connected']}")
    
    # Component analysis
    comp = network_results['components']
    print(f"\n🧩 CONNECTIVITY:")
    print(f"  • Connected components: {comp['num_components']:,}")
    print(f"  • Largest component size: {comp['largest_component_size']:,}")
    print(f"  • Nodes in largest component: {network_results['largest_component_nodes']:,}")
    
    # Degree analysis
    degree = network_results['degree_analysis']
    print(f"\n📈 DEGREE STATISTICS:")
    print(f"  • Average degree: {degree['avg_degree']:.2f}")
    print(f"  • Maximum degree: {degree['max_degree']}")
    print(f"  • Minimum degree: {degree['min_degree']}")
    
    # Hub nodes
    print(f"\n🎆 TOP 5 HUB NODES (Highest Degree):")
    for i, (node, deg) in enumerate(network_results['hub_nodes'][:5], 1):
        node_type = node.split(':')[1] if ':' in node else 'unknown'
        node_id = node.split(':')[-1] if ':' in node else node
        print(f"  {i}. {node_type.title()} {node_id[:20]}... (degree: {deg})")
    
    # Node types
    node_types = network_results['node_types']
    print(f"\n📁 NODE TYPE DISTRIBUTION:")
    for node_type, count in node_types.items():
        print(f"  • {node_type.title()}: {count:,}")
    
    # Discussion patterns
    thread = discussion_results['thread_analysis']
    print(f"\n💬 DISCUSSION PATTERNS:")
    print(f"  • Average thread depth: {thread['avg_thread_depth']:.1f}")
    print(f"  • Maximum thread depth: {thread['max_thread_depth']}")
    print(f"  • Total reply chains: {thread['total_reply_chains']:,}")
    
    # Engagement patterns
    engage = discussion_results['engagement_patterns']
    print(f"\n👥 USER ENGAGEMENT:")
    print(f"  • Active authors: {engage['active_authors']:,}")
    print(f"  • Participation rate: {engage['participation_rate']:.1f}%")
    print(f"  • Content creators (>1 post): {engage['content_creators']:,}")
    print(f"  • Power users (top 10%): {engage['power_users']:,}")
    
    # Domain patterns
    domains = discussion_results['domain_patterns']
    print(f"\n🌐 EXTERNAL LINKING:")
    print(f"  • Total external links: {domains['total_external_links']:,}")
    print(f"  • Unique domains linked: {domains['unique_domains']:,}")
    print(f"  • Posts with external links: {domains['posts_with_links']:,}")
    print(f"  • Average links per post: {domains['avg_links_per_post']:.1f}")
    
    # Clustering
    clustering = network_results['clustering']
    print(f"\n🌐 NETWORK CLUSTERING:")
    print(f"  • Average local clustering: {clustering['avg_clustering']:.4f}")
    print(f"  • Global clustering coefficient: {clustering['global_clustering']:.4f}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Load data and create network
    print("Loading data and creating network...")
    graph = create_discussion_network()
    
    # Load dataframes for additional analysis
    nodes_df = pd.read_csv('data/processed/nodes.csv')
    edges_df = pd.read_csv('data/processed/edges.csv')
    
    # Analyze network structure
    network_results = analyze_network_structure(graph)
    
    # Analyze discussion patterns
    discussion_results = analyze_discussion_patterns(graph, nodes_df, edges_df)
    
    # Print insights
    print_network_insights(network_results, discussion_results)
    
    # Create visualizations
    plot_network_analysis(network_results, discussion_results, 
                         save_path='plots/network_analysis.png')
    
    # Save results
    import json
    combined_results = {
        'network_structure': network_results,
        'discussion_patterns': discussion_results
    }
    
    # Convert non-serializable objects to strings
    serializable_results = json.loads(json.dumps(combined_results, default=str))
    
    with open('analysis/network_analysis_results.json', 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print("\n✅ Network analysis complete! Results saved to 'analysis/network_analysis_results.json'")