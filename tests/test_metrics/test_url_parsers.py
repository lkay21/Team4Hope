import pytest
from src.url_parsers import detect, fetch_metadata
from src.url_parsers.url_type_handler import get_url_category, handle_url


def test_get_url_category_hf_model():
    url = "https://huggingface.co/someuser/somemodel"
    assert get_url_category(url) == "MODEL"


def test_get_url_category_hf_dataset():
    url = "https://huggingface.co/datasets/someuser/somedataset"
    assert get_url_category(url) == "DATASET"


def test_get_url_category_github():
    url = "https://github.com/someorg/somerepo"
    assert get_url_category(url) == "CODE"


def test_get_url_category_unknown():
    url = "https://example.com/not-a-known-url"
    assert get_url_category(url) is None


def test_handle_url_valid():
    url = "https://huggingface.co/someuser/somemodel"
    result = handle_url(url)
    assert result["url"] == url
    assert result["category"] == "MODEL"
    assert result["name"] == "somemodel"


def test_handle_url_invalid():
    url = "https://example.com/whatever"
    result = handle_url(url)
    assert result["url"] == url
    assert result["category"] is None
    assert result["name"] is None


def test_detect_hf_dataset():
    url = "https://huggingface.co/datasets/someuser/somedataset"
    assert detect(url) == "hf_dataset"


def test_detect_hf_model():
    url = "https://huggingface.co/someuser/somemodel"
    assert detect(url) == "hf_model"


def test_detect_github_repo():
    url = "https://github.com/someorg/somerepo"
    assert detect(url) == "github_repo"


def test_detect_unknown():
    url = "https://randomsite.com/thing"
    assert detect(url) == "unknown"


def test_fetch_metadata_hf_model():
    url = "https://huggingface.co/someuser/somemodel"
    result = fetch_metadata(url)
    assert result == {"url": url, "type": "hf_model"}


def test_fetch_metadata_unknown():
    url = "https://notarealhost.com/foo"
    result = fetch_metadata(url)
    assert result == {"url": url, "type": "unknown"}
