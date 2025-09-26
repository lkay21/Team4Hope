"""
Tests for LLM data fetcher module.
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock, MagicMock
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))


class TestGetGenAIMetricData:
    """Test the get_genai_metric_data function."""
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', 'test-key')
    @patch('src.metrics.data_fetcher.llm.requests.post')
    def test_successful_genai_call(self, mock_post):
        """Test successful GenAI API call."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "0.85"
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        assert result == {"metric": "0.85"}
        mock_post.assert_called_once()
        
        # Check the call arguments
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://genai.rcac.purdue.edu/api/chat/completions"
        assert call_args[1]["headers"]["Authorization"] == "Bearer test-key"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"
        assert call_args[1]["timeout"] == 20
        
        # Check the body
        body = call_args[1]["json"]
        assert body["model"] == "llama3.1:latest"
        assert len(body["messages"]) == 1
        assert body["messages"][0]["role"] == "user"
        assert "Test prompt" in body["messages"][0]["content"]
        assert "https://github.com/test/repo" in body["messages"][0]["content"]
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', None)
    def test_no_api_key(self):
        """Test behavior when API key is not set."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        assert result == {}
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', 'test-key')
    @patch('src.metrics.data_fetcher.llm.requests.post')
    def test_http_error(self, mock_post):
        """Test handling of HTTP errors."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        mock_post.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        assert result == {}
        mock_post.assert_called_once()
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', 'test-key')
    @patch('src.metrics.data_fetcher.llm.requests.post')
    def test_timeout_error(self, mock_post):
        """Test handling of timeout errors."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        assert result == {}
        mock_post.assert_called_once()
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', 'test-key')
    @patch('src.metrics.data_fetcher.llm.requests.post')
    def test_connection_error(self, mock_post):
        """Test handling of connection errors."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        assert result == {}
        mock_post.assert_called_once()
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', 'test-key')
    @patch('src.metrics.data_fetcher.llm.requests.post')
    def test_invalid_json_response(self, mock_post):
        """Test handling of invalid JSON response."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        assert result == {}
        mock_post.assert_called_once()
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', 'test-key')
    @patch('src.metrics.data_fetcher.llm.requests.post')
    def test_empty_response_structure(self, mock_post):
        """Test handling of empty or malformed response structure."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        # Test cases that should return {"metric": ""} (successful but empty content)
        success_cases = [
            {},  # Empty response
            {"choices": [{}]},  # Choice without message
            {"choices": [{"message": {}}]},  # Message without content
        ]
        
        for response_data in success_cases:
            mock_response = Mock()
            mock_response.json.return_value = response_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
            assert result == {"metric": ""}
        
        # Test cases that should return {} (due to exceptions)
        error_cases = [
            {"choices": []},  # Empty choices - causes IndexError
            {"choices": [{"message": {"content": None}}]},  # None content - AttributeError on .strip()
        ]
        
        for response_data in error_cases:
            mock_response = Mock()
            mock_response.json.return_value = response_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
            assert result == {}
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', 'test-key')
    @patch('src.metrics.data_fetcher.llm.requests.post')
    def test_whitespace_stripping(self, mock_post):
        """Test that response content is stripped of whitespace."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "  \n  0.75  \n  "
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        assert result == {"metric": "0.75"}
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', 'test-key')
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_URL', 'https://custom.endpoint.com/api')
    @patch('src.metrics.data_fetcher.llm.requests.post')
    def test_custom_endpoint_url(self, mock_post):
        """Test using custom endpoint URL from environment variable."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "0.9"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        assert result == {"metric": "0.9"}
        
        # Check that custom URL was used
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://custom.endpoint.com/api"
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', 'test-key')
    @patch('src.metrics.data_fetcher.llm.requests.post')
    def test_complex_response_content(self, mock_post):
        """Test with complex response content."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Based on my analysis, the score is **0.82** for this repository."
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        expected_content = "Based on my analysis, the score is **0.82** for this repository."
        assert result == {"metric": expected_content}
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', None)
    def test_no_api_key_env_var(self):
        """Test when API key environment variable is not set at all."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        assert result == {}
    
    @patch('src.metrics.data_fetcher.llm.PURDUE_GENAI_API_KEY', 'test-key')
    @patch('src.metrics.data_fetcher.llm.requests.post')
    def test_general_exception_handling(self, mock_post):
        """Test handling of general exceptions."""
        from src.metrics.data_fetcher.llm import get_genai_metric_data
        
        mock_post.side_effect = Exception("Unexpected error")
        
        result = get_genai_metric_data("https://github.com/test/repo", "Test prompt")
        
        assert result == {}
        mock_post.assert_called_once()