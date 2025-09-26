from __future__ import annotations
from typing import Dict, Any
from ..types import MetricResult
from ..data_fetcher import get_genai_metric_data

class CodeQualityMetric:
    """
    Evaluate code quality using GenAI LLM analysis with fallback to traditional metrics.
    Returns a score in [0, 1] range where:
    - 0 represents horrible code quality
    - 1 represents perfect code quality
    
    Considers: test coverage, code format, comment/code ratio, and maintainability.
    """
    id = "code_quality"

    def compute(self, context: Dict[str, Any]) -> MetricResult:
        import time
        import re
        start = time.time()
        
        # Start with traditional implementation as base
        cq = context.get("code_quality", {})
        keys = ("test_coverage_norm","style_norm","comment_ratio_norm","maintainability_norm")
        vals = [float(cq[k]) for k in keys if k in cq]
        base_value = sum(vals)/len(vals) if vals else 0.5
        
        # Get URLs from context for GenAI analysis
        code_url = context.get("code_url", "")
        model_url = context.get("model_url", "")
        
        # Use code_url first (more relevant for code quality), then model_url
        target_url = code_url or model_url
        
        value = base_value
        details = {"components": vals, "method": "traditional"}
        
        # Try GenAI enhancement if we have a URL
        if target_url:
            try:
                # Create comprehensive prompt for code quality evaluation
                prompt = """Analyze the code quality for this repository/model based on the following criteria:

1. Test Coverage - How well the code is tested
2. Code Format - Code style, formatting, and consistency  
3. Comment/Code Ratio - Quality and quantity of comments and documentation
4. Maintainability - How easy the code is to understand, modify, and extend

Evaluate the overall code quality on a scale from 0.0 to 1.0 where:
- 0.0 = Horrible code quality (no tests, poor formatting, no comments, unmaintainable)
- 1.0 = Perfect code quality (excellent tests, clean formatting, well-documented, highly maintainable)

Consider factors like:
- Presence of test files and test coverage
- Consistent code style and formatting
- Meaningful variable names and function documentation
- Code organization and structure
- README quality and examples

Return only a decimal number between 0.0 and 1.0. URL:"""

                # Get GenAI evaluation
                genai_response = get_genai_metric_data(target_url, prompt)
                
                # Extract score from response
                if genai_response:
                    response_str = str(genai_response)
                    # Multiple patterns to extract numerical score
                    patterns = [
                        r'(\d+\.\d+)',  # decimal like 0.75
                        r'(\d+)',       # integer like 1
                        r'0\.(\d+)',    # decimal starting with 0.
                    ]
                    
                    extracted_score = None
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
                                    extracted_score = raw_score
                                    break
                                elif raw_score > 1.0 and raw_score <= 100.0:
                                    # Handle percentage format
                                    extracted_score = min(1.0, raw_score / 100.0)
                                    break
                            except ValueError:
                                continue
                    
                    if extracted_score is not None:
                        # Blend GenAI score with traditional score (60% traditional, 40% GenAI)
                        # This provides stability while incorporating GenAI insights
                        value = 0.6 * base_value + 0.4 * extracted_score
                        details.update({
                            "genai_score": extracted_score,
                            "blended": True,
                            "method": "traditional_with_genai",
                            "url_used": target_url
                        })
                    else:
                        # If no valid score extracted, keep traditional score
                        details.update({
                            "genai_response": response_str[:100],
                            "extraction_failed": True,
                            "method": "traditional_fallback"
                        })
                        
            except Exception as e:
                # Silently fall back to traditional method on any error
                details.update({
                    "error": str(e)[:100],
                    "method": "traditional_fallback"
                })
        
        seconds = time.time() - start
        return MetricResult(self.id, value, details=details, binary=0, seconds=seconds)
