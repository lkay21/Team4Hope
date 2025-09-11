from typing import Dict, Any

WEIGHTS = {
    "size": 0.05, "license": 0.10, "ramp_up_time": 0.10, "bus_factor": 0.10,
    "dataset_code_availability": 0.15, "dataset_quality": 0.15,
    "code_quality": 0.15, "performance_claims": 0.20
}

def compute_all(raw: Dict[str, Any]) -> Dict[str, float]:
    # TODO: compute each metric in [0,1] and support parallelism later
    return {k: 0.0 for k in WEIGHTS}

def net_score(scores: Dict[str, float]) -> float:
    return sum(WEIGHTS[k] * scores[k] for k in WEIGHTS)
