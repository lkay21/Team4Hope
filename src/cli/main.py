import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import argparse
import json
from typing import Any, Dict, List
from src.url_parsers.url_type_handler import (
    extract_links,
    handle_url,
)
from src.cli.schema import default_ndjson

<<<<<<< HEAD
=======
# def _warn_invalid_github_token() -> None:
#     """Warn to stderr (only) if GITHUB_TOKEN clearly isn't a real token."""
#     tok = os.getenv("GITHUB_TOKEN")
#     if not tok:
#         return
#     # Real GitHub tokens commonly start with ghp_ or github_pat_
#     looks_valid = tok.startswith("ghp_") or tok.startswith("github_pat_")
#     if not looks_valid:
#         print("WARNING: Invalid GitHub token; continuing unauthenticated.", file=sys.stderr)

def _warn_invalid_github_token_once() -> None:
    """
    Warn exactly once, to stderr only, if GITHUB_TOKEN is clearly invalid.
    """
    # Prevent double-prints if this is called more than once
    if os.environ.get("_BAD_GH_TOKEN_WARNED") == "1":
        return

    tok = os.getenv("GITHUB_TOKEN")
    if tok:
        # Real tokens commonly start with ghp_ or github_pat_
        looks_valid = tok.startswith("ghp_") or tok.startswith("github_pat_")
        if not looks_valid:
            print("WARNING: Invalid GitHub token; continuing unauthenticated.", file=sys.stderr)
    os.environ["_BAD_GH_TOKEN_WARNED"] = "1"


>>>>>>> origin/main

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CLI for trustworthy model re-use")
    p.add_argument(
        "args", nargs="*",
        help="Commands (install, test) or URLs to evaluate (HF model/dataset or GitHub repo)"
    )
    p.add_argument(
        "--ndjson", action="store_true",
        help="Emit NDJSON records to stdout"
    )
    p.add_argument(
        "-v", "--verbosity", type=int,
        default=int(os.getenv("LOG_VERBOSITY", "0")),
        help="Log verbosity (default from env LOG_VERBOSITY, default 0)"
    )
    return p.parse_args()


def _placeholder(url_or_label: str, category: str) -> Dict[str, Any]:
    """
    Produce a valid NDJSON-shaped placeholder record for the given category.
    Ensures all required fields exist and validate.
    """
    rec = default_ndjson(url_or_label)
    # default_ndjson already sets all score/latency fields; we only force name/category
    rec["name"] = url_or_label.rstrip("/").split("/")[-1] if url_or_label else None
    rec["category"] = category
    return rec


def _pick_primary(dataset_rec: Dict[str, Any] | None,
                  code_rec: Dict[str, Any] | None,
                  model_rec: Dict[str, Any] | None,
                  fallbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Choose which record's NDJSON fields should be promoted to the top level.
    Preference: MODEL > DATASET > CODE > first available fallback.
    """
    if model_rec:   return model_rec
    if dataset_rec: return dataset_rec
    if code_rec:    return code_rec
    return fallbacks[0] if fallbacks else _placeholder("input", "MODEL")


def evaluate_url(u: str) -> Dict[str, Any]:
    """
    Evaluate an input string that may contain 0–3 URLs.
    Returns a single dict that:
      - has all top-level NDJSON fields (flat) from the chosen 'primary' link
      - and also contains nested 'dataset', 'code', 'model' sections (each valid NDJSON)
    """
    links = extract_links(u)

    # Score each discovered link
    scored: List[Dict[str, Any]] = [handle_url(link) for link in links]

    # Slot scored links by their detected category
    dataset_rec = next((r for r in scored if r.get("category") == "DATASET"), None)
    code_rec    = next((r for r in scored if r.get("category") == "CODE"), None)
    model_rec   = next((r for r in scored if r.get("category") == "MODEL"), None)

    # Build valid placeholders for any missing roles
    dataset = dataset_rec or _placeholder(u, "DATASET")
    code    = code_rec    or _placeholder(u, "CODE")
    model   = model_rec   or _placeholder(u, "MODEL")

    # Pick the primary record whose NDJSON fields get promoted to the top level
    primary = _pick_primary(dataset_rec, code_rec, model_rec, scored)

    # Start with a clone of the primary NDJSON (flat fields present)
    record = dict(primary)

    # Ensure top-level name/category are set (tests assert on name)
    record["name"] = primary.get("name") or (links[0].rstrip("/").split("/")[-1] if links else u.rstrip("/").split("/")[-1])
    record["category"] = primary.get("category") or "MODEL"

    # Attach nested sections (each is an independently valid NDJSON-shaped dict)
    record["dataset"] = dataset
    record["code"] = code
    record["model"] = model

    return record


def validate_ndjson(record: Dict[str, Any]) -> bool:
    """
    Validate a *flat* NDJSON record (the same schema produced by default_ndjson/handle_url).
    This is used by unit tests on the top-level record we emit.
    """
    string_fields = {"name", "category"}
    score_fields = {
        "net_score", "ramp_up_time", "bus_factor", "performance_claims", "license",
        "size_score", "dataset_and_code_score", "dataset_quality", "code_quality"
    }
    latency_fields = {
        "net_score_latency", "ramp_up_time_latency", "bus_factor_latency",
        "performance_claims_latency", "license_latency", "size_score_latency",
        "dataset_and_code_score_latency", "dataset_quality_latency", "code_quality_latency"
    }

    if not isinstance(record, dict):
        return False
    if not score_fields.issubset(record.keys()) \
       or not latency_fields.issubset(record.keys()) \
       or not string_fields.issubset(record.keys()):
        return False

    for string in string_fields:
        if not isinstance(record[string], (str, type(None))):
            return False

    for score in score_fields:
        score_metric = record[score]
        if isinstance(score_metric, dict):
            for v in score_metric.values():
                if v is not None and (not isinstance(v, float) or not (0.0 <= v <= 1.0)):
                    return False
        else:
            if score_metric is not None:
                if not isinstance(score_metric, float) or not (0.0 <= score_metric <= 1.0):
                    return False

    for latency in latency_fields:
        latency_metric = record[latency]
        if latency_metric is not None:
            if not isinstance(latency_metric, int) or latency_metric < 0:
                return False

    return True


def main() -> int:
    args = parse_args()
    try:
        _warn_invalid_github_token_once()

        if not args.args:
            print("No command or URLs provided", file=sys.stderr)
            return 1

        command = args.args[0]

        # if command == "install":
        #     print("Installing dependencies...not implemented yet.")
        #     return 0
        if command == "install":
           import subprocess, pathlib, shlex, sys as _sys


           req = pathlib.Path("requirements.txt")
           if not req.exists() or req.stat().st_size == 0:
               print("Installing dependencies...done.")  # nothing to install, still succeed
               return 0


           # Detect virtualenv: True if inside a venv/venv-like environment
           in_venv = hasattr(_sys, "real_prefix") or (_sys.prefix != getattr(_sys, "base_prefix", _sys.prefix)) or bool(os.getenv("VIRTUAL_ENV"))


           # Build pip command safely using the current interpreter
           base_cmd = [_sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
           if not in_venv:
               base_cmd.insert(4, "--user")  # ... pip install --user -r requirements.txt


           try:
               # Capture output so we don’t spam stdout; forward errors to stderr on failure
               proc = subprocess.run(base_cmd, capture_output=True, text=True)
               if proc.returncode != 0:
                   # Show a concise error; include pip’s stderr for debugging
                   err = proc.stderr.strip() or proc.stdout.strip()
                   print(f"ERROR: Dependency installation failed ({' '.join(shlex.quote(p) for p in base_cmd)}):", file=sys.stderr)
                   if err:
                       print(err, file=sys.stderr)
                   return 1


               print("Installing dependencies...done.")
               return 0
           except Exception as e:
               print(f"ERROR: Dependency installation failed ({e})", file=sys.stderr)
               return 1
        elif command == "test":
            print("Running tests...not implemented yet.")
            return 0
        # elif command == "test":
        #    import os, subprocess, json, re


        #    # If invoked from within pytest (unit tests), avoid recursion & satisfy your test expectation
        #    if os.environ.get("PYTEST_CURRENT_TEST"):
        #        print("Running tests...not implemented yet.")
        #        return 0


        #    # Otherwise, run the real test suite and emit the single-line summary required by the spec.
        #    # Try to avoid recursion/long ops: exclude tests that shell out to ./run or exercise install.
        #    pytest_cmd = [
        #        "pytest",
        #        "--disable-warnings",
        #        "--maxfail=1",
        #        "-k", "not subprocess and not install",
        #        "--cov=src",
        #        "--cov-report=json:cov.json",
        #        "--json-report",
        #        "--json-report-file=report.json",
        #    ]


        #    try:
        #        proc = subprocess.run(pytest_cmd, capture_output=True, text=True, timeout=180)
        #    except subprocess.TimeoutExpired:
        #        print("0/0 test cases passed. 0% line coverage achieved.")
        #        return 1


        #    # Defaults
        #    total = passed = coverage_percent = 0


        #    # Coverage from cov.json (pytest-cov)
        #    try:
        #        with open("cov.json") as f:
        #            cov_data = json.load(f)
        #            coverage_percent = int(round(cov_data["totals"]["percent_covered"]))
        #    except Exception:
        #        # fallback: scrape a % from stdout if present
        #        m = re.search(r"(\d+)%", proc.stdout)
        #        if m:
        #            coverage_percent = int(m.group(1))


        #    # Counts from report.json (pytest-json-report)
        #    try:
        #        with open("report.json") as f:
        #            rep = json.load(f)
        #            summary = rep.get("summary", {})
        #            total = int(summary.get("total", 0))
        #            passed = int(summary.get("passed", 0))
        #    except Exception:
        #        # fallback: parse stdout summary
        #        m_passed = re.search(r"(\d+)\s+passed", proc.stdout)
        #        m_failed = re.search(r"(\d+)\s+failed", proc.stdout)
        #        p = int(m_passed.group(1)) if m_passed else 0
        #        f = int(m_failed.group(1)) if m_failed else 0
        #        passed, total = p, p + f


        #    # Print EXACTLY one line per the spec
        #    print(f"{passed}/{total} test cases passed. {coverage_percent}% line coverage achieved.")


        #    # Success if pytest exited cleanly AND all selected tests passed
        #    return 0 if (proc.returncode == 0 and passed == total and total > 0) else 1
        else:
            args.urls = args.args
            for u in args.urls:
                rec = evaluate_url(u)

                # Optional debug
                if args.verbosity > 0:
                    print(f"DEBUG raw rec = {rec}", file=sys.stderr)

                # Validate the top-level NDJSON **only** (tests expect this)
                if validate_ndjson(rec):
                    print(json.dumps(rec))
                else:
                    print(json.dumps({
                        "name": rec.get("name") or u.rstrip("/").split("/")[-1],
                        "error": "Invalid record"
                    }))
            return 0

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
