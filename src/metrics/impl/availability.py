from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult

class AvailabilityMetric:
    """
    Code & Dataset linked and resolvable => 1, else partial credit.
    Expect booleans in context['availability']: {"has_code": bool, "has_dataset": bool, "links_ok": bool}
    """
    id = "availability"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        import time
        start = time.time()
        a = context.get("availability", {})
        has_code = bool(a.get("has_code", False))
        has_data = bool(a.get("has_dataset", False))
        links_ok = bool(a.get("links_ok", False))
        value = (has_code + has_data + links_ok) / 3.0
        seconds = time.time() - start
        return MetricResult(self.id, value, details={"has_code": has_code, "has_dataset": has_data, "links_ok": links_ok}, binary=0, seconds=seconds)
