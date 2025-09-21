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
        import time
        start = time.time()
        c = context.get("size_components", {})
        hardware_keys = ["raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"]
        size_score = {}
        for hw in hardware_keys:
            # Default to 0 if not provided
            size_score[hw] = float(c.get(hw, 0.0))
        # Optionally, compute an overall value as the mean
        value = sum(size_score.values()) / len(size_score) if size_score else 0.0
        seconds = time.time() - start
        return MetricResult(self.id, value, details={"size_score": size_score}, binary=0, seconds=seconds)
