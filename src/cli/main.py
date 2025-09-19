import argparse
import json
import os
import sys
from typing import Any, Dict
from url_parsers import handle_url, get_url_category
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
    empty_metrics = default_ndjson(name=u)

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
        if not isinstance(record[string], (str, type(None))):
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
