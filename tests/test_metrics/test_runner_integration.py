import pytest
from src.metrics.runner import run_metrics, build_registry_from_plan
from src.metrics.ops_plan import default_ops


def test_run_metrics_all_default_ops():
    # Use all default ops from the milestone plan
    ops = default_ops

    # Build a context with dummy values in the format each metric expects
    context = {
        # size.py expects normalized hardware-specific size components
        "size_components": {
            "raspberry_pi": 0.8,
            "jetson_nano": 0.6,
            "desktop_pc": 0.0,
            "aws_server": 0.0,
        },

        # license_compliance.py expects a string license id
        "license": "mit",

        # ramp_up_time.py expects a numeric ramp_up_time value
        "ramp_up_time": 0.7,

        # bus_factor.py expects a numeric bus_factor value
        "bus_factor": 0.5,

        # availability.py expects a dict with specific flags
        "availability": {"has_code": True, "has_dataset": True, "links_ok": True},

        # dataset_quality.py expects dict with cleanliness, documentation, class_balance
        "dataset_quality": {"cleanliness": 0.9, "documentation": 0.8, "class_balance": 1.0},

        # code_quality.py expects dict with test_coverage_norm, style_norm, comment_ratio_norm, maintainability_norm
        "code_quality": {
            "test_coverage_norm": 0.8,
            "style_norm": 0.9,
            "comment_ratio_norm": 0.85,
            "maintainability_norm": 0.9,
        },

        # performance_claims.py expects either requirements_score OR passed/total
        "requirements_score": 0.95,
    }

    registry = build_registry_from_plan()
    results, summary = run_metrics(ops, context, registry)

    # Ensure every op from default_ops produced a result
    for op in ops:
        metric_id = getattr(op, "metric_id", getattr(op, "id", None))
        assert metric_id is not None, "Operationalization missing metric identifier"
        assert metric_id in results, f"{metric_id} missing from results"
        assert results[metric_id].value is not None, f"{metric_id} has no value"

    # Spot-check a few values for correctness
    # size: (0.8 + 0.6 + 0.0 + 0.0)/4 = 0.35
    assert results["size"].value == pytest.approx(0.35)
    assert results["license_compliance"].value in (0, 1)
    assert results["performance_claims"].value == pytest.approx(0.95)
