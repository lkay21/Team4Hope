import pytest
from src.metrics.impl.code_quality import CodeQualityMetric
from src.metrics.impl.dataset_quality import DatasetQualityMetric
from src.metrics.types import MetricResult


# -------------------
# CodeQualityMetric Tests
# -------------------

def test_code_quality_all_components():
    metric = CodeQualityMetric()
    context = {
        "code_quality": {
            "test_coverage_norm": 0.9,
            "style_norm": 0.8,
            "comment_ratio_norm": 0.7,
            "maintainability_norm": 0.6,
        }
    }
    result = metric.compute(context)
    assert isinstance(result, MetricResult)
    assert result.value == pytest.approx((0.9 + 0.8 + 0.7 + 0.6) / 4)
    assert len(result.details["components"]) == 4


def test_code_quality_partial_components():
    metric = CodeQualityMetric()
    context = {"code_quality": {"test_coverage_norm": 0.5, "style_norm": 0.3}}
    result = metric.compute(context)
    assert result.value == pytest.approx((0.5 + 0.3) / 2)
    assert len(result.details["components"]) == 2


def test_code_quality_no_components():
    metric = CodeQualityMetric()
    context = {"code_quality": {}}
    result = metric.compute(context)
    assert result.value == 0.0
    assert result.details["components"] == []


def test_code_quality_string_inputs():
    metric = CodeQualityMetric()
    context = {"code_quality": {"test_coverage_norm": "0.4", "style_norm": "0.6"}}
    result = metric.compute(context)
    assert result.value == pytest.approx((0.4 + 0.6) / 2)


# -------------------
# DatasetQualityMetric Tests
# -------------------

def test_dataset_quality_all_components():
    metric = DatasetQualityMetric()
    context = {
        "dataset_quality": {
            "cleanliness": 1.0,
            "documentation": 0.5,
            "class_balance": 0.75,
        }
    }
    result = metric.compute(context)
    assert isinstance(result, MetricResult)
    assert result.value == pytest.approx((1.0 + 0.5 + 0.75) / 3)
    assert len(result.details["components"]) == 3


def test_dataset_quality_partial_components():
    metric = DatasetQualityMetric()
    context = {"dataset_quality": {"cleanliness": 0.4}}
    result = metric.compute(context)
    assert result.value == pytest.approx(0.4)
    assert len(result.details["components"]) == 1


def test_dataset_quality_no_components():
    metric = DatasetQualityMetric()
    context = {"dataset_quality": {}}
    result = metric.compute(context)
    assert result.value == 0.0
    assert result.details["components"] == []


def test_dataset_quality_string_inputs():
    metric = DatasetQualityMetric()
    context = {"dataset_quality": {"documentation": "0.9", "class_balance": "0.6"}}
    result = metric.compute(context)
    assert result.value == pytest.approx((0.9 + 0.6) / 2)
