from __future__ import annotations
from typing import Dict, Any, List, Tuple
from .types import MetricResult
from .registry import MetricRegistry
from .operationalization import Operationalization, normalize, binarize
from .netscore import netscore
from .timing import time_call

def build_registry_from_plan() -> MetricRegistry:
    from .impl.size import SizeMetric
    from .impl.license_compliance import LicenseComplianceMetric
    from .impl.ramp_up_time import RampUpTimeMetric
    from .impl.bus_factor import BusFactorMetric
    from .impl.availability import AvailabilityMetric
    from .impl.dataset_quality import DatasetQualityMetric
    from .impl.code_quality import CodeQualityMetric
    from .impl.performance_claims import PerformanceClaimsMetric

    reg = MetricRegistry()
    reg.register(SizeMetric())
    reg.register(LicenseComplianceMetric())
    reg.register(RampUpTimeMetric())
    reg.register(BusFactorMetric())
    reg.register(AvailabilityMetric())
    reg.register(DatasetQualityMetric())
    reg.register(CodeQualityMetric())
    reg.register(PerformanceClaimsMetric())
    return reg

def run_metrics(
    ops: List[Operationalization],
    context: Dict[str, Any],
    registry: MetricRegistry | None = None
) -> Tuple[Dict[str, MetricResult], Dict[str, Any]]:
    reg = registry or build_registry_from_plan()

    # Optional per-metric params
    ctx = dict(context)
    ctx["params"] = {op.metric_id: op.params for op in ops}

    results: Dict[str, MetricResult] = {}
    for op in ops:
        metric = reg.get(op.metric_id)

        def thunk():
            return metric.compute(ctx)  # returns a MetricResult with value set (0..1)

        r, secs = time_call(thunk)
        # normalize if the metric produced a raw value that needs normalization
        # NOTE: Our impls below already return 0..1, but keep this hook for future
        norm_val = normalize(r.value, op)
        results[op.metric_id] = MetricResult(
            id=r.id,
            value=norm_val,
            binary=binarize(norm_val),
            details=r.details,
            seconds=secs
        )

    summary = netscore(results, ops)
    return results, summary
