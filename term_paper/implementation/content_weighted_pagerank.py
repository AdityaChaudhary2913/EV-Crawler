"""
Content-Weighted PageRank Implementation
=========================================

This module implements Content-Weighted PageRank (CW-PR) for the EV dataset.
CW-PR combines structural authority (PageRank) with content relevance scores.

Author: Aditya Chaudhary, Aayush Deshmukh, Utkarsh Agrawal
Course: IKG (Introduction to Knowledge Graphs)
Date: November 2025
"""

import numpy as np
import pandas as pd
import networkx as nx
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kendalltau, spearmanr


class ContentWeightedPageRank:
    """
    Content-Weighted PageRank implementation for heterogeneous social networks.
    
    Combines structural importance (PageRank) with content quality signals
    (relevance scores) to identify authoritative authors and high-quality content.
    """
    
    def __init__(self, 
                 nodes_file: str,
                 edges_file: str,
                 posts_file: str,
                 damping: float = 0.85,
                 max_iter: int = 100,
                 tol: float = 1e-6):
        """
        Initialize CW-PR with data files and parameters.
        
        Parameters:
        -----------
        nodes_file : str
            Path to nodes.csv
        edges_file : str
            Path to edges.csv
        posts_file : str
            Path to posts.jsonl
        damping : float
            Damping factor (default 0.85)
        max_iter : int
            Maximum iterations (default 100)
        tol : float
            Convergence tolerance (default 1e-6)
        """
        self.damping = damping
        self.max_iter = max_iter
        self.tol = tol
        
        # Load data
        print("Loading data...")
        self.nodes_df = pd.read_csv(nodes_file)
        self.edges_df = pd.read_csv(edges_file)
        self.posts = self._load_posts(posts_file)
        
        print(f"Loaded {len(self.nodes_df)} nodes, {len(self.edges_df)} edges")
        
        # Build graph
        self.G = self._build_graph()
        print(f"Built graph with {self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges")
        
        # Extract content weights
        self.content_weights = self._extract_content_weights()
        
        # Define edge type weights
        self.edge_type_weights = {
            'AUTHORED_BY': 1.0,
            'REPLY_TO': 0.8,
            'IN_CONTAINER': 0.5,
            'LINKS_TO_DOMAIN': 0.3,
            'MENTIONS_BRAND': 0.6,
            'MENTIONS_POLICY': 0.6
        }
        
    def _load_posts(self, posts_file: str) -> List[Dict]:
        """Load posts from JSONL file."""
        posts = []
        with open(posts_file, 'r') as f:
            for line in f:
                posts.append(json.loads(line))
        return posts
    
    def _build_graph(self) -> nx.DiGraph:
        """Build NetworkX directed graph from edges."""
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for _, row in self.nodes_df.iterrows():
            node_id = row['node_id']
            node_type = row['node_type']
            G.add_node(node_id, node_type=node_type)
        
        # Add edges with attributes
        for _, row in self.edges_df.iterrows():
            src = row['src_id']
            dst = row['dst_id']
            edge_type = row['edge_type']
            weight = row.get('weight', 1.0)
            
            G.add_edge(src, dst, edge_type=edge_type, weight=weight)
        
        return G
    
    def _extract_content_weights(self) -> Dict[str, float]:
        """Extract and normalize content weights from posts."""
        weights = {}
        
        # Get relevance scores from posts
        for post in self.posts:
            post_id = f"{post['platform']}:{post['kind']}:{post['id']}"
            relevance_score = post.get('relevance_score', 0.0)
            weights[post_id] = max(relevance_score, 0.1)  # Minimum weight 0.1
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights
    
    def compute_pagerank(self, 
                        use_content_weights: bool = True,
                        personalization: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Compute (Content-Weighted) PageRank.
        
        Parameters:
        -----------
        use_content_weights : bool
            Whether to use content weights (default True)
        personalization : dict, optional
            Personalization vector (default None)
            
        Returns:
        --------
        dict : Node -> PageRank score mapping
        """
        N = self.G.number_of_nodes()
        nodes = list(self.G.nodes())
        node_idx = {node: idx for idx, node in enumerate(nodes)}
        
        # Initialize scores
        scores = np.ones(N) / N
        
        # Teleportation vector (content weights or uniform)
        if use_content_weights and personalization is None:
            w = np.array([self.content_weights.get(n, 1.0 / N) for n in nodes])
            w = w / w.sum()  # Normalize
        elif personalization is not None:
            w = np.array([personalization.get(n, 1.0 / N) for n in nodes])
            w = w / w.sum()
        else:
            w = np.ones(N) / N
        
        # Build weighted transition matrix
        M = np.zeros((N, N))
        for u, v, data in self.G.edges(data=True):
            i, j = node_idx[u], node_idx[v]
            edge_type = data.get('edge_type', 'UNKNOWN')
            edge_weight = self.edge_type_weights.get(edge_type, 0.5)
            
            out_degree = self.G.out_degree(u)
            if out_degree > 0:
                M[j, i] = edge_weight / out_degree
        
        # Power iteration
        converged = False
        for iteration in range(self.max_iter):
            scores_new = (1 - self.damping) * w + self.damping * (M @ scores)
            
            # Check convergence
            diff = np.linalg.norm(scores_new - scores, 1)
            if diff < self.tol:
                print(f"Converged in {iteration + 1} iterations (diff={diff:.2e})")
                converged = True
                break
            
            scores = scores_new
        
        if not converged:
            print(f"Warning: Did not converge after {self.max_iter} iterations")
        
        # Return as dictionary
        return {node: scores[node_idx[node]] for node in nodes}
    
    def compute_hits(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Compute HITS authority and hub scores.
        
        Returns:
        --------
        tuple : (authority_scores, hub_scores)
        """
        hubs, authorities = nx.hits(self.G, max_iter=self.max_iter, tol=self.tol)
        return authorities, hubs
    
    def get_top_k(self, scores: Dict[str, float], k: int = 10, 
                  node_type: Optional[str] = None) -> List[Tuple[str, float]]:
        """
        Get top-k nodes by score, optionally filtered by node type.
        
        Parameters:
        -----------
        scores : dict
            Node -> score mapping
        k : int
            Number of top nodes to return
        node_type : str, optional
            Filter by node type (e.g., 'author', 'post')
            
        Returns:
        --------
        list : List of (node_id, score) tuples
        """
        # Filter by node type if specified
        if node_type:
            filtered_scores = {
                node: score for node, score in scores.items()
                if self.G.nodes[node].get('node_type') == node_type
            }
        else:
            filtered_scores = scores
        
        # Sort and return top-k
        sorted_scores = sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:k]
    
    def evaluate_ranking(self, 
                        predicted_scores: Dict[str, float],
                        ground_truth_scores: Dict[str, float],
                        k_values: List[int] = [5, 10, 20]) -> Dict[str, float]:
        """
        Evaluate ranking quality against ground truth.
        
        Parameters:
        -----------
        predicted_scores : dict
            Predicted node scores
        ground_truth_scores : dict
            Ground truth scores
        k_values : list
            List of k values for Precision@k, nDCG@k
            
        Returns:
        --------
        dict : Evaluation metrics
        """
        # Get common nodes
        common_nodes = set(predicted_scores.keys()) & set(ground_truth_scores.keys())
        
        # Rank correlation
        pred_vals = [predicted_scores[n] for n in common_nodes]
        gt_vals = [ground_truth_scores[n] for n in common_nodes]
        
        kendall_tau, _ = kendalltau(pred_vals, gt_vals)
        spearman_rho, _ = spearmanr(pred_vals, gt_vals)
        
        metrics = {
            'kendall_tau': kendall_tau,
            'spearman_rho': spearman_rho
        }
        
        # Precision@k and nDCG@k
        for k in k_values:
            # Get top-k predictions and ground truth
            pred_top_k = set([node for node, _ in 
                             sorted(predicted_scores.items(), key=lambda x: x[1], reverse=True)[:k]])
            gt_top_k = set([node for node, _ in 
                           sorted(ground_truth_scores.items(), key=lambda x: x[1], reverse=True)[:k]])
            
            # Precision@k
            precision_k = len(pred_top_k & gt_top_k) / k
            metrics[f'precision@{k}'] = precision_k
            
            # nDCG@k (simplified version)
            dcg = 0
            for i, (node, _) in enumerate(sorted(predicted_scores.items(), 
                                                 key=lambda x: x[1], reverse=True)[:k]):
                if node in ground_truth_scores:
                    dcg += ground_truth_scores[node] / np.log2(i + 2)
            
            idcg = 0
            for i, (node, score) in enumerate(sorted(ground_truth_scores.items(), 
                                                     key=lambda x: x[1], reverse=True)[:k]):
                idcg += score / np.log2(i + 2)
            
            ndcg_k = dcg / idcg if idcg > 0 else 0
            metrics[f'ndcg@{k}'] = ndcg_k
        
        return metrics
    
    def plot_convergence(self, history: List[float], output_file: str):
        """Plot convergence history."""
        plt.figure(figsize=(10, 6))
        plt.plot(history, marker='o')
        plt.xlabel('Iteration')
        plt.ylabel('L1 Norm Difference')
        plt.title('PageRank Convergence')
        plt.yscale('log')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"Convergence plot saved to {output_file}")
    
    def plot_score_distribution(self, 
                                scores: Dict[str, float],
                                title: str,
                                output_file: str):
        """Plot score distribution."""
        values = list(scores.values())
        
        plt.figure(figsize=(10, 6))
        plt.hist(values, bins=50, alpha=0.7, edgecolor='black')
        plt.xlabel('Score')
        plt.ylabel('Frequency')
        plt.title(title)
        plt.yscale('log')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300)
        plt.close()
        print(f"Score distribution plot saved to {output_file}")
    
    def compare_methods(self, 
                       node_type: str = 'author',
                       k: int = 10) -> pd.DataFrame:
        """
        Compare different ranking methods.
        
        Parameters:
        -----------
        node_type : str
            Node type to analyze
        k : int
            Number of top nodes
            
        Returns:
        --------
        DataFrame : Comparison results
        """
        print(f"\nComparing ranking methods for top-{k} {node_type}s...")
        
        # Compute different rankings
        print("1. Computing Content-Weighted PageRank...")
        cwpr_scores = self.compute_pagerank(use_content_weights=True)
        
        print("2. Computing Standard PageRank...")
        std_pr_scores = self.compute_pagerank(use_content_weights=False)
        
        print("3. Computing HITS...")
        auth_scores, hub_scores = self.compute_hits()
        
        print("4. Computing Degree Centrality...")
        degree_scores = dict(self.G.in_degree())
        
        # Get top-k for each method
        cwpr_top = self.get_top_k(cwpr_scores, k, node_type)
        std_pr_top = self.get_top_k(std_pr_scores, k, node_type)
        auth_top = self.get_top_k(auth_scores, k, node_type)
        degree_top = self.get_top_k(degree_scores, k, node_type)
        
        # Create comparison dataframe
        comparison_data = []
        for rank in range(k):
            comparison_data.append({
                'Rank': rank + 1,
                'CW-PR': cwpr_top[rank][0] if rank < len(cwpr_top) else 'N/A',
                'CW-PR Score': f"{cwpr_top[rank][1]:.6f}" if rank < len(cwpr_top) else 'N/A',
                'Std PR': std_pr_top[rank][0] if rank < len(std_pr_top) else 'N/A',
                'HITS Auth': auth_top[rank][0] if rank < len(auth_top) else 'N/A',
                'Degree': degree_top[rank][0] if rank < len(degree_top) else 'N/A'
            })
        
        df = pd.DataFrame(comparison_data)
        return df
    
    def evaluate_ranking_quality(self, k_values=[10, 20]) -> pd.DataFrame:
        """
        Compute evaluation metrics (Precision@k, nDCG@k) for all methods.
        Uses relevance scores from posts as ground truth.
        
        Parameters:
        -----------
        k_values : list
            List of k values to evaluate
            
        Returns:
        --------
        pd.DataFrame : Evaluation results
        """
        print("\n" + "="*60)
        print("Computing Evaluation Metrics")
        print("="*60)
        
        # Build ground truth from relevance scores
        # Map authors to their average relevance scores
        author_relevance = {}
        author_post_counts = {}
        
        for post_data in self.posts:
            author = post_data.get('author_name', '') or post_data.get('author', '')
            if not author:
                continue
            
            platform = post_data.get('platform', 'reddit')
            author_node = f"{platform}:author:{author}"
            relevance = post_data.get('relevance_score', 0.0)
            
            if author_node not in author_relevance:
                author_relevance[author_node] = 0
                author_post_counts[author_node] = 0
            
            author_relevance[author_node] += relevance
            author_post_counts[author_node] += 1
        
        # Calculate average relevance per author
        for author in author_relevance:
            if author_post_counts[author] > 0:
                author_relevance[author] /= author_post_counts[author]
        
        # Get all author nodes from the graph
        authors = [n for n in self.G.nodes() if self.G.nodes[n].get('node_type') == 'author']
        
        # Ensure all authors have a relevance score (0 if not in posts)
        for author in authors:
            if author not in author_relevance:
                author_relevance[author] = 0
        
        print(f"Ground truth: {len(author_relevance)} authors with relevance scores")
        print(f"Authors with relevance > 0: {sum(1 for v in author_relevance.values() if v > 0)}")
        
        # Define top-k relevant authors based on relevance scores
        # These are our "ground truth" relevant authors
        sorted_by_relevance = sorted(author_relevance.items(), key=lambda x: x[1], reverse=True)
        
        # Compute rankings for all methods
        methods = {
            'Degree Centrality': dict(self.G.in_degree()),
            'Relevance Score Only': author_relevance,
            'Standard PageRank': self.compute_pagerank(use_content_weights=False),
            'HITS (Authority)': self.compute_hits()[0],
            'CW-PR (Ours)': self.compute_pagerank(use_content_weights=True)
        }
        
        results = []
        
        for method_name, scores in methods.items():
            print(f"\nEvaluating: {method_name}")
            
            # Filter to authors only and sort by score
            author_scores = {n: scores.get(n, 0) for n in authors}
            ranked_authors = sorted(author_scores.items(), key=lambda x: x[1], reverse=True)
            
            for k in k_values:
                # Get top-k from this method
                top_k_authors = [author for author, _ in ranked_authors[:k]]
                
                # Get top-k from ground truth (relevant authors)
                relevant_k_authors = {author for author, _ in sorted_by_relevance[:k]}
                
                # Compute Precision@k
                # How many of the top-k are actually in the relevant set?
                precision_k = len(set(top_k_authors) & relevant_k_authors) / k
                
                # Compute nDCG@k
                # DCG = sum of (relevance / log2(rank+1)) for ranked items
                dcg = 0
                for rank, author in enumerate(top_k_authors, start=1):
                    relevance = author_relevance.get(author, 0)
                    dcg += relevance / np.log2(rank + 1)
                
                # Ideal DCG: best possible ranking by relevance
                ideal_ranking = [author for author, _ in sorted_by_relevance[:k]]
                idcg = 0
                for rank, author in enumerate(ideal_ranking, start=1):
                    relevance = author_relevance.get(author, 0)
                    idcg += relevance / np.log2(rank + 1)
                
                # nDCG
                ndcg_k = dcg / idcg if idcg > 0 else 0
                
                results.append({
                    'Method': method_name,
                    'k': k,
                    'Precision': precision_k,
                    'nDCG': ndcg_k
                })
                
                print(f"  P@{k}: {precision_k:.3f}, nDCG@{k}: {ndcg_k:.3f}")
        
        # Create results dataframe
        results_df = pd.DataFrame(results)
        
        # Pivot to get the format needed for the paper
        pivot_df = results_df.pivot(index='Method', columns='k')
        
        # Flatten column names
        pivot_df.columns = [f'{metric}@{k}' for metric, k in pivot_df.columns]
        pivot_df = pivot_df.reset_index()
        
        # Reorder columns
        col_order = ['Method']
        for k in k_values:
            col_order.extend([f'Precision@{k}', f'nDCG@{k}'])
        pivot_df = pivot_df[col_order]
        
        # Rename columns for paper
        rename_map = {}
        for k in k_values:
            rename_map[f'Precision@{k}'] = f'P@{k}'
            rename_map[f'nDCG@{k}'] = f'nDCG@{k}'
        pivot_df = pivot_df.rename(columns=rename_map)
        
        return pivot_df


def main():
    """Main execution function."""
    # Set paths
    crawler_root = Path(__file__).parent.parent.parent  # Go up 3 levels
    data_dir = crawler_root / "data" / "processed"
    figures_dir = Path(__file__).parent.parent / "figures"  # term_paper/figures
    
    nodes_file = data_dir / 'nodes.csv'
    edges_file = data_dir / 'edges.csv'
    posts_file = data_dir / 'posts.jsonl'
    
    # Check if files exist
    if not all([nodes_file.exists(), edges_file.exists(), posts_file.exists()]):
        print("Error: Data files not found!")
        print(f"Looking in: {data_dir}")
        return
    
    # Initialize CW-PR
    print("="*60)
    print("Content-Weighted PageRank Implementation")
    print("="*60)
    
    cwpr = ContentWeightedPageRank(
        nodes_file=str(nodes_file),
        edges_file=str(edges_file),
        posts_file=str(posts_file),
        damping=0.85,
        max_iter=100,
        tol=1e-6
    )
    
    # Compute CW-PR scores
    print("\n" + "="*60)
    print("Computing Content-Weighted PageRank...")
    print("="*60)
    cwpr_scores = cwpr.compute_pagerank(use_content_weights=True)
    
    # Get top-10 authors
    print("\n" + "="*60)
    print("Top-10 Authors by Content-Weighted PageRank")
    print("="*60)
    top_authors = cwpr.get_top_k(cwpr_scores, k=10, node_type='author')
    
    for rank, (author, score) in enumerate(top_authors, 1):
        print(f"{rank:2d}. {author:30s} - Score: {score:.6f}")
    
    # Compare methods
    print("\n" + "="*60)
    print("Method Comparison")
    print("="*60)
    comparison_df = cwpr.compare_methods(node_type='author', k=10)
    print(comparison_df.to_string(index=False))
    
    # Save results
    output_dir = Path(__file__).parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    comparison_df.to_csv(output_dir / 'method_comparison.csv', index=False)
    print(f"\nResults saved to {output_dir}/method_comparison.csv")
    
    # Evaluate ranking quality with real metrics
    evaluation_df = cwpr.evaluate_ranking_quality(k_values=[10, 20])
    
    print("\n" + "="*60)
    print("Ranking Performance Evaluation")
    print("="*60)
    print(evaluation_df.to_string(index=False))
    
    # Save evaluation metrics
    evaluation_df.to_csv(output_dir / 'evaluation_metrics.csv', index=False)
    print(f"\nEvaluation metrics saved to {output_dir}/evaluation_metrics.csv")
    
    # Print LaTeX table format (manual formatting to avoid jinja2 dependency)
    print("\n" + "="*60)
    print("LaTeX Table Format (for paper)")
    print("="*60)
    print("\\begin{tabular}{lcccc}")
    print("\\toprule")
    print("Method & P@10 & P@20 & nDCG@10 & nDCG@20 \\\\")
    print("\\midrule")
    for _, row in evaluation_df.iterrows():
        print(f"{row['Method']} & {row['P@10']:.2f} & {row['P@20']:.2f} & {row['nDCG@10']:.2f} & {row['nDCG@20']:.2f} \\\\")
    print("\\bottomrule")
    print("\\end{tabular}")
    
    # Plot score distribution
    figures_dir.mkdir(parents=True, exist_ok=True)
    cwpr.plot_score_distribution(
        cwpr_scores,
        'Content-Weighted PageRank Score Distribution',
        str(figures_dir / 'score_distribution.pdf')
    )
    
    print("\n" + "="*60)
    print("Analysis Complete!")
    print("="*60)


if __name__ == '__main__':
    main()
