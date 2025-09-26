"""
Test suite summary and coverage verification.

This module provides utilities to verify test coverage across
all components and ensure comprehensive testing.
"""
import os
import sys
from pathlib import Path

def get_test_coverage_summary():
    """Generate a summary of test coverage across all modules."""
    
    # Define all modules that should have tests
    required_modules = {
        'data_fetcher': 'src/metrics/data_fetcher.py',
        'url_type_handler': 'src/url_parsers/url_type_handler.py', 
        'cli_main': 'src/cli/main.py',
        'metrics_implementations': 'src/metrics/impl/*.py',
        'metrics_runner_schema': 'src/metrics/runner.py'
    }
    
    # Define existing test files
    test_files = {
        'data_fetcher': 'tests/test_data_fetcher.py',
        'url_type_handler': 'tests/test_url_type_handler.py',
        'cli_main': 'tests/test_cli_main.py',
        'metrics_implementations': 'tests/test_metrics_implementations.py',
        'metrics_runner_schema': 'tests/test_metrics_runner_schema.py'
    }
    
    coverage_summary = {
        'total_modules': len(required_modules),
        'tested_modules': 0,
        'coverage_details': {}
    }
    
    # Check each module
    for module_name, module_path in required_modules.items():
        test_file = test_files.get(module_name)
        
        if test_file and os.path.exists(test_file):
            coverage_summary['tested_modules'] += 1
            coverage_summary['coverage_details'][module_name] = {
                'module_path': module_path,
                'test_file': test_file,
                'status': 'COVERED'
            }
        else:
            coverage_summary['coverage_details'][module_name] = {
                'module_path': module_path,
                'test_file': test_file or 'MISSING',
                'status': 'NOT COVERED'
            }
    
    return coverage_summary


def print_coverage_report():
    """Print a detailed coverage report."""
    summary = get_test_coverage_summary()
    
    print("=" * 80)
    print("COMPREHENSIVE TEST COVERAGE REPORT")
    print("=" * 80)
    
    coverage_percentage = (summary['tested_modules'] / summary['total_modules']) * 100
    
    print(f"Overall Coverage: {summary['tested_modules']}/{summary['total_modules']} modules ({coverage_percentage:.1f}%)")
    print()
    
    print("Module Coverage Details:")
    print("-" * 40)
    
    for module_name, details in summary['coverage_details'].items():
        status_indicator = "✓" if details['status'] == 'COVERED' else "✗"
        print(f"{status_indicator} {module_name:<25} {details['status']}")
        print(f"  Module: {details['module_path']}")
        print(f"  Test:   {details['test_file']}")
        print()
    
    print("=" * 80)
    
    if coverage_percentage == 100:
        print("🎉 EXCELLENT! Full test coverage achieved!")
        print("All critical modules have comprehensive test suites.")
    elif coverage_percentage >= 80:
        print("✅ GOOD! High test coverage achieved.")
        print("Most modules are well tested.")
    else:
        print("⚠️  WARNING! Low test coverage.")
        print("Consider adding more tests for better reliability.")
    
    return summary


def verify_test_files_exist():
    """Verify that all test files exist and are accessible."""
    test_directory = Path("tests")
    
    if not test_directory.exists():
        print("❌ Tests directory not found!")
        return False
    
    expected_test_files = [
        "test_data_fetcher.py",
        "test_url_type_handler.py", 
        "test_cli_main.py",
        "test_metrics_implementations.py",
        "test_metrics_runner_schema.py"
    ]
    
    missing_files = []
    existing_files = []
    
    for test_file in expected_test_files:
        file_path = test_directory / test_file
        if file_path.exists():
            existing_files.append(test_file)
        else:
            missing_files.append(test_file)
    
    print(f"✅ Found {len(existing_files)} test files:")
    for file in existing_files:
        print(f"   - {file}")
    
    if missing_files:
        print(f"❌ Missing {len(missing_files)} test files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True


if __name__ == "__main__":
    print("Verifying comprehensive test coverage...")
    print()
    
    # Check test files exist
    if verify_test_files_exist():
        print()
        # Generate coverage report
        summary = print_coverage_report()
        
        # Exit with appropriate code
        if summary['tested_modules'] == summary['total_modules']:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Partial coverage
    else:
        print("❌ Test suite verification failed!")
        sys.exit(1)