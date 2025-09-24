"""
data_fetcher.py
Comprehensive data fetcher for metrics computation.
Fetches metadata from Hugging Face, GitHub, and other sources.
"""

import requests
import time
import re
import ast
import os
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, unquote
import logging

logger = logging.getLogger(__name__)

def safe_request(url: str, timeout: int = 10, **kwargs) -> Optional[requests.Response]:
    """Make a safe HTTP request with error handling."""
    try:
        response = requests.get(url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response
    except Exception as e:
        logger.warning(f"Request failed for {url}: {e}")
        return None

def extract_repo_info(github_url: str) -> tuple:
    """Extract owner and repo name from GitHub URL."""
    try:
        # Handle various GitHub URL formats
        if "github.com" not in github_url:
            return None, None
        
        path = urlparse(github_url).path.strip('/')
        parts = path.split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
    except Exception:
        pass
    return None, None

def extract_hf_model_id(hf_url: str) -> Optional[str]:
    """Extract model ID from Hugging Face URL."""
    try:
        if "huggingface.co" not in hf_url:
            return None
        
        path = urlparse(hf_url).path.strip('/')
        parts = path.split('/')
        
        # Handle /datasets/owner/name or /owner/name
        if parts[0] == "datasets" and len(parts) >= 3:
            return f"{parts[1]}/{parts[2]}"
        elif len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
    except Exception:
        pass
    return None

def check_availability(code_url: str, dataset_url: str, model_url: str) -> Dict[str, Any]:
    """Check if URLs are accessible and valid."""
    results = {
        "has_code": False,
        "has_dataset": False,
        "has_model": False,
        "links_ok": False
    }
    
    urls = [
        ("code", code_url),
        ("dataset", dataset_url), 
        ("model", model_url)
    ]
    
    accessible_count = 0
    for name, url in urls:
        if url and url.strip():
            try:
                response = requests.head(url, timeout=10, allow_redirects=True)
                is_accessible = response.status_code in [200, 301, 302]
                results[f"has_{name}"] = is_accessible
                if is_accessible:
                    accessible_count += 1
            except Exception as e:
                logger.debug(f"Failed to check {name} URL {url}: {e}")
                results[f"has_{name}"] = False
        else:
            results[f"has_{name}"] = False
    
    results["links_ok"] = accessible_count >= 2  # At least 2 out of 3 should work
    return results

def get_huggingface_model_data(model_url: str) -> Dict[str, Any]:
    """Fetch Hugging Face model metadata."""
    try:
        from huggingface_hub import model_info, HfApi
        
        model_id = extract_hf_model_id(model_url)
        if not model_id:
            return {}
        
        info = model_info(model_id)
        api = HfApi()
        
        # Get basic model info
        data = {
            "license": None,
            "tags": info.tags or [],
            "downloads": getattr(info, 'downloads', 0),
            "pipeline_tag": info.pipeline_tag,
            "model_id": info.modelId,
            "sha": info.sha,
            "card_data": info.cardData or {}
        }
        
        # Extract license
        if info.cardData:
            data["license"] = info.cardData.get("license", "")
        
        # Get file sizes for size metric
        try:
            files = api.list_repo_files(model_id, repo_type="model")
            total_size = 0
            for file_path in files:
                try:
                    file_info = api.get_paths_info(model_id, file_path, repo_type="model")
                    if hasattr(file_info, 'size') and file_info.size:
                        total_size += file_info.size
                except:
                    continue
            data["total_size_bytes"] = total_size
        except:
            data["total_size_bytes"] = 0
            
        return data
        
    except Exception as e:
        logger.warning(f"Failed to fetch HuggingFace model data: {e}")
        return {}

def get_huggingface_dataset_data(dataset_url: str) -> Dict[str, Any]:
    """Fetch Hugging Face dataset metadata."""
    try:
        from huggingface_hub import dataset_info
        from datasets import load_dataset_builder
        
        dataset_id = extract_hf_model_id(dataset_url)
        if not dataset_id:
            return {}
        
        info = dataset_info(dataset_id)
        data = {
            "license": None,
            "card_data": info.cardData or {},
            "tags": info.tags or [],
            "downloads": getattr(info, 'downloads', 0)
        }
        
        # Extract license
        if info.cardData:
            data["license"] = info.cardData.get("license", "")
        
        # Try to get dataset structure info
        try:
            builder = load_dataset_builder(dataset_id)
            data["features"] = str(builder.info.features) if builder.info.features else ""
            data["splits"] = list(builder.info.splits.keys()) if builder.info.splits else []
            data["description"] = builder.info.description or ""
        except Exception as e:
            logger.debug(f"Could not load dataset builder: {e}")
            data["features"] = ""
            data["splits"] = []
            data["description"] = ""
            
        return data
        
    except Exception as e:
        logger.warning(f"Failed to fetch HuggingFace dataset data: {e}")
        return {}

def get_github_repo_data(code_url: str) -> Dict[str, Any]:
    """Fetch GitHub repository metadata."""
    owner, repo = extract_repo_info(code_url)
    if not owner or not repo:
        return {}
    
    # Get GitHub token if available
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    data = {
        "contributors": {},
        "files": [],
        "license": None,
        "stars": 0,
        "forks": 0,
        "created_at": None,
        "updated_at": None
    }
    
    try:
        # Get repository info
        repo_response = safe_request(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers
        )
        if repo_response:
            repo_data = repo_response.json()
            data.update({
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
                "license": repo_data.get("license", {}).get("spdx_id") if repo_data.get("license") else None
            })
        
        # Get contributors for bus factor
        contributors_response = safe_request(
            f"https://api.github.com/repos/{owner}/{repo}/contributors",
            headers=headers
        )
        if contributors_response:
            contributors_data = contributors_response.json()
            if contributors_data and isinstance(contributors_data, list):
                total_contributions = sum(c.get("contributions", 0) for c in contributors_data)
                if total_contributions > 0:
                    top_contributor_contributions = contributors_data[0].get("contributions", 0)
                    data["contributors"] = {
                        "contributors_count": len(contributors_data),
                        "top_contributor_pct": top_contributor_contributions / total_contributions,
                        "total_contributions": total_contributions
                    }
        
        # Get file tree for code analysis
        tree_response = safe_request(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1",
            headers=headers
        )
        if not tree_response:
            # Try 'master' branch
            tree_response = safe_request(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1",
                headers=headers
            )
        
        if tree_response:
            tree_data = tree_response.json()
            if "tree" in tree_data:
                data["files"] = [
                    item["path"] for item in tree_data["tree"] 
                    if item["type"] == "blob"
                ]
        
    except Exception as e:
        logger.warning(f"Failed to fetch GitHub data: {e}")
    
    return data

def analyze_code_quality(files: List[str]) -> Dict[str, float]:
    """Analyze code quality metrics from file list."""
    if not files:
        return {
            "test_coverage_norm": 0.0,
            "style_norm": 0.5,  # neutral default
            "comment_ratio_norm": 0.0,
            "maintainability_norm": 0.5
        }
    
    python_files = [f for f in files if f.endswith('.py')]
    test_files = [f for f in files if 'test' in f.lower() and f.endswith('.py')]
    
    # Simple heuristics
    test_coverage_norm = min(1.0, len(test_files) / max(1, len(python_files) * 0.3))
    
    # Check for common quality indicators
    has_requirements = any('requirements' in f for f in files)
    has_readme = any(f.lower().startswith('readme') for f in files)
    has_setup = any(f in ['setup.py', 'pyproject.toml', 'setup.cfg'] for f in files)
    
    quality_indicators = sum([has_requirements, has_readme, has_setup])
    maintainability_norm = quality_indicators / 3.0
    
    return {
        "test_coverage_norm": test_coverage_norm,
        "style_norm": 0.5,  # Would need actual code analysis
        "comment_ratio_norm": 0.5,  # Would need actual code analysis  
        "maintainability_norm": maintainability_norm
    }

def normalize_downloads(downloads: int) -> float:
    """Normalize download count to 0-1 scale."""
    if downloads <= 0:
        return 0.0
    elif downloads >= 1000000:  # 1M+ downloads = 1.0
        return 1.0
    else:
        # Log scale for downloads
        import math
        return min(1.0, math.log10(downloads) / 6.0)  # log10(1M) = 6

def normalize_stars(stars: int) -> float:
    """Normalize GitHub stars to 0-1 scale."""
    if stars <= 0:
        return 0.0
    elif stars >= 10000:  # 10k+ stars = 1.0
        return 1.0
    else:
        import math
        return min(1.0, math.log10(stars) / 4.0)  # log10(10k) = 4

def compute_size_scores(total_size_bytes: int) -> Dict[str, float]:
    """Compute hardware-specific size scores."""
    if total_size_bytes <= 0:
        return {
            "raspberry_pi": 0.01,
            "jetson_nano": 0.01, 
            "desktop_pc": 0.01,
            "aws_server": 0.01
        }
    
    # Size thresholds in bytes (these are rough estimates)
    mb = 1024 * 1024
    gb = 1024 * mb
    
    # Raspberry Pi: very limited (prefer < 100MB)
    rpi_score = max(0.01, min(1.0, 1.0 - (total_size_bytes / (100 * mb))))
    
    # Jetson Nano: limited (prefer < 1GB) 
    jetson_score = max(0.01, min(1.0, 1.0 - (total_size_bytes / (1 * gb))))
    
    # Desktop PC: moderate (prefer < 10GB)
    desktop_score = max(0.01, min(1.0, 1.0 - (total_size_bytes / (10 * gb))))
    
    # AWS Server: high capacity (prefer < 100GB)
    aws_score = max(0.01, min(1.0, 1.0 - (total_size_bytes / (100 * gb))))
    
    return {
        "raspberry_pi": rpi_score,
        "jetson_nano": jetson_score,
        "desktop_pc": desktop_score, 
        "aws_server": aws_score
    }

def fetch_comprehensive_metrics_data(code_url: str, dataset_url: str, model_url: str) -> Dict[str, Any]:
    """
    Fetch all necessary data for metrics computation from various sources.
    
    Args:
        code_url: GitHub repository URL
        dataset_url: Hugging Face dataset URL  
        model_url: Hugging Face model URL
        
    Returns:
        Dictionary containing all metric computation data
    """
    
    data = {
        "availability": {},
        "license": None,
        "repo_meta": {},
        "code_quality": {},
        "dataset_quality": {},
        "ramp": {},
        "size_components": {},
        "requirements_passed": 0,
        "requirements_total": 1,
        "compatible_licenses": ["mit", "apache-2.0", "bsd-3-clause", "bsd", "mpl-2.0"]
    }
    
    try:
        # Check URL availability first
        data["availability"] = check_availability(code_url, dataset_url, model_url)
        
        # Fetch Hugging Face model data
        if model_url and "huggingface.co" in model_url and "/datasets/" not in model_url:
            logger.info(f"Fetching HuggingFace model data from {model_url}")
            hf_model_data = get_huggingface_model_data(model_url)
            
            if hf_model_data:
                # License information
                data["license"] = hf_model_data.get("license", "")
                
                # Ramp up time components
                downloads = hf_model_data.get("downloads", 0)
                data["ramp"]["downloads_norm"] = normalize_downloads(downloads)
                data["ramp"]["likes_norm"] = 0.5  # HF doesn't expose likes directly
                
                # Recency based on recent activity (simplified)
                data["ramp"]["recency_norm"] = 0.7  # Default to fairly recent
                
                # Size components
                total_size = hf_model_data.get("total_size_bytes", 0)
                data["size_components"] = compute_size_scores(total_size)
                
                # Performance claims from model card
                card_data = hf_model_data.get("card_data", {})
                if card_data and "model-index" in card_data:
                    data["requirements_passed"] = 1
                    data["requirements_total"] = 1
                else:
                    data["requirements_passed"] = 0
        
        # Fetch Hugging Face dataset data
        if dataset_url and "huggingface.co/datasets" in dataset_url:
            logger.info(f"Fetching HuggingFace dataset data from {dataset_url}")
            hf_dataset_data = get_huggingface_dataset_data(dataset_url)
            
            if hf_dataset_data:
                # Dataset quality components
                card_data = hf_dataset_data.get("card_data", {})
                has_description = bool(hf_dataset_data.get("description", "").strip())
                has_features = bool(hf_dataset_data.get("features", "").strip())
                has_splits = len(hf_dataset_data.get("splits", [])) > 0
                
                data["dataset_quality"] = {
                    "cleanliness": 0.8 if has_features else 0.3,  # Heuristic
                    "documentation": 0.9 if has_description else 0.2,
                    "class_balance": 0.7 if has_splits else 0.3  # Heuristic
                }
                
                # Update license if not set from model
                if not data["license"] and hf_dataset_data.get("license"):
                    data["license"] = hf_dataset_data["license"]
        
        # Fetch GitHub repository data
        if code_url and "github.com" in code_url:
            logger.info(f"Fetching GitHub repository data from {code_url}")
            github_data = get_github_repo_data(code_url)
            
            if github_data:
                # Repository metadata for bus factor
                data["repo_meta"] = github_data.get("contributors", {})
                
                # Code quality analysis
                files = github_data.get("files", [])
                data["code_quality"] = analyze_code_quality(files)
                
                # Ramp up time - add GitHub popularity signals
                stars = github_data.get("stars", 0)
                if "likes_norm" not in data["ramp"]:
                    data["ramp"]["likes_norm"] = normalize_stars(stars)
                
                # Update license if not set
                if not data["license"] and github_data.get("license"):
                    data["license"] = github_data["license"]
                
                # Enhanced recency from GitHub activity
                updated_at = github_data.get("updated_at")
                if updated_at:
                    try:
                        from datetime import datetime, timezone
                        updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        now = datetime.now(timezone.utc)
                        days_old = (now - updated).days
                        # More recent = higher score
                        data["ramp"]["recency_norm"] = max(0.1, min(1.0, 1.0 - (days_old / 365.0)))
                    except:
                        pass
        
        # Fill in defaults for missing components
        if not data["ramp"].get("downloads_norm"):
            data["ramp"]["downloads_norm"] = 0.1
        if not data["ramp"].get("likes_norm"):
            data["ramp"]["likes_norm"] = 0.1  
        if not data["ramp"].get("recency_norm"):
            data["ramp"]["recency_norm"] = 0.5
            
        if not data["code_quality"]:
            data["code_quality"] = analyze_code_quality([])
            
        if not data["dataset_quality"]:
            data["dataset_quality"] = {
                "cleanliness": 0.5,
                "documentation": 0.3,
                "class_balance": 0.5
            }
            
        if not data["size_components"]:
            data["size_components"] = compute_size_scores(0)
            
        logger.info("Successfully fetched comprehensive metrics data")
        return data
        
    except Exception as e:
        logger.error(f"Error fetching comprehensive metrics data: {e}")
        # Return defaults on error
        return {
            "availability": {"has_code": False, "has_dataset": False, "has_model": False, "links_ok": False},
            "license": "",
            "repo_meta": {"contributors_count": 1, "top_contributor_pct": 1.0},
            "code_quality": {"test_coverage_norm": 0.0, "style_norm": 0.5, "comment_ratio_norm": 0.0, "maintainability_norm": 0.5},
            "dataset_quality": {"cleanliness": 0.5, "documentation": 0.3, "class_balance": 0.5},
            "ramp": {"likes_norm": 0.1, "downloads_norm": 0.1, "recency_norm": 0.5},
            "size_components": {"raspberry_pi": 0.01, "jetson_nano": 0.01, "desktop_pc": 0.01, "aws_server": 0.01},
            "requirements_passed": 0,
            "requirements_total": 1,
            "compatible_licenses": ["mit", "apache-2.0", "bsd-3-clause", "bsd", "mpl-2.0"]
        }