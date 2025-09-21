import os
import pytest
from src.metrics.types import MetricResult
from src.metrics.operationalization import Operationalization
from src.metrics.netscore import netscore

def make_metric(value: float, binary: int, seconds: float = 0.0):
    return MetricResult("dummy", value, details={}, binary=binary, seconds=seconds)

def make_op(metric_id: str, weight: float):
    # Fill in dummy args for required params
    return Operationalization(
        metric_id=metric_id,
        weight=weight,
        params={},              # empty dict
        normalization=None,     # no normalization
        norm_params={}          # empty dict
    )

def test_simple_average():
    results = {
        "m1": make_metric(0.9, 1),
        "m2": make_metric(0.2, 0),
    }
    ops = [make_op("m1", 1.0), make_op("m2", 1.0)]
    out = netscore(results, ops)
    assert out["NetScore_weighted"] == pytest.approx(0.5)
    assert out["NetScore_binary"] in (0, 1)

def test_threshold_respected(monkeypatch):
    # Case 1: binary=0, weight=1.0 -> weighted=0.0
    results = {"m1": make_metric(0.5, 0)}
    ops = [make_op("m1", 1.0)]

    monkeypatch.setenv("NETSCORE_THRESHOLD", "0.5")
    assert netscore(results, ops)["NetScore_binary"] == 0

    # Case 2: binary=1, weight=1.0 -> weighted=1.0
    results = {"m1": make_metric(0.5, 1)}
    ops = [make_op("m1", 1.0)]

    monkeypatch.setenv("NETSCORE_THRESHOLD", "0.5")
    assert netscore(results, ops)["NetScore_binary"] == 1


def test_zero_weights():
    results = {"m1": make_metric(0.7, 1)}
    ops = [make_op("m1", 0.0)]
    out = netscore(results, ops)
    assert out["NetScore_weighted"] == 0.0

def test_component_structure():
    results = {"m1": make_metric(0.8, 1, seconds=2.5)}
    ops = [make_op("m1", 1.5)]
    out = netscore(results, ops)
    comp = out["components"][0]
    assert comp["metric_id"] == "m1"
    assert comp["binary"] == 1
    assert comp["value"] == 0.8
    assert comp["weight"] == 1.5
    assert comp["seconds"] == 2.5
