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
    models = {0: ['https://github.com/google-research/bert', ' https://huggingface.co/datasets/bookcorpus/bookcorpus', ' https://huggingface.co/google-bert/bert-base-uncased\n'], 1: ['', '', 'https://huggingface.co/parvk11/audience_classifier_model\n'], 2: ['', '', 'https://huggingface.co/openai/whisper-tiny/tree/main']}
    ndjsons = evaluate_url(models)
    assert isinstance(ndjsons, dict)


def test_validate_ndjson_valid_record():
    models = {0: ['https://github.com/google-research/bert', ' https://huggingface.co/datasets/bookcorpus/bookcorpus', ' https://huggingface.co/google-bert/bert-base-uncased\n'], 1: ['', '', 'https://huggingface.co/parvk11/audience_classifier_model\n'], 2: ['', '', 'https://huggingface.co/openai/whisper-tiny/tree/main']}
    ndsjons = evaluate_url(models)
    for ndjson in ndsjons.values():
        assert validate_ndjson(ndjson) is True


def test_validate_ndjson_invalid_record_missing_field():
    bad = {"name": "x","category": "x"}  # missing many required fields
    assert validate_ndjson(bad) is False


def test_validate_ndjson_invalid_score_type():
    models = {0: ['https://github.com/google-research/bert', ' https://huggingface.co/datasets/bookcorpus/bookcorpus', ' https://huggingface.co/google-bert/bert-base-uncased\n'], 1: ['', '', 'https://huggingface.co/parvk11/audience_classifier_model\n'], 2: ['', '', 'https://huggingface.co/openai/whisper-tiny/tree/main']}
    ndsjons = evaluate_url(models)
    for ndjson in ndsjons.values():
        ndjson["size_score"]["raspberry_pi"] = "not-a-number"  # invalid type
        assert validate_ndjson(ndjson) is False


def test_validate_ndjson_invalid_latency_type():
    models = {0: ['https://github.com/google-research/bert', ' https://huggingface.co/datasets/bookcorpus/bookcorpus', ' https://huggingface.co/google-bert/bert-base-uncased\n'], 1: ['', '', 'https://huggingface.co/parvk11/audience_classifier_model\n'], 2: ['', '', 'https://huggingface.co/openai/whisper-tiny/tree/main']}
    ndsjons = evaluate_url(models)
    for ndjson in ndsjons.values():
        ndjson["size_score_latency"] = "fast"  # invalid type
        assert validate_ndjson(ndjson) is False
