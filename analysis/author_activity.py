"""Analysis of author activity patterns in the EV dataset."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

def analyze_author_activity(nodes_file: str = 'data/processed/nodes.csv', 
                          edges_file: str = 'data/processed/edges.csv') -> Dict:
    """
    Analyze author activity patterns in the EV discussion data.
    
    Args:
        nodes_file: Path to nodes CSV file
        edges_file: Path to edges CSV file
        
    Returns:
        Dictionary containing various author activity metrics
    """
    
    # Load data
    nodes_df = pd.read_csv(nodes_file)
    edges_df = pd.read_csv(edges_file)
    
    # Filter for authors only
    authors_df = nodes_df[nodes_df['node_type'] == 'author'].copy()
    
    # Get authorship relationships (posts and comments authored by users)
    authored_edges = edges_df[edges_df['edge_type'] == 'AUTHORED_BY'].copy()
    
    # Count posts and comments per author
    author_activity = authored_edges.groupby('dst_id').agg({
        'src_id': 'count',  # Total items authored
        'weight': 'sum'     # Total weight (should be same as count for AUTHORED_BY)
    }).reset_index()
    author_activity.columns = ['author_id', 'total_authored', 'total_weight']
    
    # Separate posts vs comments
    post_authors = authored_edges[authored_edges['src_id'].str.contains('reddit:post:')]
    comment_authors = authored_edges[authored_edges['src_id'].str.contains('reddit:comment:')]
    
    posts_per_author = post_authors.groupby('dst_id').size().reset_index()
    posts_per_author.columns = ['author_id', 'posts_count']
    
    comments_per_author = comment_authors.groupby('dst_id').size().reset_index()
    comments_per_author.columns = ['author_id', 'comments_count']
    
    # Merge all activity data
    activity_summary = author_activity.merge(
        posts_per_author, on='author_id', how='left'
    ).merge(
        comments_per_author, on='author_id', how='left'
    ).fillna(0)
    
    # Convert counts to integers
    activity_summary['posts_count'] = activity_summary['posts_count'].astype(int)
    activity_summary['comments_count'] = activity_summary['comments_count'].astype(int)
    
    # Calculate engagement ratio (comments per post)
    activity_summary['engagement_ratio'] = activity_summary.apply(
        lambda row: row['comments_count'] / max(row['posts_count'], 1), axis=1
    )
    
    # Sort by total activity
    activity_summary = activity_summary.sort_values('total_authored', ascending=False)
    
    # Create analysis results
    results = {
        'total_authors': len(authors_df),
        'active_authors': len(activity_summary[activity_summary['total_authored'] > 0]),
        'top_authors': activity_summary.head(20).to_dict('records'),
        'activity_distribution': {
            'mean_posts_per_author': activity_summary['posts_count'].mean(),
            'mean_comments_per_author': activity_summary['comments_count'].mean(),
            'median_posts_per_author': activity_summary['posts_count'].median(),
            'median_comments_per_author': activity_summary['comments_count'].median(),
            'max_posts_by_single_author': activity_summary['posts_count'].max(),
            'max_comments_by_single_author': activity_summary['comments_count'].max()
        },
        'engagement_patterns': {
            'high_posters_low_commenters': len(activity_summary[
                (activity_summary['posts_count'] > activity_summary['posts_count'].quantile(0.75)) &
                (activity_summary['comments_count'] < activity_summary['comments_count'].quantile(0.25))
            ]),
            'high_commenters_low_posters': len(activity_summary[
                (activity_summary['comments_count'] > activity_summary['comments_count'].quantile(0.75)) &
                (activity_summary['posts_count'] < activity_summary['posts_count'].quantile(0.25))
            ]),
            'balanced_contributors': len(activity_summary[
                (activity_summary['posts_count'] > activity_summary['posts_count'].quantile(0.5)) &
                (activity_summary['comments_count'] > activity_summary['comments_count'].quantile(0.5))
            ])
        },
        'activity_summary_df': activity_summary
    }
    
    return results

def plot_author_activity(results: Dict, save_path: str = None) -> None:
    """
    Create visualizations of author activity patterns.
    
    Args:
        results: Results from analyze_author_activity
        save_path: Optional path to save the plot
    """
    
    activity_df = results['activity_summary_df']
    
    # Create a figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Author Activity Analysis - EV Discussions', fontsize=16, fontweight='bold')
    
    # 1. Top 20 most active authors
    top_20 = activity_df.head(20)
    ax1 = axes[0, 0]
    bars = ax1.bar(range(len(top_20)), top_20['total_authored'], 
                   color='steelblue', alpha=0.7)
    ax1.set_title('Top 20 Most Active Authors', fontweight='bold')
    ax1.set_xlabel('Author Rank')
    ax1.set_ylabel('Total Posts + Comments')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    # 2. Distribution of posts vs comments
    ax2 = axes[0, 1]
    # Filter out authors with 0 activity for cleaner visualization
    active_authors = activity_df[activity_df['total_authored'] > 0]
    scatter = ax2.scatter(active_authors['posts_count'], active_authors['comments_count'], 
                         alpha=0.6, color='coral')
    ax2.set_title('Posts vs Comments Distribution', fontweight='bold')
    ax2.set_xlabel('Number of Posts')
    ax2.set_ylabel('Number of Comments')
    ax2.grid(True, alpha=0.3)
    
    # Add diagonal line for reference (equal posts and comments)
    max_val = max(active_authors['posts_count'].max(), active_authors['comments_count'].max())
    ax2.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, linewidth=1)
    
    # 3. Activity distribution histogram
    ax3 = axes[1, 0]
    # Use log scale for better visualization of long tail
    bins = [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000]
    ax3.hist(active_authors['total_authored'], bins=bins, color='lightgreen', 
             alpha=0.7, edgecolor='black')
    ax3.set_title('Distribution of Author Activity Levels', fontweight='bold')
    ax3.set_xlabel('Total Posts + Comments')
    ax3.set_ylabel('Number of Authors')
    ax3.set_xscale('log')
    ax3.grid(True, alpha=0.3)
    
    # 4. Engagement patterns pie chart
    ax4 = axes[1, 1]
    engagement_data = results['engagement_patterns']
    labels = ['High Posters\n(Low Comments)', 'High Commenters\n(Low Posts)', 'Balanced\nContributors']
    sizes = [engagement_data['high_posters_low_commenters'], 
             engagement_data['high_commenters_low_posters'],
             engagement_data['balanced_contributors']]
    colors = ['lightcoral', 'lightskyblue', 'lightgreen']
    
    ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax4.set_title('Author Engagement Patterns', fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    plt.show()

def print_author_insights(results: Dict) -> None:
    """
    Print key insights from author activity analysis.
    
    Args:
        results: Results from analyze_author_activity
    """
    
    print("=" * 50)
    print("📊 AUTHOR ACTIVITY ANALYSIS - EV DISCUSSIONS")
    print("=" * 50)
    
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"  • Total Authors: {results['total_authors']:,}")
    print(f"  • Active Authors: {results['active_authors']:,}")
    print(f"  • Participation Rate: {results['active_authors']/results['total_authors']*100:.1f}%")
    
    print(f"\n🏆 TOP 5 MOST ACTIVE AUTHORS:")
    for i, author in enumerate(results['top_authors'][:5], 1):
        author_name = author['author_id'].split(':')[-1]  # Extract username
        print(f"  {i}. {author_name}")
        print(f"     • Total Activity: {author['total_authored']} items")
        print(f"     • Posts: {author['posts_count']}, Comments: {author['comments_count']}")
        print(f"     • Engagement Ratio: {author['engagement_ratio']:.1f} comments/post")
    
    dist = results['activity_distribution']
    print(f"\n📊 ACTIVITY DISTRIBUTION:")
    print(f"  • Average posts per author: {dist['mean_posts_per_author']:.1f}")
    print(f"  • Average comments per author: {dist['mean_comments_per_author']:.1f}")
    print(f"  • Most posts by single author: {dist['max_posts_by_single_author']}")
    print(f"  • Most comments by single author: {dist['max_comments_by_single_author']}")
    
    engage = results['engagement_patterns']
    print(f"\n🎯 ENGAGEMENT PATTERNS:")
    print(f"  • High Posters (Low Comments): {engage['high_posters_low_commenters']} authors")
    print(f"  • High Commenters (Low Posts): {engage['high_commenters_low_posters']} authors")
    print(f"  • Balanced Contributors: {engage['balanced_contributors']} authors")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    # Run the analysis
    results = analyze_author_activity()
    
    # Print insights
    print_author_insights(results)
    
    # Create visualizations
    plot_author_activity(results, save_path='plots/author_activity_analysis.png')
    
    # Save detailed results to CSV
    results['activity_summary_df'].to_csv('analysis/author_activity_results.csv', index=False)
    print("\n✅ Detailed results saved to 'analysis/author_activity_results.csv'")