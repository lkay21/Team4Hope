import pytest
from src.metrics.types import MetricResult

def test_metric_result_roundtrip():
    # Create an object
    m = MetricResult(
        id="test",
        value=0.9,
        binary=1,
        details={"source": "unit"},
        seconds=0.05,
    )
    # Check fields
    assert m.id == "test"
    assert m.value == 0.9
    assert m.binary == 1
    assert m.details["source"] == "unit"
    assert m.seconds == pytest.approx(0.05)

def test_metric_result_is_frozen():
    m = MetricResult("id", 0.1, 0, {}, 0.0)
    with pytest.raises(Exception):
        m.id = "changed"  # should raise because frozen=True

def test_metric_protocol_contract():
    from typing import Protocol

    # Metric protocol says: class must have id and compute(context) -> MetricResult
    class DummyMetric:
        id = "dummy"
        def compute(self, context):
            return MetricResult("dummy", 1.0, 1, {}, 0.0)

    d = DummyMetric()
    result = d.compute({})
    assert isinstance(result, MetricResult)
    assert result.id == "dummy"
    assert result.value == 1.0
