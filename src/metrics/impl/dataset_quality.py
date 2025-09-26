from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult
from ..data_fetcher import get_genai_metric_data

class DatasetQualityMetric:
    """
    Evaluate dataset quality using GenAI LLM analysis.
    Returns a score in [0, 1] range where 0 represents a very bad dataset and 1 represents a great dataset.
    """
    id = "dataset_quality"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        import time
        import re
        start = time.time()
        
        # Start with original implementation as base
        dq = context.get("dataset_quality", {})
        vals = [float(dq[k]) for k in ("cleanliness","documentation","class_balance") if k in dq]
        base_value = sum(vals)/len(vals) if vals else 0.5
        
        # Get the dataset URL from context for potential GenAI enhancement
        dataset_url = context.get("dataset_url", "")
        
        value = base_value
        details = {"components": vals, "method": "original"}
        
        # Only try GenAI if we have a dataset URL
        if dataset_url:
            try:
                # Simple prompt for GenAI enhancement
                prompt = """Rate this dataset quality from 0.0 to 1.0. Consider documentation, structure, and usability. Respond with just a number like 0.8"""
                
                # Get GenAI evaluation with timeout protection
                genai_response = get_genai_metric_data(dataset_url, prompt)
                
                # Extract score more carefully
                if genai_response:
                    score_match = re.search(r'0?\.?\d+', str(genai_response))
                    if score_match:
                        genai_score = float(score_match.group())
                        if 0.0 <= genai_score <= 1.0:
                            # Blend with original score (70% original, 30% GenAI)
                            value = 0.7 * base_value + 0.3 * genai_score
                            details.update({
                                "genai_score": genai_score,
                                "blended": True,
                                "method": "original_with_genai"
                            })
                        
            except Exception as e:
                # Silently fall back to original - no error logging
                pass
        
        seconds = time.time() - start
        return MetricResult(self.id, value, details=details, binary=0, seconds=seconds)
