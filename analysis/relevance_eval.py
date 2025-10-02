"""Relevance evaluation: prepare labels and score labeled data."""
from __future__ import annotations

import argparse
import os
from typing import List

import numpy as np
import pandas as pd


def prepare_labels(out_dir: str, sample_size: int = 400) -> None:
    posts_path = os.path.join(out_dir, "posts.jsonl")
    labels_dir = os.path.join(out_dir, "labels")
    os.makedirs(labels_dir, exist_ok=True)
    if not os.path.exists(posts_path):
        print("posts.jsonl not found; run crawler first.")
        return
    df = pd.read_json(posts_path, lines=True)
    if df.empty:
        print("No records to label.")
        return
    df = df.sort_values("relevance_score", ascending=False).reset_index(drop=True)
    # Quantile-based sampling
    idxs = np.linspace(0, len(df) - 1, num=min(sample_size, len(df)), dtype=int)
    sub = df.iloc[idxs][["id", "platform", "kind", "created_iso", "url", "text", "relevance_score"]]
    sub["label"] = ""
    sub.to_csv(os.path.join(labels_dir, "labels.csv"), index=False)
    print(f"Wrote labeling CSV with {len(sub)} rows to {os.path.join(labels_dir, 'labels.csv')}")


def dcg(scores: List[int]) -> float:
    return sum((s / np.log2(i + 2)) for i, s in enumerate(scores))


def analyze_relevance_distribution(out_dir: str) -> None:
    """Analyze actual relevance score distribution from posts.jsonl"""
    posts_path = os.path.join(out_dir, "posts.jsonl")
    tables_dir = os.path.join(out_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)
    
    if not os.path.exists(posts_path):
        print("posts.jsonl not found; run crawler first.")
        return
        
    df = pd.read_json(posts_path, lines=True)
    if df.empty:
        print("No records found for relevance analysis.")
        return

    # Analyze relevance score distribution
    scores = df["relevance_score"]
    
    # Count items by relevance level
    zero_score = (scores == 0.0).sum()
    positive_score = (scores > 0.0).sum()
    high_score = (scores >= 3.0).sum()
    very_high_score = (scores >= 5.0).sum()
    
    # Basic statistics
    mean_score = scores.mean()
    median_score = scores.median()
    max_score = scores.max()
    std_score = scores.std()
    
    # Calculate meaningful thresholds based on actual data
    relevant_threshold = 1.0  # Items with score > 1.0 considered relevant
    relevant_items = (scores > relevant_threshold).sum()
    relevance_rate = relevant_items / len(scores) if len(scores) > 0 else 0.0
    
    out = pd.DataFrame([{
        "total_items": len(scores),
        "zero_score_items": zero_score,
        "positive_score_items": positive_score,
        "high_score_items": high_score,
        "very_high_score_items": very_high_score,
        "relevance_rate": relevance_rate,
        "mean_score": mean_score,
        "median_score": median_score,
        "max_score": max_score,
        "std_score": std_score,
        "relevant_threshold": relevant_threshold,
    }])
    
    out.to_csv(os.path.join(tables_dir, "relevance_analysis.csv"), index=False)
    print(f"Wrote relevance analysis to {os.path.join(tables_dir, 'relevance_analysis.csv')}")
    print(f"Summary: {len(scores)} items, {positive_score} positive scores ({positive_score/len(scores):.1%}), max score: {max_score:.2f}")


def score_labels(out_dir: str, k: int) -> None:
    labels_path = os.path.join(out_dir, "labels", "labels.csv")
    tables_dir = os.path.join(out_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)
    if not os.path.exists(labels_path):
        print("labels.csv not found; run with --prepare_labels first.")
        print("Running automatic relevance analysis instead...")
        analyze_relevance_distribution(out_dir)
        return
    df = pd.read_csv(labels_path)
    if "label" not in df.columns:
        print("No label column present.")
        return
    df = df.sort_values("relevance_score", ascending=False)
    df_k = df.head(k)
    labels = [1 if str(x).strip() in {"1", "true", "True"} else 0 for x in df_k["label"].tolist()]
    precision_at_k = sum(labels) / max(1, len(labels))
    ndcg_at_k = 0.0
    if labels:
        ideal = sorted(labels, reverse=True)
        ndcg_at_k = dcg(labels) / max(dcg(ideal), 1e-9)

    # harvest rate: fraction of labeled that are positive
    all_labels = [1 if str(x).strip() in {"1", "true", "True"} else 0 for x in df["label"].tolist()]
    harvest = (sum(all_labels) / max(1, len(all_labels))) if all_labels else 0.0

    out = pd.DataFrame(
        [
            {
                "k": k,
                "precision@k": precision_at_k,
                "nDCG@k": ndcg_at_k,
                "harvest_rate": harvest,
            }
        ]
    )
    out.to_csv(os.path.join(tables_dir, "relevance_metrics.csv"), index=False)
    print(f"Wrote relevance metrics to {os.path.join(tables_dir, 'relevance_metrics.csv')}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prepare_labels", action="store_true")
    p.add_argument("--score_labels", action="store_true")
    p.add_argument("--analyze_distribution", action="store_true", help="Analyze relevance score distribution")
    p.add_argument("--k", type=int, default=100)
    args = p.parse_args()
    out_dir = "data/processed"
    
    if args.prepare_labels:
        prepare_labels(out_dir)
    if args.score_labels:
        score_labels(out_dir, args.k)
    if args.analyze_distribution:
        analyze_relevance_distribution(out_dir)
    
    # If no specific arguments, run distribution analysis by default
    if not any([args.prepare_labels, args.score_labels, args.analyze_distribution]):
        print("No specific analysis requested, running relevance distribution analysis...")
        analyze_relevance_distribution(out_dir)


if __name__ == "__main__":
    main()
