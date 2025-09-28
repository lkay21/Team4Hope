"""Data fetcher package.

This package contains a refactored implementation of the former
`src.metrics.data_fetcher` module. The package re-exports the original
public functions and names so existing imports continue to work.
"""
"""Data fetcher package.

This package contains a refactored implementation of the former
`src.metrics.data_fetcher` module. The package re-exports the original
public functions and names so existing imports continue to work.

We import the helper modules first and set the package-level names, then
import the aggregator. This ordering ensures tests that patch
`src.metrics.data_fetcher.<name>` will affect the functions used by the
aggregator (avoids stale local references inside the aggregator module).
"""

# import helpers and expose them at package level

from .aggregator import fetch_comprehensive_metrics_data
from . import utils as _utils
from . import huggingface as _huggingface
from . import github as _github
from . import heuristics as _heuristics
from . import llm as _llm
safe_request = _utils.safe_request
extract_repo_info = _utils.extract_repo_info
extract_hf_model_id = _utils.extract_hf_model_id
check_availability = _utils.check_availability

get_huggingface_model_data = _huggingface.get_huggingface_model_data
get_huggingface_dataset_data = _huggingface.get_huggingface_dataset_data

get_github_repo_data = _github.get_github_repo_data

analyze_code_quality = _heuristics.analyze_code_quality
normalize_downloads = _heuristics.normalize_downloads
normalize_stars = _heuristics.normalize_stars
compute_size_scores = _heuristics.compute_size_scores
analyze_performance_claims = _heuristics.analyze_performance_claims
get_genai_metric_data = _llm.get_genai_metric_data

# now import the aggregator which will import helpers from the package
# namespace

__all__ = [
    "safe_request",
    "extract_repo_info",
    "extract_hf_model_id",
    "check_availability",
    "get_huggingface_model_data",
    "get_huggingface_dataset_data",
    "get_github_repo_data",
    "analyze_code_quality",
    "normalize_downloads",
    "normalize_stars",
    "compute_size_scores",
    "analyze_performance_claims",
    "get_genai_metric_data",
    "fetch_comprehensive_metrics_data",
]
