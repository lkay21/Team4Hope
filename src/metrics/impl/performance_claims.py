from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult

class PerformanceClaimsMetric:
    """
    Average over requirement assertions: supply context['requirements_passed'] (0..N) and total (N).
    You can also pass a weighted fraction via context['requirements_score'] in 0..1.
    """
    id = "performance_claims"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        import time
        start = time.time()
        if "requirements_score" in context:
            value = float(context["requirements_score"])
            details = {"mode": "weighted", "requirements_score": value}
        else:
            passed = int(context.get("requirements_passed", 0))
            total = max(1, int(context.get("requirements_total", 1)))
            value = passed / total
            details = {"mode": "simple", "passed": passed, "total": total}
        seconds = time.time() - start
        return MetricResult(self.id, value, details=details, binary=0, seconds=seconds)
