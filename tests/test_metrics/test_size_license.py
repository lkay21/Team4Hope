import pytest
from src.metrics.impl.size import SizeMetric
from src.metrics.types import MetricResult

def test_size_metric_all_components():
    metric = SizeMetric()
    context = {
        "size_components": {
            "raspberry_pi": 0.5,
            "jetson_nano": 0.8,
            "desktop_pc": 0.2,
            "aws_server": 1.0,
        }
    }
    result = metric.compute(context)
    assert isinstance(result, MetricResult)
    expected = (0.5 + 0.8 + 0.2 + 1.0) / 4
    assert result.value == pytest.approx(expected)
    assert set(result.details["size_score"].keys()) == {
        "raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"
    }

def test_size_metric_partial_components():
    metric = SizeMetric()
    context = {"size_components": {"raspberry_pi": 0.7, "jetson_nano": 0.3}}
    result = metric.compute(context)
    expected = (0.7 + 0.3 + 0.0 + 0.0) / 4  # missing hw defaults to 0
    assert result.value == pytest.approx(expected)

def test_size_metric_no_components():
    metric = SizeMetric()
    context = {"size_components": {}}
    result = metric.compute(context)
    assert result.value == 0.0
    assert all(v == 0.0 for v in result.details["size_score"].values())

def test_size_metric_string_inputs():
    metric = SizeMetric()
    context = {"size_components": {"raspberry_pi": "0.4", "jetson_nano": "0.6"}}
    result = metric.compute(context)
    expected = (0.4 + 0.6 + 0.0 + 0.0) / 4
    assert result.value == pytest.approx(expected)

def test_size_metric_missing_context_key():
    metric = SizeMetric()
    result = metric.compute({})
    assert result.value == 0.0
