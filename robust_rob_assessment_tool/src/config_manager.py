"""
Enhanced configuration management system for ROB assessment tool.

This module provides comprehensive configuration loading, validation, and management
with support for parallel processing options and detailed error reporting.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParallelConfig:
    """Configuration for parallel processing options."""
    enabled: bool = True
    max_workers: int = 4
    max_documents_per_batch: int = 50
    checkpoint_interval: int = 10
    retry_attempts: int = 3
    timeout_seconds: int = 300
    memory_limit_gb: float = 8.0
    auto_detect_workers: bool = True


@dataclass
class ProcessingConfig:
    """Configuration for document processing options."""
    llm_output_mode: str = "json"
    eval_optional_items: bool = True
    max_text_length: int = 25000
    start_index: int = 0
    batch_size: int = 1
    enable_resume: bool = True


@dataclass
class PathConfig:
    """Configuration for file paths and directories."""
    input_folder: str = ""
    output_folder: str = ""
    checkpoint_file: str = ""
    temp_folder: str = "temp_parallel"
    llm_pricing_config: str = "config/llm_pricing.json"


@dataclass
class Domain6Config:
    """Configuration for Domain 6 assessment thresholds."""
    thresholds: Dict[str, int] = field(default_factory=lambda: {
        "definitely_low": 5,
        "probably_low": 10,
        "probably_high": 15
    })
    default_assessment: str = "Probably low"


@dataclass
class LLMModelConfig:
    """Configuration for individual LLM models."""
    name: str = ""
    api_key: str = ""
    base_url: str = ""
    model_name: str = ""
    use_streaming: bool = False
    max_retries: int = 3
    timeout: int = 60


@dataclass
class ROBFrameworkConfig:
    """Configuration for ROB framework settings."""
    type: str = "rob2"
    core_items: bool = True
    optional_items: bool = True
    custom_domains: List[str] = field(default_factory=list)


@dataclass
class CostTrackingConfig:
    """Configuration for cost tracking and analysis."""
    enabled: bool = True
    currency: str = "USD"
    track_by_model: bool = True
    generate_reports: bool = True
    cost_alerts: bool = False
    max_cost_threshold: float = 100.0


@dataclass
class ROBConfig:
    """Main configuration class containing all settings."""
    paths: PathConfig = field(default_factory=PathConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    parallel: ParallelConfig = field(default_factory=ParallelConfig)
    domain6: Domain6Config = field(default_factory=Domain6Config)
    rob_framework: ROBFrameworkConfig = field(default_factory=ROBFrameworkConfig)
    cost_tracking: CostTrackingConfig = field(default_factory=CostTrackingConfig)
    llm_models: List[LLMModelConfig] = field(default_factory=list)


class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails."""
    pass


class ConfigManager:
    """Enhanced configuration manager with validation and error reporting."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default path.
        """
        self.config_path = config_path or "config/config.json"
        self.config: Optional[ROBConfig] = None
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
    
    def load_config(self, config_path: Optional[str] = None) -> ROBConfig:
        """
        Load configuration from file with comprehensive validation.
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            ROBConfig: Loaded and validated configuration
            
        Raises:
            ConfigValidationError: If configuration is invalid
            FileNotFoundError: If configuration file doesn't exist
        """
        if config_path:
            self.config_path = config_path
            
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"Invalid JSON in configuration file: {e}")
        
        # Parse configuration sections
        self.config = self._parse_config(config_data)
        
        # Validate configuration
        self._validate_config()
        
        if self.validation_errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(
                f"  - {error}" for error in self.validation_errors
            )
            raise ConfigValidationError(error_msg)
        
        if self.validation_warnings:
            logger.warning("Configuration warnings:\n" + "\n".join(
                f"  - {warning}" for warning in self.validation_warnings
            ))
        
        return self.config
    
    def _parse_config(self, config_data: Dict[str, Any]) -> ROBConfig:
        """Parse configuration data into structured config object."""
        config = ROBConfig()
        
        # Parse paths
        if 'paths' in config_data:
            paths_data = config_data['paths']
            config.paths = PathConfig(
                input_folder=paths_data.get('input_folder', ''),
                output_folder=paths_data.get('output_folder', ''),
                checkpoint_file=paths_data.get('checkpoint_file', ''),
                temp_folder=paths_data.get('temp_folder', 'temp_parallel'),
                llm_pricing_config=paths_data.get('llm_pricing_config', 'config/llm_pricing.json')
            )
        
        # Parse processing settings
        if 'processing' in config_data:
            proc_data = config_data['processing']
            config.processing = ProcessingConfig(
                llm_output_mode=proc_data.get('llm_output_mode', 'json'),
                eval_optional_items=proc_data.get('eval_optional_items', True),
                max_text_length=proc_data.get('max_text_length', 25000),
                start_index=proc_data.get('start_index', 0),
                batch_size=proc_data.get('batch_size', 1),
                enable_resume=proc_data.get('enable_resume', True)
            )
        
        # Parse parallel processing settings
        if 'parallel' in config_data:
            parallel_data = config_data['parallel']
            config.parallel = ParallelConfig(
                enabled=parallel_data.get('enabled', True),
                max_workers=parallel_data.get('max_workers', 4),
                max_documents_per_batch=parallel_data.get('max_documents_per_batch', 50),
                checkpoint_interval=parallel_data.get('checkpoint_interval', 10),
                retry_attempts=parallel_data.get('retry_attempts', 3),
                timeout_seconds=parallel_data.get('timeout_seconds', 300),
                memory_limit_gb=parallel_data.get('memory_limit_gb', 8.0),
                auto_detect_workers=parallel_data.get('auto_detect_workers', True)
            )
        
        # Parse domain6 settings
        if 'domain6' in config_data:
            domain6_data = config_data['domain6']
            config.domain6 = Domain6Config(
                thresholds=domain6_data.get('thresholds', {
                    "definitely_low": 5,
                    "probably_low": 10,
                    "probably_high": 15
                }),
                default_assessment=domain6_data.get('default_assessment', 'Probably low')
            )
        
        # Parse ROB framework settings
        if 'rob_framework' in config_data:
            rob_data = config_data['rob_framework']
            config.rob_framework = ROBFrameworkConfig(
                type=rob_data.get('type', 'rob2'),
                core_items=rob_data.get('core_items', True),
                optional_items=rob_data.get('optional_items', True),
                custom_domains=rob_data.get('custom_domains', [])
            )
        
        # Parse cost tracking settings
        if 'cost_tracking' in config_data:
            cost_data = config_data['cost_tracking']
            config.cost_tracking = CostTrackingConfig(
                enabled=cost_data.get('enabled', True),
                currency=cost_data.get('currency', 'USD'),
                track_by_model=cost_data.get('track_by_model', True),
                generate_reports=cost_data.get('generate_reports', True),
                cost_alerts=cost_data.get('cost_alerts', False),
                max_cost_threshold=cost_data.get('max_cost_threshold', 100.0)
            )
        
        # Parse LLM models
        if 'llm_models' in config_data:
            config.llm_models = []
            for model_data in config_data['llm_models']:
                model_config = LLMModelConfig(
                    name=model_data.get('name', ''),
                    api_key=model_data.get('api_key', ''),
                    base_url=model_data.get('base_url', ''),
                    model_name=model_data.get('model_name', ''),
                    use_streaming=model_data.get('use_streaming', False),
                    max_retries=model_data.get('max_retries', 3),
                    timeout=model_data.get('timeout', 60)
                )
                config.llm_models.append(model_config)
        
        return config
    
    def _validate_config(self) -> None:
        """Validate configuration and collect errors/warnings."""
        self.validation_errors = []
        self.validation_warnings = []
        
        if not self.config:
            self.validation_errors.append("Configuration is None")
            return
        
        # Validate paths
        self._validate_paths()
        
        # Validate processing settings
        self._validate_processing()
        
        # Validate parallel settings
        self._validate_parallel()
        
        # Validate LLM models
        self._validate_llm_models()
        
        # Validate domain6 settings
        self._validate_domain6()
        
        # Validate cost tracking
        self._validate_cost_tracking()
    
    def _validate_paths(self) -> None:
        """Validate path configurations."""
        paths = self.config.paths
        
        if not paths.input_folder:
            self.validation_errors.append("Input folder path is required")
        elif not os.path.exists(paths.input_folder):
            self.validation_warnings.append(f"Input folder does not exist: {paths.input_folder}")
        
        if not paths.output_folder:
            self.validation_errors.append("Output folder path is required")
        
        if paths.checkpoint_file and not os.path.dirname(paths.checkpoint_file):
            self.validation_warnings.append("Checkpoint file directory not specified")
    
    def _validate_processing(self) -> None:
        """Validate processing configurations."""
        proc = self.config.processing
        
        if proc.llm_output_mode not in ['json', 'table']:
            self.validation_errors.append(f"Invalid llm_output_mode: {proc.llm_output_mode}")
        
        if proc.max_text_length <= 0:
            self.validation_errors.append("max_text_length must be positive")
        
        if proc.start_index < 0:
            self.validation_errors.append("start_index must be non-negative")
        
        if proc.batch_size <= 0:
            self.validation_errors.append("batch_size must be positive")
    
    def _validate_parallel(self) -> None:
        """Validate parallel processing configurations."""
        parallel = self.config.parallel
        
        if parallel.max_workers <= 0:
            self.validation_errors.append("max_workers must be positive")
        elif parallel.max_workers > 32:
            self.validation_warnings.append("max_workers > 32 may cause resource issues")
        
        if parallel.max_documents_per_batch <= 0:
            self.validation_errors.append("max_documents_per_batch must be positive")
        
        if parallel.checkpoint_interval <= 0:
            self.validation_errors.append("checkpoint_interval must be positive")
        
        if parallel.retry_attempts < 0:
            self.validation_errors.append("retry_attempts must be non-negative")
        
        if parallel.timeout_seconds <= 0:
            self.validation_errors.append("timeout_seconds must be positive")
        
        if parallel.memory_limit_gb <= 0:
            self.validation_errors.append("memory_limit_gb must be positive")
    
    def _validate_llm_models(self) -> None:
        """Validate LLM model configurations."""
        if not self.config.llm_models:
            self.validation_errors.append("At least one LLM model must be configured")
            return
        
        model_names = set()
        for i, model in enumerate(self.config.llm_models):
            if not model.name:
                self.validation_errors.append(f"Model {i+1}: name is required")
            elif model.name in model_names:
                self.validation_errors.append(f"Model {i+1}: duplicate name '{model.name}'")
            else:
                model_names.add(model.name)
            
            if not model.api_key:
                self.validation_errors.append(f"Model '{model.name}': api_key is required")
            
            if not model.base_url:
                self.validation_errors.append(f"Model '{model.name}': base_url is required")
            
            if not model.model_name:
                self.validation_errors.append(f"Model '{model.name}': model_name is required")
            
            if model.max_retries < 0:
                self.validation_errors.append(f"Model '{model.name}': max_retries must be non-negative")
            
            if model.timeout <= 0:
                self.validation_errors.append(f"Model '{model.name}': timeout must be positive")
    
    def _validate_domain6(self) -> None:
        """Validate Domain 6 configurations."""
        domain6 = self.config.domain6
        
        required_thresholds = ['definitely_low', 'probably_low', 'probably_high']
        for threshold in required_thresholds:
            if threshold not in domain6.thresholds:
                self.validation_errors.append(f"Domain6: missing threshold '{threshold}'")
            elif domain6.thresholds[threshold] <= 0:
                self.validation_errors.append(f"Domain6: threshold '{threshold}' must be positive")
        
        # Check threshold ordering
        if all(t in domain6.thresholds for t in required_thresholds):
            def_low = domain6.thresholds['definitely_low']
            prob_low = domain6.thresholds['probably_low']
            prob_high = domain6.thresholds['probably_high']
            
            if not (def_low < prob_low < prob_high):
                self.validation_errors.append(
                    "Domain6: thresholds must be in ascending order: definitely_low < probably_low < probably_high"
                )
        
        valid_assessments = ['Definitely low', 'Probably low', 'Probably high', 'Definitely high']
        if domain6.default_assessment not in valid_assessments:
            self.validation_errors.append(f"Domain6: invalid default_assessment '{domain6.default_assessment}'")
    
    def _validate_cost_tracking(self) -> None:
        """Validate cost tracking configurations."""
        cost = self.config.cost_tracking
        
        if cost.max_cost_threshold <= 0:
            self.validation_errors.append("Cost tracking: max_cost_threshold must be positive")
        
        # Currency validation would require checking against pricing config
        # This will be handled when pricing config is loaded
    
    def create_template_config(self, output_path: str) -> None:
        """
        Create a comprehensive configuration template with documentation.
        
        Args:
            output_path: Path where to save the template
        """
        template = {
            "_comment": "ROB Assessment Tool Configuration Template",
            "_documentation": {
                "paths": "File and directory paths for input, output, and temporary files",
                "processing": "Document processing and analysis settings",
                "parallel": "Parallel processing configuration for improved performance",
                "domain6": "Domain 6 assessment thresholds and default values",
                "rob_framework": "ROB framework type and assessment scope",
                "cost_tracking": "LLM usage cost tracking and reporting settings",
                "llm_models": "LLM model configurations for assessment"
            },
            "paths": {
                "_comment": "Configure file and directory paths",
                "input_folder": "path/to/input/documents",
                "output_folder": "path/to/output/results",
                "checkpoint_file": "path/to/checkpoint/file.pkl",
                "temp_folder": "temp_parallel",
                "llm_pricing_config": "config/llm_pricing.json"
            },
            "processing": {
                "_comment": "Document processing configuration",
                "llm_output_mode": "json",
                "_llm_output_mode_options": ["json", "table"],
                "eval_optional_items": True,
                "max_text_length": 25000,
                "_max_text_length_note": "Maximum text length per document (characters)",
                "start_index": 0,
                "_start_index_note": "Starting document index (for partial processing)",
                "batch_size": 1,
                "_batch_size_note": "Number of documents per processing batch",
                "enable_resume": True,
                "_enable_resume_note": "Enable checkpoint/resume functionality"
            },
            "parallel": {
                "_comment": "Parallel processing configuration for improved performance",
                "enabled": True,
                "_enabled_note": "Enable/disable parallel processing",
                "max_workers": 4,
                "_max_workers_note": "Maximum number of parallel workers (auto-detected if auto_detect_workers=true)",
                "max_documents_per_batch": 50,
                "_max_documents_per_batch_note": "Maximum documents per worker batch",
                "checkpoint_interval": 10,
                "_checkpoint_interval_note": "Save checkpoint every N processed documents",
                "retry_attempts": 3,
                "_retry_attempts_note": "Number of retry attempts for failed operations",
                "timeout_seconds": 300,
                "_timeout_seconds_note": "Timeout for individual document processing (seconds)",
                "memory_limit_gb": 8.0,
                "_memory_limit_gb_note": "Memory limit per worker process (GB)",
                "auto_detect_workers": True,
                "_auto_detect_workers_note": "Automatically detect optimal number of workers based on system resources"
            },
            "domain6": {
                "_comment": "Domain 6 assessment thresholds and defaults",
                "thresholds": {
                    "definitely_low": 5,
                    "probably_low": 10,
                    "probably_high": 15,
                    "_note": "Thresholds must be in ascending order"
                },
                "default_assessment": "Probably low",
                "_default_assessment_options": ["Definitely low", "Probably low", "Probably high", "Definitely high"]
            },
            "rob_framework": {
                "_comment": "ROB framework configuration",
                "type": "rob2",
                "_type_options": ["rob2", "rob1", "custom"],
                "core_items": True,
                "_core_items_note": "Assess core ROB domains",
                "optional_items": True,
                "_optional_items_note": "Assess optional ROB domains",
                "custom_domains": [],
                "_custom_domains_note": "List of custom domain names for assessment"
            },
            "cost_tracking": {
                "_comment": "LLM usage cost tracking and reporting",
                "enabled": True,
                "_enabled_note": "Enable cost tracking and reporting",
                "currency": "USD",
                "_currency_options": ["USD", "EUR", "GBP", "CNY", "JPY"],
                "track_by_model": True,
                "_track_by_model_note": "Track costs separately for each LLM model",
                "generate_reports": True,
                "_generate_reports_note": "Generate detailed cost reports",
                "cost_alerts": False,
                "_cost_alerts_note": "Enable cost threshold alerts",
                "max_cost_threshold": 100.0,
                "_max_cost_threshold_note": "Maximum cost threshold for alerts (in selected currency)"
            },
            "llm_models": [
                {
                    "_comment": "Primary LLM model configuration",
                    "name": "Primary Model",
                    "_name_note": "Unique identifier for this model",
                    "api_key": "your_api_key_here",
                    "_api_key_note": "API key for accessing the LLM service",
                    "base_url": "https://api.openai.com/v1",
                    "_base_url_note": "Base URL for the LLM API endpoint",
                    "model_name": "gpt-4",
                    "_model_name_note": "Specific model identifier (e.g., gpt-4, claude-3-opus)",
                    "use_streaming": False,
                    "_use_streaming_note": "Enable streaming responses (if supported)",
                    "max_retries": 3,
                    "_max_retries_note": "Maximum retry attempts for failed API calls",
                    "timeout": 60,
                    "_timeout_note": "API call timeout in seconds"
                },
                {
                    "_comment": "Secondary LLM model configuration (optional)",
                    "name": "Secondary Model",
                    "api_key": "your_secondary_api_key_here",
                    "base_url": "https://api.anthropic.com/v1",
                    "model_name": "claude-3-sonnet",
                    "use_streaming": False,
                    "max_retries": 3,
                    "timeout": 60
                }
            ]
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Configuration template created: {output_path}")
    
    def get_validation_report(self) -> Tuple[List[str], List[str]]:
        """
        Get validation errors and warnings.
        
        Returns:
            Tuple of (errors, warnings)
        """
        return self.validation_errors.copy(), self.validation_warnings.copy()
    
    def save_config(self, config: ROBConfig, output_path: str) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration object to save
            output_path: Path where to save the configuration
        """
        # Convert config object back to dictionary format
        config_dict = self._config_to_dict(config)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Configuration saved: {output_path}")
    
    def _config_to_dict(self, config: ROBConfig) -> Dict[str, Any]:
        """Convert configuration object to dictionary format."""
        return {
            "paths": {
                "input_folder": config.paths.input_folder,
                "output_folder": config.paths.output_folder,
                "checkpoint_file": config.paths.checkpoint_file,
                "temp_folder": config.paths.temp_folder,
                "llm_pricing_config": config.paths.llm_pricing_config
            },
            "processing": {
                "llm_output_mode": config.processing.llm_output_mode,
                "eval_optional_items": config.processing.eval_optional_items,
                "max_text_length": config.processing.max_text_length,
                "start_index": config.processing.start_index,
                "batch_size": config.processing.batch_size,
                "enable_resume": config.processing.enable_resume
            },
            "parallel": {
                "enabled": config.parallel.enabled,
                "max_workers": config.parallel.max_workers,
                "max_documents_per_batch": config.parallel.max_documents_per_batch,
                "checkpoint_interval": config.parallel.checkpoint_interval,
                "retry_attempts": config.parallel.retry_attempts,
                "timeout_seconds": config.parallel.timeout_seconds,
                "memory_limit_gb": config.parallel.memory_limit_gb,
                "auto_detect_workers": config.parallel.auto_detect_workers
            },
            "domain6": {
                "thresholds": config.domain6.thresholds,
                "default_assessment": config.domain6.default_assessment
            },
            "rob_framework": {
                "type": config.rob_framework.type,
                "core_items": config.rob_framework.core_items,
                "optional_items": config.rob_framework.optional_items,
                "custom_domains": config.rob_framework.custom_domains
            },
            "cost_tracking": {
                "enabled": config.cost_tracking.enabled,
                "currency": config.cost_tracking.currency,
                "track_by_model": config.cost_tracking.track_by_model,
                "generate_reports": config.cost_tracking.generate_reports,
                "cost_alerts": config.cost_tracking.cost_alerts,
                "max_cost_threshold": config.cost_tracking.max_cost_threshold
            },
            "llm_models": [
                {
                    "name": model.name,
                    "api_key": model.api_key,
                    "base_url": model.base_url,
                    "model_name": model.model_name,
                    "use_streaming": model.use_streaming,
                    "max_retries": model.max_retries,
                    "timeout": model.timeout
                }
                for model in config.llm_models
            ]
        }