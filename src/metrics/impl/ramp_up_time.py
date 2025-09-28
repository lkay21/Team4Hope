"""Ramp-up time metric implementation."""
from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult


class RampUpTimeMetric:
    """
    Heuristic: average of normalized popularity + downloads + recency signals provided by parser.
    Expect fields in context['ramp'] as already-normalized 0..1: likes_norm, downloads_norm, recency_norm.
    """
    id = "ramp_up_time"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        """Compute ramp-up time metric."""
        import time
        start = time.time()
        ramp_up = context.get("ramp_up", {})
        value = float(ramp_up.get("example_norm", 0.0))
        seconds = time.time() - start
        return MetricResult(
            self.id,
            value,
            details={
                "ramp_up": ramp_up},
            binary=0,
            seconds=seconds)
