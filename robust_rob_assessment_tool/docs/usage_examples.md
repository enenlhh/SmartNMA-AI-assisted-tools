# Usage Examples

This document provides comprehensive usage examples for the ROB Assessment Tool v2.0, covering various scenarios from basic usage to advanced configurations.

## Table of Contents

1. [Quick Start Examples](#quick-start-examples)
2. [Interactive Mode Examples](#interactive-mode-examples)
3. [Command Line Examples](#command-line-examples)
4. [Parallel Processing Examples](#parallel-processing-examples)
5. [Checkpoint and Resume Examples](#checkpoint-and-resume-examples)
6. [Cost Management Examples](#cost-management-examples)
7. [Troubleshooting Examples](#troubleshooting-examples)
8. [Advanced Scenarios](#advanced-scenarios)

## Quick Start Examples

### Example 1: First-Time Setup

```bash
# 1. Clone and setup
git clone https://github.com/enenlhh/SmartNMA-AI-assisted-tools.git
cd SmartNMA-AI-assisted-tools/robust_rob_assessment_tool
python -m venv rob_env
source rob_env/bin/activate  # On Windows: rob_env\Scripts\activate
pip install -r requirements.txt

# 2. Create configuration from template
cp config/config_template.json config/my_config.json

# 3. Edit configuration (add your API keys)
# Edit config/my_config.json with your preferred editor

# 4. Test installation
python main.py --version

# 5. Run interactive mode
python main.py
```

### Example 2: Basic Assessment (5 Documents)

```bash
# Prepare your documents
mkdir -p input/test_documents
# Copy 5 PDF files to input/test_documents/

# Create minimal configuration
cat > config/test_config.json << EOF
{
  "paths": {
    "input_folder": "input/test_documents",
    "output_folder": "output/test_results"
  },
  "processing": {
    "max_text_length": 15000,
    "eval_optional_items": false
  },
  "parallel": {
    "enabled": false
  },
  "llm_models": [
    {
      "name": "Test Model",
      "api_key": "your_api_key_here",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-3.5-turbo"
    }
  ]
}
EOF

# Run assessment
python main.py start -c config/test_config.json
```

## Interactive Mode Examples

### Example 3: Using Interactive Mode (Beginner-Friendly)

```bash
# Start interactive mode
python main.py

# Expected interaction:
# Welcome to ROB Assessment Tool
# Please select your language:
# 1. English
# 2. 中文
# Enter your choice (1-2): 1

# Select operation:
# 1. Start new assessment
# 2. Resume assessment  
# 3. Monitor progress
# 4. Clean up temporary files
# 5. Merge results
# 6. Exit
# Enter your choice (1-6): 1

# Follow the prompts to:
# - Select configuration file
# - Review system information
# - Configure processing options
# - Confirm and start assessment
```

### Example 4: Interactive Language Selection

```bash
# Start with Chinese interface
python main.py -l zh

# Start with English interface  
python main.py -l en

# Let user choose interactively
python main.py
```

## Command Line Examples

### Example 5: Basic Command Line Usage

```bash
# Start new assessment
python main.py start -c config/config.json

# Start with custom parameters
python main.py start -c config/config.json -w 4 --batch-size 25

# Start with specific input/output directories
python main.py start -c config/config.json \
  -i /path/to/documents \
  -o /path/to/results

# Start from specific document index
python main.py start -c config/config.json --start-index 10
```

### Example 6: Resume Operations

```bash
# Resume from checkpoint
python main.py resume -s checkpoint_20241201_143022.json

# Resume with different worker count
python main.py resume -s checkpoint.json -w 8

# Resume with new configuration
python main.py resume -s checkpoint.json -c config/new_config.json
```

### Example 7: Monitoring and Management

```bash
# Monitor progress (auto-detect running assessment)
python main.py monitor

# Monitor specific assessment
python main.py monitor -s state_file.json

# Monitor with custom refresh rate
python main.py monitor -r 15 --no-clear

# Clean up temporary files
python main.py cleanup

# Clean up with confirmation
python main.py cleanup --force

# Keep results, clean only temp files
python main.py cleanup --keep-results
```

### Example 8: Result Merging

```bash
# Merge batch results
python main.py merge -i output/batch_results -o final_results.xlsx

# Merge to JSON format
python main.py merge -i output/batches -o results.json --format json

# Merge both Excel and JSON
python main.py merge -i output/batches -o results --format both

# Include failed documents in results
python main.py merge -i output/batches -o results.xlsx --include-failed
```

## Parallel Processing Examples

### Example 9: Optimal Parallel Configuration

```bash
# Let system auto-detect optimal workers
python main.py start -c config/config.json

# Configuration for auto-detection:
{
  "parallel": {
    "enabled": true,
    "auto_detect_workers": true,
    "max_documents_per_batch": 50
  }
}

# Manual worker specification
python main.py start -c config/config.json -w 8

# Configuration for manual control:
{
  "parallel": {
    "enabled": true,
    "max_workers": 8,
    "auto_detect_workers": false
  }
}
```

### Example 10: Resource-Constrained Environment

```bash
# Configuration for limited resources
{
  "parallel": {
    "enabled": true,
    "max_workers": 2,
    "max_documents_per_batch": 10,
    "memory_limit_gb": 4.0,
    "timeout_seconds": 600
  },
  "processing": {
    "max_text_length": 10000
  }
}

# Run with resource constraints
python main.py start -c config/limited_resources.json
```

### Example 11: High-Performance Setup

```bash
# Configuration for high-performance server
{
  "parallel": {
    "enabled": true,
    "max_workers": 16,
    "max_documents_per_batch": 100,
    "memory_limit_gb": 16.0,
    "checkpoint_interval": 50
  },
  "processing": {
    "max_text_length": 30000
  }
}

# Run high-performance assessment
python main.py start -c config/high_performance.json
```

## Checkpoint and Resume Examples

### Example 12: Checkpoint Management

```bash
# Enable frequent checkpointing
{
  "parallel": {
    "checkpoint_interval": 5  # Save every 5 documents
  },
  "processing": {
    "enable_resume": true
  }
}

# Start assessment with checkpointing
python main.py start -c config/checkpoint_config.json

# If interrupted, resume from last checkpoint
python main.py resume -s checkpoint_latest.json
```

### Example 13: Manual Checkpoint Creation

```python
# Example script for manual checkpoint management
import json
from datetime import datetime

# Create checkpoint manually
checkpoint_data = {
    "session_id": "manual_session_001",
    "start_time": datetime.now().isoformat(),
    "total_documents": 100,
    "completed_documents": 25,
    "current_batch": 3,
    "config_snapshot": {...}  # Your configuration
}

with open(f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
    json.dump(checkpoint_data, f, indent=2)
```

### Example 14: Checkpoint Recovery Scenarios

```bash
# Scenario 1: Normal resume after interruption
python main.py resume -s checkpoint_20241201_143022.json

# Scenario 2: Resume with modified configuration
python main.py resume -s checkpoint.json -c config/modified_config.json

# Scenario 3: Resume from corrupted checkpoint (will start fresh)
python main.py resume -s corrupted_checkpoint.json
# Tool will detect corruption and offer to start new assessment

# Scenario 4: Resume with different resource allocation
python main.py resume -s checkpoint.json -w 4  # Change worker count
```

## Cost Management Examples

### Example 15: Budget-Conscious Assessment

```bash
# Configuration for cost control
{
  "cost_tracking": {
    "enabled": true,
    "currency": "USD",
    "cost_alerts": true,
    "max_cost_threshold": 50.0
  },
  "processing": {
    "max_text_length": 8000  # Reduce token usage
  },
  "llm_models": [
    {
      "name": "Budget Model",
      "model_name": "gpt-3.5-turbo"  # Cheaper model
    }
  ]
}

# Run with cost monitoring
python main.py start -c config/budget_config.json
```

### Example 16: Multi-Currency Cost Tracking

```bash
# Configuration for international projects
{
  "cost_tracking": {
    "enabled": true,
    "currency": "EUR",  # Primary currency
    "track_by_model": true,
    "generate_reports": true
  }
}

# The tool will show costs in EUR and provide conversions to other currencies
```

### Example 17: Cost Analysis and Reporting

```bash
# After assessment completion, analyze costs
python -c "
import json
with open('output/cost_report.json', 'r') as f:
    cost_data = json.load(f)
    
print(f'Total Cost: ${cost_data[\"total_cost\"]:.2f}')
print(f'Cost per Document: ${cost_data[\"cost_per_document\"]:.2f}')
print(f'Token Usage: {cost_data[\"total_tokens\"]:,}')
"
```

## Troubleshooting Examples

### Example 18: Debugging Configuration Issues

```bash
# Validate configuration before running
python main.py start -c config/config.json --validate-only

# Check system information
python main.py --system-info

# Run with verbose logging
python main.py start -c config/config.json --verbose --log-file debug.log

# Test with minimal configuration
cat > config/minimal_test.json << EOF
{
  "paths": {
    "input_folder": "input/test",
    "output_folder": "output/test"
  },
  "parallel": {"enabled": false},
  "llm_models": [{
    "name": "Test",
    "api_key": "test_key",
    "base_url": "https://api.openai.com/v1",
    "model_name": "gpt-3.5-turbo"
  }]
}
EOF

python main.py start -c config/minimal_test.json --batch-size 1
```

### Example 19: Handling API Errors

```bash
# Configuration with robust error handling
{
  "llm_models": [
    {
      "name": "Primary Model",
      "api_key": "your_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-4",
      "max_retries": 5,      # Increase retries
      "timeout": 120         # Increase timeout
    }
  ],
  "parallel": {
    "retry_attempts": 3,     # Retry failed documents
    "timeout_seconds": 600   # Longer processing timeout
  }
}
```

### Example 20: Memory and Performance Issues

```bash
# Configuration for memory-constrained systems
{
  "parallel": {
    "enabled": true,
    "max_workers": 2,        # Reduce workers
    "memory_limit_gb": 4.0,  # Set memory limit
    "max_documents_per_batch": 10  # Smaller batches
  },
  "processing": {
    "max_text_length": 10000  # Reduce text length
  }
}

# Monitor system resources during processing
# On Linux/macOS:
top -p $(pgrep -f "python main.py")

# On Windows:
# Use Task Manager to monitor python.exe processes
```

## Advanced Scenarios

### Example 21: Multi-Stage Assessment Pipeline

```bash
#!/bin/bash
# Multi-stage assessment script

# Stage 1: Quick assessment with cheaper model
echo "Stage 1: Initial assessment with GPT-3.5"
python main.py start -c config/stage1_config.json

# Stage 2: Detailed assessment of uncertain cases with GPT-4
echo "Stage 2: Detailed assessment of uncertain cases"
python main.py start -c config/stage2_config.json

# Stage 3: Final review and consolidation
echo "Stage 3: Consolidating results"
python main.py merge -i output/stage1 -o output/consolidated_stage1.xlsx
python main.py merge -i output/stage2 -o output/consolidated_stage2.xlsx
```

### Example 22: Batch Processing Multiple Projects

```bash
#!/bin/bash
# Process multiple systematic review projects

projects=("cardiology_review" "oncology_review" "neurology_review")

for project in "${projects[@]}"; do
    echo "Processing project: $project"
    
    # Create project-specific configuration
    sed "s/PROJECT_NAME/$project/g" config/template_config.json > config/${project}_config.json
    
    # Run assessment
    python main.py start -c config/${project}_config.json
    
    # Move results to project directory
    mkdir -p results/$project
    mv output/* results/$project/
    
    echo "Completed project: $project"
done
```

### Example 23: Integration with External Tools

```python
# Example: Integration with systematic review management tools
import subprocess
import json
import pandas as pd

def run_rob_assessment(input_dir, output_dir, config_file):
    """Run ROB assessment and return results"""
    
    # Run assessment
    result = subprocess.run([
        'python', 'main.py', 'start',
        '-c', config_file,
        '-i', input_dir,
        '-o', output_dir
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Assessment failed: {result.stderr}")
    
    # Load results
    results_file = f"{output_dir}/rob_results.xlsx"
    df = pd.read_excel(results_file)
    
    return df

def export_to_revman(rob_results, output_file):
    """Export results to RevMan format"""
    # Convert to RevMan-compatible format
    revman_data = rob_results.to_dict('records')
    
    with open(output_file, 'w') as f:
        json.dump(revman_data, f, indent=2)

# Usage
if __name__ == "__main__":
    results = run_rob_assessment(
        input_dir="input/systematic_review",
        output_dir="output/rob_assessment",
        config_file="config/production_config.json"
    )
    
    export_to_revman(results, "output/revman_export.json")
```

### Example 24: Custom Reporting and Analysis

```python
# Example: Custom analysis of ROB assessment results
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_rob_results(results_file):
    """Analyze ROB assessment results"""
    
    # Load results
    df = pd.read_excel(results_file)
    
    # Calculate confidence distribution
    confidence_dist = df['confidence_level'].value_counts()
    print("Confidence Level Distribution:")
    print(confidence_dist)
    
    # Analyze domain-specific patterns
    domain_columns = [col for col in df.columns if 'domain_' in col]
    domain_analysis = df[domain_columns].apply(pd.value_counts)
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Confidence distribution plot
    plt.subplot(2, 2, 1)
    confidence_dist.plot(kind='bar')
    plt.title('Confidence Level Distribution')
    plt.xticks(rotation=45)
    
    # Domain risk distribution
    plt.subplot(2, 2, 2)
    domain_risk_counts = df[domain_columns].apply(lambda x: x.value_counts().get('High Risk', 0))
    domain_risk_counts.plot(kind='bar')
    plt.title('High Risk Count by Domain')
    plt.xticks(rotation=45)
    
    # Cost analysis
    if 'total_cost' in df.columns:
        plt.subplot(2, 2, 3)
        plt.hist(df['total_cost'], bins=20)
        plt.title('Cost Distribution per Document')
        plt.xlabel('Cost ($)')
        plt.ylabel('Frequency')
    
    # Processing time analysis
    if 'processing_time' in df.columns:
        plt.subplot(2, 2, 4)
        plt.scatter(df['document_length'], df['processing_time'])
        plt.title('Processing Time vs Document Length')
        plt.xlabel('Document Length (characters)')
        plt.ylabel('Processing Time (seconds)')
    
    plt.tight_layout()
    plt.savefig('rob_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return df

# Usage
if __name__ == "__main__":
    results = analyze_rob_results("output/rob_results.xlsx")
```

### Example 25: Automated Quality Control

```python
# Example: Automated quality control checks
import pandas as pd
import numpy as np

def quality_control_check(results_file, threshold_low_confidence=0.3):
    """Perform quality control checks on ROB assessment results"""
    
    df = pd.read_excel(results_file)
    
    # Check 1: High proportion of low confidence results
    low_confidence_ratio = (df['confidence_level'] == 'Low Confidence').mean()
    if low_confidence_ratio > threshold_low_confidence:
        print(f"WARNING: {low_confidence_ratio:.1%} of results have low confidence")
        print("Consider reviewing configuration or using different models")
    
    # Check 2: Unusual cost patterns
    if 'cost_per_document' in df.columns:
        cost_std = df['cost_per_document'].std()
        cost_mean = df['cost_per_document'].mean()
        
        outliers = df[df['cost_per_document'] > cost_mean + 2*cost_std]
        if len(outliers) > 0:
            print(f"WARNING: {len(outliers)} documents have unusually high costs")
            print("Documents with high costs:", outliers['document_name'].tolist())
    
    # Check 3: Processing time anomalies
    if 'processing_time' in df.columns:
        time_q95 = df['processing_time'].quantile(0.95)
        slow_documents = df[df['processing_time'] > time_q95]
        
        if len(slow_documents) > 0:
            print(f"INFO: {len(slow_documents)} documents took longer than 95th percentile to process")
    
    # Check 4: Domain-specific issues
    domain_columns = [col for col in df.columns if 'domain_' in col]
    for domain in domain_columns:
        uncertain_ratio = (df[domain] == 'Uncertain').mean()
        if uncertain_ratio > 0.5:
            print(f"WARNING: {domain} has {uncertain_ratio:.1%} uncertain assessments")
    
    return df

# Usage
if __name__ == "__main__":
    quality_control_check("output/rob_results.xlsx")
```

## Best Practices Summary

### Configuration Best Practices
1. **Start with templates** and modify incrementally
2. **Test with small datasets** before full assessment
3. **Use version control** for configuration files
4. **Document configuration changes** and rationale

### Processing Best Practices
1. **Enable checkpointing** for long assessments
2. **Monitor system resources** during processing
3. **Use appropriate batch sizes** for your system
4. **Implement cost controls** to prevent budget overruns

### Quality Assurance Best Practices
1. **Always review low-confidence results** manually
2. **Spot-check high-confidence results** regularly
3. **Maintain consistent assessment criteria** across projects
4. **Document manual overrides** and decisions

### Performance Best Practices
1. **Use parallel processing** when system resources allow
2. **Optimize text length limits** based on document types
3. **Choose appropriate LLM models** for accuracy vs. cost balance
4. **Regular cleanup** of temporary files and checkpoints

These examples provide a comprehensive guide for using the ROB Assessment Tool v2.0 in various scenarios. Adapt the configurations and commands to match your specific requirements and system capabilities.