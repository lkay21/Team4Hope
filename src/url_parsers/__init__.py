from typing import Dict
from .url_type_handler import get_url_category, handle_url


def detect(url: str) -> str:
    if "huggingface.co/datasets/" in url:
        return "hf_dataset"
    if "huggingface.co/" in url:
        return "hf_model"
    if "github.com/" in url:
        return "github_repo"
    return "unknown"


def fetch_metadata(url: str) -> Dict:
    # Implement function
    return {"url": url, "type": detect(url)}
