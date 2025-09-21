import pytest
from src.metrics.runner import run_metrics, build_registry_from_plan
from src.metrics.ops_plan import make_op  # correct import

def test_run_metrics_basic():
    ops = [make_op("size"), make_op("license_compliance")]
    context = {
        "size_components": {"raspberry_pi": 0.8},  # hardware-style input
        "license": "mit"
    }
    registry = build_registry_from_plan()
    results, summary = run_metrics(ops, context, registry)

    assert "size" in results
    assert "license_compliance" in results
    # Only one hardware key provided, mean = 0.8
    assert results["size"].value == pytest.approx(0.8)
