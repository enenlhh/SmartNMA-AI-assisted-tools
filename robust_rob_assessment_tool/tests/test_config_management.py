#!/usr/bin/env python3
"""
Test script for configuration management system.

This script tests the enhanced configuration and pricing management systems
to ensure they work correctly with validation and error handling.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_manager import ConfigManager, ConfigValidationError
from src.pricing_manager import PricingManager, PricingValidationError


def test_config_manager():
    """Test the enhanced configuration manager."""
    print("Testing Configuration Manager...")
    
    # Test loading existing config
    try:
        config_manager = ConfigManager("config/config.json")
        config = config_manager.load_config()
        print("✓ Successfully loaded existing configuration")
        
        # Print some config details
        print(f"  - Input folder: {config.paths.input_folder}")
        print(f"  - Parallel workers: {config.parallel.max_workers}")
        print(f"  - LLM models: {len(config.llm_models)}")
        
    except Exception as e:
        print(f"✗ Failed to load existing configuration: {e}")
    
    # Test creating template config
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            template_path = f.name
        
        config_manager.create_template_config(template_path)
        print("✓ Successfully created configuration template")
        
        # Test loading the template
        template_manager = ConfigManager(template_path)
        template_config = template_manager.load_config()
        print("✓ Successfully loaded template configuration")
        
        # Cleanup
        os.unlink(template_path)
        
    except Exception as e:
        print(f"✗ Failed to create/load template configuration: {e}")
    
    # Test validation with invalid config
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            invalid_config = {
                "paths": {
                    "input_folder": "",  # Invalid: empty path
                    "output_folder": "test_output"
                },
                "processing": {
                    "max_text_length": -1000  # Invalid: negative value
                },
                "parallel": {
                    "max_workers": 0  # Invalid: zero workers
                },
                "llm_models": []  # Invalid: no models
            }
            json.dump(invalid_config, f)
            invalid_path = f.name
        
        invalid_manager = ConfigManager(invalid_path)
        try:
            invalid_manager.load_config()
            print("✗ Should have failed validation for invalid config")
        except ConfigValidationError as e:
            print("✓ Successfully caught validation errors for invalid config")
            print(f"  - Validation errors detected: {len(str(e).split('- ')) - 1}")
        
        # Cleanup
        os.unlink(invalid_path)
        
    except Exception as e:
        print(f"✗ Failed to test invalid configuration: {e}")


def test_pricing_manager():
    """Test the pricing manager."""
    print("\nTesting Pricing Manager...")
    
    # Test loading existing pricing config
    try:
        pricing_manager = PricingManager("config/llm_pricing.json")
        pricing_config = pricing_manager.load_pricing_config()
        print("✓ Successfully loaded existing pricing configuration")
        
        # Print some pricing details
        models = pricing_manager.get_supported_models()
        currencies = pricing_manager.get_supported_currencies()
        print(f"  - Supported models: {len(models)}")
        print(f"  - Supported currencies: {len(currencies)}")
        
    except Exception as e:
        print(f"✗ Failed to load existing pricing configuration: {e}")
    
    # Test cost calculation
    try:
        cost, currency = pricing_manager.calculate_cost("gpt-4", 1000, 500)
        print(f"✓ Cost calculation successful: {cost:.4f} {currency}")
        
        # Test currency conversion
        cost_eur, currency_eur = pricing_manager.calculate_cost("gpt-4", 1000, 500, "EUR")
        print(f"✓ Currency conversion successful: {cost_eur:.4f} {currency_eur}")
        
    except Exception as e:
        print(f"✗ Failed cost calculation: {e}")
    
    # Test model matching
    try:
        # Test exact match
        pricing = pricing_manager.get_model_pricing("gpt-4")
        if pricing:
            print("✓ Exact model matching works")
        
        # Test fuzzy matching
        pricing = pricing_manager.get_model_pricing("gpt-4-turbo-preview")
        if pricing:
            print("✓ Fuzzy model matching works")
        else:
            print("- Fuzzy matching didn't find match (expected for some cases)")
        
    except Exception as e:
        print(f"✗ Failed model matching test: {e}")
    
    # Test creating default pricing config
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            default_path = f.name
        
        pricing_manager.create_default_pricing_config(default_path)
        print("✓ Successfully created default pricing configuration")
        
        # Test loading the default config
        default_manager = PricingManager(default_path)
        default_config = default_manager.load_pricing_config()
        print("✓ Successfully loaded default pricing configuration")
        
        # Cleanup
        os.unlink(default_path)
        
    except Exception as e:
        print(f"✗ Failed to create/load default pricing configuration: {e}")


def test_integration():
    """Test integration between config and pricing managers."""
    print("\nTesting Integration...")
    
    try:
        # Load both configurations
        config_manager = ConfigManager("config/config.json")
        config = config_manager.load_config()
        
        pricing_manager = PricingManager(config.paths.llm_pricing_config)
        pricing_config = pricing_manager.load_pricing_config()
        
        print("✓ Successfully loaded both configurations")
        
        # Test if configured models have pricing information
        models_with_pricing = 0
        for llm_model in config.llm_models:
            pricing = pricing_manager.get_model_pricing(llm_model.model_name)
            if pricing:
                models_with_pricing += 1
        
        print(f"✓ Found pricing for {models_with_pricing}/{len(config.llm_models)} configured models")
        
        # Test cost tracking configuration
        if config.cost_tracking.enabled:
            target_currency = config.cost_tracking.currency
            if target_currency in pricing_manager.get_supported_currencies():
                print(f"✓ Cost tracking currency '{target_currency}' is supported")
            else:
                print(f"⚠ Cost tracking currency '{target_currency}' not found in pricing config")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")


def main():
    """Run all tests."""
    print("ROB Assessment Tool - Configuration Management Tests")
    print("=" * 60)
    
    test_config_manager()
    test_pricing_manager()
    test_integration()
    
    print("\n" + "=" * 60)
    print("Configuration management tests completed!")


if __name__ == "__main__":
    main()