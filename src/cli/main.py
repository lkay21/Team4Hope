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
