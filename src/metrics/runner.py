from __future__ import annotations
from typing import Dict, Any, List, Tuple
from .types import MetricResult
from .registry import MetricRegistry
from .operationalization import Operationalization, normalize, binarize
from .netscore import netscore
from .timing import time_call

# NEW imports for parallelism
from concurrent.futures import ThreadPoolExecutor, as_completed
import os, time


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


# internal helper for both sequential & parallel paths
def _compute_one(op: Operationalization, metric, ctx: Dict[str, Any]) -> Tuple[str, MetricResult]:
    # time just the metric compute
    def thunk():
        return metric.compute(ctx)  # returns MetricResult with value set (0..1)
    r, secs = time_call(thunk)

    # normalize + binarize
    norm_val = normalize(r.value, op)
    res = MetricResult(
        id=r.id,
        value=norm_val,
        binary=binarize(norm_val),
        details=r.details,
        seconds=secs
    )
    return op.metric_id, res


def run_metrics(
    ops: List[Operationalization],
    context: Dict[str, Any],
    registry: MetricRegistry | None = None,
    *,
    parallel: bool = False,
    max_workers: int | None = None
) -> Tuple[Dict[str, MetricResult], Dict[str, Any]]:
    """
    Execute all metrics and return (results_by_id, netscore_summary).

    Args:
        ops: operationalizations (which metrics, weights, normalization)
        context: shared read-only context for metrics
        registry: optional pre-built registry
        parallel: if True, run metrics concurrently via ThreadPoolExecutor
        max_workers: optional cap on threads; default is a sensible value
    """
    reg = registry or build_registry_from_plan()

    # Per-metric params (optional)
    ctx = dict(context)
    ctx["params"] = {op.metric_id: op.params for op in ops}

    results: Dict[str, MetricResult] = {}

    if not parallel:
        # ---- original sequential path ----
        for op in ops:
            metric = reg.get(op.metric_id)
            mid, res = _compute_one(op, metric, ctx)
            results[mid] = res
    else:
        # ---- parallel path ----
        # sensible default: more threads than cores (metrics are usually I/O/light CPU)
        if max_workers is None:
            max_workers = min(32, (os.cpu_count() or 4) * 5)

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {
                ex.submit(_compute_one, op, reg.get(op.metric_id), ctx): op.metric_id
                for op in ops
            }
            for fut in as_completed(futures):
                mid, res = fut.result()  # will raise if metric threw; you can wrap in try/except if desired
                results[mid] = res

    summary = netscore(results, ops)
    return results, summary