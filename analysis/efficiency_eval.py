"""Efficiency evaluation from metrics.csv.

Computes:
- throughput_items_per_sec (items_written / elapsed_sec)
- success_rate (success_calls / (success_calls + error_calls))
- dedup_rate (dedup_skipped / (items_written + dedup_skipped))
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
    # Use the last row as cumulative snapshot
    last = df.iloc[-1]
    elapsed = float(last.get("elapsed_sec", 0.0) or 0.0)
    items_written = float(last.get("items_written", 0.0) or 0.0)
    success_calls = float(last.get("success_calls", 0.0) or 0.0)
    error_calls = float(last.get("error_calls", 0.0) or 0.0)
    dedup_skipped = float(last.get("dedup_skipped", 0.0) or 0.0)

    throughput = items_written / elapsed if elapsed > 0 else 0.0
    total_calls = success_calls + error_calls if (success_calls + error_calls) > 0 else 1.0
    success_rate = success_calls / total_calls
    dedup_rate = dedup_skipped / max(1.0, items_written + dedup_skipped)

    out = pd.DataFrame(
        [
            {
                "throughput_items_per_sec": throughput,
                "success_rate": success_rate,
                "dedup_rate": dedup_rate,
            }
        ]
    )
    out.to_csv(os.path.join(tables_dir, "efficiency_metrics.csv"), index=False)
    print(f"Wrote efficiency metrics to {os.path.join(tables_dir, 'efficiency_metrics.csv')}")


if __name__ == "__main__":
    main()
