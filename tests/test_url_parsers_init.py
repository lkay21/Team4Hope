"""
Tests for url_parsers module initialization functions.
"""
from src.url_parsers import detect, fetch_metadata
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'src'))


class TestDetect:
    """Test the detect function."""

    def test_detect_hf_dataset(self):
        """Test detection of Hugging Face dataset URLs."""
        url = "https://huggingface.co/datasets/squad"
        assert detect(url) == "hf_dataset"

        url = "https://huggingface.co/datasets/username/dataset-name"
        assert detect(url) == "hf_dataset"

    def test_detect_hf_model(self):
        """Test detection of Hugging Face model URLs."""
        url = "https://huggingface.co/bert-base-uncased"
        assert detect(url) == "hf_model"

        url = "https://huggingface.co/openai/whisper-tiny"
        assert detect(url) == "hf_model"

    def test_detect_github_repo(self):
        """Test detection of GitHub repository URLs."""
        url = "https://github.com/user/repo"
        assert detect(url) == "github_repo"

        url = "https://github.com/google-research/bert"
        assert detect(url) == "github_repo"

    def test_detect_unknown(self):
        """Test detection of unknown URL types."""
        url = "https://example.com"
        assert detect(url) == "unknown"

        url = "https://gitlab.com/user/repo"
        assert detect(url) == "unknown"

        url = ""
        assert detect(url) == "unknown"

    def test_detect_edge_cases(self):
        """Test detection with edge cases."""
        # URL that contains multiple patterns - first match wins
        url = "https://github.com/user/repo-about-huggingface.co/datasets/"
        # datasets comes first in the function
        assert detect(url) == "hf_dataset"

        # Case sensitivity
        url = "https://GITHUB.COM/user/repo"
        assert detect(url) == "unknown"  # Case sensitive


class TestFetchMetadata:
    """Test the fetch_metadata function."""

    def test_fetch_metadata_hf_dataset(self):
        """Test metadata fetching for HF dataset."""
        url = "https://huggingface.co/datasets/squad"
        result = fetch_metadata(url)

        assert result["url"] == url
        assert result["type"] == "hf_dataset"

    def test_fetch_metadata_hf_model(self):
        """Test metadata fetching for HF model."""
        url = "https://huggingface.co/bert-base-uncased"
        result = fetch_metadata(url)

        assert result["url"] == url
        assert result["type"] == "hf_model"

    def test_fetch_metadata_github_repo(self):
        """Test metadata fetching for GitHub repo."""
        url = "https://github.com/user/repo"
        result = fetch_metadata(url)

        assert result["url"] == url
        assert result["type"] == "github_repo"

    def test_fetch_metadata_unknown(self):
        """Test metadata fetching for unknown type."""
        url = "https://example.com"
        result = fetch_metadata(url)

        assert result["url"] == url
        assert result["type"] == "unknown"

    def test_fetch_metadata_empty_url(self):
        """Test metadata fetching for empty URL."""
        url = ""
        result = fetch_metadata(url)

        assert result["url"] == url
        assert result["type"] == "unknown"
