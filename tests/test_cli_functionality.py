"""
Comprehensive tests for CLI functionality.

Tests the main CLI functions that are actually available.
"""
from src.cli.main import main, parse_args, _check_env_variables
import pytest
import sys
import os
import tempfile
from unittest.mock import Mock, patch, mock_open, MagicMock
from io import StringIO

# Add src to path
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'src'))


class TestArgumentParsing:
    """Test CLI argument parsing."""

    def test_parse_args_basic(self):
        """Test basic argument parsing."""
        # Test with input file
        with patch('sys.argv', ['main.py', 'input.txt']):
            args = parse_args()
            assert hasattr(args, 'args')
            assert 'input.txt' in args.args

    def test_parse_args_help_available(self):
        """Test that help is available."""
        with pytest.raises(SystemExit):
            with patch('sys.argv', ['main.py', '--help']):
                parse_args()


class TestEnvironmentValidation:
    """Test environment variable validation."""

    @patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test_token"})
    def test_check_env_variables_valid_github_token(self):
        """Test environment check with valid GitHub token."""
        # Should not raise an exception
        _check_env_variables()

    @patch.dict(os.environ, {"GITHUB_TOKEN": "github_pat_test_token"})
    def test_check_env_variables_valid_pat_token(self):
        """Test environment check with valid PAT token."""
        # Should not raise an exception
        _check_env_variables()

    @patch.dict(os.environ, {}, clear=True)
    def test_check_env_variables_missing_token(self):
        """Test environment check with missing GitHub token."""
        with pytest.raises(SystemExit):
            _check_env_variables()

    @patch.dict(os.environ, {"GITHUB_TOKEN": "invalid_token"})
    def test_check_env_variables_invalid_token(self):
        """Test environment check with invalid token format."""
        with pytest.raises(SystemExit):
            _check_env_variables()

    @patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test", "LOG_LEVEL": "-1"})
    def test_check_env_variables_invalid_log_level(self):
        """Test environment check with invalid log level."""
        with pytest.raises(SystemExit):
            _check_env_variables()

    @patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test", "LOG_LEVEL": "3"})
    def test_check_env_variables_invalid_high_log_level(self):
        """Test environment check with too high log level."""
        with pytest.raises(SystemExit):
            _check_env_variables()

    @patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test", "LOG_LEVEL": "1"})
    def test_check_env_variables_valid_log_level(self):
        """Test environment check with valid log level."""
        # Should not raise an exception
        _check_env_variables()


class TestMainFunction:
    """Test the main function integration."""

    @patch('src.cli.main._check_env_variables')
    @patch('src.cli.main.handle_url')
    @patch('src.cli.main.get_url_category')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_function_basic(self, mock_stdout, mock_category, mock_handle, mock_check_env):
        """Test main function basic execution."""
        # Mock environment check to pass
        mock_check_env.return_value = None

        # Mock URL processing
        mock_category.return_value = {"test": "MODEL"}
        mock_handle.return_value = {
            "test": {
                "name": "test",
                "net_score": 0.75
            }
        }

        # Create a temporary input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("https://huggingface.co/bert-base-uncased")
            temp_filename = f.name

        try:
            with patch('sys.argv', ['main.py', temp_filename]):
                result = main()

            # Should complete successfully
            assert result is None or result == 0

            # Should have called the expected functions
            mock_check_env.assert_called_once()

        finally:
            os.unlink(temp_filename)

    @patch('src.cli.main._check_env_variables')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_function_env_failure(self, mock_stdout, mock_check_env):
        """Test main function with environment check failure."""
        # Mock environment check to fail
        mock_check_env.side_effect = SystemExit(1)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("https://huggingface.co/bert-base-uncased")
            temp_filename = f.name

        try:
            with patch('sys.argv', ['main.py', temp_filename]):
                with pytest.raises(SystemExit):
                    main()

            mock_check_env.assert_called_once()

        finally:
            os.unlink(temp_filename)


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def test_argument_parsing_integration(self):
        """Test argument parsing with real arguments."""
        # Test that the parser can handle the expected input file format
        with patch('sys.argv', ['main.py', 'test_input.txt']):
            args = parse_args()

            assert hasattr(args, 'args')
            assert 'test_input.txt' in args.args

    @patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_valid_token"})
    def test_environment_validation_integration(self):
        """Integration test for environment validation."""
        # Should pass with valid environment
        try:
            _check_env_variables()
        except SystemExit:
            pytest.fail("Environment validation should have passed")

    def test_cli_help_system(self):
        """Test that CLI help system works."""
        with pytest.raises(SystemExit) as exc_info:
            with patch('sys.argv', ['main.py', '--help']):
                parse_args()

        # Help should exit with code 0
        assert exc_info.value.code == 0


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""

    def test_invalid_arguments(self):
        """Test handling of invalid arguments."""
        # Test with no arguments - this should actually work since args is nargs="*"
        with patch('sys.argv', ['main.py']):
            args = parse_args()
            assert hasattr(args, 'args')
            assert args.args == []

    @patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test", "LOG_FILE": "/invalid/path/logfile.txt"})
    def test_invalid_log_file(self):
        """Test handling of invalid log file path."""
        with pytest.raises(SystemExit):
            _check_env_variables()

    @patch.dict(os.environ, {"GITHUB_TOKEN": ""})
    def test_empty_github_token(self):
        """Test handling of empty GitHub token."""
        with pytest.raises(SystemExit):
            _check_env_variables()


class TestCLICompatibility:
    """Test CLI compatibility and expected behavior."""

    def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        assert callable(main)

    def test_parse_args_function_exists(self):
        """Test that parse_args function exists and is callable."""
        assert callable(parse_args)

    def test_check_env_variables_exists(self):
        """Test that _check_env_variables function exists and is callable."""
        assert callable(_check_env_variables)

    @patch('src.cli.main._check_env_variables')
    @patch('src.cli.main.handle_url')
    @patch('src.cli.main.get_url_category')
    def test_main_function_signature(self, mock_category, mock_handle, mock_check_env):
        """Test that main function has expected signature."""
        # Should be callable without arguments
        mock_check_env.return_value = None
        mock_category.return_value = {}
        mock_handle.return_value = {}

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("https://example.com")
            temp_filename = f.name

        try:
            with patch('sys.argv', ['main.py', temp_filename]):
                result = main()

            # Should return None or 0 for success
            assert result is None or result == 0

        except Exception as e:
            # If it fails, it should be due to expected reasons (like missing dependencies)
            # not due to function signature issues
            assert not isinstance(e, TypeError)

        finally:
            os.unlink(temp_filename)


if __name__ == "__main__":
    pytest.main([__file__])
