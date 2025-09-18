import json
import subprocess
import sys
import pytest

from src.cli.main import main, parse_args


# --------------------------
# Black Box (subprocess)
# --------------------------

def run_cli(*args):
    """Helper to run ./run as a subprocess and capture output."""
    return subprocess.run(
        ["./run", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )


def test_subprocess_no_args():
    result = run_cli()
    assert result.returncode == 1
    assert "No command or URLs provided" in result.stderr


def test_subprocess_install():
    result = run_cli("install")
    assert result.returncode == 0
    assert "Installing dependencies" in result.stdout


def test_subprocess_test_command():
    result = run_cli("test")
    assert result.returncode == 0
    assert "Running tests" in result.stdout


def test_subprocess_url_output_ndjson():
    url = "https://huggingface.co/bert-base-uncased"
    result = run_cli("--ndjson", url)
    assert result.returncode == 0
    rec = json.loads(result.stdout.strip())
    assert rec["name"] == url
    # Check for all expected top-level fields in the new schema
    expected_fields = [
        "name", "category", "net_score", "net_score_latency", "ramp_up_time", "ramp_up_time_latency",
        "bus_factor", "bus_factor_latency", "performance_claims", "performance_claims_latency", "license", "license_latency",
        "size_score", "size_score_latency", "dataset_and_code_score", "dataset_and_code_score_latency",
        "dataset_quality", "dataset_quality_latency", "code_quality", "code_quality_latency"
    ]
    for field in expected_fields:
        assert field in rec


# --------------------------
# White Box (direct calls)
# --------------------------

def test_direct_no_args(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["run"])  # simulate no args
    exit_code = main()
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No command or URLs provided" in captured.err


def test_direct_install(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["run", "install"])
    exit_code = main()
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Installing dependencies" in captured.out


def test_direct_test_command(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["run", "test"])
    exit_code = main()
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Running tests" in captured.out


def test_direct_url_ndjson(capsys, monkeypatch):
    url = "https://huggingface.co/bert-base-uncased"
    monkeypatch.setattr(sys, "argv", ["run", "--ndjson", url])
    exit_code = main()
    captured = capsys.readouterr()
    rec = json.loads(captured.out.strip())
    assert rec["name"] == url
    expected_fields = [
        "name", "category", "net_score", "net_score_latency", "ramp_up_time", "ramp_up_time_latency",
        "bus_factor", "bus_factor_latency", "performance_claims", "performance_claims_latency", "license", "license_latency",
        "size_score", "size_score_latency", "dataset_and_code_score", "dataset_and_code_score_latency",
        "dataset_quality", "dataset_quality_latency", "code_quality", "code_quality_latency"
    ]
    for field in expected_fields:
        assert field in rec
