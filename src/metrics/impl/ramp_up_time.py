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

        # Get normalized components for ramp-up calculation
        likes_norm = ramp_up.get("likes_norm", 0.0)
        downloads_norm = ramp_up.get("downloads_norm", 0.0)
        recency_norm = ramp_up.get("recency_norm", 0.0)

        # Calculate value as average of the three normalized components
        components = [likes_norm, downloads_norm, recency_norm]
        non_zero_components = [c for c in components if c > 0]

        if non_zero_components:
            value = sum(non_zero_components) / len(non_zero_components)
        else:
            value = 0.0

        seconds = time.time() - start
        return MetricResult(
            self.id,
            value,
            details={
                "ramp_up": ramp_up},
            binary=0,
            seconds=seconds)
