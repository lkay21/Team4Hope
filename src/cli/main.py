import argparse
import json
import os
import sys
from typing import Any, Dict
from src.url_parsers import handle_url, get_url_category
from src.cli.schema import default_ndjson
import logging
from pathlib import Path

def _warn_invalid_github_token_once() -> None:
    """Warn exactly once, to stderr only, if GITHUB_TOKEN looks invalid."""
    if os.environ.get("_BAD_GH_TOKEN_WARNED") == "1":
        return
    os.environ["_BAD_GH_TOKEN_WARNED"] = "1"

    tok = os.getenv("GITHUB_TOKEN")
    if not tok:
        sys.stderr.write("WARNING: Invalid GitHub token; continuing unauthenticated.\n")
        return
    
    looks_valid = tok.startswith("ghp_") or tok.startswith("github_pat_")
    if not looks_valid:
        sys.stderr.write("WARNING: Invalid GitHub token; continuing unauthenticated.\n")
        os.environ["GITHUB_TOKEN"] = ""  # Clear invalid token

def _setup_logging(verbosity: int) -> None:
    """Setup logging based on LOG_FILE env var and verbosity"""
    log_path = os.getenv("LOG_FILE")
    handlers = []
    
    if log_path:
        try:
            # Ensure parent directory exists
            Path(log_path).parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_path))
        except (OSError, PermissionError):
            sys.stderr.write(f"WARNING: Cannot write to log file {log_path}\n")

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if verbosity > 0 else logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

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
        _setup_logging(args.verbosity)
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
            import subprocess
            import re

            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--cov", "--tb=short"],
                capture_output=True,
                text=True
            )
            output = result.stdout
            error = result.stderr


            passed_match = re.search(r"=+ (\d+) passed.*?in [\d\.]+s =+", output)
            total_match = re.search(r"collected (\d+) items", output)
            cov_match = re.search(r"(\d+)%\s+coverage", output) or re.search(r"TOTAL.*?(\d+)%", output)

            passed = int(passed_match.group(1)) if passed_match else 0
            total = int(total_match.group(1)) if total_match else 0
            coverage = int(cov_match.group(1)) if cov_match else 0

            print(f"{passed}/{total} test cases passed. {coverage}% line coverage achieved.")
            
            return result.returncode
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
                    print(json.dumps(ndjson, separators=(",", ":")))
                else:
                    name = ndjson.get("name", "unknown")
                    print(json.dumps({"name": name, "error": "Invalid record"}))

            return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
