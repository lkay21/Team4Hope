"""
Comprehensive data fetcher for metrics computation.
- Uses Hugging Face Hub API for model/dataset metadata
- Uses GitHub REST for repo metadata
- Performs simple local heuristics (file list, size scoring)
- Returns a single dict with everything metrics need
"""
from __future__ import annotations

import logging
import math
import os
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)
# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------

def safe_request(url: str, timeout: int = 10, **kwargs) -> Optional[requests.Response]:
    """Make a safe HTTP GET request with error handling."""
    try:
        resp = requests.get(url, timeout=timeout, **kwargs)
        resp.raise_for_status()
        return resp
    except Exception as e:
        logger.debug(f"Request failed for {url}: {e}")
        return None


def extract_repo_info(github_url: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract (owner, repo) from a GitHub URL."""
    try:
        if "github.com" not in github_url:
            return None, None
        path = urlparse(github_url).path.strip("/")
        parts = path.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
    except Exception:
        pass
    return None, None


def extract_hf_model_id(hf_url: str) -> Optional[str]:
    """Extract the canonical repo_id for HF (model or dataset)."""
    try:
        if "huggingface.co" not in hf_url:
            return None

        path = urlparse(hf_url).path.strip("/")
        parts = path.split("/")

        # datasets/<id>  OR  datasets/<owner>/<name>
        if parts and parts[0] == "datasets":
            if len(parts) == 2:
                # e.g., https://huggingface.co/datasets/glue  -> "glue"
                return parts[1]
            elif len(parts) >= 3:
                # e.g., https://huggingface.co/datasets/user/name -> "user/name"
                return f"{parts[1]}/{parts[2]}"

        # model URLs are <owner>/<name> (e.g., facebook/bart-base)
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    except Exception:
        pass
    return None


def check_availability(code_url: str, dataset_url: str, model_url: str) -> Dict[str, Any]:
    """HEAD the URLs and report availability of each and overall links_ok."""
    results = {"has_code": False, "has_dataset": False, "has_model": False, "links_ok": False}
    urls = [("code", code_url), ("dataset", dataset_url), ("model", model_url)]
    ok = 0
    for name, url in urls:
        if url and url.strip():
            try:
                r = requests.head(url, timeout=10, allow_redirects=True)
                good = r.status_code in (200, 301, 302)
                results[f"has_{name}"] = good
                ok += int(good)
            except Exception as e:
                logger.debug(f"Failed to check {name} URL {url}: {e}")
                results[f"has_{name}"] = False
        else:
            results[f"has_{name}"] = False
    results["links_ok"] = ok >= 2
    return results

# ---------------------------------------------------------------------
# Hugging Face
# ---------------------------------------------------------------------

def get_huggingface_model_data(model_url: str) -> Dict[str, Any]:
    """Fetch HF model metadata via the Hub API."""
    try:
        from huggingface_hub import HfApi, model_info

        model_id = extract_hf_model_id(model_url)
        if not model_id:
            return {}

        info = model_info(model_id)
        api = HfApi()

        data: Dict[str, Any] = {
            "license": None,
            "tags": getattr(info, "tags", []) or [],
            "downloads": getattr(info, "downloads", 0) or 0,
            "pipeline_tag": getattr(info, "pipeline_tag", None),
            "model_id": getattr(info, "modelId", model_id),
            "sha": getattr(info, "sha", None),
            "card_data": getattr(info, "cardData", {}) or {},
        }
        if data["card_data"]:
            data["license"] = data["card_data"].get("license", "")

        # total size (best-effort)
        total_size = 0
        try:
            files = api.list_repo_files(model_id, repo_type="model")
            for fp in files:
                try:
                    fi = api.get_paths_info(model_id, fp, repo_type="model")
                    size = getattr(fi, "size", None)
                    if size:
                        total_size += int(size)
                except Exception:
                    continue
        except Exception:
            pass
        data["total_size_bytes"] = total_size
        return data
    except Exception as e:
        logger.debug(f"Failed to fetch HF model data: {e}")
        return {}


def get_huggingface_dataset_data(dataset_url: str) -> Dict[str, Any]:
    """Fetch HF dataset metadata via the Hub + datasets library (best-effort)."""
    try:
        from huggingface_hub import dataset_info
        from datasets import load_dataset_builder

        dataset_id = extract_hf_model_id(dataset_url)
        if not dataset_id:
            return {}

        info = dataset_info(dataset_id)
        data: Dict[str, Any] = {
            "license": None,
            "card_data": getattr(info, "cardData", {}) or {},
            "tags": getattr(info, "tags", []) or [],
            "downloads": getattr(info, "downloads", 0) or 0,
        }
        if data["card_data"]:
            data["license"] = data["card_data"].get("license", "")

        try:
            builder = load_dataset_builder(dataset_id)
            data["features"] = str(getattr(builder.info, "features", "") or "")
            data["splits"] = list(getattr(builder.info, "splits", {}).keys()) if getattr(builder.info, "splits", None) else []
            data["description"] = getattr(builder.info, "description", "") or ""
        except Exception as e:
            logger.debug(f"Could not load dataset builder: {e}")
            data["features"], data["splits"], data["description"] = "", [], ""
        return data
    except Exception as e:
        logger.debug(f"Failed to fetch HF dataset data: {e}")
        return {}

# ---------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------

def get_github_repo_data(code_url: str) -> Dict[str, Any]:
    """Fetch GitHub repository metadata used by metrics (bus factor, etc.)."""
    owner, repo = extract_repo_info(code_url)
    if not owner or not repo:
        return {}

    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    data: Dict[str, Any] = {
        "contributors": {},
        "files": [],
        "license": None,
        "stars": 0,
        "forks": 0,
        "created_at": None,
        "updated_at": None,
    }

    try:
        repo_resp = safe_request(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
        if repo_resp:
            rd = repo_resp.json()
            data.update({
                "stars": rd.get("stargazers_count", 0) or 0,
                "forks": rd.get("forks_count", 0) or 0,
                "created_at": rd.get("created_at"),
                "updated_at": rd.get("updated_at"),
                "license": (rd.get("license") or {}).get("spdx_id") if rd.get("license") else None,
            })

        contrib_resp = safe_request(f"https://api.github.com/repos/{owner}/{repo}/contributors", headers=headers)
        if contrib_resp:
            lst = contrib_resp.json()
            if isinstance(lst, list) and lst:
                total = sum(c.get("contributions", 0) for c in lst)
                top = lst[0].get("contributions", 0) if total else 0
                data["contributors"] = {
                    "contributors_count": len(lst),
                    "top_contributor_pct": (top / total) if total else 1.0,
                    "total_contributions": total,
                }

        # try main then master
        for branch in ("main", "master"):
            tree_resp = safe_request(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1",
                headers=headers,
            )
            if tree_resp and tree_resp.ok:
                tree = tree_resp.json().get("tree", [])
                data["files"] = [it["path"] for it in tree if it.get("type") == "blob"]
                break
    except Exception as e:
        logger.debug(f"Failed to fetch GitHub data: {e}")

    return data

# ---------------------------------------------------------------------
# Local/code heuristics & normalizers
# ---------------------------------------------------------------------

def analyze_code_quality(files: List[str]) -> Dict[str, float]:
    """Lightweight heuristics based on file list."""
    if not files:
        return {
            "test_coverage_norm": 0.0,
            "style_norm": 0.5,
            "comment_ratio_norm": 0.5,
            "maintainability_norm": 0.5,
        }
    py = [f for f in files if f.endswith(".py")]
    tests = [f for f in files if f.endswith(".py") and "test" in f.lower()]
    test_coverage_norm = min(1.0, len(tests) / max(1, len(py) * 0.3))
    has_requirements = any("requirements" in f.lower() for f in files)
    has_readme = any(os.path.basename(f).lower().startswith("readme") for f in files)
    has_setup = any(f in {"setup.py", "pyproject.toml", "setup.cfg"} for f in files)
    maintainability_norm = (int(has_requirements) + int(has_readme) + int(has_setup)) / 3.0
    return {
        "test_coverage_norm": test_coverage_norm,
        "style_norm": 0.5,
        "comment_ratio_norm": 0.5,
        "maintainability_norm": maintainability_norm,
    }


def normalize_downloads(downloads: int) -> float:
    if downloads <= 0:
        return 0.0
    return min(1.0, math.log10(max(downloads, 1)) / 6.0)  # 1e6 -> 1.0


def normalize_stars(stars: int) -> float:
    if stars <= 0:
        return 0.0
    return min(1.0, math.log10(max(stars, 1)) / 4.0)  # 1e4 -> 1.0


def compute_size_scores(total_size_bytes: int) -> Dict[str, float]:
    if total_size_bytes <= 0:
        return {"raspberry_pi": 0.01, "jetson_nano": 0.01, "desktop_pc": 0.01, "aws_server": 0.01}
    mb = 1024 * 1024
    gb = 1024 * mb
    rpi = max(0.01, min(1.0, 1.0 - (total_size_bytes / (100 * mb))))
    jetson = max(0.01, min(1.0, 1.0 - (total_size_bytes / (1 * gb))))
    desktop = max(0.01, min(1.0, 1.0 - (total_size_bytes / (10 * gb))))
    aws = max(0.01, min(1.0, 1.0 - (total_size_bytes / (100 * gb))))
    return {"raspberry_pi": rpi, "jetson_nano": jetson, "desktop_pc": desktop, "aws_server": aws}

# ---------------------------------------------------------------------
# Main aggregator
# ---------------------------------------------------------------------

def fetch_comprehensive_metrics_data(code_url: str, dataset_url: str, model_url: str) -> Dict[str, Any]:
    """
    Fetch and compute all data required by metrics.

    Returns a dict with keys used by metric implementations, including:
    availability, license, repo_meta, code_quality, dataset_quality,
    ramp (downloads/likes/recency), size_components, requirements_* and
    compatible_licenses.
    """
    data: Dict[str, Any] = {
        "availability": {},
        "license": None,
        "repo_meta": {},
        "code_quality": {},
        "dataset_quality": {},
        "ramp": {},
        "size_components": {},
        "requirements_passed": 0,
        "requirements_total": 1,
        "compatible_licenses": ["mit", "apache-2.0", "bsd-3-clause", "bsd", "mpl-2.0"],
    }

    try:
        # availability
        data["availability"] = check_availability(code_url, dataset_url, model_url)

        # HF model
        if model_url and "huggingface.co" in model_url and "/datasets/" not in model_url:
            logger.info(f"Fetching HF model data from {model_url}")
            hf_m = get_huggingface_model_data(model_url)
            if hf_m:
                if hf_m.get("license"):
                    data["license"] = hf_m.get("license")
                downloads = int(hf_m.get("downloads", 0) or 0)
                data.setdefault("ramp", {})
                data["ramp"]["downloads_norm"] = normalize_downloads(downloads)
                data["ramp"]["likes_norm"] = 0.5  # HF likes not exposed consistently
                data["ramp"]["recency_norm"] = 0.7  # default; refined by GitHub below
                total_size = int(hf_m.get("total_size_bytes", 0) or 0)
                data["size_components"] = compute_size_scores(total_size)
                card_data = hf_m.get("card_data", {}) or {}
                if "model-index" in card_data:
                    data["requirements_passed"], data["requirements_total"] = 1, 1

        # HF dataset
        if dataset_url and "huggingface.co/datasets" in dataset_url:
            logger.info(f"Fetching HF dataset data from {dataset_url}")
            hf_d = get_huggingface_dataset_data(dataset_url)
            if hf_d:
                desc = (hf_d.get("description") or "").strip()
                features = (hf_d.get("features") or "").strip()
                splits = hf_d.get("splits", []) or []
                data["dataset_quality"] = {
                    "cleanliness": 0.8 if features else 0.3,
                    "documentation": 0.9 if desc else 0.2,
                    "class_balance": 0.7 if splits else 0.3,
                }
                if not data.get("license") and hf_d.get("license"):
                    data["license"] = hf_d["license"]

        # GitHub repo
        if code_url and "github.com" in code_url:
            logger.info(f"Fetching GitHub data from {code_url}")
            gh = get_github_repo_data(code_url)
            if gh:
                data["repo_meta"] = gh.get("contributors", {})
                files = gh.get("files", [])
                data["code_quality"] = analyze_code_quality(files)
                stars = int(gh.get("stars", 0) or 0)
                data.setdefault("ramp", {})
                data["ramp"].setdefault("likes_norm", normalize_stars(stars))
                if not data.get("license") and gh.get("license"):
                    data["license"] = gh["license"]
                # recency from updated_at
                try:
                    from datetime import datetime, timezone
                    updated = gh.get("updated_at")
                    if updated:
                        dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                        days = (datetime.now(timezone.utc) - dt).days
                        data["ramp"]["recency_norm"] = max(0.1, min(1.0, 1.0 - (days / 365.0)))
                except Exception:
                    pass

        # fill defaults
        r = data.setdefault("ramp", {})
        r.setdefault("downloads_norm", 0.1)
        r.setdefault("likes_norm", 0.1)
        r.setdefault("recency_norm", 0.5)
        if not data.get("code_quality"):
            data["code_quality"] = analyze_code_quality([])
        if not data.get("dataset_quality"):
            data["dataset_quality"] = {"cleanliness": 0.5, "documentation": 0.3, "class_balance": 0.5}
        if not data.get("size_components"):
            data["size_components"] = compute_size_scores(0)

        logger.info("Successfully fetched comprehensive metrics data")
        return data
    except Exception as e:
        logger.error(f"Error fetching comprehensive metrics data: {e}")
        return {
            "availability": {"has_code": False, "has_dataset": False, "has_model": False, "links_ok": False},
            "license": "",
            "repo_meta": {"contributors_count": 1, "top_contributor_pct": 1.0},
            "code_quality": {"test_coverage_norm": 0.0, "style_norm": 0.5, "comment_ratio_norm": 0.5, "maintainability_norm": 0.5},
            "dataset_quality": {"cleanliness": 0.5, "documentation": 0.3, "class_balance": 0.5},
            "ramp": {"likes_norm": 0.1, "downloads_norm": 0.1, "recency_norm": 0.5},
            "size_components": {"raspberry_pi": 0.01, "jetson_nano": 0.01, "desktop_pc": 0.01, "aws_server": 0.01},
            "requirements_passed": 0,
            "requirements_total": 1,
            "compatible_licenses": ["mit", "apache-2.0", "bsd-3-clause", "bsd", "mpl-2.0"],
        }
