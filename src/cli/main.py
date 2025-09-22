import argparse
import json
import os
import sys
from typing import Any, Dict
from src.url_parsers import handle_url, get_url_category
from src.cli.schema import default_ndjson

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CLI for trustworthy model re-use")
    p.add_argument("args", nargs="*", help="Commands(install, test) or URLs to evaluate (HF model/dataset or GitHub repo)")
    p.add_argument("--ndjson", action="store_true", help="Emit NDJSON records to stdout")
    p.add_argument("-v","--verbosity", type=int, default=int(os.getenv("LOG_VERBOSITY", "0")),
                   help="Log verbosity (default from env LOG_VERBOSITY, default 0)")

    return p.parse_args()

def evaluate_url(u: str) -> Dict[str, Any]:
    # TODO: dispatch to url_parsers and metrics, check URL type
    # For now, return a dummy record
    # Return the required fields incl. overall score and subscores
    empty_metrics = default_ndjson(u)

    if get_url_category(u) is None:
        return empty_metrics
    else:
        return handle_url(u)

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
        else:
            args.urls = args.args

            for u in args.urls:
                rec = evaluate_url(u)

                if validate_ndjson(rec):
                    print(json.dumps(rec))
                else:
                    name = u.rstrip('/').split('/')[-1]
                    print(json.dumps({"name": name, "error": "Invalid record"}))
            return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
