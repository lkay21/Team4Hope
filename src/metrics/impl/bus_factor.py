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
        import os
        start = time.time()
        
        # Try LLM first if model_url is available
        model_url = context.get("model_url", "")
        value = None
        llm_used = False
        
        if model_url:
            prompt = "Analyze the bus factor for this repository. Bus factor measures how well-distributed contributions are among developers (0 = one person dominates, 1 = well distributed). Return only a decimal number between 0.0 and 1.0:"
            llm_result = get_genai_metric_data(model_url, prompt)
            if llm_result.get("metric"):
                try:
                    # Try to parse as simple float first
                    response = llm_result["metric"].strip()
                    try:
                        llm_value = float(response)
                        if 0 <= llm_value <= 1:
                            value = llm_value
                            llm_used = True
                        elif 0 <= llm_value <= 100:  # Handle percentage
                            value = llm_value / 100.0
                            llm_used = True
                    except ValueError:
                        # If simple parsing fails, try regex as backup
                        import re
                        patterns = [
                            r"\*\*([0-9]*\.?[0-9]+)\*\*",    # **0.75**
                            r"([0-9]*\.?[0-9]+)",            # any number
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, response.lower())
                            for match in matches:
                                try:
                                    val = float(match)
                                    if 0 <= val <= 1:
                                        value = val
                                        llm_used = True
                                        break
                                    elif 0 <= val <= 100:
                                        value = val / 100.0
                                        llm_used = True
                                        break
                                except ValueError:
                                    continue
                            if llm_used:
                                break
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
