import pytest
from src.metrics.types import MetricResult
from src.cli.main import evaluate_url, validate_ndjson


# -----------------------------
# MetricResult dataclass schema
# -----------------------------

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


# -----------------------------
# NDJSON output schema
# -----------------------------

def test_evaluate_url_structure():
    url = "https://huggingface.co/someuser/somemodel"
    rec = evaluate_url(url)

    # Check top-level keys
    assert "url" in rec
    assert "scores" in rec
    assert "overall" in rec

    # Check URL is preserved
    assert rec["url"] == url

    # Check score fields exist with score + latency
    for field, metric in rec["scores"].items():
        assert "score" in metric
        assert "latency" in metric


def test_validate_ndjson_valid_record():
    url = "https://huggingface.co/someuser/somemodel"
    rec = evaluate_url(url)
    assert validate_ndjson(rec) is True


def test_validate_ndjson_invalid_record_missing_field():
    bad = {"url": "x", "scores": {}, "overall": None}
    assert validate_ndjson(bad) is False


def test_validate_ndjson_invalid_score_type():
    url = "https://huggingface.co/someuser/somemodel"
    rec = evaluate_url(url)
    rec["scores"]["size"]["score"] = "not-a-number"  # invalid type
    assert validate_ndjson(rec) is False


def test_validate_ndjson_invalid_latency_type():
    url = "https://huggingface.co/someuser/somemodel"
    rec = evaluate_url(url)
    rec["scores"]["size"]["latency"] = "fast"  # invalid type
    assert validate_ndjson(rec) is False
