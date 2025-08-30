#!/usr/bin/env python3
"""
Unit tests for CostAnalyzer and cost tracking functionality.

Tests comprehensive cost tracking, multi-currency support, detailed reporting,
and cost optimization recommendations.
"""

import unittest
import tempfile
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cost_analyzer import CostAnalyzer, TokenUsage, ModelCostSummary, CostReport


class TestTokenUsage(unittest.TestCase):
    """Test the TokenUsage data class."""
    
    def test_token_usage_creation(self):
        """Test TokenUsage creation and attributes."""
        timestamp = datetime.now()
        usage = TokenUsage(
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
            timestamp=timestamp,
            document_name="test_doc.pdf",
            operation="core_assessment"
        )
        
        self.assertEqual(usage.model, "gpt-4")
        self.assertEqual(usage.input_tokens, 1000)
        self.assertEqual(usage.output_tokens, 500)
        self.assertEqual(usage.timestamp, timestamp)
        self.assertEqual(usage.document_name, "test_doc.pdf")
        self.assertEqual(usage.operation, "core_assessment")


class TestModelCostSummary(unittest.TestCase):
    """Test the ModelCostSummary data class."""
    
    def test_model_cost_summary_creation(self):
        """Test ModelCostSummary creation and calculations."""
        summary = ModelCostSummary(
            model="gpt-4",
            total_input_tokens=5000,
            total_output_tokens=2500,
            total_tokens=7500,
            input_cost_usd=0.15,
            output_cost_usd=0.15,
            total_cost_usd=0.30,
            api_calls=10
        )
        
        self.assertEqual(summary.model, "gpt-4")
        self.assertEqual(summary.total_tokens, 7500)
        self.assertEqual(summary.total_cost_usd, 0.30)
        self.assertEqual(summary.api_calls, 10)


class TestCostAnalyzer(unittest.TestCase):
    """Test the CostAnalyzer class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.pricing_config_path = Path(self.temp_dir) / "test_pricing.json"
        
        # Create test pricing configuration
        self.test_pricing_config = {
            "models": {
                "gpt-4": {
                    "input_cost_per_1k_tokens": 0.03,
                    "output_cost_per_1k_tokens": 0.06,
                    "currency": "USD"
                },
                "gpt-3.5-turbo": {
                    "input_cost_per_1k_tokens": 0.0015,
                    "output_cost_per_1k_tokens": 0.002,
                    "currency": "USD"
                },
                "claude-3-sonnet": {
                    "input_cost_per_1k_tokens": 0.003,
                    "output_cost_per_1k_tokens": 0.015,
                    "currency": "USD"
                }
            },
            "currency_rates": {
                "USD": 1.0,
                "EUR": 0.85,
                "CNY": 7.2,
                "GBP": 0.75
            },
            "last_updated": "2024-01-01"
        }
        
        # Save pricing configuration
        with open(self.pricing_config_path, 'w') as f:
            json.dump(self.test_pricing_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyzer_initialization(self):
        """Test CostAnalyzer initialization."""
        analyzer = CostAnalyzer(str(self.pricing_config_path), "test_session")
        
        self.assertEqual(analyzer.session_id, "test_session")
        self.assertIsNotNone(analyzer.start_time)
        self.assertEqual(len(analyzer.usage_records), 0)
        self.assertIn("models", analyzer.pricing_config)
        self.assertIn("currency_rates", analyzer.pricing_config)
    
    def test_analyzer_initialization_with_auto_session_id(self):
        """Test CostAnalyzer initialization with automatic session ID."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        self.assertTrue(analyzer.session_id.startswith("session_"))
        self.assertIsNotNone(analyzer.start_time)
    
    def test_pricing_config_loading(self):
        """Test pricing configuration loading and validation."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Check that all expected models are loaded
        self.assertIn("gpt-4", analyzer.pricing_config["models"])
        self.assertIn("gpt-3.5-turbo", analyzer.pricing_config["models"])
        self.assertIn("claude-3-sonnet", analyzer.pricing_config["models"])
        
        # Check currency rates
        self.assertEqual(analyzer.pricing_config["currency_rates"]["USD"], 1.0)
        self.assertEqual(analyzer.pricing_config["currency_rates"]["EUR"], 0.85)
    
    def test_pricing_config_validation_errors(self):
        """Test pricing configuration validation with missing sections."""
        # Test missing models section
        invalid_config = {"currency_rates": {"USD": 1.0}}
        invalid_path = Path(self.temp_dir) / "invalid.json"
        
        with open(invalid_path, 'w') as f:
            json.dump(invalid_config, f)
        
        with self.assertRaises(ValueError) as context:
            CostAnalyzer(str(invalid_path))
        
        self.assertIn("models", str(context.exception))
    
    def test_usage_tracking(self):
        """Test token usage tracking."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Track usage for different models
        analyzer.track_usage("gpt-4", 1000, 500, "doc1.pdf", "core_assessment")
        analyzer.track_usage("gpt-3.5-turbo", 800, 300, "doc2.pdf", "optional_assessment")
        analyzer.track_usage("gpt-4", 1200, 600, "doc3.pdf", "study_id_extraction")
        
        # Check usage records
        self.assertEqual(len(analyzer.usage_records), 3)
        
        # Check model usage aggregation
        self.assertIn("gpt-4", analyzer.model_usage)
        self.assertIn("gpt-3.5-turbo", analyzer.model_usage)
        
        gpt4_usage = analyzer.model_usage["gpt-4"]
        self.assertEqual(gpt4_usage["input_tokens"], 2200)  # 1000 + 1200
        self.assertEqual(gpt4_usage["output_tokens"], 1100)  # 500 + 600
        self.assertEqual(gpt4_usage["api_calls"], 2)
        self.assertEqual(len(gpt4_usage["documents"]), 2)  # doc1.pdf, doc3.pdf
    
    def test_cost_calculation(self):
        """Test cost calculation for different models."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Test GPT-4 cost calculation
        input_cost, output_cost, total_cost = analyzer.calculate_cost("gpt-4", 1000, 500)
        
        expected_input_cost = (1000 / 1000) * 0.03  # $0.03
        expected_output_cost = (500 / 1000) * 0.06  # $0.03
        expected_total = expected_input_cost + expected_output_cost  # $0.06
        
        self.assertAlmostEqual(input_cost, expected_input_cost, places=4)
        self.assertAlmostEqual(output_cost, expected_output_cost, places=4)
        self.assertAlmostEqual(total_cost, expected_total, places=4)
        
        # Test GPT-3.5-turbo cost calculation
        input_cost, output_cost, total_cost = analyzer.calculate_cost("gpt-3.5-turbo", 2000, 1000)
        
        expected_input_cost = (2000 / 1000) * 0.0015  # $0.003
        expected_output_cost = (1000 / 1000) * 0.002   # $0.002
        expected_total = expected_input_cost + expected_output_cost  # $0.005
        
        self.assertAlmostEqual(input_cost, expected_input_cost, places=4)
        self.assertAlmostEqual(output_cost, expected_output_cost, places=4)
        self.assertAlmostEqual(total_cost, expected_total, places=4)
    
    def test_cost_calculation_unknown_model(self):
        """Test cost calculation for unknown model."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        input_cost, output_cost, total_cost = analyzer.calculate_cost("unknown-model", 1000, 500)
        
        self.assertEqual(input_cost, 0.0)
        self.assertEqual(output_cost, 0.0)
        self.assertEqual(total_cost, 0.0)
    
    def test_currency_conversion(self):
        """Test currency conversion functionality."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Test USD to EUR conversion
        eur_amount = analyzer.convert_currency(10.0, "EUR")
        self.assertAlmostEqual(eur_amount, 8.5, places=2)  # 10.0 * 0.85
        
        # Test USD to CNY conversion
        cny_amount = analyzer.convert_currency(10.0, "CNY")
        self.assertAlmostEqual(cny_amount, 72.0, places=2)  # 10.0 * 7.2
        
        # Test USD to USD (should be same)
        usd_amount = analyzer.convert_currency(10.0, "USD")
        self.assertEqual(usd_amount, 10.0)
        
        # Test unsupported currency
        with self.assertRaises(ValueError):
            analyzer.convert_currency(10.0, "JPY")
    
    def test_model_summary_generation(self):
        """Test model cost summary generation."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Track some usage
        analyzer.track_usage("gpt-4", 2000, 1000, "doc1.pdf")
        analyzer.track_usage("gpt-4", 1000, 500, "doc2.pdf")
        
        summary = analyzer.get_model_summary("gpt-4")
        
        self.assertEqual(summary.model, "gpt-4")
        self.assertEqual(summary.total_input_tokens, 3000)
        self.assertEqual(summary.total_output_tokens, 1500)
        self.assertEqual(summary.total_tokens, 4500)
        self.assertEqual(summary.api_calls, 2)
        
        # Check cost calculations
        expected_input_cost = (3000 / 1000) * 0.03  # $0.09
        expected_output_cost = (1500 / 1000) * 0.06  # $0.09
        expected_total_cost = expected_input_cost + expected_output_cost  # $0.18
        
        self.assertAlmostEqual(summary.input_cost_usd, expected_input_cost, places=4)
        self.assertAlmostEqual(summary.output_cost_usd, expected_output_cost, places=4)
        self.assertAlmostEqual(summary.total_cost_usd, expected_total_cost, places=4)
    
    def test_model_summary_for_unused_model(self):
        """Test model summary for model with no usage."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        summary = analyzer.get_model_summary("gpt-4")
        
        self.assertEqual(summary.model, "gpt-4")
        self.assertEqual(summary.total_tokens, 0)
        self.assertEqual(summary.total_cost_usd, 0.0)
        self.assertEqual(summary.api_calls, 0)
    
    def test_overall_cost_summary(self):
        """Test overall cost summary generation."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Track usage for multiple models
        analyzer.track_usage("gpt-4", 1000, 500, "doc1.pdf")
        analyzer.track_usage("gpt-3.5-turbo", 2000, 1000, "doc2.pdf")
        analyzer.track_usage("gpt-4", 800, 400, "doc3.pdf")
        
        summary = analyzer.get_cost_summary()
        
        self.assertEqual(summary["session_id"], analyzer.session_id)
        self.assertEqual(summary["total_api_calls"], 3)
        self.assertEqual(summary["models_used"], 2)
        self.assertIn("total_cost_usd", summary)
        self.assertIn("total_tokens", summary)
        self.assertIn("model_summaries", summary)
        
        # Check that model summaries are included
        model_summaries = summary["model_summaries"]
        self.assertEqual(len(model_summaries), 2)
        
        # Find GPT-4 summary
        gpt4_summary = next(s for s in model_summaries if s["model"] == "gpt-4")
        self.assertEqual(gpt4_summary["total_input_tokens"], 1800)  # 1000 + 800
        self.assertEqual(gpt4_summary["total_output_tokens"], 900)   # 500 + 400
        self.assertEqual(gpt4_summary["api_calls"], 2)
    
    def test_cost_optimization_recommendations(self):
        """Test cost optimization recommendation generation."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Track usage with different cost patterns
        # GPT-4 is more expensive per token
        analyzer.track_usage("gpt-4", 1000, 500, "doc1.pdf")
        analyzer.track_usage("gpt-4", 1000, 500, "doc2.pdf")
        
        # GPT-3.5-turbo is cheaper per token
        analyzer.track_usage("gpt-3.5-turbo", 1000, 500, "doc3.pdf")
        
        recommendations = analyzer.generate_recommendations()
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Should recommend using cheaper model
        recommendation_text = " ".join(recommendations).lower()
        self.assertTrue(
            "gpt-3.5-turbo" in recommendation_text or 
            "cheaper" in recommendation_text or
            "cost" in recommendation_text
        )
    
    def test_high_output_ratio_recommendation(self):
        """Test recommendation for high output-to-input ratio."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Track usage with high output ratio
        analyzer.track_usage("gpt-4", 1000, 800, "doc1.pdf")  # 0.8 ratio
        analyzer.track_usage("gpt-4", 1000, 700, "doc2.pdf")  # 0.7 ratio
        
        recommendations = analyzer.generate_recommendations()
        
        # Should recommend optimizing prompts
        recommendation_text = " ".join(recommendations).lower()
        self.assertTrue(
            "output" in recommendation_text or 
            "prompt" in recommendation_text or
            "ratio" in recommendation_text
        )
    
    def test_high_cost_warning_recommendation(self):
        """Test recommendation for high total cost."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Track high-cost usage (simulate expensive operations)
        for i in range(50):  # Many expensive calls
            analyzer.track_usage("gpt-4", 2000, 1000, f"doc{i}.pdf")
        
        recommendations = analyzer.generate_recommendations()
        
        # Should warn about high cost
        recommendation_text = " ".join(recommendations).lower()
        self.assertTrue(
            "high" in recommendation_text and "cost" in recommendation_text or
            "batch" in recommendation_text or
            "cheaper" in recommendation_text
        )
    
    def test_detailed_log_saving(self):
        """Test saving detailed usage log."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Track some usage
        analyzer.track_usage("gpt-4", 1000, 500, "doc1.pdf", "core_assessment")
        analyzer.track_usage("gpt-3.5-turbo", 800, 300, "doc2.pdf", "optional_assessment")
        
        # Save detailed log
        log_path = Path(self.temp_dir) / "detailed_log.json"
        analyzer.save_detailed_log(str(log_path))
        
        self.assertTrue(log_path.exists())
        
        # Load and verify log content
        with open(log_path, 'r') as f:
            log_data = json.load(f)
        
        self.assertEqual(log_data["session_id"], analyzer.session_id)
        self.assertIn("usage_records", log_data)
        self.assertIn("summary", log_data)
        self.assertEqual(len(log_data["usage_records"]), 2)
        
        # Check usage record structure
        record = log_data["usage_records"][0]
        self.assertIn("model", record)
        self.assertIn("input_tokens", record)
        self.assertIn("output_tokens", record)
        self.assertIn("timestamp", record)
        self.assertIn("document_name", record)
        self.assertIn("operation", record)
    
    def test_session_reset(self):
        """Test session reset functionality."""
        analyzer = CostAnalyzer(str(self.pricing_config_path), "original_session")
        
        # Track some usage
        analyzer.track_usage("gpt-4", 1000, 500, "doc1.pdf")
        
        original_session_id = analyzer.session_id
        original_start_time = analyzer.start_time
        
        # Reset session
        analyzer.reset_session("new_session")
        
        self.assertEqual(analyzer.session_id, "new_session")
        self.assertNotEqual(analyzer.session_id, original_session_id)
        self.assertGreater(analyzer.start_time, original_start_time)
        self.assertEqual(len(analyzer.usage_records), 0)
        self.assertEqual(len(analyzer.model_usage), 0)
    
    def test_session_reset_with_auto_id(self):
        """Test session reset with automatic ID generation."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        original_session_id = analyzer.session_id
        
        # Reset without providing new ID
        analyzer.reset_session()
        
        self.assertNotEqual(analyzer.session_id, original_session_id)
        self.assertTrue(analyzer.session_id.startswith("session_"))
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        analyzer = CostAnalyzer(str(self.pricing_config_path))
        
        # Test with zero tokens
        analyzer.track_usage("gpt-4", 0, 0, "empty_doc.pdf")
        summary = analyzer.get_model_summary("gpt-4")
        self.assertEqual(summary.total_cost_usd, 0.0)
        
        # Test with very large token counts
        analyzer.track_usage("gpt-4", 1000000, 500000, "large_doc.pdf")
        large_summary = analyzer.get_model_summary("gpt-4")
        self.assertGreater(large_summary.total_cost_usd, 0)
        
        # Test recommendations with no usage
        empty_analyzer = CostAnalyzer(str(self.pricing_config_path))
        recommendations = empty_analyzer.generate_recommendations()
        self.assertIn("No usage data", recommendations[0])


if __name__ == '__main__':
    unittest.main()