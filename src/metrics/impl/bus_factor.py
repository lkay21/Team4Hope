from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult

class BusFactorMetric:
    """
    Heuristic: higher is better when contribution is spread. Expect:
      contributors_count (>=1), top_contributor_pct (0..1).
    We map: value = 1 - top_contributor_pct, optionally scaled by log(contributors).
    """
    id = "bus_factor"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        meta = context.get("repo_meta", {})
        top_pct = float(meta.get("top_contributor_pct", 1.0))  # 1.0 == single dev dominates
        value = max(0.0, min(1.0, 1.0 - top_pct))
        return MetricResult(self.id, value, details={"top_contributor_pct": top_pct}, binary=0, seconds=0.0)
