#!/bin/bash
set -e

echo "🧹 Cleaning old coverage data..."
rm -f .coverage .coverage.* 
rm -rf htmlcov/

echo "✅ Running tests with coverage..."
COVERAGE_FILE=/tmp/.coverage pytest --cov=src --cov-report=term-missing "$@"
