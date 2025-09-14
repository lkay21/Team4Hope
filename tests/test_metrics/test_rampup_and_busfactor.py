import pytest
from src.metrics.impl.bus_factor import BusFactorMetric
from src.metrics.impl.ramp_up_time import RampUpTimeMetric
from src.metrics.types import MetricResult


# -------------------
# BusFactorMetric Tests
# -------------------

def test_bus_factor_balanced_contributors():
    metric = BusFactorMetric()
    context = {"repo_meta": {"top_contributor_pct": 0.25}}
    result = metric.compute(context)
    assert isinstance(result, MetricResult)
    assert result.value == pytest.approx(0.75)
    assert result.details["top_contributor_pct"] == 0.25


def test_bus_factor_single_contributor():
    metric = BusFactorMetric()
    context = {"repo_meta": {"top_contributor_pct": 1.0}}
    result = metric.compute(context)
    assert result.value == 0.0
    assert result.details["top_contributor_pct"] == 1.0


def test_bus_factor_invalid_or_missing():
    metric = BusFactorMetric()
    context = {}  # no repo_meta
    result = metric.compute(context)
    assert result.value == 0.0  # default top_contributor_pct = 1.0


# -------------------
# RampUpTimeMetric Tests
# -------------------

def test_ramp_up_all_components():
    metric = RampUpTimeMetric()
    context = {"ramp": {"likes_norm": 0.8, "downloads_norm": 0.6, "recency_norm": 0.4}}
    result = metric.compute(context)
    assert isinstance(result, MetricResult)
    assert result.value == pytest.approx((0.8 + 0.6 + 0.4) / 3)
    assert len(result.details["components"]) == 3


def test_ramp_up_partial_components():
    metric = RampUpTimeMetric()
    context = {"ramp": {"likes_norm": 0.9}}
    result = metric.compute(context)
    assert result.value == pytest.approx(0.9)
    assert result.details["components"] == [0.9]


def test_ramp_up_no_components():
    metric = RampUpTimeMetric()
    context = {"ramp": {}}
    result = metric.compute(context)
    assert result.value == 0.0
    assert result.details["components"] == []
