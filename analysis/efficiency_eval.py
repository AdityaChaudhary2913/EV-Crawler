"""Efficiency evaluation from metrics.csv.

Computes:
- throughput_items_per_sec (items_written / elapsed_sec)
- success_rate (success_calls / (success_calls + error_calls))
- dedup_rate (dedup_skipped / (items_written + dedup_skipped))
- items_per_api_call (items_written / success_calls)
- api_efficiency (success_calls / (success_calls + error_calls))
"""
from __future__ import annotations

import os
import pandas as pd


def main():
    out_dir = "data/processed"
    metrics_path = os.path.join(out_dir, "metrics.csv")
    tables_dir = os.path.join(out_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)
    
    if not os.path.exists(metrics_path):
        print("metrics.csv not found.")
        return
        
    df = pd.read_csv(metrics_path)
    if df.empty:
        print("metrics.csv is empty.")
        return
        
    # Sum all metrics across all crawl sessions for cumulative totals
    total_elapsed = df["elapsed_sec"].sum()
    total_items_written = df["items_written"].sum()
    total_items_fetched = df["items_fetched"].sum()
    total_success_calls = df["success_calls"].sum()
    total_error_calls = df["error_calls"].sum()
    total_dedup_skipped = df["dedup_skipped"].sum()

    # Calculate metrics
    throughput = total_items_written / total_elapsed if total_elapsed > 0 else 0.0
    
    total_calls = total_success_calls + total_error_calls
    success_rate = total_success_calls / total_calls if total_calls > 0 else 0.0
    
    dedup_rate = total_dedup_skipped / (total_items_written + total_dedup_skipped) if (total_items_written + total_dedup_skipped) > 0 else 0.0
    
    # Additional useful metrics
    items_per_api_call = total_items_written / total_success_calls if total_success_calls > 0 else 0.0
    fetch_to_write_ratio = total_items_written / total_items_fetched if total_items_fetched > 0 else 0.0

    out = pd.DataFrame(
        [
            {
                "throughput_items_per_sec": throughput,
                "success_rate": success_rate,
                "dedup_rate": dedup_rate,
                "items_per_api_call": items_per_api_call,
                "fetch_to_write_ratio": fetch_to_write_ratio,
                "total_api_calls": total_calls,
                "total_items_written": total_items_written,
                "total_elapsed_sec": total_elapsed,
            }
        ]
    )
    out.to_csv(os.path.join(tables_dir, "efficiency_metrics.csv"), index=False)
    print(f"Wrote efficiency metrics to {os.path.join(tables_dir, 'efficiency_metrics.csv')}")
    print(f"Summary: {total_items_written} items written, {total_calls} API calls, {success_rate:.1%} success rate")


if __name__ == "__main__":
    main()
