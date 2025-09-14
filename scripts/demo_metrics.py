from metrics import default_ops, run_metrics, build_registry_from_plan

context = {
    "size_components": {"loc_norm": 0.6, "db_norm": 0.4, "params_norm": 0.7, "artifacts_norm": 0.5},
    "license": "Apache-2.0",
    "ramp": {"likes_norm": 0.8, "downloads_norm": 0.7, "recency_norm": 0.9},
    "repo_meta": {"top_contributor_pct": 0.4},
    "availability": {"has_code": True, "has_dataset": True, "links_ok": True},
    "dataset_quality": {"cleanliness": 0.7, "documentation": 0.6, "class_balance": 0.8},
    "code_quality": {"test_coverage_norm": 0.6, "style_norm": 0.7, "comment_ratio_norm": 0.5, "maintainability_norm": 0.65},
    "requirements_passed": 7, "requirements_total": 9
}

if __name__ == "__main__":
    results, summary = run_metrics(default_ops, context, registry=build_registry_from_plan())
    import json
    print(json.dumps({
        "results": {k: {"id": v.id, "value": v.value, "binary": v.binary, "details": v.details, "seconds": v.seconds}
                    for k, v in results.items()},
        "netscore": summary
    }, indent=2))
