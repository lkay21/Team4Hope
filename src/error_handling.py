"""
Standardized error handling for the Team4Hope project.
Provides custom exceptions and a utility for user-friendly error reporting.
"""
from typing import Optional
import sys
import logging

class Team4HopeError(Exception):
    """Base exception for all project errors."""
    pass

class InvalidURLError(Team4HopeError):
    """Raised when a URL is invalid or unsupported."""
    pass

class MetricCalculationError(Team4HopeError):
    """Raised when a metric cannot be calculated."""
    pass

class DependencyError(Team4HopeError):
    """Raised when a required dependency is missing or fails."""
    pass

def handle_error(e: Exception, message: Optional[str] = None, exit_code: int = 1):
    """
    Standardized error handler: logs, prints, and exits with code 1 (or given code).
    """
    if message:
        print(f"Error: {message}", file=sys.stderr)
    else:
        print(f"Error: {str(e)}", file=sys.stderr)
    logging.error(str(e))
    sys.exit(exit_code)
