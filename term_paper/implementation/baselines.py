"""
Baseline Methods for Comparison
================================

This module implements baseline ranking methods for comparison with CW-PR:
- Standard PageRank
- HITS (Authority/Hub)
- Degree Centrality
- Relevance Score Only

Author: Aditya Chaudhary, Aayush Deshmukh, Utkarsh Agrawal
"""

import networkx as nx
import numpy as np
from typing import Dict


def standard_pagerank(G: nx.DiGraph, 
                     damping: float = 0.85,
                     max_iter: int = 100,
                     tol: float = 1e-6) -> Dict[str, float]:
    """Standard PageRank without content weighting."""
    return nx.pagerank(G, alpha=damping, max_iter=max_iter, tol=tol)


def hits_scores(G: nx.DiGraph,
                max_iter: int = 100,
                tol: float = 1e-6) -> tuple:
    """HITS algorithm for authority and hub scores."""
    hubs, authorities = nx.hits(G, max_iter=max_iter, tol=tol)
    return authorities, hubs


def degree_centrality(G: nx.DiGraph, direction: str = 'in') -> Dict[str, float]:
    """
    Degree centrality.
    
    Parameters:
    -----------
    G : nx.DiGraph
        The graph
    direction : str
        'in', 'out', or 'total'
    """
    if direction == 'in':
        degrees = dict(G.in_degree())
    elif direction == 'out':
        degrees = dict(G.out_degree())
    else:
        degrees = dict(G.degree())
    
    # Normalize
    max_degree = max(degrees.values()) if degrees else 1
    return {k: v / max_degree for k, v in degrees.items()}


def relevance_only_ranking(posts: list) -> Dict[str, float]:
    """Ranking based purely on relevance scores."""
    scores = {}
    for post in posts:
        post_id = f"{post['platform']}:{post['kind']}:{post['id']}"
        scores[post_id] = post.get('relevance_score', 0.0)
    
    # Normalize
    max_score = max(scores.values()) if scores else 1
    return {k: v / max_score for k, v in scores.items()}
