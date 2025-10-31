"""Complete analysis runner for EV discussion dataset.

This script runs all analysis modules and generates a comprehensive report.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from datetime import datetime

# Add analysis directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import analysis modules
from author_activity import analyze_author_activity, plot_author_activity, print_author_insights
from brand_topic_analysis import analyze_brand_mentions, plot_brand_topic_analysis, print_brand_topic_insights
from network_analysis import create_discussion_network, analyze_network_structure, analyze_discussion_patterns, plot_network_analysis, print_network_insights

warnings.filterwarnings('ignore')

def create_output_directories():
    """Create necessary output directories."""
    directories = ['analysis/results', 'analysis/plots']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def run_complete_analysis(
    nodes_file="/Users/adityachaudhary/Desktop/SEMESTER_7/IKG/Crawler/data/processed/nodes.csv",
    edges_file="/Users/adityachaudhary/Desktop/SEMESTER_7/IKG/Crawler/data/processed/edges.csv",
    output_dir="analysis",
):
    """
    Run complete analysis pipeline for EV discussion data.
    
    Args:
        nodes_file: Path to nodes CSV file
        edges_file: Path to edges CSV file
        output_dir: Directory to save results
    """
    
    print("\n" + "=" * 80)
    print("🚗 ELECTRIC VEHICLE DISCUSSION ANALYSIS - COMPLETE PIPELINE")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if data files exist
    if not os.path.exists(nodes_file) or not os.path.exists(edges_file):
        print(f"\u274c Error: Data files not found!")
        print(f"  Expected: {nodes_file}")
        print(f"  Expected: {edges_file}")
        print(f"  Current directory: {os.getcwd()}")
        return
    
    # Create output directories
    create_output_directories()
    
    # Data overview
    print(f"\n📊 DATA OVERVIEW:")
    nodes_df = pd.read_csv(nodes_file)
    edges_df = pd.read_csv(edges_file)
    print(f"  • Nodes: {len(nodes_df):,} ({nodes_df['node_type'].value_counts().to_dict()})")
    print(f"  • Edges: {len(edges_df):,} ({edges_df['edge_type'].value_counts().to_dict()})")
    
    results = {}
    
    try:
        # 1. Author Activity Analysis
        print(f"\n\n👥 RUNNING AUTHOR ACTIVITY ANALYSIS...")
        print("-" * 50)
        
        author_results = analyze_author_activity(nodes_file, edges_file)
        results['author_activity'] = author_results
        
        # Print insights
        print_author_insights(author_results)
        
        # Create visualizations
        plt.style.use('default')  # Reset style
        plot_author_activity(author_results, 
                            save_path=f'{output_dir}/plots/author_activity_analysis.png')
        
        # Save detailed results
        author_results['activity_summary_df'].to_csv(
            f'{output_dir}/results/author_activity_results.csv', index=False)
        
        print("✅ Author activity analysis completed!")
        
    except Exception as e:
        print(f"❌ Error in author activity analysis: {e}")
        results['author_activity'] = {'error': str(e)}
    
    try:
        # 2. Brand and Topic Analysis
        print(f"\n\n🏷️ RUNNING BRAND & TOPIC ANALYSIS...")
        print("-" * 50)
        
        brand_results = analyze_brand_mentions(nodes_file, edges_file)
        results['brand_topic'] = brand_results
        
        # Print insights
        print_brand_topic_insights(brand_results)
        
        # Create visualizations
        plt.style.use('default')  # Reset style
        plot_brand_topic_analysis(brand_results, 
                                 save_path=f'{output_dir}/plots/brand_topic_analysis.png')
        
        # Save results
        import json
        with open(f'{output_dir}/results/brand_topic_results.json', 'w') as f:
            serializable_results = json.loads(json.dumps(brand_results, default=str))
            json.dump(serializable_results, f, indent=2)
        
        print("✅ Brand and topic analysis completed!")
        
    except Exception as e:
        print(f"❌ Error in brand/topic analysis: {e}")
        results['brand_topic'] = {'error': str(e)}
    
    try:
        # 3. Network Structure Analysis
        print(f"\n\n🕸️ RUNNING NETWORK ANALYSIS...")
        print("-" * 50)
        
        # Create network
        graph = create_discussion_network(nodes_file, edges_file)
        
        # Analyze network structure
        network_results = analyze_network_structure(graph)
        
        # Analyze discussion patterns
        discussion_results = analyze_discussion_patterns(graph, nodes_df, edges_df)
        
        results['network'] = {
            'structure': network_results,
            'discussion_patterns': discussion_results
        }
        
        # Print insights
        print_network_insights(network_results, discussion_results)
        
        # Create visualizations
        plt.style.use('default')  # Reset style
        plot_network_analysis(network_results, discussion_results,
                             save_path=f'{output_dir}/plots/network_analysis.png')
        
        # Save results
        combined_network_results = {
            'network_structure': network_results,
            'discussion_patterns': discussion_results
        }
        
        with open(f'{output_dir}/results/network_analysis_results.json', 'w') as f:
            serializable_results = json.loads(json.dumps(combined_network_results, default=str))
            json.dump(serializable_results, f, indent=2)
        
        print("✅ Network analysis completed!")
        
    except Exception as e:
        print(f"❌ Error in network analysis: {e}")
        results['network'] = {'error': str(e)}
    
    # Generate summary report
    print(f"\n\n📄 GENERATING SUMMARY REPORT...")
    print("-" * 50)
    
    try:
        generate_summary_report(results, output_file=f'{output_dir}/results/complete_analysis_summary.txt')
        print("✅ Summary report generated!")
    except Exception as e:
        print(f"❌ Error generating summary report: {e}")
    
    # Final summary
    print(f"\n\n" + "=" * 80)
    print("🎆 ANALYSIS PIPELINE COMPLETED!")
    print("=" * 80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📁 Results saved to: {output_dir}/results/")
    print(f"🖼️ Plots saved to: {output_dir}/plots/")
    
    print("\n📈 Generated files:")
    result_files = [
        f"{output_dir}/results/author_activity_results.csv",
        f"{output_dir}/results/brand_topic_results.json",
        f"{output_dir}/results/network_analysis_results.json",
        f"{output_dir}/results/complete_analysis_summary.txt",
        f"{output_dir}/plots/author_activity_analysis.png",
        f"{output_dir}/plots/brand_topic_analysis.png",
        f"{output_dir}/plots/network_analysis.png"
    ]
    
    for file_path in result_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (not created)")
    
    return results

def generate_summary_report(results: dict, output_file: str = None):
    """
    Generate a comprehensive summary report of all analyses.
    
    Args:
        results: Combined results from all analyses
        output_file: Path to save the report
    """
    
    report_lines = []
    
    # Header
    report_lines.extend([
        "=" * 80,
        "🚗 ELECTRIC VEHICLE DISCUSSION ANALYSIS - COMPREHENSIVE REPORT",
        "=" * 80,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ])
    
    # Executive Summary
    report_lines.extend([
        "📋 EXECUTIVE SUMMARY",
        "-" * 30,
    ])
    
    # Author Activity Summary
    if 'author_activity' in results and 'error' not in results['author_activity']:
        author_data = results['author_activity']
        report_lines.extend([
            f"\n👥 AUTHOR ACTIVITY:",
            f"  • Total Authors: {author_data['total_authors']:,}",
            f"  • Active Authors: {author_data['active_authors']:,}",
            f"  • Participation Rate: {author_data['active_authors']/author_data['total_authors']*100:.1f}%",
        ])
        
        if author_data['top_authors']:
            top_author = author_data['top_authors'][0]
            author_name = top_author['author_id'].split(':')[-1]
            report_lines.append(
                f"  • Most Active Author: {author_name} ({top_author['total_authored']} contributions)"
            )
    
    # Brand Analysis Summary
    if 'brand_topic' in results and 'error' not in results['brand_topic']:
        brand_data = results['brand_topic']
        data_summary = brand_data.get('data_summary', {})
        report_lines.extend([
            f"\n🏷️ BRAND & TOPIC ANALYSIS:",
            f"  • Total Posts: {data_summary.get('total_posts', 0):,}",
            f"  • Posts with Brand Mentions: {data_summary.get('posts_with_brand_mentions', 0):,}",
            f"  • Brand Mention Rate: {data_summary.get('brand_mention_rate', 0):.1f}%",
        ])
        
        domain_data = brand_data.get('domain_analysis', {})
        if domain_data:
            report_lines.append(
                f"  • Unique Domains Linked: {domain_data.get('unique_domains', 0):,}"
            )
    
    # Network Analysis Summary
    if 'network' in results and 'error' not in results['network']:
        network_data = results['network']
        if 'structure' in network_data:
            basic_stats = network_data['structure'].get('basic_stats', {})
            components = network_data['structure'].get('components', {})
            
            report_lines.extend([
                f"\n🕸️ NETWORK STRUCTURE:",
                f"  • Total Nodes: {basic_stats.get('num_nodes', 0):,}",
                f"  • Total Edges: {basic_stats.get('num_edges', 0):,}",
                f"  • Network Density: {basic_stats.get('density', 0):.6f}",
                f"  • Connected Components: {components.get('num_components', 0):,}",
                f"  • Largest Component: {components.get('largest_component_size', 0):,} nodes",
            ])
        
        if 'discussion_patterns' in network_data:
            engage_data = network_data['discussion_patterns'].get('engagement_patterns', {})
            thread_data = network_data['discussion_patterns'].get('thread_analysis', {})
            
            report_lines.extend([
                f"\n💬 DISCUSSION PATTERNS:",
                f"  • Participation Rate: {engage_data.get('participation_rate', 0):.1f}%",
                f"  • Average Thread Depth: {thread_data.get('avg_thread_depth', 0):.1f}",
                f"  • Total Reply Chains: {thread_data.get('total_reply_chains', 0):,}",
            ])
    
    # Key Insights
    report_lines.extend([
        "",
        "💡 KEY INSIGHTS",
        "-" * 30,
    ])
    
    # Generate insights based on available data
    insights = []
    
    if 'author_activity' in results and 'error' not in results['author_activity']:
        author_data = results['author_activity']
        participation_rate = author_data['active_authors']/author_data['total_authors']*100
        
        if participation_rate < 50:
            insights.append(f"1. Low participation rate ({participation_rate:.1f}%) indicates many lurkers")
        else:
            insights.append(f"1. High participation rate ({participation_rate:.1f}%) shows active community")
    
    if 'brand_topic' in results and 'error' not in results['brand_topic']:
        brand_data = results['brand_topic']
        mention_rate = brand_data.get('data_summary', {}).get('brand_mention_rate', 0)
        
        if mention_rate > 20:
            insights.append(f"2. High brand mention rate ({mention_rate:.1f}%) suggests commercial interest")
        else:
            insights.append(f"2. Moderate brand mentions ({mention_rate:.1f}%) indicate balanced discussion")
    
    if 'network' in results and 'error' not in results['network']:
        network_data = results['network']
        if 'structure' in network_data:
            density = network_data['structure'].get('basic_stats', {}).get('density', 0)
            
            if density < 0.001:
                insights.append("3. Low network density indicates specialized discussion clusters")
            else:
                insights.append("3. Higher network density suggests interconnected community")
    
    # Add insights to report
    for insight in insights:
        report_lines.append(f"  • {insight}")
    
    # Errors section
    errors = []
    for analysis_type, data in results.items():
        if isinstance(data, dict) and 'error' in data:
            errors.append(f"  • {analysis_type.replace('_', ' ').title()}: {data['error']}")
    
    if errors:
        report_lines.extend([
            "",
            "⚠️ ANALYSIS ERRORS",
            "-" * 30,
        ])
        report_lines.extend(errors)
    
    # Footer
    report_lines.extend([
        "",
        "=" * 80,
        "Report generated by EV Discussion Analysis Pipeline",
        "=" * 80,
    ])
    
    # Join all lines
    report_text = "\n".join(report_lines)
    
    # Print to console
    print(report_text)
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"\n✅ Summary report saved to: {output_file}")

if __name__ == "__main__":
    # Run complete analysis pipeline
    results = run_complete_analysis()
    
    if results:
        print(f"\n\n🎉 Analysis pipeline completed successfully!")
        print(f"Check the 'analysis/results/' and 'analysis/plots/' directories for outputs.")
    else:
        print(f"\n\n❌ Analysis pipeline encountered errors.")