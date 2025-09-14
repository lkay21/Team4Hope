from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Dict, Any, Literal

Norm = Literal["identity", "minmax", "invert_minmax", "zscore"]

@dataclass(frozen=True)
class Operationalization:
    metric_id: str
    params: Dict[str, Any]
    weight: float                   # >= 0
    normalization: Norm
    norm_params: Dict[str, float]   # {"min":..,"max":..} or {"mu":..,"sigma":..}
    greater_is_better: bool = True  # for identity

def normalize(value: float, op: Operationalization) -> float:
    n = op.normalization
    p = op.norm_params or {}
    if n == "identity":
        return value if op.greater_is_better else -value
    if n == "minmax":
        mn, mx = p.get("min", 0.0), p.get("max", 1.0)
        if mx == mn: return 0.0
        return (value - mn) / (mx - mn)
    if n == "invert_minmax":
        mn, mx = p.get("min", 0.0), p.get("max", 1.0)
        if mx == mn: return 0.0
        return 1.0 - (value - mn) / (mx - mn)
    if n == "zscore":
        mu, sigma = p.get("mu", 0.0), p.get("sigma", 1.0)
        if sigma == 0: return 0.0
        return (value - mu) / sigma
    raise ValueError(f"Unknown normalization: {n}")

def binarize(score: float, threshold: float | None = None) -> int:
    """
    Project requirement: "Each score should be either 0 or 1" (plan Table 2).
    We produce a binary view using a threshold (default 0.5 or METRIC_THRESHOLD env).
    """
    if threshold is None:
        threshold = float(os.getenv("METRIC_THRESHOLD", "0.5"))
    return 1 if score >= threshold else 0
