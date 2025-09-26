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
        
        # Get the dataset URL from context
        dataset_url = context.get("dataset_url", "")
        
        if not dataset_url:
            # Fallback to original implementation if no dataset URL
            dq = context.get("dataset_quality", {})
            vals = [float(dq[k]) for k in ("cleanliness","documentation","class_balance") if k in dq]
            value = sum(vals)/len(vals) if vals else 0.0
            seconds = time.time() - start
            return MetricResult(self.id, value, details={"fallback": "no_dataset_url", "components": vals}, binary=0, seconds=seconds)
        
        # Create a prompt for dataset quality evaluation
        prompt = """Evaluate the quality of this dataset based on the following criteria:
1. Data cleanliness and consistency
2. Documentation quality and completeness
3. Dataset structure and organization
4. Metadata and descriptions
5. Overall usability for machine learning tasks

Please provide a quality score from 0.0 to 1.0 where:
- 0.0 = Very bad dataset (poor quality, missing documentation, inconsistent data)
- 1.0 = Excellent dataset (high quality, well-documented, clean and consistent)

Respond with only the numerical score (e.g., 0.75). Dataset URL:"""

        try:
            # Get GenAI evaluation
            genai_response = get_genai_metric_data(dataset_url, prompt)
            
            # Extract numerical score from response
            score_match = re.search(r'(\d+\.?\d*)', str(genai_response))
            if score_match:
                raw_score = float(score_match.group(1))
                # Ensure score is in [0, 1] range
                value = max(0.0, min(1.0, raw_score))
            else:
                value = 0.0  # Default if no valid score found
                
            details = {
                "genai_response": str(genai_response),
                "extracted_score": value,
                "method": "genai_llm"
            }
            
        except Exception as e:
            # Fallback to original implementation on error
            dq = context.get("dataset_quality", {})
            vals = [float(dq[k]) for k in ("cleanliness","documentation","class_balance") if k in dq]
            value = sum(vals)/len(vals) if vals else 0.0
            details = {
                "error": str(e),
                "fallback": "original_method",
                "components": vals
            }
        
        seconds = time.time() - start
        return MetricResult(self.id, value, details=details, binary=0, seconds=seconds)
