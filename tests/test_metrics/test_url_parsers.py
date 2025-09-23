import pytest
from src.url_parsers import detect, fetch_metadata
from src.url_parsers.url_type_handler import get_url_category, handle_url


# # def test_get_url_category_hf_model():
# #     url = "https://huggingface.co/someuser/somemodel"
# #     assert get_url_category(url) == "MODEL"


# # def test_get_url_category_hf_dataset():
# #     url = "https://huggingface.co/datasets/someuser/somedataset"
# #     assert get_url_category(url) == "DATASET"


# # def test_get_url_category_github():
# #     url = "https://github.com/someorg/somerepo"
# #     assert get_url_category(url) == "CODE"


# # def test_get_url_category_unknown():
# #     url = "https://example.com/not-a-known-url"
# #     assert get_url_category(url) is None


# def test_handle_url_valid():
#     models = {0: ['https://github.com/google-research/bert', ' https://huggingface.co/datasets/bookcorpus/bookcorpus', ' https://huggingface.co/google-bert/bert-base-uncased\n'], 1: ['', '', 'https://huggingface.co/parvk11/audience_classifier_model\n'], 2: ['', '', 'https://huggingface.co/openai/whisper-tiny/tree/main']}
#     result = handle_url(url)
#     # URL itself is not stored, just category + name
#     assert result["category"] == "MODEL"
#     assert result["name"] == "somemodel"


# def test_handle_url_invalid():
#     url = "https://example.com/whatever"
#     result = handle_url(url)
#     assert result["category"] is None
#     assert result["name"] is None


# def test_detect_hf_dataset():
#     url = "https://huggingface.co/datasets/someuser/somedataset"
#     assert detect(url) == "hf_dataset"


# def test_detect_hf_model():
#     url = "https://huggingface.co/someuser/somemodel"
#     assert detect(url) == "hf_model"


# def test_detect_github_repo():
#     url = "https://github.com/someorg/somerepo"
#     assert detect(url) == "github_repo"


# def test_detect_unknown():
#     url = "https://randomsite.com/thing"
#     assert detect(url) == "unknown"


# def test_fetch_metadata_hf_model():
#     url = "https://huggingface.co/someuser/somemodel"
#     result = fetch_metadata(url)
#     assert result == {"url": url, "type": "hf_model"}


# def test_fetch_metadata_unknown():
#     url = "https://notarealhost.com/foo"
#     result = fetch_metadata(url)
#     assert result == {"url": url, "type": "unknown"}

def test_get_url_category_models():
    models = {
        0: ['https://github.com/google-research/bert', 'https://huggingface.co/datasets/bookcorpus/bookcorpus', 'https://huggingface.co/google-bert/bert-base-uncased'],
        1: ['', '', 'https://huggingface.co/parvk11/audience_classifier_model'],
        2: ['', '', 'https://huggingface.co/openai/whisper-tiny/tree/main']
    }
    categories = get_url_category(models)
    assert categories == ['MODEL', 'MODEL', 'MODEL']

def test_get_url_category_missing_model_url():
    models = {
        0: ['https://github.com/google-research/bert', 'https://huggingface.co/datasets/bookcorpus/bookcorpus', ''],
        1: ['', '', ''],
    }
    categories = get_url_category(models)
    assert categories == [None, None]

def test_handle_url_returns_ndjsons():
    models = {
        0: ['https://github.com/google-research/bert', 'https://huggingface.co/datasets/bookcorpus/bookcorpus', 'https://huggingface.co/google-bert/bert-base-uncased'],
        1: ['', '', 'https://huggingface.co/parvk11/audience_classifier_model'],
    }
    ndjsons = handle_url(models)
    assert isinstance(ndjsons, dict)
    assert 0 in ndjsons and 1 in ndjsons
    for ndjson in ndjsons.values():
        assert "name" in ndjson
        assert "category" in ndjson
        assert ndjson["category"] == "MODEL"

def test_handle_url_blank_urls_defaults():
    models = {
        0: ['', '', ''],
    }
    ndjsons = handle_url(models)
    assert isinstance(ndjsons, dict)
    assert 0 in ndjsons
    ndjson = ndjsons[0]
    # All scores should be 0 or None as per default_ndjson
    # assert ndjson["net_score"] == 0.0
    assert ndjson["category"] == "MODEL"
