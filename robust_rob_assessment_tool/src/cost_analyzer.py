"""
Cost Analyzer for LLM Usage Tracking

This module provides comprehensive cost tracking and analysis for LLM API usage
in the ROB assessment tool, including multi-currency support and detailed reporting.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class TokenUsage:
    """Data class for tracking token usage per API call"""
    model: str
    input_tokens: int
    output_tokens: int
    timestamp: datetime
    document_name: Optional[str] = None
    operation: Optional[str] = None


@dataclass
class ModelCostSummary:
    """Summary of costs for a specific model"""
    model: str
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    api_calls: int


@dataclass
class CostReport:
    """Comprehensive cost report"""
    session_id: str
    start_time: datetime
    end_time: datetime
    total_cost_usd: float
    total_tokens: int
    total_api_calls: int
    model_summaries: List[ModelCostSummary]
    currency_conversions: Dict[str, float]
    recommendations: List[str]


class CostAnalyzer:
    """
    Comprehensive cost tracking and analysis for LLM usage
    
    Features:
    - Token consumption tracking per model
    - Multi-currency cost calculation
    - Detailed cost reports generation
    - Cost optimization recommendations
    """
    
    def __init__(self, pricing_config_path: str, session_id: str = None):
        """
        Initialize the cost analyzer
        
        Args:
            pricing_config_path: Path to LLM pricing configuration file
            session_id: Unique identifier for this analysis session
        """
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.usage_records: List[TokenUsage] = []
        
        # Load pricing configuration
        self.pricing_config = self._load_pricing_config(pricing_config_path)
        
        # Initialize tracking dictionaries
        self.model_usage = defaultdict(lambda: {
            'input_tokens': 0,
            'output_tokens': 0,
            'api_calls': 0,
            'documents': set()
        })
    
    def _load_pricing_config(self, config_path: str) -> Dict:
        """Load LLM pricing configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate required fields
            if 'models' not in config:
                raise ValueError("Pricing config missing 'models' section")
            if 'currency_rates' not in config:
                raise ValueError("Pricing config missing 'currency_rates' section")
            
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Pricing configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in pricing configuration: {e}")
    
    def track_usage(self, model: str, input_tokens: int, output_tokens: int, 
                   document_name: str = None, operation: str = None) -> None:
        """
        Track token usage for a specific API call
        
        Args:
            model: Name of the LLM model used
            input_tokens: Number of input tokens consumed
            output_tokens: Number of output tokens generated
            document_name: Name of document being processed (optional)
            operation: Type of operation performed (optional)
        """
        # Create usage record
        usage = TokenUsage(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            timestamp=datetime.now(),
            document_name=document_name,
            operation=operation
        )
        
        self.usage_records.append(usage)
        
        # Update model usage tracking
        self.model_usage[model]['input_tokens'] += input_tokens
        self.model_usage[model]['output_tokens'] += output_tokens
        self.model_usage[model]['api_calls'] += 1
        
        if document_name:
            self.model_usage[model]['documents'].add(document_name)
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Tuple[float, float, float]:
        """
        Calculate cost for specific token usage
        
        Args:
            model: Name of the LLM model
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Tuple of (input_cost_usd, output_cost_usd, total_cost_usd)
        """
        if model not in self.pricing_config['models']:
            # Return zero cost for unknown models
            return 0.0, 0.0, 0.0
        
        model_pricing = self.pricing_config['models'][model]
        
        # Calculate costs (pricing is per 1K tokens)
        input_cost = (input_tokens / 1000) * model_pricing['input_cost_per_1k_tokens']
        output_cost = (output_tokens / 1000) * model_pricing['output_cost_per_1k_tokens']
        total_cost = input_cost + output_cost
        
        return input_cost, output_cost, total_cost
    
    def convert_currency(self, amount_usd: float, target_currency: str) -> float:
        """
        Convert USD amount to target currency
        
        Args:
            amount_usd: Amount in USD
            target_currency: Target currency code (e.g., 'EUR', 'CNY')
            
        Returns:
            Converted amount in target currency
        """
        if target_currency == 'USD':
            return amount_usd
        
        if target_currency not in self.pricing_config['currency_rates']:
            raise ValueError(f"Unsupported currency: {target_currency}")
        
        rate = self.pricing_config['currency_rates'][target_currency]
        return amount_usd * rate
    
    def get_model_summary(self, model: str) -> ModelCostSummary:
        """
        Get cost summary for a specific model
        
        Args:
            model: Name of the LLM model
            
        Returns:
            ModelCostSummary object with detailed cost information
        """
        if model not in self.model_usage:
            return ModelCostSummary(
                model=model,
                total_input_tokens=0,
                total_output_tokens=0,
                total_tokens=0,
                input_cost_usd=0.0,
                output_cost_usd=0.0,
                total_cost_usd=0.0,
                api_calls=0
            )
        
        usage = self.model_usage[model]
        input_tokens = usage['input_tokens']
        output_tokens = usage['output_tokens']
        
        input_cost, output_cost, total_cost = self.calculate_cost(
            model, input_tokens, output_tokens
        )
        
        return ModelCostSummary(
            model=model,
            total_input_tokens=input_tokens,
            total_output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            input_cost_usd=input_cost,
            output_cost_usd=output_cost,
            total_cost_usd=total_cost,
            api_calls=usage['api_calls']
        )
    
    def get_cost_summary(self) -> Dict:
        """
        Get overall cost summary
        
        Returns:
            Dictionary with summary statistics
        """
        total_cost = 0.0
        total_tokens = 0
        total_api_calls = 0
        model_summaries = []
        
        for model in self.model_usage.keys():
            summary = self.get_model_summary(model)
            model_summaries.append(summary)
            total_cost += summary.total_cost_usd
            total_tokens += summary.total_tokens
            total_api_calls += summary.api_calls
        
        return {
            'session_id': self.session_id,
            'total_cost_usd': total_cost,
            'total_tokens': total_tokens,
            'total_api_calls': total_api_calls,
            'models_used': len(self.model_usage),
            'model_summaries': [asdict(summary) for summary in model_summaries],
            'start_time': self.start_time.isoformat(),
            'duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60
        }
    
    def generate_recommendations(self) -> List[str]:
        """
        Generate cost optimization recommendations based on usage patterns
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if not self.model_usage:
            return ["No usage data available for recommendations"]
        
        # Analyze model usage efficiency
        model_costs = {}
        for model in self.model_usage.keys():
            summary = self.get_model_summary(model)
            if summary.total_tokens > 0:
                cost_per_token = summary.total_cost_usd / summary.total_tokens
                model_costs[model] = cost_per_token
        
        if len(model_costs) > 1:
            # Find most and least cost-effective models
            cheapest_model = min(model_costs.keys(), key=lambda x: model_costs[x])
            most_expensive_model = max(model_costs.keys(), key=lambda x: model_costs[x])
            
            if model_costs[most_expensive_model] > model_costs[cheapest_model] * 2:
                recommendations.append(
                    f"Consider using {cheapest_model} instead of {most_expensive_model} "
                    f"for cost savings (${model_costs[cheapest_model]:.6f} vs "
                    f"${model_costs[most_expensive_model]:.6f} per token)"
                )
        
        # Check for high-cost operations
        total_cost = sum(self.get_model_summary(model).total_cost_usd for model in self.model_usage.keys())
        if total_cost > 10.0:  # Threshold for high cost
            recommendations.append(
                f"High total cost detected (${total_cost:.2f}). "
                "Consider batch processing or using cheaper models for initial screening."
            )
        
        # Analyze token efficiency
        for model in self.model_usage.keys():
            summary = self.get_model_summary(model)
            if summary.total_output_tokens > 0:
                output_ratio = summary.total_output_tokens / summary.total_input_tokens
                if output_ratio > 0.5:  # High output-to-input ratio
                    recommendations.append(
                        f"Model {model} has high output-to-input ratio ({output_ratio:.2f}). "
                        "Consider optimizing prompts to reduce output length."
                    )
        
        if not recommendations:
            recommendations.append("Usage patterns appear optimal. No specific recommendations at this time.")
        
        return recommendations
    
    def save_detailed_log(self, output_path: str) -> None:
        """
        Save detailed usage log to JSON file
        
        Args:
            output_path: Path to save the detailed log
        """
        log_data = {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'usage_records': [
                {
                    'model': record.model,
                    'input_tokens': record.input_tokens,
                    'output_tokens': record.output_tokens,
                    'timestamp': record.timestamp.isoformat(),
                    'document_name': record.document_name,
                    'operation': record.operation
                }
                for record in self.usage_records
            ],
            'summary': self.get_cost_summary()
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def reset_session(self, new_session_id: str = None) -> None:
        """
        Reset the analyzer for a new session
        
        Args:
            new_session_id: New session identifier (optional)
        """
        self.session_id = new_session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.usage_records.clear()
        self.model_usage.clear()