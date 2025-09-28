"""
Tests for error handling module.
"""
from src.error_handling import (
    Team4HopeError, InvalidURLError, MetricCalculationError,
    DependencyError, handle_error
)
import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src to path
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'src'))


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_team4hope_error(self):
        """Test base Team4HopeError exception."""
        error = Team4HopeError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_invalid_url_error(self):
        """Test InvalidURLError exception."""
        error = InvalidURLError("Invalid URL provided")
        assert str(error) == "Invalid URL provided"
        assert isinstance(error, Team4HopeError)
        assert isinstance(error, Exception)

    def test_metric_calculation_error(self):
        """Test MetricCalculationError exception."""
        error = MetricCalculationError("Cannot calculate metric")
        assert str(error) == "Cannot calculate metric"
        assert isinstance(error, Team4HopeError)
        assert isinstance(error, Exception)

    def test_dependency_error(self):
        """Test DependencyError exception."""
        error = DependencyError("Missing dependency")
        assert str(error) == "Missing dependency"
        assert isinstance(error, Team4HopeError)
        assert isinstance(error, Exception)


class TestHandleError:
    """Test the handle_error function."""

    @patch('sys.stderr', new_callable=StringIO)
    @patch('logging.error')
    def test_handle_error_with_custom_message(self, mock_log, mock_stderr):
        """Test handle_error with custom message."""
        test_exception = ValueError("Original error")

        with pytest.raises(SystemExit) as exc_info:
            handle_error(test_exception, "Custom error message", 1)

        assert exc_info.value.code == 1
        assert "Error: Custom error message" in mock_stderr.getvalue()
        mock_log.assert_called_once_with("Original error")

    @patch('sys.stderr', new_callable=StringIO)
    @patch('logging.error')
    def test_handle_error_without_custom_message(self, mock_log, mock_stderr):
        """Test handle_error without custom message."""
        test_exception = ValueError("Test error")

        with pytest.raises(SystemExit) as exc_info:
            handle_error(test_exception)

        assert exc_info.value.code == 1
        assert "Error: Test error" in mock_stderr.getvalue()
        mock_log.assert_called_once_with("Test error")

    @patch('sys.stderr', new_callable=StringIO)
    @patch('logging.error')
    def test_handle_error_custom_exit_code(self, mock_log, mock_stderr):
        """Test handle_error with custom exit code."""
        test_exception = RuntimeError("Runtime error")

        with pytest.raises(SystemExit) as exc_info:
            handle_error(test_exception, "Custom message", 42)

        assert exc_info.value.code == 42
        assert "Error: Custom message" in mock_stderr.getvalue()
        mock_log.assert_called_once_with("Runtime error")

    @patch('sys.stderr', new_callable=StringIO)
    @patch('logging.error')
    def test_handle_error_with_team4hope_error(self, mock_log, mock_stderr):
        """Test handle_error with Team4HopeError."""
        test_exception = InvalidURLError("Bad URL")

        with pytest.raises(SystemExit) as exc_info:
            handle_error(test_exception, None, 2)

        assert exc_info.value.code == 2
        assert "Error: Bad URL" in mock_stderr.getvalue()
        mock_log.assert_called_once_with("Bad URL")
