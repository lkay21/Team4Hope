import pytest
from src.cli.main import evaluate_url, validate_ndjson


def test_evaluate_url_structure():
    url = "https://huggingface.co/someuser/somemodel"
    rec = evaluate_url(url)

    # Top-level must be a dict with three slots
    assert isinstance(rec, dict)
    assert "dataset" in rec
    assert "code" in rec
    assert "model" in rec

    # Each slot must be a dict
    assert isinstance(rec["dataset"], dict)
    assert isinstance(rec["code"], dict)
    assert isinstance(rec["model"], dict)


def test_validate_ndjson_valid_record():
    url = "https://huggingface.co/someuser/somemodel"
    rec = evaluate_url(url)

    # All three sections must pass schema validation
    for section in ["dataset", "code", "model"]:
        assert validate_ndjson(rec[section]) is True


def test_validate_ndjson_invalid_record_missing_field():
    url = "https://huggingface.co/someuser/somemodel"
    rec = evaluate_url(url)

    # Remove a required field from model record
    bad_rec = rec["model"].copy()
    bad_rec.pop("name", None)

    assert validate_ndjson(bad_rec) is False


def test_validate_ndjson_invalid_score_type():
    url = "https://huggingface.co/someuser/somemodel"
    rec = evaluate_url(url)

    bad_rec = rec["model"].copy()
    bad_rec["size_score"]["raspberry_pi"] = "not-a-number"

    assert validate_ndjson(bad_rec) is False


def test_validate_ndjson_invalid_latency_type():
    url = "https://huggingface.co/someuser/somemodel"
    rec = evaluate_url(url)

    bad_rec = rec["model"].copy()
    bad_rec["size_score_latency"] = "fast"

    assert validate_ndjson(bad_rec) is False
