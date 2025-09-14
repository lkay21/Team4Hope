from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult

class DatasetQualityMetric:
    """
    Combine cleanliness, documentation, class_balance (0..1 each).
    """
    id = "dataset_quality"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        dq = context.get("dataset_quality", {})
        vals = [float(dq[k]) for k in ("cleanliness","documentation","class_balance") if k in dq]
        value = sum(vals)/len(vals) if vals else 0.0
        return MetricResult(self.id, value, details={"components": vals}, binary=0, seconds=0.0)
