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


def score_labels(out_dir: str, k: int) -> None:
    labels_path = os.path.join(out_dir, "labels", "labels.csv")
    tables_dir = os.path.join(out_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)
    if not os.path.exists(labels_path):
        print("labels.csv not found; run with --prepare_labels first.")
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
    p.add_argument("--k", type=int, default=100)
    args = p.parse_args()
    out_dir = "data/processed"
    if args.prepare_labels:
        prepare_labels(out_dir)
    if args.score_labels:
        score_labels(out_dir, args.k)


if __name__ == "__main__":
    main()
