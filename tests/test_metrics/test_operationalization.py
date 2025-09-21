import os
import pytest
from src.metrics.operationalization import Operationalization, normalize, binarize

def make_op(metric_id="m1", weight=1.0, norm="identity", norm_params=None, greater_is_better=True):
    return Operationalization(
        metric_id=metric_id,
        params={},
        weight=weight,
        normalization=norm,
        norm_params=norm_params or {},
        greater_is_better=greater_is_better,
    )

# --- normalize() tests ---

def test_identity_greater_is_better():
    op = make_op(norm="identity", greater_is_better=True)
    assert normalize(0.7, op) == 0.7

def test_identity_less_is_better():
    op = make_op(norm="identity", greater_is_better=False)
    assert normalize(0.7, op) == -0.7

def test_minmax_normal_case():
    op = make_op(norm="minmax", norm_params={"min": 0.0, "max": 10.0})
    assert normalize(5.0, op) == 0.5

def test_minmax_zero_range():
    op = make_op(norm="minmax", norm_params={"min": 1.0, "max": 1.0})
    assert normalize(1.0, op) == 0.0  # avoid div by zero

def test_invert_minmax_normal_case():
    op = make_op(norm="invert_minmax", norm_params={"min": 0.0, "max": 10.0})
    assert normalize(5.0, op) == 0.5  # inverted

def test_invert_minmax_zero_range():
    op = make_op(norm="invert_minmax", norm_params={"min": 2.0, "max": 2.0})
    assert normalize(2.0, op) == 0.0

def test_zscore_normal_case():
    op = make_op(norm="zscore", norm_params={"mu": 5.0, "sigma": 2.0})
    assert normalize(7.0, op) == 1.0  # (7-5)/2

def test_zscore_zero_sigma():
    op = make_op(norm="zscore", norm_params={"mu": 5.0, "sigma": 0.0})
    assert normalize(7.0, op) == 0.0

def test_unknown_normalization():
    op = make_op(norm="not_real")
    with pytest.raises(ValueError):
        normalize(1.0, op)

# --- binarize() tests ---

def test_binarize_default_threshold():
    assert binarize(0.6) == 1
    assert binarize(0.4) == 0

def test_binarize_custom_threshold():
    assert binarize(0.7, threshold=0.8) == 0
    assert binarize(0.9, threshold=0.8) == 1

def test_binarize_env_override(monkeypatch):
    monkeypatch.setenv("METRIC_THRESHOLD", "0.75")
    assert binarize(0.8) == 1
    assert binarize(0.7) == 0
