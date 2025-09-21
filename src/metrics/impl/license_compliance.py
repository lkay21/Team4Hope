from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult

class LicenseComplianceMetric:
    """
    1 if a compatible license string is detected, else 0. 'compatible_licenses' may be provided in context.
    """
    id = "license_compliance"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        import time
        start = time.time()
        lic = (context.get("license") or "").lower()
        allow = set(context.get("compatible_licenses", ["mit","bsd","apache-2.0","mpl","cc-by"]))
        value = 1.0 if any(a in lic for a in allow) else 0.0
        seconds = time.time() - start
        return MetricResult(self.id, value, details={"license": lic}, binary=0, seconds=seconds)
