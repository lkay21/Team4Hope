This folder contains metrics-related helpers and the refactored
`data_fetcher` package.

Goal of the reorganization:
- Provide clearer module boundaries (Hugging Face, GitHub, heuristics, and
  optional LLM helpers) without changing external behavior.
- Move the original monolithic `data_fetcher.py` into a package layout under
  `data_fetcher/` so each responsibility lives in its own module.

Package layout:
- `data_fetcher/` - the package that re-exports the public API for backward
  compatibility. It contains the aggregator and helper modules:
  - `huggingface.py` - HF model/dataset helpers
  - `github.py` - GitHub helpers
  - `heuristics.py` - local heuristics and normalizers
  - `llm.py` - optional LLM-backed metric helpers (prototype)
  - `utils.py` - shared small utilities

Notes:
- The package preserves the original public import path `src.metrics.data_fetcher`
  so existing code and tests continue to work. The old monolith file has been
  removed and replaced by the package.
- Consider adding unit tests for `llm.py` if you plan to enable GenAI calls in
  CI or production environments (these require an API key).
