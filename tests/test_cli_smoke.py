from subprocess import run, PIPE
import json
def test_run_smoke():
    r = run(["./run", "https://huggingface.co/google-bert/bert-base-uncased"], stdout=PIPE, text=True)
    assert r.returncode == 0
    rec = json.loads(r.stdout.strip())
    expected_fields = [
        "name", "category", "net_score", "net_score_latency", "ramp_up_time", "ramp_up_time_latency",
        "bus_factor", "bus_factor_latency", "performance_claims", "performance_claims_latency", "license", "license_latency",
        "size_score", "size_score_latency", "dataset_and_code_score", "dataset_and_code_score_latency",
        "dataset_quality", "dataset_quality_latency", "code_quality", "code_quality_latency"
    ]
    for field in expected_fields:
        assert field in rec
