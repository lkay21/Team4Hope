from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult
from src.metrics.data_fetcher.llm import get_genai_metric_data

class CodeQualityMetric:
    """
    Evaluate code quality using GenAI LLM analysis with fallback to heuristic scoring.
    Returns a score in [0, 1] range based on code quality factors.
    """
    id = "code_quality"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        import time
        import re
        start = time.time()
        
        # Try LLM first if model_url is available
        model_url = context.get("model_url", "")
        value = None
        llm_used = False
        
        if model_url:
            prompt = """Analyze the code quality of this repository based on the following criteria:
1. Test coverage and testing practices
2. Code style and consistency
3. Documentation and comments
4. Code maintainability and structure
5. Error handling and robustness
6. Dependencies and configuration management

Please provide a code quality score from 0.0 to 1.0 where:
- 0.0 = Very poor code quality (no tests, poor style, no documentation)
- 1.0 = Excellent code quality (comprehensive tests, clean code, well documented)

Respond with only the numerical score (e.g., 0.75). Repository URL:"""
            
            try:
                # Get GenAI evaluation
                llm_result = get_genai_metric_data(model_url, prompt)
                if llm_result.get("metric"):
                    response = llm_result["metric"].strip()
                    
                    # Try to parse as simple float first
                    try:
                        llm_value = float(response)
                        if 0 <= llm_value <= 1:
                            value = llm_value
                            llm_used = True
                        elif 0 <= llm_value <= 100:  # Handle percentage
                            value = llm_value / 100.0
                            llm_used = True
                    except ValueError:
                        # If simple parsing fails, try regex patterns
                        patterns = [
                            r"(\d+(?:\.\d+)?)",          # any decimal number
                            r"\*\*([0-9]*\.?[0-9]+)\*\*", # **0.75**
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, response)
                            for match in matches:
                                try:
                                    val = float(match)
                                    if 0 <= val <= 1:
                                        value = val
                                        llm_used = True
                                        break
                                    elif 0 <= val <= 100:  # Handle scores out of 100
                                        value = val / 100.0
                                        llm_used = True
                                        break
                                    elif 0 <= val <= 10:   # Handle scores out of 10
                                        value = val / 10.0
                                        llm_used = True
                                        break
                                except ValueError:
                                    continue
                            if llm_used:
                                break
            except Exception as e:
                # LLM call failed, will fall back to heuristic
                pass
        
        # Fallback to original heuristic method if LLM didn't work
        if value is None:
            cq = context.get("code_quality", {})
            keys = ("test_coverage_norm","style_norm","comment_ratio_norm","maintainability_norm")
            vals = [float(cq[k]) for k in keys if k in cq]
            value = sum(vals)/len(vals) if vals else 0.0
        
        seconds = time.time() - start
        details = {"llm_used": llm_used}
        if not llm_used:
            cq = context.get("code_quality", {})
            keys = ("test_coverage_norm","style_norm","comment_ratio_norm","maintainability_norm")
            vals = [float(cq[k]) for k in keys if k in cq]
            details["components"] = vals
            details["fallback_method"] = "heuristic"
        
        return MetricResult(self.id, value, details=details, binary=0, seconds=seconds)
