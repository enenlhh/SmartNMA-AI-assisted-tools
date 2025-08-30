#!/usr/bin/env python3
"""
Unit tests for configuration validation and error handling.

Tests configuration manager, pricing manager, and validation logic
to ensure proper error handling and configuration integrity.
"""

import unittest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_manager import ConfigManager, ConfigValidationError
from src.pricing_manager import PricingManager, PricingValidationError


class TestConfigManager(unittest.TestCase):
    """Test the ConfigManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Create valid test configuration
        self.valid_config = {
            "paths": {
                "input_folder": str(Path(self.temp_dir) / "input"),
                "output_folder": str(Path(self.temp_dir) / "output"),
                "temp_folder": str(Path(self.temp_dir) / "temp"),
                "llm_pricing_config": str(Path(self.temp_dir) / "pricing.json")
            },
            "processing": {
                "llm_output_mode": "json",
                "eval_optional_items": True,
                "max_text_length": 25000,
                "chunk_overlap": 200
            },
            "parallel": {
                "max_workers": 4,
                "batch_size": 10,
                "timeout_seconds": 300
            },
            "llm_models": [
                {
                    "model_name": "gpt-4",
                    "api_key": "test_key",
                    "base_url": "https://api.openai.com/v1"
                }
            ],
            "cost_tracking": {
                "enabled": True,
                "currency": "USD",
                "budget_limit": 100.0
            }
        }
        
        # Create input directory
        Path(self.temp_dir, "input").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_valid_config_loading(self):
        """Test loading a valid configuration."""
        with open(self.config_path, 'w') as f:
            json.dump(self.valid_config, f, indent=2)
        
        config_manager = ConfigManager(str(self.config_path))
        config = config_manager.load_config()
        
        self.assertIsNotNone(config)
        self.assertEqual(config.paths.input_folder, self.valid_config["paths"]["input_folder"])
        self.assertEqual(config.processing.llm_output_mode, "json")
        self.assertTrue(config.processing.eval_optional_items)
        self.assertEqual(len(config.llm_models), 1)
    
    def test_missing_required_sections(self):
        """Test validation with missing required sections."""
        invalid_configs = [
            {},  # Empty config
            {"paths": {}},  # Missing other sections
            {"processing": {}, "llm_models": []},  # Missing paths
            {"paths": {"input_folder": "/tmp"}}  # Missing processing and models
        ]
        
        for i, invalid_config in enumerate(invalid_configs):
            with self.subTest(config_index=i):
                config_path = Path(self.temp_dir) / f"invalid_{i}.json"
                with open(config_path, 'w') as f:
                    json.dump(invalid_config, f)
                
                config_manager = ConfigManager(str(config_path))
                with self.assertRaises(ConfigValidationError):
                    config_manager.load_config()
    
    def test_invalid_path_validation(self):
        """Test validation of invalid paths."""
        invalid_path_config = self.valid_config.copy()
        invalid_path_config["paths"]["input_folder"] = ""  # Empty path
        
        config_path = Path(self.temp_dir) / "invalid_paths.json"
        with open(config_path, 'w') as f:
            json.dump(invalid_path_config, f)
        
        config_manager = ConfigManager(str(config_path))
        with self.assertRaises(ConfigValidationError) as context:
            config_manager.load_config()
        
        self.assertIn("input_folder", str(context.exception))
    
    def test_invalid_processing_parameters(self):
        """Test validation of invalid processing parameters."""
        invalid_processing_configs = [
            {"max_text_length": -1000},  # Negative value
            {"max_text_length": "invalid"},  # Wrong type
            {"llm_output_mode": "invalid_mode"},  # Invalid mode
            {"chunk_overlap": -100}  # Negative overlap
        ]
        
        for i, invalid_processing in enumerate(invalid_processing_configs):
            with self.subTest(processing_index=i):
                invalid_config = self.valid_config.copy()
                invalid_config["processing"].update(invalid_processing)
                
                config_path = Path(self.temp_dir) / f"invalid_processing_{i}.json"
                with open(config_path, 'w') as f:
                    json.dump(invalid_config, f)
                
                config_manager = ConfigManager(str(config_path))
                with self.assertRaises(ConfigValidationError):
                    config_manager.load_config()
    
    def test_invalid_parallel_configuration(self):
        """Test validation of invalid parallel configuration."""
        invalid_parallel_configs = [
            {"max_workers": 0},  # Zero workers
            {"max_workers": -1},  # Negative workers
            {"batch_size": 0},  # Zero batch size
            {"timeout_seconds": -1}  # Negative timeout
        ]
        
        for i, invalid_parallel in enumerate(invalid_parallel_configs):
            with self.subTest(parallel_index=i):
                invalid_config = self.valid_config.copy()
                invalid_config["parallel"].update(invalid_parallel)
                
                config_path = Path(self.temp_dir) / f"invalid_parallel_{i}.json"
                with open(config_path, 'w') as f:
                    json.dump(invalid_config, f)
                
                config_manager = ConfigManager(str(config_path))
                with self.assertRaises(ConfigValidationError):
                    config_manager.load_config()
    
    def test_invalid_llm_models(self):
        """Test validation of invalid LLM model configurations."""
        invalid_model_configs = [
            [],  # No models
            [{"model_name": ""}],  # Empty model name
            [{"model_name": "gpt-4"}],  # Missing API key
            [{"model_name": "gpt-4", "api_key": ""}],  # Empty API key
        ]
        
        for i, invalid_models in enumerate(invalid_model_configs):
            with self.subTest(models_index=i):
                invalid_config = self.valid_config.copy()
                invalid_config["llm_models"] = invalid_models
                
                config_path = Path(self.temp_dir) / f"invalid_models_{i}.json"
                with open(config_path, 'w') as f:
                    json.dump(invalid_config, f)
                
                config_manager = ConfigManager(str(config_path))
                with self.assertRaises(ConfigValidationError):
                    config_manager.load_config()
    
    def test_template_config_creation(self):
        """Test creation of template configuration."""
        template_path = Path(self.temp_dir) / "template_config.json"
        
        config_manager = ConfigManager(str(self.config_path))
        config_manager.create_template_config(str(template_path))
        
        self.assertTrue(template_path.exists())
        
        # Load and validate template
        with open(template_path, 'r') as f:
            template_config = json.load(f)
        
        self.assertIn("paths", template_config)
        self.assertIn("processing", template_config)
        self.assertIn("parallel", template_config)
        self.assertIn("llm_models", template_config)
        
        # Template should be valid
        template_manager = ConfigManager(str(template_path))
        # Should not raise exception
        template_manager.load_config()
    
    def test_config_file_not_found(self):
        """Test handling of missing configuration file."""
        non_existent_path = Path(self.temp_dir) / "non_existent.json"
        
        config_manager = ConfigManager(str(non_existent_path))
        with self.assertRaises(FileNotFoundError):
            config_manager.load_config()
    
    def test_invalid_json_format(self):
        """Test handling of invalid JSON format."""
        invalid_json_path = Path(self.temp_dir) / "invalid.json"
        with open(invalid_json_path, 'w') as f:
            f.write("{ invalid json content")
        
        config_manager = ConfigManager(str(invalid_json_path))
        with self.assertRaises(json.JSONDecodeError):
            config_manager.load_config()
    
    def test_cost_tracking_validation(self):
        """Test cost tracking configuration validation."""
        invalid_cost_configs = [
            {"enabled": True, "currency": "INVALID"},  # Invalid currency
            {"enabled": True, "budget_limit": -100},  # Negative budget
            {"enabled": "invalid"}  # Wrong type for enabled
        ]
        
        for i, invalid_cost in enumerate(invalid_cost_configs):
            with self.subTest(cost_index=i):
                invalid_config = self.valid_config.copy()
                invalid_config["cost_tracking"] = invalid_cost
                
                config_path = Path(self.temp_dir) / f"invalid_cost_{i}.json"
                with open(config_path, 'w') as f:
                    json.dump(invalid_config, f)
                
                config_manager = ConfigManager(str(config_path))
                with self.assertRaises(ConfigValidationError):
                    config_manager.load_config()


class TestPricingManager(unittest.TestCase):
    """Test the PricingManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.pricing_path = Path(self.temp_dir) / "test_pricing.json"
        
        # Create valid pricing configuration
        self.valid_pricing = {
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
                }
            },
            "currency_rates": {
                "USD": 1.0,
                "EUR": 0.85,
                "CNY": 7.2
            },
            "last_updated": "2024-01-01"
        }
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_valid_pricing_loading(self):
        """Test loading valid pricing configuration."""
        with open(self.pricing_path, 'w') as f:
            json.dump(self.valid_pricing, f, indent=2)
        
        pricing_manager = PricingManager(str(self.pricing_path))
        pricing_config = pricing_manager.load_pricing_config()
        
        self.assertIsNotNone(pricing_config)
        self.assertIn("models", pricing_config)
        self.assertIn("currency_rates", pricing_config)
        
        # Test model retrieval
        models = pricing_manager.get_supported_models()
        self.assertIn("gpt-4", models)
        self.assertIn("gpt-3.5-turbo", models)
    
    def test_missing_required_sections(self):
        """Test validation with missing required sections."""
        invalid_pricing_configs = [
            {},  # Empty config
            {"models": {}},  # Missing currency_rates
            {"currency_rates": {}},  # Missing models
        ]
        
        for i, invalid_pricing in enumerate(invalid_pricing_configs):
            with self.subTest(pricing_index=i):
                pricing_path = Path(self.temp_dir) / f"invalid_pricing_{i}.json"
                with open(pricing_path, 'w') as f:
                    json.dump(invalid_pricing, f)
                
                pricing_manager = PricingManager(str(pricing_path))
                with self.assertRaises(PricingValidationError):
                    pricing_manager.load_pricing_config()
    
    def test_invalid_model_pricing(self):
        """Test validation of invalid model pricing."""
        invalid_model_configs = [
            {"input_cost_per_1k_tokens": -0.01},  # Negative cost
            {"input_cost_per_1k_tokens": "invalid"},  # Wrong type
            {"output_cost_per_1k_tokens": -0.01},  # Negative cost
            {}  # Missing required fields
        ]
        
        for i, invalid_model in enumerate(invalid_model_configs):
            with self.subTest(model_index=i):
                invalid_pricing = self.valid_pricing.copy()
                invalid_pricing["models"]["invalid_model"] = invalid_model
                
                pricing_path = Path(self.temp_dir) / f"invalid_model_{i}.json"
                with open(pricing_path, 'w') as f:
                    json.dump(invalid_pricing, f)
                
                pricing_manager = PricingManager(str(pricing_path))
                with self.assertRaises(PricingValidationError):
                    pricing_manager.load_pricing_config()
    
    def test_invalid_currency_rates(self):
        """Test validation of invalid currency rates."""
        invalid_currency_configs = [
            {"USD": -1.0},  # Negative rate
            {"USD": "invalid"},  # Wrong type
            {}  # Missing USD base rate
        ]
        
        for i, invalid_currency in enumerate(invalid_currency_configs):
            with self.subTest(currency_index=i):
                invalid_pricing = self.valid_pricing.copy()
                invalid_pricing["currency_rates"] = invalid_currency
                
                pricing_path = Path(self.temp_dir) / f"invalid_currency_{i}.json"
                with open(pricing_path, 'w') as f:
                    json.dump(invalid_pricing, f)
                
                pricing_manager = PricingManager(str(pricing_path))
                with self.assertRaises(PricingValidationError):
                    pricing_manager.load_pricing_config()
    
    def test_cost_calculation(self):
        """Test cost calculation functionality."""
        with open(self.pricing_path, 'w') as f:
            json.dump(self.valid_pricing, f, indent=2)
        
        pricing_manager = PricingManager(str(self.pricing_path))
        pricing_manager.load_pricing_config()
        
        # Test valid cost calculation
        cost, currency = pricing_manager.calculate_cost("gpt-4", 1000, 500)
        expected_cost = (1000 / 1000) * 0.03 + (500 / 1000) * 0.06  # $0.06
        
        self.assertAlmostEqual(cost, expected_cost, places=4)
        self.assertEqual(currency, "USD")
        
        # Test currency conversion
        cost_eur, currency_eur = pricing_manager.calculate_cost("gpt-4", 1000, 500, "EUR")
        expected_cost_eur = expected_cost * 0.85
        
        self.assertAlmostEqual(cost_eur, expected_cost_eur, places=4)
        self.assertEqual(currency_eur, "EUR")
    
    def test_model_matching(self):
        """Test model name matching functionality."""
        with open(self.pricing_path, 'w') as f:
            json.dump(self.valid_pricing, f, indent=2)
        
        pricing_manager = PricingManager(str(self.pricing_path))
        pricing_manager.load_pricing_config()
        
        # Test exact match
        pricing = pricing_manager.get_model_pricing("gpt-4")
        self.assertIsNotNone(pricing)
        self.assertEqual(pricing["input_cost_per_1k_tokens"], 0.03)
        
        # Test case insensitive match
        pricing = pricing_manager.get_model_pricing("GPT-4")
        self.assertIsNotNone(pricing)
        
        # Test non-existent model
        pricing = pricing_manager.get_model_pricing("non-existent-model")
        self.assertIsNone(pricing)
    
    def test_default_pricing_creation(self):
        """Test creation of default pricing configuration."""
        default_path = Path(self.temp_dir) / "default_pricing.json"
        
        pricing_manager = PricingManager(str(self.pricing_path))
        pricing_manager.create_default_pricing_config(str(default_path))
        
        self.assertTrue(default_path.exists())
        
        # Load and validate default config
        default_manager = PricingManager(str(default_path))
        default_config = default_manager.load_pricing_config()
        
        self.assertIn("models", default_config)
        self.assertIn("currency_rates", default_config)
        self.assertGreater(len(default_config["models"]), 0)
    
    def test_supported_currencies(self):
        """Test getting supported currencies."""
        with open(self.pricing_path, 'w') as f:
            json.dump(self.valid_pricing, f, indent=2)
        
        pricing_manager = PricingManager(str(self.pricing_path))
        pricing_manager.load_pricing_config()
        
        currencies = pricing_manager.get_supported_currencies()
        self.assertIn("USD", currencies)
        self.assertIn("EUR", currencies)
        self.assertIn("CNY", currencies)
        self.assertEqual(len(currencies), 3)


class TestErrorHandling(unittest.TestCase):
    """Test error handling across configuration components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_validation_error_details(self):
        """Test that ConfigValidationError provides detailed error information."""
        config_path = Path(self.temp_dir) / "invalid_config.json"
        
        # Create config with multiple validation errors
        invalid_config = {
            "paths": {
                "input_folder": "",  # Empty path
                "output_folder": "/non/existent/path"
            },
            "processing": {
                "max_text_length": -1000,  # Negative value
                "llm_output_mode": "invalid_mode"  # Invalid mode
            },
            "parallel": {
                "max_workers": 0  # Zero workers
            },
            "llm_models": []  # No models
        }
        
        with open(config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        config_manager = ConfigManager(str(config_path))
        
        with self.assertRaises(ConfigValidationError) as context:
            config_manager.load_config()
        
        error_message = str(context.exception)
        
        # Should contain details about multiple validation errors
        self.assertIn("input_folder", error_message)
        self.assertIn("max_text_length", error_message)
        self.assertIn("max_workers", error_message)
        self.assertIn("llm_models", error_message)
    
    def test_pricing_validation_error_details(self):
        """Test that PricingValidationError provides detailed error information."""
        pricing_path = Path(self.temp_dir) / "invalid_pricing.json"
        
        # Create pricing config with multiple validation errors
        invalid_pricing = {
            "models": {
                "gpt-4": {
                    "input_cost_per_1k_tokens": -0.01,  # Negative cost
                    "output_cost_per_1k_tokens": "invalid"  # Wrong type
                }
            },
            "currency_rates": {
                "EUR": -0.85  # Negative rate
            }
            # Missing USD base rate
        }
        
        with open(pricing_path, 'w') as f:
            json.dump(invalid_pricing, f)
        
        pricing_manager = PricingManager(str(pricing_path))
        
        with self.assertRaises(PricingValidationError) as context:
            pricing_manager.load_pricing_config()
        
        error_message = str(context.exception)
        
        # Should contain details about validation errors
        self.assertIn("cost", error_message.lower())
    
    def test_graceful_degradation(self):
        """Test graceful degradation when optional features fail."""
        # This would test scenarios where non-critical components fail
        # but the system continues to operate
        
        # For now, just test that the managers handle missing optional fields
        minimal_config = {
            "paths": {
                "input_folder": str(Path(self.temp_dir) / "input"),
                "output_folder": str(Path(self.temp_dir) / "output")
            },
            "processing": {
                "llm_output_mode": "json"
            },
            "llm_models": [
                {
                    "model_name": "gpt-4",
                    "api_key": "test_key"
                }
            ]
        }
        
        # Create input directory
        Path(self.temp_dir, "input").mkdir(exist_ok=True)
        
        config_path = Path(self.temp_dir) / "minimal_config.json"
        with open(config_path, 'w') as f:
            json.dump(minimal_config, f)
        
        # Should load successfully with defaults for missing optional fields
        config_manager = ConfigManager(str(config_path))
        config = config_manager.load_config()
        
        self.assertIsNotNone(config)
        # Should have default values for missing optional fields
        self.assertIsNotNone(config.parallel)


if __name__ == '__main__':
    unittest.main()