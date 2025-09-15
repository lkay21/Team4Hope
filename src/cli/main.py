import argparse
import json
import os
import sys
from typing import Any, Dict

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
    return {
        "url": u,
        "scores": {"size": {"score": None, "latency": None}, "license": {"score": None, "latency": None}, "ramp_up_time": {"score": None, "latency": None}, "bus_factor": {"score": None, "latency": None},
                   "dataset_and_code_score": {"score": None, "latency": None}, "dataset_quality": {"score": None, "latency": None}, "code_quality": {"score": None, "latency": None},
                   "performance_claims": {"score": None, "latency": None}},
        "overall": None
    }

def validate_ndjson(record: Dict[str, Any]) -> bool:
    required_fields = {"url", "scores", "overall"}
    score_fields = {"size", "license", "ramp_up_time", "bus_factor",
                    "dataset_and_code_score", "dataset_quality", "code_quality",
                    "performance_claims"}
    if not required_fields.issubset(record.keys()):
        return False
    if not isinstance(record["scores"], dict):
        return False
    if not score_fields.issubset(record["scores"].keys()):
        return False
    for field in score_fields:
        metric = record["scores"][field]
        if not isinstance(metric, dict):
            return False
        if "score" not in metric or "latency" not in metric:
            return False
        # score can be none or float between 0 and 1
        if metric["score"] is not None:
            if not isinstance(metric["score"], (int, float)):
                return False
            if not (0 <= metric["score"] <= 1):
                return False
        # latency can be none or int (milliseconds)
        if metric["latency"] is not None and not isinstance(metric["latency"], int):
            return False
        
    # overall can be none, int, or float
    if record["overall"] is not None and not isinstance(record["overall"], (int, float)):
        return False
    return True

def main() -> int:
    args = parse_args()
    try:
        if not args.args:
            print("No command or URLs provided", file=sys.stderr)
            return 1
        
        command = args.args[0]

        if command == "install":
            print("Installing dependencies...not implemented yet.")
            return 0
        elif command == "test":
            print("Running tests...not implemented yet.")
            return 0
        else:
            args.urls = args.args
            
            for u in args.urls:
                rec = evaluate_url(u)
                if args.ndjson:
                    if validate_ndjson(rec):
                        print(json.dumps(rec))
                    else:
                        print(f"ERROR: Invalid record for URL {u}", file=sys.stderr)
                else:
                    print(rec) 
            return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
