"""
LLM pricing configuration management system.

This module provides comprehensive pricing data loading, validation, and 
multi-currency cost calculation capabilities for LLM usage tracking.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelPricing:
    """Pricing information for a specific LLM model."""
    model_name: str
    input_cost_per_1k_tokens: float
    output_cost_per_1k_tokens: float
    currency: str = "USD"
    provider: str = ""
    last_updated: Optional[str] = None
    notes: str = ""


@dataclass
class CurrencyRate:
    """Currency exchange rate information."""
    currency_code: str
    rate_to_usd: float
    last_updated: Optional[str] = None


@dataclass
class PricingConfig:
    """Complete pricing configuration with models and currency rates."""
    models: Dict[str, ModelPricing] = field(default_factory=dict)
    currency_rates: Dict[str, float] = field(default_factory=dict)
    default_currency: str = "USD"
    last_updated: Optional[str] = None


class PricingValidationError(Exception):
    """Exception raised when pricing configuration validation fails."""
    pass


class PricingManager:
    """Enhanced pricing manager with validation and multi-currency support."""
    
    def __init__(self, pricing_config_path: Optional[str] = None):
        """
        Initialize pricing manager.
        
        Args:
            pricing_config_path: Path to pricing configuration file
        """
        self.pricing_config_path = pricing_config_path or "config/llm_pricing.json"
        self.pricing_config: Optional[PricingConfig] = None
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
    
    def load_pricing_config(self, config_path: Optional[str] = None) -> PricingConfig:
        """
        Load pricing configuration from file with validation.
        
        Args:
            config_path: Optional path to pricing configuration file
            
        Returns:
            PricingConfig: Loaded and validated pricing configuration
            
        Raises:
            PricingValidationError: If pricing configuration is invalid
            FileNotFoundError: If pricing configuration file doesn't exist
        """
        if config_path:
            self.pricing_config_path = config_path
            
        if not os.path.exists(self.pricing_config_path):
            # Create default pricing config if it doesn't exist
            self.create_default_pricing_config(self.pricing_config_path)
        
        try:
            with open(self.pricing_config_path, 'r', encoding='utf-8') as f:
                pricing_data = json.load(f)
        except json.JSONDecodeError as e:
            raise PricingValidationError(f"Invalid JSON in pricing configuration file: {e}")
        
        # Parse pricing configuration
        self.pricing_config = self._parse_pricing_config(pricing_data)
        
        # Validate pricing configuration
        self._validate_pricing_config()
        
        if self.validation_errors:
            error_msg = "Pricing configuration validation failed:\n" + "\n".join(
                f"  - {error}" for error in self.validation_errors
            )
            raise PricingValidationError(error_msg)
        
        if self.validation_warnings:
            logger.warning("Pricing configuration warnings:\n" + "\n".join(
                f"  - {warning}" for warning in self.validation_warnings
            ))
        
        return self.pricing_config
    
    def _parse_pricing_config(self, pricing_data: Dict[str, Any]) -> PricingConfig:
        """Parse pricing configuration data into structured config object."""
        config = PricingConfig()
        
        # Parse model pricing
        if 'models' in pricing_data:
            for model_name, model_data in pricing_data['models'].items():
                pricing = ModelPricing(
                    model_name=model_name,
                    input_cost_per_1k_tokens=model_data.get('input_cost_per_1k_tokens', 0.0),
                    output_cost_per_1k_tokens=model_data.get('output_cost_per_1k_tokens', 0.0),
                    currency=model_data.get('currency', 'USD'),
                    provider=model_data.get('provider', ''),
                    last_updated=model_data.get('last_updated'),
                    notes=model_data.get('notes', '')
                )
                config.models[model_name] = pricing
        
        # Parse currency rates
        if 'currency_rates' in pricing_data:
            config.currency_rates = pricing_data['currency_rates']
        
        # Parse other settings
        config.default_currency = pricing_data.get('default_currency', 'USD')
        config.last_updated = pricing_data.get('last_updated')
        
        return config
    
    def _validate_pricing_config(self) -> None:
        """Validate pricing configuration and collect errors/warnings."""
        self.validation_errors = []
        self.validation_warnings = []
        
        if not self.pricing_config:
            self.validation_errors.append("Pricing configuration is None")
            return
        
        # Validate models
        self._validate_models()
        
        # Validate currency rates
        self._validate_currency_rates()
        
        # Validate default currency
        self._validate_default_currency()
    
    def _validate_models(self) -> None:
        """Validate model pricing configurations."""
        if not self.pricing_config.models:
            self.validation_warnings.append("No model pricing configurations found")
            return
        
        for model_name, pricing in self.pricing_config.models.items():
            if pricing.input_cost_per_1k_tokens < 0:
                self.validation_errors.append(f"Model '{model_name}': input cost cannot be negative")
            
            if pricing.output_cost_per_1k_tokens < 0:
                self.validation_errors.append(f"Model '{model_name}': output cost cannot be negative")
            
            if pricing.input_cost_per_1k_tokens == 0 and pricing.output_cost_per_1k_tokens == 0:
                self.validation_warnings.append(f"Model '{model_name}': both input and output costs are zero")
            
            if not pricing.currency:
                self.validation_errors.append(f"Model '{model_name}': currency is required")
            elif pricing.currency not in self.pricing_config.currency_rates:
                self.validation_warnings.append(
                    f"Model '{model_name}': currency '{pricing.currency}' not found in currency_rates"
                )
    
    def _validate_currency_rates(self) -> None:
        """Validate currency rate configurations."""
        if not self.pricing_config.currency_rates:
            self.validation_errors.append("Currency rates are required")
            return
        
        # USD should always be present with rate 1.0
        if 'USD' not in self.pricing_config.currency_rates:
            self.validation_errors.append("USD currency rate is required")
        elif self.pricing_config.currency_rates['USD'] != 1.0:
            self.validation_errors.append("USD currency rate must be 1.0")
        
        for currency, rate in self.pricing_config.currency_rates.items():
            # Skip comment fields
            if currency.startswith('_'):
                continue
            try:
                rate_float = float(rate)
                if rate_float <= 0:
                    self.validation_errors.append(f"Currency '{currency}': rate must be positive")
            except (ValueError, TypeError):
                self.validation_errors.append(f"Currency '{currency}': rate must be a number")
    
    def _validate_default_currency(self) -> None:
        """Validate default currency setting."""
        if self.pricing_config.default_currency not in self.pricing_config.currency_rates:
            self.validation_errors.append(
                f"Default currency '{self.pricing_config.default_currency}' not found in currency_rates"
            )
    
    def get_model_pricing(self, model_name: str) -> Optional[ModelPricing]:
        """
        Get pricing information for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelPricing object or None if not found
        """
        if not self.pricing_config:
            return None
        
        # Try exact match first
        if model_name in self.pricing_config.models:
            return self.pricing_config.models[model_name]
        
        # Try partial matching for common model variations
        for config_model_name, pricing in self.pricing_config.models.items():
            if self._models_match(model_name, config_model_name):
                return pricing
        
        return None
    
    def _models_match(self, requested_model: str, config_model: str) -> bool:
        """Check if two model names match with fuzzy matching."""
        # Normalize names for comparison
        requested_lower = requested_model.lower().replace('-', '').replace('_', '')
        config_lower = config_model.lower().replace('-', '').replace('_', '')
        
        # Check if one is contained in the other
        return requested_lower in config_lower or config_lower in requested_lower
    
    def calculate_cost(
        self, 
        model_name: str, 
        input_tokens: int, 
        output_tokens: int, 
        target_currency: Optional[str] = None
    ) -> Tuple[float, str]:
        """
        Calculate cost for LLM usage.
        
        Args:
            model_name: Name of the model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            target_currency: Target currency for cost calculation
            
        Returns:
            Tuple of (cost, currency)
        """
        if not self.pricing_config:
            return 0.0, "USD"
        
        pricing = self.get_model_pricing(model_name)
        if not pricing:
            logger.warning(f"No pricing found for model: {model_name}")
            return 0.0, target_currency or self.pricing_config.default_currency
        
        # Calculate base cost in model's currency
        input_cost = (input_tokens / 1000) * pricing.input_cost_per_1k_tokens
        output_cost = (output_tokens / 1000) * pricing.output_cost_per_1k_tokens
        total_cost = input_cost + output_cost
        
        # Convert currency if needed
        if target_currency and target_currency != pricing.currency:
            total_cost = self._convert_currency(total_cost, pricing.currency, target_currency)
            return total_cost, target_currency
        
        return total_cost, pricing.currency
    
    def _convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount between currencies."""
        if from_currency == to_currency:
            return amount
        
        if not self.pricing_config or not self.pricing_config.currency_rates:
            return amount
        
        try:
            from_rate = float(self.pricing_config.currency_rates.get(from_currency, 1.0))
            to_rate = float(self.pricing_config.currency_rates.get(to_currency, 1.0))
            
            # Convert to USD first, then to target currency
            usd_amount = amount / from_rate
            target_amount = usd_amount * to_rate
            
            return target_amount
        except (ValueError, TypeError):
            # If conversion fails, return original amount
            return amount
    
    def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies."""
        if not self.pricing_config:
            return ["USD"]
        
        # Filter out comment fields (keys starting with '_')
        return [currency for currency in self.pricing_config.currency_rates.keys() 
                if not currency.startswith('_')]
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported models."""
        if not self.pricing_config:
            return []
        
        return list(self.pricing_config.models.keys())
    
    def create_default_pricing_config(self, output_path: str) -> None:
        """
        Create a comprehensive default pricing configuration.
        
        Args:
            output_path: Path where to save the pricing configuration
        """
        default_config = {
            "_comment": "LLM Pricing Configuration for Cost Tracking",
            "_documentation": {
                "models": "Pricing information for different LLM models",
                "currency_rates": "Exchange rates relative to USD (USD must be 1.0)",
                "default_currency": "Default currency for cost reporting",
                "last_updated": "Date when pricing information was last updated"
            },
            "models": {
                "gpt-4": {
                    "input_cost_per_1k_tokens": 0.03,
                    "output_cost_per_1k_tokens": 0.06,
                    "currency": "USD",
                    "provider": "OpenAI",
                    "last_updated": "2024-01-01",
                    "notes": "GPT-4 standard pricing"
                },
                "gpt-4-turbo": {
                    "input_cost_per_1k_tokens": 0.01,
                    "output_cost_per_1k_tokens": 0.03,
                    "currency": "USD",
                    "provider": "OpenAI",
                    "last_updated": "2024-01-01",
                    "notes": "GPT-4 Turbo optimized pricing"
                },
                "gpt-4o": {
                    "input_cost_per_1k_tokens": 0.005,
                    "output_cost_per_1k_tokens": 0.015,
                    "currency": "USD",
                    "provider": "OpenAI",
                    "last_updated": "2024-01-01",
                    "notes": "GPT-4o latest model"
                },
                "gpt-3.5-turbo": {
                    "input_cost_per_1k_tokens": 0.0015,
                    "output_cost_per_1k_tokens": 0.002,
                    "currency": "USD",
                    "provider": "OpenAI",
                    "last_updated": "2024-01-01",
                    "notes": "GPT-3.5 Turbo cost-effective option"
                },
                "claude-3-opus": {
                    "input_cost_per_1k_tokens": 0.015,
                    "output_cost_per_1k_tokens": 0.075,
                    "currency": "USD",
                    "provider": "Anthropic",
                    "last_updated": "2024-01-01",
                    "notes": "Claude 3 Opus highest capability"
                },
                "claude-3-sonnet": {
                    "input_cost_per_1k_tokens": 0.003,
                    "output_cost_per_1k_tokens": 0.015,
                    "currency": "USD",
                    "provider": "Anthropic",
                    "last_updated": "2024-01-01",
                    "notes": "Claude 3 Sonnet balanced performance"
                },
                "claude-3-haiku": {
                    "input_cost_per_1k_tokens": 0.00025,
                    "output_cost_per_1k_tokens": 0.00125,
                    "currency": "USD",
                    "provider": "Anthropic",
                    "last_updated": "2024-01-01",
                    "notes": "Claude 3 Haiku fastest and most cost-effective"
                },
                "claude-3.5-sonnet": {
                    "input_cost_per_1k_tokens": 0.003,
                    "output_cost_per_1k_tokens": 0.015,
                    "currency": "USD",
                    "provider": "Anthropic",
                    "last_updated": "2024-01-01",
                    "notes": "Claude 3.5 Sonnet enhanced capabilities"
                },
                "gemini-pro": {
                    "input_cost_per_1k_tokens": 0.0005,
                    "output_cost_per_1k_tokens": 0.0015,
                    "currency": "USD",
                    "provider": "Google",
                    "last_updated": "2024-01-01",
                    "notes": "Google Gemini Pro"
                },
                "gemini-pro-vision": {
                    "input_cost_per_1k_tokens": 0.0005,
                    "output_cost_per_1k_tokens": 0.0015,
                    "currency": "USD",
                    "provider": "Google",
                    "last_updated": "2024-01-01",
                    "notes": "Google Gemini Pro with vision capabilities"
                }
            },
            "currency_rates": {
                "_comment": "Exchange rates relative to USD (USD must always be 1.0)",
                "USD": 1.0,
                "EUR": 0.85,
                "GBP": 0.75,
                "CNY": 7.2,
                "JPY": 110.0,
                "CAD": 1.35,
                "AUD": 1.55,
                "CHF": 0.88,
                "SEK": 10.5,
                "NOK": 11.0
            },
            "default_currency": "USD",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "_update_note": "Please update pricing information regularly as LLM providers may change their rates"
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Default pricing configuration created: {output_path}")
    
    def update_pricing_config(self, updates: Dict[str, Any], output_path: Optional[str] = None) -> None:
        """
        Update pricing configuration with new data.
        
        Args:
            updates: Dictionary containing updates to apply
            output_path: Optional path to save updated configuration
        """
        if not self.pricing_config:
            raise PricingValidationError("No pricing configuration loaded")
        
        # Apply updates
        if 'models' in updates:
            for model_name, model_data in updates['models'].items():
                if model_name in self.pricing_config.models:
                    # Update existing model
                    existing = self.pricing_config.models[model_name]
                    for key, value in model_data.items():
                        setattr(existing, key, value)
                else:
                    # Add new model
                    pricing = ModelPricing(
                        model_name=model_name,
                        input_cost_per_1k_tokens=model_data.get('input_cost_per_1k_tokens', 0.0),
                        output_cost_per_1k_tokens=model_data.get('output_cost_per_1k_tokens', 0.0),
                        currency=model_data.get('currency', 'USD'),
                        provider=model_data.get('provider', ''),
                        last_updated=model_data.get('last_updated'),
                        notes=model_data.get('notes', '')
                    )
                    self.pricing_config.models[model_name] = pricing
        
        if 'currency_rates' in updates:
            self.pricing_config.currency_rates.update(updates['currency_rates'])
        
        if 'default_currency' in updates:
            self.pricing_config.default_currency = updates['default_currency']
        
        # Update timestamp
        self.pricing_config.last_updated = datetime.now().strftime("%Y-%m-%d")
        
        # Save if path provided
        if output_path:
            self.save_pricing_config(output_path)
    
    def save_pricing_config(self, output_path: Optional[str] = None) -> None:
        """
        Save pricing configuration to file.
        
        Args:
            output_path: Path where to save the configuration
        """
        if not self.pricing_config:
            raise PricingValidationError("No pricing configuration to save")
        
        save_path = output_path or self.pricing_config_path
        
        # Convert config object back to dictionary format
        config_dict = self._pricing_config_to_dict(self.pricing_config)
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Pricing configuration saved: {save_path}")
    
    def _pricing_config_to_dict(self, config: PricingConfig) -> Dict[str, Any]:
        """Convert pricing configuration object to dictionary format."""
        models_dict = {}
        for model_name, pricing in config.models.items():
            models_dict[model_name] = {
                "input_cost_per_1k_tokens": pricing.input_cost_per_1k_tokens,
                "output_cost_per_1k_tokens": pricing.output_cost_per_1k_tokens,
                "currency": pricing.currency,
                "provider": pricing.provider,
                "last_updated": pricing.last_updated,
                "notes": pricing.notes
            }
        
        return {
            "models": models_dict,
            "currency_rates": config.currency_rates,
            "default_currency": config.default_currency,
            "last_updated": config.last_updated
        }
    
    def get_validation_report(self) -> Tuple[List[str], List[str]]:
        """
        Get validation errors and warnings.
        
        Returns:
            Tuple of (errors, warnings)
        """
        return self.validation_errors.copy(), self.validation_warnings.copy()