"""
URL type handler for Model, Dataset, and Code URLs.
Detects the type of a given URL and provides a handler interface.
"""
from typing import Literal, Optional
import re

UrlCategory = Literal['MODEL', 'DATASET', 'CODE']

# Patterns for Hugging Face and GitHub
HF_MODEL_PATTERN = re.compile(r"^https://huggingface.co/[^/]+/[^/]+($|/tree/|/blob/|/main|/resolve/)")
HF_DATASET_PATTERN = re.compile(r"^https://huggingface.co/datasets/[^/]+/[^/]+($|/tree/|/blob/|/main|/resolve/)")
GITHUB_CODE_PATTERN = re.compile(r"^https://github.com/[^/]+/[^/]+($|/tree/|/blob/|/main|/commit/|/releases/)")


def get_url_category(url: str) -> Optional[UrlCategory]:
    """
    Detects the category of a given URL.
    Returns 'MODEL', 'DATASET', or 'CODE', or None if unknown.
    """
    if HF_MODEL_PATTERN.match(url):
        return 'MODEL'
    if HF_DATASET_PATTERN.match(url):
        return 'DATASET'
    if GITHUB_CODE_PATTERN.match(url):
        return 'CODE'
    return None


def handle_url(url: str) -> dict:
    """
    Returns a dictionary with the detected category and name for the URL.
    """
    category = get_url_category(url)
    if category:
        name = url.rstrip('/').split('/')[-1]
    else:
        name = None
    return {
        'url': url,
        'category': category,
        'name': name
    }
