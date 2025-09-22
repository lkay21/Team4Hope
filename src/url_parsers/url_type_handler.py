"""
URL type handler for Model, Dataset, and Code URLs.
Detects the type of a given URL and provides a handler interface.
"""
from typing import Literal, Optional
import re
from src.cli.schema import default_ndjson
from src.metrics.ops_plan import default_ops
from src.metrics.runner import run_metrics

UrlCategory = Literal['MODEL', 'DATASET', 'CODE']

# Patterns for Hugging Face and GitHub
HF_MODEL_PATTERN = re.compile(r"^https://huggingface.co/[^/]+/[^/]+($|/tree/|/blob/|/main|/resolve/)")
HF_DATASET_PATTERN = re.compile(r"^https://huggingface.co/datasets/[^/]+/[^/]+($|/tree/|/blob/|/main|/resolve/)")
GITHUB_CODE_PATTERN = re.compile(r"^https://github.com/[^/]+/[^/]+($|/tree/|/blob/|/main|/commit/|/releases/)")


def get_url_category(models: dict) -> dict:
    """
    Detects the category of a given URL.
    Returns 'MODEL', 'DATASET', or 'CODE', or None if unknown.
    """
    categories = []

    for model in models:
        links = models[model]
        if len(links) > 2 and links[2]:
            categories.append('MODEL')
        else:
            categories.append(None)

    # WILL IT EVER NOT BE A MODEL???
    # Change this function to be seeing what links are missing for further handling downstream
   

        # if model[2] and HF_MODEL_PATTERN.match(model['url']):
        #     categories.append('MODEL')
        # else:
        #     categories.append(None)

        # if HF_MODEL_PATTERN.match(model['url']):
        #     return 'MODEL'
        # if HF_DATASET_PATTERN.match(model['url']):
        #     return 'DATASET'
        # if GITHUB_CODE_PATTERN.match(model['url']):
        #     return 'CODE'
        
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
    ndjsons = {}

    for i, links in models.items():
        code_url, dataset_url, model_url = links[0], links[1], links[2]
        context = {"code_url": code_url, "dataset_url": dataset_url, "model_url": model_url}
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
            "net_score": summary.get("net_score"),
            "net_score_latency": int(summary.get("net_score_latency", 0)),
            "ramp_up_time": get_metric("ramp_up_time"),
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
