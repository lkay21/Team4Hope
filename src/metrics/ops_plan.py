from __future__ import annotations
from .operationalization import Operationalization

# Weights & metric set taken from the Milestone 1 plan's Net Score table.
# Size(w1=0.05), License(0.10), RampUp(0.10), BusFactor(0.10),
# Availability (Code+Data) (0.15), DatasetQuality(0.15),
# CodeQuality(0.15), PerformanceClaims(0.20).

default_ops = [
    Operationalization("size", {}, 0.05, "minmax", {"min": 0.0, "max": 1.0}, True),
    Operationalization("license_compliance", {}, 0.10, "identity", {}, True),
    Operationalization("ramp_up_time", {}, 0.10, "minmax", {"min": 0.0, "max": 1.0}, True),
    Operationalization("bus_factor", {}, 0.10, "minmax", {"min": 0.0, "max": 1.0}, True),
    Operationalization("availability", {}, 0.15, "identity", {}, True),
    Operationalization("dataset_quality", {}, 0.15, "minmax", {"min": 0.0, "max": 1.0}, True),
    Operationalization("code_quality", {}, 0.15, "minmax", {"min": 0.0, "max": 1.0}, True),
    Operationalization("performance_claims", {}, 0.20, "minmax", {"min": 0.0, "max": 1.0}, True),
]
