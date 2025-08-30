# Configuration Guide

This guide provides detailed explanations of all configuration options for the ROB Assessment Tool v2.0.

## Table of Contents

1. [Configuration File Structure](#configuration-file-structure)
2. [Path Configuration](#path-configuration)
3. [Processing Configuration](#processing-configuration)
4. [Parallel Processing Configuration](#parallel-processing-configuration)
5. [LLM Models Configuration](#llm-models-configuration)
6. [Cost Tracking Configuration](#cost-tracking-configuration)
7. [ROB Framework Configuration](#rob-framework-configuration)
8. [Domain-Specific Configuration](#domain-specific-configuration)
9. [Configuration Examples](#configuration-examples)
10. [Troubleshooting Configuration Issues](#troubleshooting-configuration-issues)

## Configuration File Structure

The tool uses a JSON configuration file with the following main sections:

```json
{
  "paths": { ... },
  "processing": { ... },
  "parallel": { ... },
  "llm_models": [ ... ],
  "cost_tracking": { ... },
  "rob_framework": { ... },
  "domain6": { ... }
}
```

## Path Configuration

### Basic Path Settings

```json
{
  "paths": {
    "input_folder": "input/documents",
    "output_folder": "output/results",
    "checkpoint_file": "checkpoints/assessment.json",
    "temp_folder": "temp_parallel",
    "llm_pricing_config": "config/llm_pricing.json"
  }
}
```

### Path Configuration Options

| Field | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `input_folder` | string | Yes | Directory containing input documents (PDF/DOCX) | - |
| `output_folder` | string | Yes | Directory for output results and reports | - |
| `checkpoint_file` | string | No | Path for checkpoint/state files | "checkpoint.json" |
| `temp_folder` | string | No | Temporary files directory for parallel processing | "temp_parallel" |
| `llm_pricing_config` | string | No | Path to LLM pricing configuration file | "config/llm_pricing.json" |

### Path Best Practices

- **Use absolute paths** for production environments
- **Ensure write permissions** for output and temp directories
- **Use separate directories** for different projects
- **Regular cleanup** of temp folders to save disk space

## Processing Configuration

### Basic Processing Settings

```json
{
  "processing": {
    "llm_output_mode": "json",
    "eval_optional_items": true,
    "max_text_length": 25000,
    "start_index": 0,
    "batch_size": 1,
    "enable_resume": true
  }
}
```

### Processing Configuration Options

| Field | Type | Required | Description | Options | Default |
|-------|------|----------|-------------|---------|---------|
| `llm_output_mode` | string | No | LLM response format | "json", "table" | "json" |
| `eval_optional_items` | boolean | No | Include optional ROB domains | true, false | true |
| `max_text_length` | integer | No | Maximum text length per document (characters) | 1000-50000 | 25000 |
| `start_index` | integer | No | Starting document index for processing | 0+ | 0 |
| `batch_size` | integer | No | Documents per processing batch | 1-100 | 1 |
| `enable_resume` | boolean | No | Enable checkpoint/resume functionality | true, false | true |

### Processing Configuration Guidelines

**LLM Output Mode:**
- `"json"`: Structured JSON responses (recommended for most models)
- `"table"`: Markdown table format (for models with limited JSON support)

**Text Length Optimization:**
- **Small documents (< 5000 chars)**: Use full text
- **Medium documents (5000-25000 chars)**: Default setting works well
- **Large documents (> 25000 chars)**: Consider reducing to control costs

**Batch Size Considerations:**
- **Single document batches (1)**: Maximum flexibility, easier debugging
- **Small batches (2-5)**: Good balance of efficiency and control
- **Large batches (10+)**: Higher efficiency but less granular control

## Parallel Processing Configuration

### Basic Parallel Settings

```json
{
  "parallel": {
    "enabled": true,
    "max_workers": 4,
    "max_documents_per_batch": 50,
    "checkpoint_interval": 10,
    "retry_attempts": 3,
    "timeout_seconds": 300,
    "memory_limit_gb": 8.0,
    "auto_detect_workers": true
  }
}
```

### Parallel Configuration Options

| Field | Type | Required | Description | Range | Default |
|-------|------|----------|-------------|-------|---------|
| `enabled` | boolean | No | Enable parallel processing | true, false | true |
| `max_workers` | integer | No | Maximum parallel workers | 1-32 | 4 |
| `max_documents_per_batch` | integer | No | Maximum documents per worker batch | 1-200 | 50 |
| `checkpoint_interval` | integer | No | Save checkpoint every N documents | 1-100 | 10 |
| `retry_attempts` | integer | No | Retry attempts for failed operations | 1-10 | 3 |
| `timeout_seconds` | integer | No | Timeout per document (seconds) | 30-1800 | 300 |
| `memory_limit_gb` | float | No | Memory limit per worker (GB) | 1.0-64.0 | 8.0 |
| `auto_detect_workers` | boolean | No | Auto-detect optimal worker count | true, false | true |

### Parallel Processing Guidelines

**Worker Count Optimization:**
- **CPU-bound tasks**: Workers = CPU cores
- **I/O-bound tasks**: Workers = 2 × CPU cores
- **Memory-limited**: Workers = Available RAM / Memory per worker
- **API rate limits**: Consider provider limits

**System Resource Recommendations:**

| System Type | CPU Cores | RAM | Recommended Workers | Batch Size |
|-------------|-----------|-----|-------------------|------------|
| Laptop | 4-8 | 8-16GB | 2-4 | 25-50 |
| Workstation | 8-16 | 16-32GB | 4-8 | 50-100 |
| Server | 16+ | 32GB+ | 8-16 | 100-200 |

## LLM Models Configuration

### Basic LLM Configuration

```json
{
  "llm_models": [
    {
      "name": "Primary Model",
      "api_key": "your_api_key_here",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-4",
      "use_streaming": false,
      "max_retries": 3,
      "timeout": 60
    }
  ]
}
```

### LLM Configuration Options

| Field | Type | Required | Description | Examples |
|-------|------|----------|-------------|----------|
| `name` | string | Yes | Unique model identifier | "Primary Model", "GPT-4", "Claude" |
| `api_key` | string | Yes | API key for the service | "sk-..." |
| `base_url` | string | Yes | API endpoint base URL | "https://api.openai.com/v1" |
| `model_name` | string | Yes | Specific model identifier | "gpt-4", "claude-3-sonnet" |
| `use_streaming` | boolean | No | Enable streaming responses | true, false |
| `max_retries` | integer | No | Maximum retry attempts | 1-10 |
| `timeout` | integer | No | Request timeout (seconds) | 30-300 |

### Popular LLM Provider Configurations

#### OpenAI Configuration
```json
{
  "name": "OpenAI GPT-4",
  "api_key": "sk-your-openai-key",
  "base_url": "https://api.openai.com/v1",
  "model_name": "gpt-4",
  "max_retries": 3,
  "timeout": 60
}
```

#### Anthropic Configuration
```json
{
  "name": "Anthropic Claude",
  "api_key": "sk-ant-your-anthropic-key",
  "base_url": "https://api.anthropic.com/v1",
  "model_name": "claude-3-sonnet-20240229",
  "max_retries": 3,
  "timeout": 90
}
```

#### Azure OpenAI Configuration
```json
{
  "name": "Azure OpenAI",
  "api_key": "your-azure-key",
  "base_url": "https://your-resource.openai.azure.com/",
  "model_name": "gpt-4",
  "max_retries": 3,
  "timeout": 60
}
```

#### Local/Self-hosted Configuration
```json
{
  "name": "Local LLM",
  "api_key": "not-required",
  "base_url": "http://localhost:8000/v1",
  "model_name": "local-model",
  "max_retries": 2,
  "timeout": 120
}
```

## Cost Tracking Configuration

### Basic Cost Tracking Settings

```json
{
  "cost_tracking": {
    "enabled": true,
    "currency": "USD",
    "track_by_model": true,
    "generate_reports": true,
    "cost_alerts": true,
    "max_cost_threshold": 100.0
  }
}
```

### Cost Tracking Options

| Field | Type | Required | Description | Options | Default |
|-------|------|----------|-------------|---------|---------|
| `enabled` | boolean | No | Enable cost tracking | true, false | true |
| `currency` | string | No | Primary currency for reporting | "USD", "EUR", "GBP", "CNY", "JPY" | "USD" |
| `track_by_model` | boolean | No | Track costs per model | true, false | true |
| `generate_reports` | boolean | No | Generate cost reports | true, false | true |
| `cost_alerts` | boolean | No | Enable cost threshold alerts | true, false | false |
| `max_cost_threshold` | float | No | Cost threshold for alerts | 0.0+ | 100.0 |

### Cost Optimization Strategies

**Budget Management:**
- Set realistic cost thresholds based on project budget
- Monitor costs regularly during long assessments
- Use cost alerts to prevent budget overruns
- Consider using cheaper models for initial testing

**Token Usage Optimization:**
- Implement text length limits for large documents
- Use efficient prompts to reduce token consumption
- Consider preprocessing to remove irrelevant content
- Monitor token usage patterns and optimize accordingly

## ROB Framework Configuration

### Basic ROB Framework Settings

```json
{
  "rob_framework": {
    "type": "rob2",
    "core_items": true,
    "optional_items": true,
    "custom_domains": []
  }
}
```

### ROB Framework Options

| Field | Type | Required | Description | Options | Default |
|-------|------|----------|-------------|---------|---------|
| `type` | string | No | ROB framework type | "rob2", "rob1", "custom" | "rob2" |
| `core_items` | boolean | No | Assess core ROB domains | true, false | true |
| `optional_items` | boolean | No | Assess optional ROB domains | true, false | true |
| `custom_domains` | array | No | Custom domain names | ["Domain 1", "Domain 2"] | [] |

### Framework-Specific Configurations

#### ROB 2.0 Configuration
```json
{
  "rob_framework": {
    "type": "rob2",
    "core_items": true,
    "optional_items": true,
    "domains": [
      "Randomization process",
      "Deviations from intended interventions",
      "Missing outcome data",
      "Measurement of the outcome",
      "Selection of the reported result"
    ]
  }
}
```

#### Custom Framework Configuration
```json
{
  "rob_framework": {
    "type": "custom",
    "core_items": true,
    "optional_items": false,
    "custom_domains": [
      "Study Design Quality",
      "Participant Selection",
      "Intervention Fidelity",
      "Outcome Assessment",
      "Statistical Analysis"
    ]
  }
}
```

## Domain-Specific Configuration

### Domain 6 Configuration (ROB 2.0)

```json
{
  "domain6": {
    "thresholds": {
      "definitely_low": 5,
      "probably_low": 10,
      "probably_high": 15
    },
    "default_assessment": "Probably low"
  }
}
```

### Domain Configuration Options

| Field | Type | Required | Description | Range |
|-------|------|----------|-------------|-------|
| `thresholds.definitely_low` | integer | No | Threshold for "definitely low" risk | 1-50 |
| `thresholds.probably_low` | integer | No | Threshold for "probably low" risk | 1-50 |
| `thresholds.probably_high` | integer | No | Threshold for "probably high" risk | 1-50 |
| `default_assessment` | string | No | Default assessment when unclear | "Definitely low", "Probably low", "Probably high", "Definitely high" |

## Configuration Examples

### Example 1: Small-Scale Assessment

```json
{
  "paths": {
    "input_folder": "input/pilot_study",
    "output_folder": "output/pilot_results"
  },
  "processing": {
    "max_text_length": 15000,
    "eval_optional_items": false
  },
  "parallel": {
    "enabled": false,
    "max_workers": 1
  },
  "llm_models": [
    {
      "name": "GPT-3.5",
      "api_key": "your_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-3.5-turbo"
    }
  ],
  "cost_tracking": {
    "enabled": true,
    "max_cost_threshold": 10.0
  }
}
```

### Example 2: Large-Scale Production Assessment

```json
{
  "paths": {
    "input_folder": "/data/systematic_review/documents",
    "output_folder": "/data/systematic_review/results",
    "checkpoint_file": "/data/systematic_review/checkpoints/main.json",
    "temp_folder": "/tmp/rob_parallel"
  },
  "processing": {
    "max_text_length": 30000,
    "eval_optional_items": true,
    "enable_resume": true
  },
  "parallel": {
    "enabled": true,
    "max_workers": 8,
    "max_documents_per_batch": 100,
    "checkpoint_interval": 25,
    "memory_limit_gb": 12.0
  },
  "llm_models": [
    {
      "name": "Primary GPT-4",
      "api_key": "your_openai_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-4",
      "timeout": 120
    },
    {
      "name": "Secondary Claude",
      "api_key": "your_anthropic_key",
      "base_url": "https://api.anthropic.com/v1",
      "model_name": "claude-3-sonnet-20240229",
      "timeout": 150
    }
  ],
  "cost_tracking": {
    "enabled": true,
    "currency": "USD",
    "track_by_model": true,
    "cost_alerts": true,
    "max_cost_threshold": 500.0
  }
}
```

### Example 3: Budget-Conscious Configuration

```json
{
  "processing": {
    "max_text_length": 10000,
    "eval_optional_items": false
  },
  "parallel": {
    "enabled": true,
    "max_workers": 2,
    "max_documents_per_batch": 25
  },
  "llm_models": [
    {
      "name": "Cost-Effective Model",
      "api_key": "your_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-3.5-turbo",
      "timeout": 60
    }
  ],
  "cost_tracking": {
    "enabled": true,
    "cost_alerts": true,
    "max_cost_threshold": 25.0
  }
}
```

## Troubleshooting Configuration Issues

### Common Configuration Errors

#### 1. Invalid JSON Format
**Error**: `JSONDecodeError: Expecting ',' delimiter`
**Solution**: Validate JSON syntax using online validators or IDE tools

#### 2. Missing Required Fields
**Error**: `Configuration validation failed: Missing required field 'input_folder'`
**Solution**: Ensure all required fields are present in configuration

#### 3. Invalid File Paths
**Error**: `FileNotFoundError: Input folder not found`
**Solution**: Verify all paths exist and are accessible

#### 4. API Key Issues
**Error**: `Authentication failed for LLM service`
**Solution**: Verify API keys are correct and have sufficient quota

#### 5. Resource Limit Exceeded
**Error**: `Requested workers exceed system capacity`
**Solution**: Reduce worker count or enable auto-detection

### Configuration Validation

Use the built-in validation to check your configuration:

```bash
# Validate configuration file
python main.py start -c config/config.json --validate-only

# Check system compatibility
python main.py --system-info

# Test with minimal configuration
python main.py start -c config/minimal_config.json --batch-size 1
```

### Performance Tuning

#### For Speed Optimization:
- Increase parallel workers (within system limits)
- Use faster LLM models
- Reduce text length limits
- Optimize batch sizes

#### For Cost Optimization:
- Use cheaper LLM models
- Implement strict text length limits
- Enable cost tracking and alerts
- Consider preprocessing to reduce token usage

#### For Reliability:
- Enable checkpointing with frequent intervals
- Use multiple retry attempts
- Implement reasonable timeouts
- Monitor error logs regularly

### Best Practices Summary

1. **Start Small**: Test with a small subset before full assessment
2. **Monitor Resources**: Keep track of system performance and costs
3. **Use Checkpoints**: Enable resume functionality for long assessments
4. **Validate Early**: Check configuration before starting large jobs
5. **Document Changes**: Keep track of configuration modifications
6. **Backup Configs**: Maintain copies of working configurations
7. **Regular Updates**: Keep pricing and model information current
8. **Security**: Protect API keys and use environment variables when possible