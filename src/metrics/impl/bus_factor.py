from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult
from src.metrics.data_fetcher.llm import get_genai_metric_data

class BusFactorMetric:
    """
    Heuristic: higher is better when contribution is spread. Expect:
      contributors_count (>=1), top_contributor_pct (0..1).
    We map: value = 1 - top_contributor_pct, optionally scaled by log(contributors).
    """
    id = "bus_factor"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        import time
        start = time.time()
        
        # Try LLM first if model_url is available
        model_url = context.get("model_url", "")
        value = None
        llm_used = False
        
        if model_url:
            prompt = "Estimate the bus factor score (0-1) for this model repository. Bus factor measures how well-distributed the contributions are among developers. Higher scores mean better distribution. Reply with a single number between 0 and 1:"
            llm_result = get_genai_metric_data(model_url, prompt)
            if llm_result.get("metric"):
                try:
                    import re
                    # Extract first number from the response
                    match = re.search(r"([-+]?[0-9]*\.?[0-9]+)", llm_result["metric"])
                    if match:
                        llm_value = float(match.group(1))
                        # If it looks like a percentage, convert to 0-1 range
                        if llm_value > 1.0:
                            llm_value = llm_value / 100.0
                        value = max(0.0, min(1.0, llm_value))
                        llm_used = True
                except Exception:
                    pass
        
        # Fallback to original heuristic if LLM didn't work
        if value is None:
            meta = context.get("repo_meta", {})
            top_pct = float(meta.get("top_contributor_pct", 1.0))  # 1.0 == single dev dominates
            value = max(0.0, min(1.0, 1.0 - top_pct))
        
        seconds = time.time() - start
        details = {"llm_used": llm_used}
        if not llm_used:
            meta = context.get("repo_meta", {})
            details["top_contributor_pct"] = float(meta.get("top_contributor_pct", 1.0))
            
        return MetricResult(self.id, value, details=details, binary=0, seconds=seconds)
