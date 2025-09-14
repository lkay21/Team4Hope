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
        "scores": {"size": None, "license": None, "ramp_up_time": None, "bus_factor": None,
                   "dataset_code_availability": None, "dataset_quality": None, "code_quality": None,
                   "performance_claims": None},
        "overall": None
    }

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
                    print(json.dumps(rec))
                else:
                    print(rec) 
            return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
