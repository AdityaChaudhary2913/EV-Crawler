"""Tiny helpers for plots (optional)."""
from __future__ import annotations

import os
from typing import List

import matplotlib.pyplot as plt


def save_hist(data: List[float], out_path: str, bins: int = 20) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure()
    plt.hist(data, bins=bins)
    plt.savefig(out_path)
    plt.close()
