# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the ROB Assessment Tool v2.0.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Configuration Problems](#configuration-problems)
3. [Runtime Errors](#runtime-errors)
4. [Performance Issues](#performance-issues)
5. [API and Network Issues](#api-and-network-issues)
6. [Memory and Resource Problems](#memory-and-resource-problems)
7. [File and Path Issues](#file-and-path-issues)
8. [Parallel Processing Issues](#parallel-processing-issues)
9. [Cost and Billing Issues](#cost-and-billing-issues)
10. [Output and Results Issues](#output-and-results-issues)
11. [Diagnostic Tools](#diagnostic-tools)
12. [Getting Additional Help](#getting-additional-help)

## Installation Issues

### Issue 1: Python Version Compatibility

**Symptoms:**
```
SyntaxError: invalid syntax
ModuleNotFoundError: No module named 'typing_extensions'
```

**Diagnosis:**
```bash
python --version
# Should show Python 3.8 or higher
```

**Solutions:**
```bash
# Install Python 3.8+ using your system package manager
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.8 python3.8-pip

# macOS with Homebrew:
brew install python@3.8

# Windows: Download from python.org

# Use specific Python version
python3.8 -m venv rob_env
source rob_env/bin/activate
python3.8 -m pip install -r requirements.txt
```

### Issue 2: Dependency Installation Failures

**Symptoms:**
```
ERROR: Could not build wheels for package
pip install failed with error code 1
```

**Solutions:**
```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# Install with verbose output to see specific errors
pip install -r requirements.txt -v

# Install dependencies individually
pip install pandas numpy openpyxl python-docx PyPDF2

# For compilation issues on Linux:
sudo apt install build-essential python3-dev

# For macOS compilation issues:
xcode-select --install
```

### Issue 3: Virtual Environment Issues

**Symptoms:**
```
Command 'python' not found
ModuleNotFoundError after installation
```

**Solutions:**
```bash
# Recreate virtual environment
rm -rf rob_env
python -m venv rob_env

# Activate properly
# Linux/macOS:
source rob_env/bin/activate

# Windows:
rob_env\Scripts\activate

# Verify activation
which python  # Should point to rob_env
pip list      # Should show installed packages
```

## Configuration Problems

### Issue 4: Invalid JSON Configuration

**Symptoms:**
```
JSONDecodeError: Expecting ',' delimiter: line 15 column 5
Configuration validation failed
```

**Diagnosis:**
```bash
# Validate JSON syntax
python -m json.tool config/config.json

# Or use online JSON validators
```

**Solutions:**
```bash
# Common JSON errors and fixes:

# Missing comma
{
  "field1": "value1"  # Add comma here
  "field2": "value2"
}

# Trailing comma (not allowed in JSON)
{
  "field1": "value1",
  "field2": "value2",  # Remove this comma
}

# Unescaped quotes
{
  "path": "C:\Users\Name"  # Should be "C:\\Users\\Name"
}

# Use configuration template as starting point
cp config/config_template.json config/config.json
```

### Issue 5: Missing Required Configuration Fields

**Symptoms:**
```
Configuration validation failed: Missing required field 'input_folder'
KeyError: 'llm_models'
```

**Solutions:**
```bash
# Check required fields
python main.py start -c config/config.json --validate-only

# Minimal working configuration:
{
  "paths": {
    "input_folder": "input/documents",
    "output_folder": "output/results"
  },
  "llm_models": [
    {
      "name": "Model1",
      "api_key": "your_key",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-3.5-turbo"
    }
  ]
}
```

### Issue 6: Invalid File Paths

**Symptoms:**
```
FileNotFoundError: Input folder not found: /path/to/input
PermissionError: Cannot write to output directory
```

**Solutions:**
```bash
# Check path existence
ls -la /path/to/input
ls -la /path/to/output

# Create missing directories
mkdir -p input/documents
mkdir -p output/results

# Fix permissions
chmod 755 input/documents
chmod 755 output/results

# Use absolute paths in configuration
{
  "paths": {
    "input_folder": "/absolute/path/to/input",
    "output_folder": "/absolute/path/to/output"
  }
}
```

## Runtime Errors

### Issue 7: Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'src.rob_evaluator'
ImportError: cannot import name 'LanguageManager'
```

**Solutions:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Run from correct directory
cd robust_rob_assessment_tool
python main.py

# Check file structure
ls -la src/
ls -la i18n/

# Reinstall if files are missing
git pull origin main
pip install -r requirements.txt --force-reinstall
```

### Issue 8: Language Manager Errors

**Symptoms:**
```
FileNotFoundError: i18n/i18n_config.json not found
KeyError: 'welcome' in language configuration
```

**Solutions:**
```bash
# Check i18n files exist
ls -la i18n/
cat i18n/i18n_config.json

# Restore missing i18n files from repository
git checkout i18n/i18n_config.json

# Use English fallback
python main.py -l en
```

## Performance Issues

### Issue 9: Slow Processing

**Symptoms:**
- Very slow document processing
- High CPU usage with low throughput
- Long wait times between documents

**Diagnosis:**
```bash
# Check system resources
top -p $(pgrep -f "python main.py")
htop  # If available

# Monitor processing
python main.py monitor -r 5
```

**Solutions:**
```bash
# Increase parallel workers
python main.py start -c config.json -w 8

# Optimize configuration
{
  "parallel": {
    "enabled": true,
    "max_workers": 8,
    "max_documents_per_batch": 50
  },
  "processing": {
    "max_text_length": 15000  # Reduce if documents are very long
  }
}

# Use faster LLM models
{
  "llm_models": [
    {
      "model_name": "gpt-3.5-turbo"  # Faster than gpt-4
    }
  ]
}
```

### Issue 10: High Memory Usage

**Symptoms:**
```
MemoryError: Unable to allocate memory
System becomes unresponsive
Process killed by system
```

**Solutions:**
```bash
# Reduce parallel workers
{
  "parallel": {
    "max_workers": 2,
    "memory_limit_gb": 4.0
  }
}

# Reduce batch sizes
{
  "parallel": {
    "max_documents_per_batch": 10
  }
}

# Reduce text length
{
  "processing": {
    "max_text_length": 10000
  }
}

# Monitor memory usage
python main.py start -c config.json --verbose
```

## API and Network Issues

### Issue 11: API Authentication Failures

**Symptoms:**
```
Authentication failed for LLM service
401 Unauthorized
Invalid API key
```

**Solutions:**
```bash
# Verify API key format
echo "API Key length: ${#API_KEY}"
# OpenAI keys start with "sk-"
# Anthropic keys start with "sk-ant-"

# Test API key manually
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.openai.com/v1/models

# Check API key permissions and quota
# Visit provider dashboard to verify key status

# Use environment variables for security
export OPENAI_API_KEY="your_key_here"
# Update configuration to use environment variable
{
  "llm_models": [
    {
      "api_key": "${OPENAI_API_KEY}"
    }
  ]
}
```

### Issue 12: Network Timeouts

**Symptoms:**
```
Request timeout after 60 seconds
Connection reset by peer
Network is unreachable
```

**Solutions:**
```bash
# Increase timeout values
{
  "llm_models": [
    {
      "timeout": 120,  # Increase from default 60
      "max_retries": 5
    }
  ]
}

# Check network connectivity
ping api.openai.com
curl -I https://api.openai.com/v1/models

# Use proxy if required
export https_proxy=http://proxy.company.com:8080
export http_proxy=http://proxy.company.com:8080
```

### Issue 13: Rate Limiting

**Symptoms:**
```
Rate limit exceeded
429 Too Many Requests
API quota exceeded
```

**Solutions:**
```bash
# Reduce parallel workers to stay within rate limits
{
  "parallel": {
    "max_workers": 2,  # Reduce concurrent requests
    "retry_attempts": 5
  }
}

# Add delays between requests (if supported by provider)
{
  "llm_models": [
    {
      "request_delay": 1.0  # 1 second delay between requests
    }
  ]
}

# Monitor API usage in provider dashboard
# Upgrade API plan if needed
```

## Memory and Resource Problems

### Issue 14: Disk Space Issues

**Symptoms:**
```
No space left on device
OSError: [Errno 28] No space left on device
```

**Solutions:**
```bash
# Check disk space
df -h

# Clean up temporary files
python main.py cleanup --force

# Remove old checkpoints
find . -name "*.checkpoint.json" -mtime +7 -delete

# Move large files to external storage
mv output/large_results /external/storage/

# Configure smaller temp directory
{
  "paths": {
    "temp_folder": "/tmp/rob_temp"  # Use system temp
  }
}
```

### Issue 15: File Handle Exhaustion

**Symptoms:**
```
OSError: [Errno 24] Too many open files
```

**Solutions:**
```bash
# Check current limits
ulimit -n

# Increase file handle limit
ulimit -n 4096

# Make permanent (Linux)
echo "* soft nofile 4096" >> /etc/security/limits.conf
echo "* hard nofile 8192" >> /etc/security/limits.conf

# Reduce parallel workers if issue persists
{
  "parallel": {
    "max_workers": 4  # Reduce from higher number
  }
}
```

## File and Path Issues

### Issue 16: Document Format Issues

**Symptoms:**
```
UnsupportedFormat: Cannot read document
PDFReadError: Invalid PDF structure
DocxPackageNotFoundError
```

**Solutions:**
```bash
# Check document formats
file input/documents/*

# Supported formats: PDF, DOCX
# Convert unsupported formats:
# DOC to DOCX: Use LibreOffice or Word
# Images: Use OCR tools like Tesseract

# Skip problematic documents
{
  "processing": {
    "skip_invalid_documents": true,
    "continue_on_error": true
  }
}

# Validate documents before processing
python -c "
import os
from pathlib import Path

input_dir = 'input/documents'
for file_path in Path(input_dir).glob('*'):
    if file_path.suffix.lower() not in ['.pdf', '.docx']:
        print(f'Unsupported format: {file_path}')
"
```

### Issue 17: Unicode and Encoding Issues

**Symptoms:**
```
UnicodeDecodeError: 'utf-8' codec can't decode
UnicodeEncodeError: 'ascii' codec can't encode
```

**Solutions:**
```bash
# Set proper locale
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# Python encoding settings
export PYTHONIOENCODING=utf-8

# Configuration for encoding handling
{
  "processing": {
    "text_encoding": "utf-8",
    "handle_encoding_errors": "replace"
  }
}
```

## Parallel Processing Issues

### Issue 18: Worker Process Failures

**Symptoms:**
```
Worker process failed to start
Process coordination error
Batch processing incomplete
```

**Solutions:**
```bash
# Check system resources
free -h
ps aux | grep python

# Reduce worker count
{
  "parallel": {
    "max_workers": 2,  # Start with fewer workers
    "auto_detect_workers": false
  }
}

# Enable detailed logging
python main.py start -c config.json --verbose --log-file worker_debug.log

# Disable parallel processing temporarily
{
  "parallel": {
    "enabled": false
  }
}
```

### Issue 19: Checkpoint Corruption

**Symptoms:**
```
Checkpoint file corrupted
Invalid checkpoint format
Cannot resume from checkpoint
```

**Solutions:**
```bash
# Validate checkpoint file
python -m json.tool checkpoint_file.json

# Restore from backup checkpoint
ls -la *.checkpoint.json
python main.py resume -s backup_checkpoint.json

# Start fresh if all checkpoints corrupted
rm *.checkpoint.json
python main.py start -c config.json

# Prevent corruption with frequent checkpoints
{
  "parallel": {
    "checkpoint_interval": 5  # Save more frequently
  }
}
```

## Cost and Billing Issues

### Issue 20: Unexpected High Costs

**Symptoms:**
- API bills higher than expected
- Cost tracking shows high token usage
- Budget alerts triggering frequently

**Solutions:**
```bash
# Enable cost monitoring
{
  "cost_tracking": {
    "enabled": true,
    "cost_alerts": true,
    "max_cost_threshold": 50.0
  }
}

# Reduce token usage
{
  "processing": {
    "max_text_length": 8000,  # Reduce from default
    "eval_optional_items": false  # Skip optional assessments
  }
}

# Use cheaper models for initial testing
{
  "llm_models": [
    {
      "model_name": "gpt-3.5-turbo"  # Cheaper than gpt-4
    }
  ]
}

# Analyze cost patterns
python -c "
import pandas as pd
df = pd.read_excel('output/cost_report.xlsx')
print('Cost per document statistics:')
print(df['cost_per_document'].describe())
print('\\nHighest cost documents:')
print(df.nlargest(5, 'cost_per_document')[['document_name', 'cost_per_document']])
"
```

## Output and Results Issues

### Issue 21: Missing or Incomplete Results

**Symptoms:**
- Empty output files
- Missing documents in results
- Incomplete Excel reports

**Solutions:**
```bash
# Check processing logs
tail -f processing.log

# Verify all documents were processed
python -c "
import os
input_count = len(os.listdir('input/documents'))
# Check if output count matches input count
print(f'Input documents: {input_count}')
"

# Re-run with error handling
{
  "processing": {
    "continue_on_error": true,
    "log_errors": true
  }
}

# Check for failed documents
grep -i "error\|failed" processing.log
```

### Issue 22: Visualization Issues

**Symptoms:**
```
HTML visualization not loading
JavaScript errors in browser
Charts not displaying
```

**Solutions:**
```bash
# Check HTML file generation
ls -la output/*.html

# Open in different browsers
# Chrome, Firefox, Safari, Edge

# Check browser console for errors
# F12 -> Console tab

# Regenerate visualization
python main.py merge -i output/batch_results -o results.xlsx --format both
```

## Diagnostic Tools

### System Information Tool

```bash
# Get comprehensive system information
python main.py --system-info

# Manual system check
python -c "
import platform
import psutil
import sys

print(f'Python version: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'CPU cores: {psutil.cpu_count()}')
print(f'Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB')
print(f'Disk space: {psutil.disk_usage(\".\").free / (1024**3):.1f} GB')
"
```

### Configuration Validation Tool

```bash
# Validate configuration
python main.py start -c config/config.json --validate-only

# Detailed validation
python -c "
import json
from pathlib import Path

config_file = 'config/config.json'
with open(config_file) as f:
    config = json.load(f)

# Check required fields
required_fields = ['paths', 'llm_models']
for field in required_fields:
    if field not in config:
        print(f'Missing required field: {field}')

# Check paths exist
if 'paths' in config:
    for path_name, path_value in config['paths'].items():
        if path_name.endswith('_folder'):
            if not Path(path_value).exists():
                print(f'Path does not exist: {path_name} = {path_value}')
"
```

### Log Analysis Tool

```bash
# Analyze log files for common issues
grep -i "error\|exception\|failed" *.log

# Count error types
grep -i "error" *.log | cut -d: -f2 | sort | uniq -c | sort -nr

# Find performance bottlenecks
grep -i "processing time\|elapsed" *.log
```

## Getting Additional Help

### Before Seeking Help

1. **Check this troubleshooting guide** for your specific issue
2. **Review configuration** against the template and examples
3. **Test with minimal configuration** to isolate the problem
4. **Collect diagnostic information** using the tools above

### Information to Include When Seeking Help

```bash
# System information
python main.py --system-info > system_info.txt

# Configuration (remove sensitive API keys)
cp config/config.json config/config_sanitized.json
# Edit config_sanitized.json to remove API keys

# Error logs
tail -100 *.log > error_logs.txt

# Python environment
pip list > pip_list.txt
python --version > python_version.txt
```

### Support Channels

1. **GitHub Issues**: https://github.com/smartebm/robust-rob-assessment-tool/issues
   - Best for: Bug reports, feature requests
   - Include: System info, configuration, error logs

2. **Email Support**: contact@smartebm.org
   - Best for: Configuration help, usage questions
   - Include: Detailed description of issue and steps taken

3. **Community Forum**: https://community.smartebm.org
   - Best for: General questions, sharing experiences
   - Search existing topics before posting

4. **Documentation**: https://docs.smartebm.org
   - Comprehensive guides and API reference
   - Updated regularly with new examples

### Creating Effective Bug Reports

```markdown
## Bug Report Template

**Environment:**
- OS: [e.g., Ubuntu 20.04, Windows 10, macOS 12.0]
- Python version: [e.g., 3.9.7]
- Tool version: [e.g., v2.0.1]

**Configuration:**
```json
{
  // Sanitized configuration (remove API keys)
}
```

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
What you expected to happen

**Actual Behavior:**
What actually happened

**Error Messages:**
```
Paste error messages here
```

**Additional Context:**
Any other relevant information
```

### Emergency Troubleshooting

If the tool is completely non-functional:

```bash
# 1. Verify basic Python functionality
python -c "print('Python is working')"

# 2. Check if main.py exists and is readable
ls -la main.py
head -5 main.py

# 3. Try minimal import test
python -c "import sys; print('Python path:', sys.path)"

# 4. Reinstall from scratch
rm -rf rob_env
git clone https://github.com/smartebm/robust-rob-assessment-tool.git
cd robust-rob-assessment-tool
python -m venv rob_env
source rob_env/bin/activate
pip install -r requirements.txt
python main.py --version
```

This troubleshooting guide covers the most common issues users encounter. If you experience an issue not covered here, please refer to the support channels listed above for additional assistance.