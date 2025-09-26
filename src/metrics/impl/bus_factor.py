from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult
from ..data_fetcher import get_genai_metric_data

class BusFactorMetric:
    """
    Evaluate knowledge concentration in model development using GenAI LLM analysis.
    Returns a score in [0, 1] range where:
    - 0 represents low necessary knowledge concentration (good - distributed knowledge)
    - 1 represents high knowledge concentration (bad - concentrated knowledge)
    """
    id = "bus_factor"
    
    def compute(self, context: Dict[str, Any]) -> MetricResult:
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
            value = min(1.0, max(0.0, top_pct))  # Direct mapping for knowledge concentration
            seconds = time.time() - start
            return MetricResult(self.id, value, details={
                "fallback": "no_url", 
                "top_contributor_pct": top_pct,
                "method": "heuristic"
            }, binary=0, seconds=seconds)
        
        # Create prompt for knowledge concentration evaluation
        prompt = """Analyze the knowledge concentration for this model/repository by examining READMEs, documentation, and comparing against well-documented research papers or discoveries.

Calculate the overlap percentage between the documentation and established research to determine knowledge concentration:

- High overlap with well-documented research = Low knowledge concentration (closer to 0.0)
- Low overlap with established research = High knowledge concentration (closer to 1.0)

Consider:
1. How well the README/documentation references existing research
2. Whether the approach builds on established methods
3. How much specialized/unique knowledge is required
4. Documentation quality and completeness
5. Overlap with well-known techniques and papers

Return only a decimal number between 0.0 and 1.0 representing knowledge concentration level.
URL:"""

        try:
            # Get GenAI evaluation
            genai_response = get_genai_metric_data(target_url, prompt)
            
            # Extract numerical score from response
            if genai_response:
                response_str = str(genai_response)
                # Try multiple patterns to extract score
                patterns = [
                    r'(\d+\.\d+)',  # decimal like 0.75
                    r'(\d+)',       # integer like 1
                    r'0\.(\d+)',    # decimal starting with 0.
                ]
                
                value = None
                for pattern in patterns:
                    matches = re.findall(pattern, response_str)
                    if matches:
                        try:
                            raw_score = float('0.' + matches[0] if pattern == r'0\.(\d+)' else matches[0])
                            # Ensure score is in [0, 1] range
                            if 0.0 <= raw_score <= 1.0:
                                value = raw_score
                                break
                            elif raw_score > 1.0 and raw_score <= 100.0:
                                # Handle percentage format
                                value = min(1.0, raw_score / 100.0)
                                break
                        except ValueError:
                            continue
                
                if value is not None:
                    details = {
                        "genai_response": response_str[:200],  # Truncate for brevity
                        "extracted_score": value,
                        "method": "genai_llm",
                        "url_used": target_url
                    }
                else:
                    # If no valid score extracted, use fallback
                    raise ValueError("No valid score extracted")
                    
            else:
                raise ValueError("No GenAI response")
                
        except Exception as e:
            # Fallback to original heuristic method
            meta = context.get("repo_meta", {})
            top_pct = float(meta.get("top_contributor_pct", 1.0))
            value = min(1.0, max(0.0, top_pct))  # Direct mapping for knowledge concentration
            details = {
                "error": str(e)[:100],
                "fallback": "heuristic_method",
                "top_contributor_pct": top_pct,
                "method": "heuristic"
            }
        
        seconds = time.time() - start
        return MetricResult(self.id, value, details=details, binary=0, seconds=seconds)
