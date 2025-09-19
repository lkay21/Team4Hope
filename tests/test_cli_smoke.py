from subprocess import run, PIPE
import ast
def test_run_smoke():
    r = run(["./run", "https://huggingface.co/google-bert/bert-base-uncased"], stdout=PIPE, text=True)
    assert r.returncode == 0
    rec =  ast.literal_eval(r.stdout.strip())
    assert rec["name"] == "bert-base-uncased"
    assert rec["category"] == "MODEL"
