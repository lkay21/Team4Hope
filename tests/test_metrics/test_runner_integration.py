import pytest
from src.metrics.runner import run_metrics, build_registry_from_plan
from src.metrics.operationalization import Operationalization

def make_op(metric_id: str, weight: float = 1.0):
    return Operationalization(
        metric_id=metric_id,
        params={},
        weight=weight,
        normalization="identity",
        norm_params={}
    )

def test_run_metrics_basic():
    ops = [make_op("size"), make_op("license_compliance")]
    context = {
        "size_components": {"loc_norm": 0.8},
        "license": "mit"
    }
    registry = build_registry_from_plan()
    results, summary = run_metrics(ops, context, registry)

    # Check results contain both metrics
    assert "size" in results
    assert "license_compliance" in results

    # Size should average one component = 0.8
    assert pytest.approx(results["size"].value) == 0.8
    # License compliance with "mit" should be 1
    assert results["license_compliance"].value == 1.0

    # Summary should have NetScore fields
    assert "NetScore_weighted" in summary
    assert "NetScore_binary" in summary
    assert summary["NetScore_weighted"] > 0
