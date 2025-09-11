from typing import Dict

def detect(url: str) -> str:
    if "huggingface.co/datasets/" in url:
        return "hf_dataset"
    if "huggingface.co/" in url:
        return "hf_model"
    if "github.com/" in url:
        return "github_repo"
    return "unknown"

def fetch_metadata(url: str) -> Dict:
    # TODO: implement per-type, with caching + backoff for rate limits
    return {"url": url, "type": detect(url)}
