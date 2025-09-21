# src/metrics/impl/size.py
"""
Size metric implementation.

[0, 1] range where 0 = very small model/dataset size and 1 = very large in size.
This is computed by averaging the provided normalized size components.
Components can include: lines of code, database size, number of parameters,
and number of artifacts/files in the repo.

See: Preliminary Design rubric (ECE30861) for justification.
"""

from src.metrics.types import MetricResult


class SizeMetric:
    """
    Computes the size metric based on normalized size components.
    """

    def compute(self, context: dict) -> MetricResult:
        # Extract size components from context
        size_components = context.get("size_components", {})

        # Convert all values to floats, ignore invalid entries
        used = []
        values = []
        for key, val in size_components.items():
            try:
                fval = float(val)
                values.append(fval)
                used.append(key)
            except (TypeError, ValueError):
                continue

        # Compute average if we have values, else 0.0
        value = sum(values) / len(values) if values else 0.0

        return MetricResult(
            id="size",
            value=value,
            binary=1 if values else 0,
            details={"used": used},
            seconds=0.0,
        )
