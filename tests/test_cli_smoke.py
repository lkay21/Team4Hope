from subprocess import run, PIPE
def test_run_smoke():
    r = run(["./run", "https://huggingface.co/bert-base-uncased"], stdout=PIPE, text=True)
    assert r.returncode == 0
    assert "huggingface.co" in r.stdout
