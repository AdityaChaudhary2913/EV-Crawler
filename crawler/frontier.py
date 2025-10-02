"""Frontier priority queue and seen set for focused crawling."""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Any, Optional, Tuple


@dataclass(order=True)
class _PQItem:
    priority: float
    seq: int
    item: Any = field(compare=False)


class Frontier:
    """A max-heap frontier with dedup by a provided key function."""

    def __init__(self):
        self._heap: list[_PQItem] = []
        self._seq = 0
        self._seen: set[str] = set()

    def seen(self, key: str) -> bool:
        return key in self._seen

    def mark_seen(self, key: str) -> None:
        self._seen.add(key)

    def push(self, priority: float, item: Any) -> None:
        # heapq is min-heap; use negative to simulate max-heap
        heapq.heappush(self._heap, _PQItem(priority=-priority, seq=self._seq, item=item))
        self._seq += 1

    def pop(self) -> Optional[Tuple[float, Any]]:
        if not self._heap:
            return None
        node = heapq.heappop(self._heap)
        return -node.priority, node.item

    def __len__(self) -> int:  # for truthiness and metrics
        return len(self._heap)
