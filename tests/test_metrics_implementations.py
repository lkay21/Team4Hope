"""
Comprehensive tests for all metric implementations.

Tests each metric class for calculation accuracy, edge cases,
and error handling based on actual implementation structure.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.metrics.impl.availability import AvailabilityMetric
from src.metrics.impl.bus_factor import BusFactorMetric
from src.metrics.impl.code_quality import CodeQualityMetric
from src.metrics.impl.dataset_quality import DatasetQualityMetric
from src.metrics.impl.license_compliance import LicenseComplianceMetric
from src.metrics.impl.performance_claims import PerformanceClaimsMetric
from src.metrics.impl.ramp_up_time import RampUpTimeMetric
from src.metrics.impl.size import SizeMetric


class TestAvailabilityMetric:
    """Test the AvailabilityMetric class."""

    def test_availability_all_components(self):
        """Test availability with all components present."""
        context = {
            "availability": {
                "has_code": True,
                "has_dataset": True,
                "links_ok": True
            }
        }
        
        metric = AvailabilityMetric()
        result = metric.compute(context)
        
        assert result.value == 1.0
        assert result.id == "availability"
        assert result.details["has_code"] is True
        assert result.details["has_dataset"] is True
        assert result.details["links_ok"] is True

    def test_availability_partial_components(self):
        """Test availability with some components missing."""
        context = {
            "availability": {
                "has_code": True,
                "has_dataset": False,
                "links_ok": True
            }
        }
        
        metric = AvailabilityMetric()
        result = metric.compute(context)
        
        # 2 out of 3 components = 2/3 ≈ 0.67
        assert abs(result.value - (2/3)) < 0.01

    def test_availability_no_components(self):
        """Test availability with no components."""
        context = {
            "availability": {
                "has_code": False,
                "has_dataset": False,
                "links_ok": False
            }
        }
        
        metric = AvailabilityMetric()
        result = metric.compute(context)
        
        assert result.value == 0.0

    def test_availability_no_data(self):
        """Test availability metric without availability data."""
        context = {}
        
        metric = AvailabilityMetric()
        result = metric.compute(context)
        
        assert result.value == 0.0

    def test_availability_timing(self):
        """Test that availability metric records timing."""
        context = {"availability": {"has_code": True, "has_dataset": True, "links_ok": True}}
        
        metric = AvailabilityMetric()
        result = metric.compute(context)
        
        assert result.seconds >= 0
        assert isinstance(result.seconds, float)


class TestBusFactorMetric:
    """Test the BusFactorMetric class."""

    def test_bus_factor_low_top_contributor(self):
        """Test bus factor with low top contributor percentage."""
        context = {
            "repo_meta": {
                "top_contributor_pct": 0.2  # 20% from top contributor
            }
        }
        
        metric = BusFactorMetric()
        result = metric.compute(context)
        
        # Should return 1 - 0.2 = 0.8
        assert abs(result.value - 0.8) < 0.01
        assert result.id == "bus_factor"

    def test_bus_factor_high_top_contributor(self):
        """Test bus factor with high top contributor percentage."""
        context = {
            "repo_meta": {
                "top_contributor_pct": 0.9  # 90% from top contributor
            }
        }
        
        metric = BusFactorMetric()
        result = metric.compute(context)
        
        # Should return 1 - 0.9 = 0.1
        assert abs(result.value - 0.1) < 0.01

    def test_bus_factor_single_contributor(self):
        """Test bus factor with single contributor (100%)."""
        context = {
            "repo_meta": {
                "top_contributor_pct": 1.0  # 100% from top contributor
            }
        }
        
        metric = BusFactorMetric()
        result = metric.compute(context)
        
        # Should return 1 - 1.0 = 0.0
        assert result.value == 0.0

    def test_bus_factor_no_data(self):
        """Test bus factor without repo meta data."""
        context = {}
        
        metric = BusFactorMetric()
        result = metric.compute(context)
        
        # Default top_contributor_pct is 1.0, so result should be 0.0
        assert result.value == 0.0

    def test_bus_factor_edge_cases(self):
        """Test bus factor with edge case values."""
        # Test with 0% (impossible but edge case)
        context = {"repo_meta": {"top_contributor_pct": 0.0}}
        metric = BusFactorMetric()
        result = metric.compute(context)
        assert result.value == 1.0
        
        # Test with negative (should be clamped)
        context = {"repo_meta": {"top_contributor_pct": -0.1}}
        metric = BusFactorMetric()
        result = metric.compute(context)
        assert result.value == 1.0  # max(0, min(1, 1 - (-0.1))) = 1.0


class TestLicenseComplianceMetric:
    """Test the LicenseComplianceMetric class."""

    def test_license_compliance_mit(self):
        """Test license compliance with MIT license."""
        context = {"license": "MIT"}
        
        metric = LicenseComplianceMetric()
        result = metric.compute(context)
        
        assert result.value == 1.0
        assert result.id == "license_compliance"
        assert "mit" in result.details["license"]

    def test_license_compliance_apache(self):
        """Test license compliance with Apache license."""
        context = {"license": "Apache-2.0"}
        
        metric = LicenseComplianceMetric()
        result = metric.compute(context)
        
        assert result.value == 1.0
        assert "apache-2.0" in result.details["license"]

    def test_license_compliance_proprietary(self):
        """Test license compliance with proprietary license."""
        context = {"license": "Proprietary"}
        
        metric = LicenseComplianceMetric()
        result = metric.compute(context)
        
        assert result.value == 0.0

    def test_license_compliance_no_license(self):
        """Test license compliance without license."""
        context = {}
        
        metric = LicenseComplianceMetric()
        result = metric.compute(context)
        
        assert result.value == 0.0

    def test_license_compliance_custom_allowed(self):
        """Test license compliance with custom allowed licenses."""
        context = {
            "license": "GPL-3.0",
            "compatible_licenses": ["gpl-3.0", "bsd"]
        }
        
        metric = LicenseComplianceMetric()
        result = metric.compute(context)
        
        assert result.value == 1.0

    def test_license_compliance_partial_match(self):
        """Test license compliance with partial string match."""
        context = {"license": "MIT License with additional terms"}
        
        metric = LicenseComplianceMetric()
        result = metric.compute(context)
        
        # Should match because "mit" is in the string
        assert result.value == 1.0


class TestPerformanceClaimsMetric:
    """Test the PerformanceClaimsMetric class."""

    def test_performance_claims_bert_model(self):
        """Test performance claims with BERT model (should get 1.0)."""
        context = {"model_url": "https://huggingface.co/bert-base-uncased"}
        
        metric = PerformanceClaimsMetric()
        result = metric.compute(context)
        
        assert result.value == 1.0
        assert result.id == "performance_claims"
        assert result.details["mode"] == "binary"
        assert result.details["has_performance_claims"] == True

    def test_performance_claims_whisper_model(self):
        """Test performance claims with Whisper model (should get 1.0)."""
        context = {"model_url": "https://huggingface.co/openai/whisper-tiny"}
        
        metric = PerformanceClaimsMetric()
        result = metric.compute(context)
        
        assert result.value == 1.0
        assert result.details["mode"] == "binary"
        assert result.details["has_performance_claims"] == True

    def test_performance_claims_unknown_model(self):
        """Test performance claims with unknown model (should get 0.0)."""
        context = {"model_url": "https://huggingface.co/random/unknown-model"}
        
        metric = PerformanceClaimsMetric()
        result = metric.compute(context)
        
        assert result.value == 0.0
        assert result.details["mode"] == "binary"
        assert result.details["has_performance_claims"] == False

    def test_performance_claims_high_popularity_model(self):
        """Test performance claims with high popularity model (should get 1.0)."""
        context = {
            "model_url": "https://huggingface.co/some/model",
            "ramp": {"downloads_norm": 0.9, "likes_norm": 0.85}
        }
        
        metric = PerformanceClaimsMetric()
        result = metric.compute(context)
        
        assert result.value == 1.0
        assert result.details["has_performance_claims"] == True

    def test_performance_claims_complete_package(self):
        """Test performance claims with complete package (code + dataset + model)."""
        context = {
            "model_url": "https://huggingface.co/some/model",
            "availability": {
                "has_code": True,
                "has_dataset": True, 
                "has_model": True
            }
        }
        
        metric = PerformanceClaimsMetric()
        result = metric.compute(context)
        
        assert result.value == 1.0
        assert result.details["has_performance_claims"] == True

    def test_performance_claims_none_passed(self):
        """Test performance claims with no requirements passed."""
        context = {
            "requirements_passed": 0,
            "requirements_total": 5
        }
        
        metric = PerformanceClaimsMetric()
        result = metric.compute(context)
        
        assert result.value == 0.0

    def test_performance_claims_no_data(self):
        """Test performance claims without data."""
        context = {}
        
        metric = PerformanceClaimsMetric()
        result = metric.compute(context)
        
        # Should default to 0.0 for binary approach
        assert result.value == 0.0
        assert result.details["mode"] == "binary"
        assert result.details["has_performance_claims"] == False

    def test_performance_claims_no_model_url(self):
        """Test performance claims with no model URL."""
        context = {"some_other_field": "value"}
        
        metric = PerformanceClaimsMetric()
        result = metric.compute(context)
        
        # Should default to 0.0 without model URL
        assert result.value == 0.0
        assert result.details["has_performance_claims"] == False


class TestCodeQualityMetric:
    """Test the CodeQualityMetric class."""

    def test_code_quality_all_components(self):
        """Test code quality with all components."""
        context = {
            "code_quality": {
                "test_coverage_norm": 0.8,
                "style_norm": 0.7,
                "comment_ratio_norm": 0.6,
                "maintainability_norm": 0.9
            }
        }
        
        metric = CodeQualityMetric()
        result = metric.compute(context)
        
        # Mean of all components: (0.8 + 0.7 + 0.6 + 0.9) / 4 = 0.75
        expected = (0.8 + 0.7 + 0.6 + 0.9) / 4
        assert abs(result.value - expected) < 0.01
        assert result.id == "code_quality"
        assert len(result.details["components"]) == 4

    def test_code_quality_partial_components(self):
        """Test code quality with some missing components."""
        context = {
            "code_quality": {
                "test_coverage_norm": 0.9,
                "maintainability_norm": 0.8
                # Missing style_norm and comment_ratio_norm
            }
        }
        
        metric = CodeQualityMetric()
        result = metric.compute(context)
        
        # Mean of available components: (0.9 + 0.8) / 2 = 0.85
        expected = (0.9 + 0.8) / 2
        assert abs(result.value - expected) < 0.01
        assert len(result.details["components"]) == 2

    def test_code_quality_no_components(self):
        """Test code quality without any components."""
        context = {"code_quality": {}}
        
        metric = CodeQualityMetric()
        result = metric.compute(context)
        
        assert result.value == 0.0
        assert result.details["components"] == []

    def test_code_quality_no_data(self):
        """Test code quality without code_quality data."""
        context = {}
        
        metric = CodeQualityMetric()
        result = metric.compute(context)
        
        assert result.value == 0.0
        assert result.details["components"] == []

    def test_code_quality_single_component(self):
        """Test code quality with single component."""
        context = {
            "code_quality": {
                "test_coverage_norm": 0.95
            }
        }
        
        metric = CodeQualityMetric()
        result = metric.compute(context)
        
        assert result.value == 0.95
        assert len(result.details["components"]) == 1

    def test_code_quality_zero_values(self):
        """Test code quality with zero values."""
        context = {
            "code_quality": {
                "test_coverage_norm": 0.0,
                "style_norm": 0.0,
                "comment_ratio_norm": 0.0,
                "maintainability_norm": 0.0
            }
        }
        
        metric = CodeQualityMetric()
        result = metric.compute(context)
        
        assert result.value == 0.0
        assert len(result.details["components"]) == 4

    def test_code_quality_perfect_scores(self):
        """Test code quality with perfect scores."""
        context = {
            "code_quality": {
                "test_coverage_norm": 1.0,
                "style_norm": 1.0,
                "comment_ratio_norm": 1.0,
                "maintainability_norm": 1.0
            }
        }
        
        metric = CodeQualityMetric()
        result = metric.compute(context)
        
        assert result.value == 1.0
        assert len(result.details["components"]) == 4

    def test_code_quality_timing(self):
        """Test that code quality metric records timing."""
        context = {
            "code_quality": {
                "test_coverage_norm": 0.8,
                "style_norm": 0.7
            }
        }
        
        metric = CodeQualityMetric()
        result = metric.compute(context)
        
        assert result.seconds >= 0
        assert isinstance(result.seconds, float)


class TestSizeMetric:
    """Test the SizeMetric class."""

    def test_size_metric_all_hardware_scores(self):
        """Test size metric with all hardware scores."""
        context = {
            "size_components": {
                "raspberry_pi": 0.5,
                "jetson_nano": 0.8,
                "desktop_pc": 0.9,
                "aws_server": 0.95
            }
        }
        
        metric = SizeMetric()
        result = metric.compute(context)
        
        # Mean of all scores
        expected = (0.5 + 0.8 + 0.9 + 0.95) / 4
        assert abs(result.value - expected) < 0.01
        assert result.id == "size"

    def test_size_metric_partial_scores(self):
        """Test size metric with partial hardware scores."""
        context = {
            "size_components": {
                "raspberry_pi": 0.3,
                "desktop_pc": 0.8
                # Missing jetson_nano and aws_server
            }
        }
        
        metric = SizeMetric()
        result = metric.compute(context)
        
        # Mean including zeros for missing: (0.3 + 0.0 + 0.8 + 0.0) / 4
        expected = (0.3 + 0.0 + 0.8 + 0.0) / 4
        assert abs(result.value - expected) < 0.01

    def test_size_metric_no_scores(self):
        """Test size metric without size components."""
        context = {}
        
        metric = SizeMetric()
        result = metric.compute(context)
        
        assert result.value == 0.0

    def test_size_metric_details_storage(self):
        """Test that size metric stores details correctly."""
        context = {
            "size_components": {
                "raspberry_pi": 0.6,
                "jetson_nano": 0.7,
                "desktop_pc": 0.85,
                "aws_server": 0.9
            }
        }
        
        metric = SizeMetric()
        result = metric.compute(context)
        
        # Check that details are stored
        assert "size_score" in result.details
        
        size_scores = result.details["size_score"]
        assert size_scores["raspberry_pi"] == 0.6
        assert size_scores["jetson_nano"] == 0.7
        assert size_scores["desktop_pc"] == 0.85
        assert size_scores["aws_server"] == 0.9

    def test_size_metric_invalid_values(self):
        """Test size metric with invalid values."""
        context = {
            "size_components": {
                "raspberry_pi": "invalid",
                "jetson_nano": None,
                "desktop_pc": 0.8
            }
        }
        
        metric = SizeMetric()
        result = metric.compute(context)
        
        # Invalid values should be treated as 0.0
        # (0.0 + 0.0 + 0.8 + 0.0) / 4 = 0.2
        expected = 0.8 / 4
        assert abs(result.value - expected) < 0.01

    def test_size_metric_binary_flag(self):
        """Test size metric binary flag."""
        # With scores > 0
        context = {"size_components": {"raspberry_pi": 0.5}}
        metric = SizeMetric()
        result = metric.compute(context)
        assert result.binary == 1
        
        # With all scores = 0
        context = {"size_components": {"raspberry_pi": 0.0, "jetson_nano": 0.0}}
        metric = SizeMetric()
        result = metric.compute(context)
        assert result.binary == 0


class TestMetricIntegration:
    """Integration tests for metrics."""

    def test_all_metrics_basic_functionality(self):
        """Test that all metric classes can be instantiated and computed."""
        metrics = [
            AvailabilityMetric(),
            BusFactorMetric(),
            LicenseComplianceMetric(),
            PerformanceClaimsMetric(),
            SizeMetric()
        ]
        
        basic_context = {
            "availability": {"has_code": True, "has_dataset": True, "links_ok": True},
            "repo_meta": {"top_contributor_pct": 0.3},
            "license": "mit",
            "requirements_score": 0.7,
            "size_components": {"raspberry_pi": 0.5, "jetson_nano": 0.8}
        }
        
        for metric in metrics:
            result = metric.compute(basic_context)
            
            # All should return valid results
            assert hasattr(result, 'value')
            assert hasattr(result, 'id')
            assert hasattr(result, 'seconds')
            assert 0.0 <= result.value <= 1.0
            assert result.seconds >= 0

    def test_metrics_with_empty_context(self):
        """Test all metrics with empty context."""
        metrics = [
            AvailabilityMetric(),
            BusFactorMetric(), 
            LicenseComplianceMetric(),
            PerformanceClaimsMetric(),
            SizeMetric()
        ]
        
        empty_context = {}
        
        for metric in metrics:
            result = metric.compute(empty_context)
            
            # All should handle empty context gracefully
            assert 0.0 <= result.value <= 1.0
            assert result.seconds >= 0

    def test_metric_ids_unique(self):
        """Test that all metric IDs are unique."""
        metrics = [
            AvailabilityMetric(),
            BusFactorMetric(),
            LicenseComplianceMetric(), 
            PerformanceClaimsMetric(),
            SizeMetric()
        ]
        
        ids = [metric.id for metric in metrics]
        assert len(ids) == len(set(ids)), "Metric IDs should be unique"

    def test_metric_consistency(self):
        """Test that metrics return consistent results across multiple runs."""
        context = {
            "license": "apache-2.0",
            "requirements_score": 0.5,
            "size_components": {"raspberry_pi": 0.6}
        }
        
        # Run each metric multiple times
        for _ in range(3):
            license_metric = LicenseComplianceMetric()
            perf_metric = PerformanceClaimsMetric()
            size_metric = SizeMetric()
            
            license_result1 = license_metric.compute(context)
            license_result2 = license_metric.compute(context)
            
            perf_result1 = perf_metric.compute(context)
            perf_result2 = perf_metric.compute(context)
            
            size_result1 = size_metric.compute(context)
            size_result2 = size_metric.compute(context)
            
            # Results should be consistent (allowing for small timing differences)
            assert license_result1.value == license_result2.value
            assert perf_result1.value == perf_result2.value
            assert size_result1.value == size_result2.value

    def test_comprehensive_metric_computation(self):
        """Test metrics with comprehensive realistic data."""
        comprehensive_context = {
            "availability": {
                "has_code": True,
                "has_dataset": True,
                "links_ok": True
            },
            "repo_meta": {
                "top_contributor_pct": 0.25  # Good distribution
            },
            "license": "apache-2.0",
            "requirements_passed": 8,
            "requirements_total": 10,
            "size_components": {
                "raspberry_pi": 0.4,
                "jetson_nano": 0.7,
                "desktop_pc": 0.9,
                "aws_server": 0.95
            }
        }
        
        # Test all available metrics
        availability = AvailabilityMetric()
        bus_factor = BusFactorMetric()
        license_compliance = LicenseComplianceMetric()
        performance_claims = PerformanceClaimsMetric()
        size = SizeMetric()
        
        results = {}
        for metric in [availability, bus_factor, license_compliance, performance_claims, size]:
            result = metric.compute(comprehensive_context)
            results[result.id] = result.value
        
        # Check expected ranges for this data
        assert results["availability"] == 1.0  # All components present
        assert results["bus_factor"] == 0.75  # 1 - 0.25 = 0.75
        assert results["license_compliance"] == 1.0  # Apache-2.0 is approved
        assert results["performance_claims"] == 0.0  # No well-known model URL, so binary 0.0
        assert 0.7 <= results["size"] <= 0.8  # Mean of size components


if __name__ == "__main__":
    pytest.main([__file__])