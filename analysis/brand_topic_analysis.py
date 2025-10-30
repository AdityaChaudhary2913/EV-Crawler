"""Analysis of brand mentions and topic patterns in the EV dataset."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from typing import Dict, List, Tuple
from collections import Counter
import json

def analyze_brand_mentions(nodes_file: str = 'data/processed/nodes.csv', 
                          edges_file: str = 'data/processed/edges.csv') -> Dict:
    """
    Analyze brand mentions and topic patterns in the EV discussion data.
    
    Args:
        nodes_file: Path to nodes CSV file
        edges_file: Path to edges CSV file
        
    Returns:
        Dictionary containing brand mention analysis and topic insights
    """
    
    # Load data
    nodes_df = pd.read_csv(nodes_file)
    edges_df = pd.read_csv(edges_file)
    
    # Get brand mentions
    brand_edges = edges_df[edges_df['edge_type'] == 'MENTIONS_BRAND'].copy()
    
    # Count brand mentions by weight (frequency)
    brand_counts = brand_edges.groupby('src_id')['weight'].sum().reset_index()
    brand_counts.columns = ['post_id', 'brand_mentions']
    brand_counts = brand_counts.sort_values('brand_mentions', ascending=False)
    
    # Get posts and their metadata
    posts_df = nodes_df[nodes_df['node_type'] == 'post'].copy()
    
    # Parse attributes to get subreddit info
    posts_df['subreddit'] = posts_df['attrs_json'].apply(
        lambda x: json.loads(x).get('subreddit', 'Unknown') if x != '{}' else 'Unknown'
    )
    
    # Merge brand mentions with post metadata
    posts_with_brands = brand_counts.merge(
        posts_df[['node_id', 'subreddit']], 
        left_on='post_id', right_on='node_id', 
        how='left'
    )
    
    # Analyze domain patterns
    domain_edges = edges_df[edges_df['edge_type'] == 'LINKS_TO_DOMAIN'].copy()
    domain_counts = domain_edges['dst_id'].value_counts().head(20)
    
    # Get most frequently linked domains
    top_domains = domain_counts.to_dict()
    
    # Analyze container (subreddit) activity
    container_edges = edges_df[edges_df['edge_type'] == 'IN_CONTAINER'].copy()
    container_counts = container_edges['dst_id'].value_counts()
    
    # Calculate brand mention distribution
    brand_distribution = {
        'total_posts_with_brands': len(brand_counts),
        'total_brand_mentions': brand_counts['brand_mentions'].sum(),
        'avg_brands_per_post': brand_counts['brand_mentions'].mean(),
        'max_brands_in_post': brand_counts['brand_mentions'].max(),
        'posts_by_brand_count': brand_counts['brand_mentions'].value_counts().to_dict()
    }
    
    # Find posts with most brand mentions
    top_brand_posts = posts_with_brands.head(10).to_dict('records')
    
    # Analyze subreddit patterns
    subreddit_brand_activity = posts_with_brands.groupby('subreddit').agg({
        'brand_mentions': ['count', 'sum', 'mean']
    }).round(2)
    
    subreddit_brand_activity.columns = ['posts_with_brands', 'total_brand_mentions', 'avg_brands_per_post']
    subreddit_brand_activity = subreddit_brand_activity.reset_index().sort_values(
        'total_brand_mentions', ascending=False
    )
    
    # Content analysis - get reply patterns
    reply_edges = edges_df[edges_df['edge_type'] == 'REPLY_TO'].copy()
    reply_patterns = {
        'total_replies': len(reply_edges),
        'posts_with_replies': reply_edges['dst_id'].nunique(),
        'avg_replies_per_thread': len(reply_edges) / reply_edges['dst_id'].nunique() if reply_edges['dst_id'].nunique() > 0 else 0
    }
    
    # Identify discussion threads (posts with many replies)
    popular_threads = reply_edges['dst_id'].value_counts().head(10)
    
    results = {
        'brand_analysis': {
            'distribution': brand_distribution,
            'top_brand_posts': top_brand_posts,
            'subreddit_patterns': subreddit_brand_activity.to_dict('records')
        },
        'domain_analysis': {
            'top_domains': top_domains,
            'total_domain_links': len(domain_edges),
            'unique_domains': domain_edges['dst_id'].nunique()
        },
        'engagement_analysis': {
            'reply_patterns': reply_patterns,
            'popular_threads': popular_threads.to_dict(),
            'container_activity': container_counts.to_dict()
        },
        'data_summary': {
            'total_posts': len(posts_df),
            'posts_with_brand_mentions': len(brand_counts),
            'brand_mention_rate': len(brand_counts) / len(posts_df) * 100 if len(posts_df) > 0 else 0
        }
    }
    
    return results

def plot_brand_topic_analysis(results: Dict, save_path: str = None) -> None:
    """
    Create visualizations for brand and topic analysis.
    
    Args:
        results: Results from analyze_brand_mentions
        save_path: Optional path to save the plot
    """
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Brand Mentions and Topic Analysis - EV Discussions', fontsize=16, fontweight='bold')
    
    # 1. Brand mention distribution
    ax1 = axes[0, 0]
    brand_dist = results['brand_analysis']['distribution']['posts_by_brand_count']
    # Limit to reasonable range for visualization
    brand_dist_filtered = {k: v for k, v in brand_dist.items() if k <= 10}
    
    bars1 = ax1.bar(brand_dist_filtered.keys(), brand_dist_filtered.values(), 
                    color='darkgreen', alpha=0.7)
    ax1.set_title('Distribution of Brand Mentions per Post', fontweight='bold')
    ax1.set_xlabel('Number of Brand Mentions')
    ax1.set_ylabel('Number of Posts')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    # 2. Top domains
    ax2 = axes[0, 1]
    top_domains = list(results['domain_analysis']['top_domains'].items())[:10]
    domains, counts = zip(*top_domains)
    
    # Clean domain names for display
    clean_domains = [d.replace('domain:', '') for d in domains]
    
    bars2 = ax2.barh(range(len(clean_domains)), counts, color='steelblue', alpha=0.7)
    ax2.set_title('Top 10 Most Linked Domains', fontweight='bold')
    ax2.set_xlabel('Number of Links')
    ax2.set_yticks(range(len(clean_domains)))
    ax2.set_yticklabels(clean_domains, fontsize=9)
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, bar in enumerate(bars2):
        width = bar.get_width()
        ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2.,
                f'{int(width)}', ha='left', va='center', fontsize=9)
    
    # 3. Subreddit brand activity
    ax3 = axes[1, 0]
    subreddit_data = results['brand_analysis']['subreddit_patterns'][:5]  # Top 5 subreddits
    
    if subreddit_data:
        subreddits = [item['subreddit'] for item in subreddit_data]
        posts_with_brands = [item['posts_with_brands'] for item in subreddit_data]
        total_mentions = [item['total_brand_mentions'] for item in subreddit_data]
        
        x = range(len(subreddits))
        width = 0.35
        
        bars3a = ax3.bar([i - width/2 for i in x], posts_with_brands, width, 
                        label='Posts with Brands', color='lightcoral', alpha=0.8)
        bars3b = ax3.bar([i + width/2 for i in x], total_mentions, width,
                        label='Total Brand Mentions', color='lightskyblue', alpha=0.8)
        
        ax3.set_title('Brand Activity by Subreddit (Top 5)', fontweight='bold')
        ax3.set_xlabel('Subreddit')
        ax3.set_ylabel('Count')
        ax3.set_xticks(x)
        ax3.set_xticklabels(subreddits, rotation=45, ha='right')
        ax3.legend()
        ax3.grid(axis='y', alpha=0.3)
    
    # 4. Popular discussion threads
    ax4 = axes[1, 1]
    popular_threads = list(results['engagement_analysis']['popular_threads'].items())[:10]
    
    if popular_threads:
        thread_ids, reply_counts = zip(*popular_threads)
        # Simplify thread IDs for display
        thread_labels = [f"Thread {i+1}" for i in range(len(thread_ids))]
        
        bars4 = ax4.bar(thread_labels, reply_counts, color='orange', alpha=0.7)
        ax4.set_title('Most Active Discussion Threads', fontweight='bold')
        ax4.set_xlabel('Discussion Threads')
        ax4.set_ylabel('Number of Replies')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    plt.show()

def print_brand_topic_insights(results: Dict) -> None:
    """
    Print key insights from brand and topic analysis.
    
    Args:
        results: Results from analyze_brand_mentions
    """
    
    print("=" * 60)
    print("🏷️  BRAND MENTIONS & TOPIC ANALYSIS - EV DISCUSSIONS")
    print("=" * 60)
    
    # Brand analysis
    brand_data = results['brand_analysis']['distribution']
    data_summary = results['data_summary']
    
    print(f"\n📊 BRAND MENTION OVERVIEW:")
    print(f"  • Total posts: {data_summary['total_posts']:,}")
    print(f"  • Posts with brand mentions: {data_summary['posts_with_brand_mentions']:,}")
    print(f"  • Brand mention rate: {data_summary['brand_mention_rate']:.1f}%")
    print(f"  • Total brand mentions: {brand_data['total_brand_mentions']:,}")
    print(f"  • Average brands per post: {brand_data['avg_brands_per_post']:.1f}")
    print(f"  • Maximum brands in single post: {brand_data['max_brands_in_post']}")
    
    # Top brand posts
    print(f"\n🏆 TOP 5 POSTS WITH MOST BRAND MENTIONS:")
    for i, post in enumerate(results['brand_analysis']['top_brand_posts'][:5], 1):
        post_id = post['post_id'].split(':')[-1]  # Extract post ID
        print(f"  {i}. Post {post_id}")
        print(f"     • Brand mentions: {post['brand_mentions']}")
        print(f"     • Subreddit: r/{post.get('subreddit', 'Unknown')}")
    
    # Domain analysis
    domain_data = results['domain_analysis']
    print(f"\n🌐 DOMAIN LINKING PATTERNS:")
    print(f"  • Total domain links: {domain_data['total_domain_links']:,}")
    print(f"  • Unique domains linked: {domain_data['unique_domains']:,}")
    
    print(f"  \n  Top 5 Most Linked Domains:")
    for i, (domain, count) in enumerate(list(domain_data['top_domains'].items())[:5], 1):
        clean_domain = domain.replace('domain:', '')
        print(f"    {i}. {clean_domain}: {count} links")
    
    # Engagement analysis
    engagement = results['engagement_analysis']
    reply_data = engagement['reply_patterns']
    
    print(f"\n💬 ENGAGEMENT & DISCUSSION PATTERNS:")
    print(f"  • Total replies: {reply_data['total_replies']:,}")
    print(f"  • Posts with replies: {reply_data['posts_with_replies']:,}")
    print(f"  • Average replies per thread: {reply_data['avg_replies_per_thread']:.1f}")
    
    # Subreddit patterns
    subreddit_data = results['brand_analysis']['subreddit_patterns'][:3]
    print(f"\n🎯 TOP 3 SUBREDDITS BY BRAND ACTIVITY:")
    for i, sub_data in enumerate(subreddit_data, 1):
        print(f"  {i}. r/{sub_data['subreddit']}")
        print(f"     • Posts with brands: {sub_data['posts_with_brands']}")
        print(f"     • Total brand mentions: {sub_data['total_brand_mentions']}")
        print(f"     • Avg brands per post: {sub_data['avg_brands_per_post']:.1f}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Run the analysis
    results = analyze_brand_mentions()
    
    # Print insights
    print_brand_topic_insights(results)
    
    # Create visualizations
    plot_brand_topic_analysis(results, save_path='plots/brand_topic_analysis.png')
    
    # Save results to JSON for further analysis
    import json
    with open('analysis/brand_topic_results.json', 'w') as f:
        # Convert any non-serializable objects to strings
        serializable_results = json.loads(json.dumps(results, default=str))
        json.dump(serializable_results, f, indent=2)
    
    print("\n✅ Detailed results saved to 'analysis/brand_topic_results.json'")