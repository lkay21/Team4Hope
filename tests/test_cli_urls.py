import json
import pytest
from src.cli.main import evaluate_url, validate_ndjson


def test_single_model():
    url = "https://huggingface.co/gpt2"
    rec = evaluate_url(url)

    assert isinstance(rec, dict)
    assert "model" in rec
    assert "dataset" in rec
    assert "code" in rec
    assert rec["model"]["category"] == "MODEL"
    assert validate_ndjson(rec)


def test_dataset_and_code():
    urls = "https://huggingface.co/datasets/squad, https://github.com/huggingface/transformers"
    rec = evaluate_url(urls)

    assert isinstance(rec, dict)
    assert "dataset" in rec and "code" in rec and "model" in rec
    assert rec["dataset"]["category"] == "DATASET"
    assert rec["code"]["category"] == "CODE"
    # model should still exist (possibly inferred placeholder)
    assert rec["model"] is not None
    assert validate_ndjson(rec)


def test_three_links():
    urls = "https://huggingface.co/datasets/squad, https://github.com/huggingface/transformers, https://huggingface.co/gpt2"
    rec = evaluate_url(urls)

    assert isinstance(rec, dict)
    assert rec["dataset"]["category"] == "DATASET"
    assert rec["code"]["category"] == "CODE"
    assert rec["model"]["category"] == "MODEL"
    assert validate_ndjson(rec)
