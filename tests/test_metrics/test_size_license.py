import pytest
from src.metrics.impl.size import SizeMetric
from src.metrics.impl.license_compliance import LicenseComplianceMetric
from src.metrics.types import MetricResult


# -------------------
# SizeMetric Tests
# -------------------

def test_size_metric_all_components():
    metric = SizeMetric()
    context = {
        "size_components": {
            "loc_norm": 0.5,
            "db_norm": 0.8,
            "params_norm": 0.2,
            "artifacts_norm": 1.0,
        }
    }
    result = metric.compute(context)
    assert isinstance(result, MetricResult)
    assert result.value == pytest.approx((0.5 + 0.8 + 0.2 + 1.0) / 4)
    assert "used" in result.details
    assert len(result.details["used"]) == 4


def test_size_metric_partial_components():
    metric = SizeMetric()
    context = {"size_components": {"loc_norm": 0.7, "db_norm": 0.3}}
    result = metric.compute(context)
    assert result.value == pytest.approx((0.7 + 0.3) / 2)
    assert len(result.details["used"]) == 2


def test_size_metric_no_components():
    metric = SizeMetric()
    context = {"size_components": {}}
    result = metric.compute(context)
    assert result.value == 0.0
    assert result.details["used"] == []


def test_size_metric_string_inputs():
    metric = SizeMetric()
    context = {"size_components": {"loc_norm": "0.4", "db_norm": "0.6"}}
    result = metric.compute(context)
    assert result.value == pytest.approx((0.4 + 0.6) / 2)


def test_size_metric_missing_context_key():
    metric = SizeMetric()
    context = {}  # no size_components
    result = metric.compute(context)
    assert result.value == 0.0


# -------------------
# LicenseComplianceMetric Tests
# -------------------

def test_license_compliance_detects_compatible():
    metric = LicenseComplianceMetric()
    context = {"license": "MIT"}
    result = metric.compute(context)
    assert isinstance(result, MetricResult)
    assert result.value == 1.0
    assert "mit" in result.details["license"]


def test_license_compliance_detects_incompatible():
    metric = LicenseComplianceMetric()
    context = {"license": "proprietary"}
    result = metric.compute(context)
    assert result.value == 0.0
    assert result.details["license"] == "proprietary"


def test_license_compliance_with_custom_list():
    metric = LicenseComplianceMetric()
    context = {"license": "weirdlicense", "compatible_licenses": ["weird"]}
    result = metric.compute(context)
    assert result.value == 1.0
    assert "weirdlicense" in result.details["license"]


def test_license_compliance_empty_context():
    metric = LicenseComplianceMetric()
    context = {}
    result = metric.compute(context)
    assert result.value == 0.0
    assert result.details["license"] == ""
