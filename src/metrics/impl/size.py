from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult

class SizeMetric:
    """
    Combines normalized components: lines_of_code, db_size_mb, num_params_m, num_artifacts.
    Provide any subset; missing values are ignored.
    Output value is 0..1; details expose components. Binarization handled upstream.
    """
    id = "size"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        c = context.get("size_components", {})
        parts = []
        # Each input should already be normalized to 0..1 by your parser; if raw, do your own min/max.
        for key in ("loc_norm", "db_norm", "params_norm", "artifacts_norm"):
            if key in c:
                parts.append(float(c[key]))
        value = sum(parts)/len(parts) if parts else 0.0
        return MetricResult(self.id, value, details={"used": parts}, binary=0, seconds=0.0)
