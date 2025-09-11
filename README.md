# Team4Hope — CLI for Trustworthy Model Re-use

## Quick start
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./run https://huggingface.co/bert-base-uncased

## Development
- Branch per area: cli-<name>, metrics-<name>, urls-<name>, qa-<name>
- Tests: pytest (aim for ≥20 tests, ≥80% coverage)
- Output: stdout (supports --ndjson)
- Logging: use LOG_VERBOSITY, LOG_PATH
