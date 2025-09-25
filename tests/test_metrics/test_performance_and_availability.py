import pytest
from src.metrics.impl.performance_claims import PerformanceClaimsMetric
from src.metrics.impl.availability import AvailabilityMetric
from src.metrics.types import MetricResult


# -------------------
# PerformanceClaimsMetric Tests
# -------------------

def test_performance_claims_weighted_score():
    metric = PerformanceClaimsMetric()
    context = {"requirements_score": 0.75}
    result = metric.compute(context)
    assert isinstance(result, MetricResult)
    assert result.value == 0.75
    assert result.details["mode"] == "weighted"


def test_performance_claims_simple_fraction():
    metric = PerformanceClaimsMetric()
    context = {"requirements_passed": 3, "requirements_total": 4}
    result = metric.compute(context)
    assert result.value == pytest.approx(0.75)
    assert result.details["mode"] == "simple"
    assert result.details["passed"] == 3
    assert result.details["total"] == 4


def test_performance_claims_defaults():
    metric = PerformanceClaimsMetric()
    context = {}
    result = metric.compute(context)
    assert result.value == 0.0  # passed=0, total=1 by default
    assert result.details["total"] == 1


# -------------------
# AvailabilityMetric Tests
# -------------------

def test_availability_all_true():
    metric = AvailabilityMetric()
    context = {"availability": {"has_code": True, "has_dataset": True, "links_ok": True}}
    result = metric.compute(context)
    assert isinstance(result, MetricResult)
    assert result.value == 1.0
    assert all(result.details.values())


def test_availability_partial():
    metric = AvailabilityMetric()
    context = {"availability": {"has_code": True, "has_dataset": False, "links_ok": True}}
    result = metric.compute(context)
    assert result.value == pytest.approx(2/3)
    assert result.details["has_dataset"] is False


def test_availability_none():
    metric = AvailabilityMetric()
    context = {"availability": {}}
    result = metric.compute(context)
    assert result.value == 0.0
    assert result.details["has_code"] is False
    assert result.details["has_dataset"] is False
    assert result.details["links_ok"] is False
