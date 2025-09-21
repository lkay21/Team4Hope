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
    Computes all metrics and maps them to the NDJSON schema.
    """
    context = {"url": url}
    ops = default_ops
    results, summary = run_metrics(ops, context=context)

    # context = {"url": url}
    # ops = default_ops

    # results, summary = run_metrics(ops, context=context)

    category = get_url_category(url)
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
    if category:
        return default_ndjson(url=url, category=category, **ndjson_args)
    else:
        return default_ndjson(url=url)

