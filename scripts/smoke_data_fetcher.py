import json, logging
from src.metrics.data_fetcher import fetch_comprehensive_metrics_data

logging.basicConfig(level=logging.ERROR)

code_url    = "https://github.com/huggingface/transformers"
dataset_url = "https://huggingface.co/datasets/glue"
model_url   = "https://huggingface.co/facebook/bart-base"

data = fetch_comprehensive_metrics_data(code_url, dataset_url, model_url)

# Show the pieces metrics actually use
keys = [
    "availability", "license", "repo_meta", "code_quality",
    "dataset_quality", "ramp", "size_components",
    "requirements_passed", "requirements_total"
]
print(json.dumps({k: data.get(k) for k in keys}, indent=2))