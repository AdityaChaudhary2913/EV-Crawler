"""Persistence: JSONL/CSV writers and crawl metrics."""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import Any, TextIO

from .utils import json_dumps


@dataclass
class Writers:
    posts_path: str
    nodes_path: str
    edges_path: str
    metrics_path: str

    posts_fh: TextIO
    nodes_fh: TextIO
    edges_fh: TextIO
    metrics_fh: TextIO
    nodes_writer: Any
    edges_writer: Any
    metrics_writer: Any


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def open_writers(out_dir: str) -> Writers:
    ensure_dir(out_dir)
    tables_dir = os.path.join(out_dir, "tables")
    figs_dir = os.path.join(out_dir, "figs")
    labels_dir = os.path.join(out_dir, "labels")
    ensure_dir(tables_dir)
    ensure_dir(figs_dir)
    ensure_dir(labels_dir)

    posts_path = os.path.join(out_dir, "posts.jsonl")
    nodes_path = os.path.join(out_dir, "nodes.csv")
    edges_path = os.path.join(out_dir, "edges.csv")
    metrics_path = os.path.join(out_dir, "metrics.csv")

    posts_fh = open(posts_path, "a", encoding="utf-8")
    nodes_fh = open(nodes_path, "w", newline="", encoding="utf-8")
    edges_fh = open(edges_path, "w", newline="", encoding="utf-8")
    metrics_fh = open(metrics_path, "a", newline="", encoding="utf-8")

    nodes_writer = csv.writer(nodes_fh)
    edges_writer = csv.writer(edges_fh)
    metrics_writer = csv.writer(metrics_fh)

    # Write headers if files are new (size 0)
    if os.path.getsize(nodes_path) == 0:
        nodes_writer.writerow(["node_id", "node_type", "attrs_json"])
    if os.path.getsize(edges_path) == 0:
        edges_writer.writerow(["src_id", "dst_id", "edge_type", "weight", "attrs_json"])
    if os.path.getsize(metrics_path) == 0:
        metrics_writer.writerow(
            [
                "ts_iso",
                "items_fetched",
                "items_written",
                "elapsed_sec",
                "success_calls",
                "error_calls",
                "dedup_skipped",
            ]
        )

    return Writers(
        posts_path,
        nodes_path,
        edges_path,
        metrics_path,
        posts_fh,
        nodes_fh,
        edges_fh,
        metrics_fh,
        nodes_writer,
        edges_writer,
        metrics_writer,
    )


def close_writers(w: Writers) -> None:
    w.posts_fh.close()
    w.nodes_fh.close()
    w.edges_fh.close()
    w.metrics_fh.close()


def write_post_jsonl(w: Writers, record: dict) -> None:
    line = json_dumps(record)
    w.posts_fh.write(line + "\n")


def write_node(w: Writers, node_id: str, node_type: str, attrs: dict | None = None) -> None:
    w.nodes_writer.writerow([node_id, node_type, json_dumps(attrs or {})])


def write_edge(
    w: Writers, src_id: str, dst_id: str, edge_type: str, weight: float = 1.0, attrs: dict | None = None
) -> None:
    w.edges_writer.writerow([src_id, dst_id, edge_type, weight, json_dumps(attrs or {})])


def write_metrics(
    w: Writers,
    ts_iso: str,
    items_fetched: int,
    items_written: int,
    elapsed_sec: float,
    success_calls: int,
    error_calls: int,
    dedup_skipped: int,
) -> None:
    w.metrics_writer.writerow(
        [ts_iso, items_fetched, items_written, round(elapsed_sec, 3), success_calls, error_calls, dedup_skipped]
    )
