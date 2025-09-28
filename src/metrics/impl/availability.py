"""Availability metric implementation."""
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
        """Compute availability metric based on link availability data."""
        import time
        start = time.time()
        availability = context.get("availability", {})
        
        # Get individual components
        has_code = availability.get("has_code", False)
        has_dataset = availability.get("has_dataset", False) 
        links_ok = availability.get("links_ok", False)
        
        # Calculate value as average of the three components
        components = [has_code, has_dataset, links_ok]
        value = sum(components) / len(components)
        
        seconds = time.time() - start
        return MetricResult(
            self.id,
            value,
            details={
                "has_code": has_code,
                "has_dataset": has_dataset,
                "links_ok": links_ok},
            binary=0,
            seconds=seconds)
