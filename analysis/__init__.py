"""EV Discussion Analysis Pipeline

A comprehensive analysis framework for Electric Vehicle discussion data from Reddit.
Provides insights into author behavior, brand mentions, and network structure.

Modules:
    - author_activity: User engagement and contribution patterns
    - brand_topic_analysis: Brand mentions and topical analysis  
    - network_analysis: Graph structure and interaction patterns
    - run_complete_analysis: Main pipeline runner

Usage:
    from analysis import run_complete_analysis
    results = run_complete_analysis()

Author: Aditya Chaudhary
Date: October 2025
"""

__version__ = "1.0.0"
__author__ = "Aditya Chaudhary"
__email__ = "adityachaudhary1306@gmail.com"

# Import main analysis functions for easy access
try:
    from .author_activity import analyze_author_activity, plot_author_activity, print_author_insights
    from .brand_topic_analysis import analyze_brand_mentions, plot_brand_topic_analysis, print_brand_topic_insights
    from .network_analysis import (
        create_discussion_network, 
        analyze_network_structure, 
        analyze_discussion_patterns, 
        plot_network_analysis, 
        print_network_insights
    )
    from .run_complete_analysis import run_complete_analysis
except ImportError:
    # Allow imports to fail gracefully if dependencies are not installed
    pass

__all__ = [
    'analyze_author_activity',
    'plot_author_activity', 
    'print_author_insights',
    'analyze_brand_mentions',
    'plot_brand_topic_analysis',
    'print_brand_topic_insights',
    'create_discussion_network',
    'analyze_network_structure',
    'analyze_discussion_patterns',
    'plot_network_analysis',
    'print_network_insights',
    'run_complete_analysis'
]