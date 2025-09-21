"""
Size metric implementation.

[0, 1] range where 0 = very small model/dataset size and 1 = very large in size.
This is computed by checking normalized size scores for different hardware
targets (e.g., Raspberry Pi, Jetson Nano, Desktop PC, AWS server).

See: Preliminary Design rubric (ECE30861) for justification.
"""

import time
from typing import Dict, Any
from src.metrics.types import MetricResult


class SizeMetric:
    """
    Computes the size metric based on normalized size scores across hardware.
    """
    id = "size"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        start = time.time()
        c = context.get("size_components", {})

        # Expected hardware-specific keys
        hardware_keys = ["raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"]

        size_score = {}
        for hw in hardware_keys:
            size_score[hw] = float(c.get(hw, 0.0))  # default to 0 if missing

        # Compute overall value as the mean of available hardware scores
        value = sum(size_score.values()) / len(size_score) if size_score else 0.0

        seconds = time.time() - start
        return MetricResult(
            id=self.id,
            value=value,
            binary=0,
            details={"size_score": size_score},
            seconds=seconds,
        )
