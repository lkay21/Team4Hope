"""Code quality metric implementation with GenAI analysis."""
from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult


class CodeQualityMetric:
    """
    Combine test_coverage_norm, style_norm, comment_ratio_norm, maintainability_norm (0..1 each).
    """
    id = "code_quality"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        """Compute code quality metric using traditional metrics."""
        import time
        start = time.time()
        code_quality = context.get("code_quality", {})
        keys = ("test_coverage_norm", "style_norm",
                "comment_ratio_norm", "maintainability_norm")
        vals = [float(code_quality[k]) for k in keys if k in code_quality]
        value = sum(vals) / len(vals) if vals else 0.0
        seconds = time.time() - start
        return MetricResult(
            self.id,
            value,
            details={
                "components": vals},
            binary=0,
            seconds=seconds)
