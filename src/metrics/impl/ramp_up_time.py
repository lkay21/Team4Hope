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
        r = context.get("ramp", {})
        vals = [float(r[k]) for k in ("likes_norm","downloads_norm","recency_norm") if k in r]
        value = sum(vals)/len(vals) if vals else 0.0
        return MetricResult(self.id, value, details={"components": vals}, binary=0, seconds=0.0)
