"""Bus factor metric implementation with GenAI analysis."""
from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult
from ..data_fetcher import get_genai_metric_data


class BusFactorMetric:
    """
    Evaluate bus factor (contribution distribution) using GenAI LLM analysis.
    Returns a score in [0, 1] range where:
    - 0 represents poor bus factor (highly concentrated contributions/knowledge)
    - 1 represents good bus factor (well-distributed contributions/knowledge)

    For GenAI analysis, we assess knowledge concentration and invert it to match
    traditional bus factor interpretation.
    """
    id = "bus_factor"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        """Compute bus factor metric using GenAI analysis with fallback to heuristics."""
        import time
        import re
        start = time.time()

        # Get model URL from context for GenAI analysis
        model_url = context.get("model_url", "")
        code_url = context.get("code_url", "")

        # Use model_url first, fallback to code_url
        target_url = model_url or code_url

        if not target_url:
            # Fallback to original heuristic method
            meta = context.get("repo_meta", {})
            top_pct = float(meta.get("top_contributor_pct", 1.0))
            # Traditional bus factor: higher = better (1 - top_pct)
            # But for knowledge concentration: higher = worse
            # So we need to invert: high top_contributor_pct = low bus factor
            # Invert for traditional bus factor
            value = min(1.0, max(0.0, 1.0 - top_pct))
            seconds = time.time() - start
            return MetricResult(self.id, value, details={
                "fallback": "no_url",
                "top_contributor_pct": top_pct,
                "method": "heuristic"
            }, binary=0, seconds=seconds)

        # Create prompt for bus factor evaluation
        prompt = """Analyze the bus factor for this model/repository by examining READMEs, documentation, and contributor distribution.

Bus factor measures how well knowledge and contributions are distributed:
- High bus factor (closer to 1.0) = Knowledge is well-distributed, good documentation, builds on established research
- Low bus factor (closer to 0.0) = Knowledge is concentrated, poor documentation, requires specialized knowledge

Consider:
1. How well the README/documentation references existing research
2. Whether the approach builds on established methods
3. How accessible the knowledge is to new contributors
4. Documentation quality and completeness
5. Overlap with well-known techniques and papers

Return only a decimal number between 0.0 and 1.0 representing bus factor score.
URL:"""

        try:
            # Get GenAI evaluation
            genai_response = get_genai_metric_data(target_url, prompt)
            value = None

            # Extract numerical score from response
            if genai_response:
                response_str = str(genai_response)
                # Try multiple patterns to extract score
                patterns = [
                    r'(\d+\.\d+)',  # decimal like 0.75
                    r'(\d+)',       # integer like 1
                    r'0\.(\d+)',    # decimal starting with 0.
                ]

                extracted_value = None
                for pattern in patterns:
                    matches = re.findall(pattern, response_str)
                    if matches:
                        try:
                            if pattern == r'0\.(\d+)':
                                raw_score = float('0.' + matches[0])
                            else:
                                raw_score = float(matches[0])

                            # Ensure score is in [0, 1] range
                            if 0.0 <= raw_score <= 1.0:
                                extracted_value = raw_score
                                break
                            if raw_score > 1.0 and raw_score <= 100.0:
                                # Handle percentage format
                                extracted_value = min(1.0, raw_score / 100.0)
                                break
                        except ValueError:
                            continue

                if extracted_value is not None:
                    details = {
                        # Truncate for brevity
                        "genai_response": response_str[:200],
                        "extracted_score": extracted_value,
                        "method": "genai_llm",
                        "url_used": target_url
                    }
                    value = extracted_value
                else:
                    # If no valid score extracted, use fallback
                    raise ValueError("No valid score extracted")

            else:
                raise ValueError("No GenAI response")

        except Exception as exc:
            # Fallback to original heuristic method
            meta = context.get("repo_meta", {})
            top_pct = float(meta.get("top_contributor_pct", 1.0))
            # Traditional bus factor calculation
            value = min(1.0, max(0.0, 1.0 - top_pct))
            details = {
                "error": str(exc)[:100],
                "fallback": "heuristic_method",
                "top_contributor_pct": top_pct,
                "method": "heuristic"
            }

        seconds = time.time() - start
        return MetricResult(
            self.id,
            value,
            details=details,
            binary=0,
            seconds=seconds)
