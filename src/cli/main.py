import argparse
import json
import os
import sys
from typing import Any, Dict
from src.url_parsers import handle_url, get_url_category
from src.cli.schema import default_ndjson

def _warn_invalid_github_token_once() -> None:
    """Warn exactly once, to stderr only, if GITHUB_TOKEN looks invalid."""
    if os.environ.get("_BAD_GH_TOKEN_WARNED") == "1":
        return
    os.environ["_BAD_GH_TOKEN_WARNED"] = "1"

    tok = os.getenv("GITHUB_TOKEN")
    if not tok:
        return
    looks_valid = tok.startswith("ghp_") or tok.startswith("github_pat_")
    if not looks_valid:
        sys.stderr.write("WARNING: Invalid GitHub token; continuing unauthenticated.\n")

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CLI for trustworthy model re-use")
    p.add_argument("args", nargs="*", help="Commands(install, test) or URLs to evaluate (HF model/dataset or GitHub repo)")
    p.add_argument("--ndjson", action="store_true", help="Emit NDJSON records to stdout")
    p.add_argument("-v","--verbosity", type=int, default=int(os.getenv("LOG_VERBOSITY", "0")),
                   help="Log verbosity (default from env LOG_VERBOSITY, default 0)")

    return p.parse_args()

def evaluate_url(models: dict) -> Dict[str, Any]:
    # TODO: dispatch to url_parsers and metrics, check URL type
    # For now, return a dummy record
    # Return the required fields incl. overall score and subscores
    # empty_metrics = []
    # for model in models:
    #     empty_metrics.append(default_ndjson(model=model))

    if not None in get_url_category(models):
        return handle_url(models)

def validate_ndjson(record: Dict[str, Any]) -> bool:
    string_fields = {"name", "category"}
    score_fields = {"net_score", "ramp_up_time", "bus_factor", "performance_claims", "license",
                    "size_score", "dataset_and_code_score", "dataset_quality", "code_quality"}
    latency_fields = {"net_score_latency", "ramp_up_time_latency", "bus_factor_latency",
                      "performance_claims_latency", "license_latency", "size_score_latency",
                      "dataset_and_code_score_latency", "dataset_quality_latency", "code_quality_latency"}
    

    if not isinstance(record, dict):
        return False
    if not score_fields.issubset(record.keys()) or not latency_fields.issubset(record.keys()) or not string_fields.issubset(record.keys()):
        return False

    for string in string_fields:
        if not isinstance(record[string], (str, type(None))) and record[string] is not None:
            return False
    
    for score in score_fields:

        score_metric = record[score]
        #if socre_metric is a dict, check inner values
        if isinstance(score_metric, dict):
            for k, v in score_metric.items():
                if v is not None and (not isinstance(v, (float)) or not (0.00 <= v <= 1.00)):
                    return False
        else:
            # score can be none or float between 0 and 1
            if score_metric is not None:
                if not isinstance(score_metric, (float)) or not (0.00 <= score_metric <= 1.00):
                    return False
                
    for latency in latency_fields:

        latency_metric = record[latency]
        # latency can be none or int (milliseconds)
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

            # Each model has a dictionary of links in order {code, dataset, model}
            models = {}
            

            if os.path.isfile(command):
                with open(command, 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        links = [link for link in line.split(',')]
                        models[i] = links


            ndjsons = evaluate_url(models)

            for ndjson in ndjsons.values():
                if validate_ndjson(ndjson):
                    print(json.dumps(ndjson))
                else:
                    name = ndjson.get("name", "unknown")
                    print(json.dumps({"name": name, "error": "Invalid record"}))

            return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
