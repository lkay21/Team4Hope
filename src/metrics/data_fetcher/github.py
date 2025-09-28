"""GitHub helpers for repository metadata."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict

from .utils import safe_request, extract_repo_info
from src.logger import get_logger

logger = get_logger("data_fetcher.github")


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
        repo_resp = safe_request(
            f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
        if repo_resp:
            rd = repo_resp.json()
            data.update({
                "stars": rd.get("stargazers_count", 0) or 0,
                "forks": rd.get("forks_count", 0) or 0,
                "created_at": rd.get("created_at"),
                "updated_at": rd.get("updated_at"),
                "license": (rd.get("license") or {}).get("spdx_id") if rd.get("license") else None,
            })

        contrib_resp = safe_request(
            f"https://api.github.com/repos/{owner}/{repo}/contributors",
            headers=headers)
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
                data["files"] = [it["path"]
                                 for it in tree if it.get("type") == "blob"]
                break
    except Exception as e:
        logger.debug(f"Failed to fetch GitHub data: {e}")

    return data
