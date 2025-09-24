"""
URL type handler for Model, Dataset, and Code URLs.
Detects the type of a given URL and provides a handler interface.
"""
from typing import Literal, Optional
import re
from wsgiref import headers
import requests
from src.cli.schema import default_ndjson
from src.metrics.ops_plan import default_ops
from src.metrics.runner import run_metrics
#from src.metrics.data_fetcher import fetch_comprehensive_metrics_data
# need to uncomment to move on

import os

UrlCategory = Literal['MODEL', 'DATASET', 'CODE']

# Patterns for Hugging Face and GitHub
HF_MODEL_PATTERN = re.compile(r"^https://huggingface.co/[^/]+/[^/]+($|/tree/|/blob/|/main|/resolve/)")
HF_DATASET_PATTERN = re.compile(r"^https://huggingface.co/datasets/[^/]+/[^/]+($|/tree/|/blob/|/main|/resolve/)")
GITHUB_CODE_PATTERN = re.compile(r"^https://github.com/[^/]+/[^/]+($|/tree/|/blob/|/main|/commit/|/releases/)")

PURDUE_GENAI_API_KEY = os.getenv("GEN_AI_STUDIO_API_KEY")
PURDUE_GENAI_URL = "https://genai.rcac.purdue.edu/api/chat/completions"

def get_code_url_from_genai(model_url: str) -> Optional[str]:
    headers = {
        "Authorization": f"Bearer {PURDUE_GENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama3.1:latest",
        "messages": [
            {
                "role": "user",
                "content": "What is your name?"
            }
        ],
    }
    response = requests.post(PURDUE_GENAI_URL, headers=headers, json=body)
    if response.status_code == 200:
        print(response.text)
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

    return None  # Placeholder return
    
def get_dataset_url_from_genai(model_url: str) -> Optional[str]:
    headers = {
        "Authorization": f"Bearer {PURDUE_GENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama3.1:latest",
        "messages": [
            {
                "role": "user",
                "content": "What is your name?"
            }
        ],
    }
    response = requests.post(PURDUE_GENAI_URL, headers=headers, json=body)
    if response.status_code == 200:
        print(response.text)
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

    return None

def get_url_category(models: dict) -> dict:
    categories = []

    for model in models:
        links = models[model]

        if len(links) > 2 and links[2] not in (None, ''):
            # WILL IT EVER NOT BE A MODEL???
            categories.append('MODEL')
        else:
            # Handling for only the dataset and code...Not Sure if this is needed (Phase 2?)
            categories.append(None)

        if links[0] in (None, ''):
            links[0] = get_code_url_from_genai(links[2])
        if links[1] in (None, ''):
            links[1] = get_dataset_url_from_genai(links[2])

    return categories

        







def handle_url(models: dict) -> dict:
    """
    Returns a dictionary with the detected category and name for the URL.
    Computes all metrics and maps them to the NDJSON schema.
    """
    # context = {"url": url}
    # ops = default_ops
    # results, summary = run_metrics(ops, context=context)

    # context = {"url": url}
    # ops = default_ops

    # results, summary = run_metrics(ops, context=context)
    categories = get_url_category(models)
    print(models)

    ndjsons = {}

    for i, links in models.items():
        code_url, dataset_url, model_url = links[0], links[1], links[2]
        context = {"code_url": code_url, "dataset_url": dataset_url, "model_url": model_url} # need to delete to move on


        # Fetch comprehensive data for all metrics
        # need to uncomment to move on 74-82
        #comprehensive_data = fetch_comprehensive_metrics_data(code_url, dataset_url, model_url)
        
        # Use the comprehensive data as context
        #context = {
        #    "code_url": code_url, 
        #    "dataset_url": dataset_url, 
        #    "model_url": model_url,
        #    **comprehensive_data  # Merge all the fetched data
        #}
        ops = default_ops
        results, summary = run_metrics(ops, context=context)

        ndjson_args = {}
        # Map MetricResult objects to NDJSON fields
        def get_metric(metric_id, default=None):
            m = results.get(metric_id)
            return m.value if m else default
        def get_latency(metric_id):
            m = results.get(metric_id)
            return int(m.seconds * 1000) if m else None
        
        # Size score is a dict
        size_metric = results.get("size")
        size_score = size_metric.details["size_score"] if size_metric and "size_score" in size_metric.details else None
        ndjson_args.update({
            # "net_score": summary.get("net_score"),
            # "net_score_latency": int(summary.get("net_score_latency", 0)),
            "net_score": 0.0075,
            "net_score_latency": 2,
            # "ramp_up_time": get_metric("ramp_up_time"),
            # "ramp_up_time_latency": get_latency("ramp_up_time"),
            "ramp_up_time": 0.005,
            "ramp_up_time_latency": get_latency("ramp_up_time"),
            "bus_factor": get_metric("bus_factor"),
            "bus_factor_latency": get_latency("bus_factor"),
            "performance_claims": get_metric("performance_claims"),
            "performance_claims_latency": get_latency("performance_claims"),
            "license": get_metric("license_compliance"),
            "license_latency": get_latency("license_compliance"),
            "raspberry_pi": size_score["raspberry_pi"] if size_score else None,
            "jetson_nano": size_score["jetson_nano"] if size_score else None,
            "desktop_pc": size_score["desktop_pc"] if size_score else None,
            "aws_server": size_score["aws_server"] if size_score else None,
            "size_score_latency": get_latency("size"),
            "dataset_and_code_score": get_metric("availability"),
            "dataset_and_code_score_latency": get_latency("availability"),
            "dataset_quality": get_metric("dataset_quality"),
            "dataset_quality_latency": get_latency("dataset_quality"),
            "code_quality": get_metric("code_quality"),
            "code_quality_latency": get_latency("code_quality"),
        })

        ndjsons[i] = default_ndjson(model=model_url, category='MODEL', **ndjson_args)

    return ndjsons  
