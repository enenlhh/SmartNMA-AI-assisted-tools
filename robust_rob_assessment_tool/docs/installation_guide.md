# Installation Guide

This comprehensive guide walks you through installing and setting up the ROB Assessment Tool v2.0 on different operating systems.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Checklist](#pre-installation-checklist)
3. [Installation Methods](#installation-methods)
4. [Platform-Specific Instructions](#platform-specific-instructions)
5. [Post-Installation Setup](#post-installation-setup)
6. [Verification and Testing](#verification-and-testing)
7. [Troubleshooting Installation Issues](#troubleshooting-installation-issues)
8. [Advanced Installation Options](#advanced-installation-options)

## System Requirements

### Minimum Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Operating System** | Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+) | 64-bit systems only |
| **Python** | 3.8 or higher | Python 3.10+ recommended |
| **RAM** | 4 GB | 8 GB+ recommended for parallel processing |
| **Storage** | 2 GB free space | Additional space needed for documents and results |
| **Network** | Internet connection | Required for LLM API access |

### Recommended Requirements

| Component | Recommendation | Benefit |
|-----------|----------------|---------|
| **Python** | 3.10 or 3.11 | Better performance and compatibility |
| **RAM** | 16 GB or more | Optimal parallel processing performance |
| **CPU** | 4+ cores | Better parallel processing efficiency |
| **Storage** | SSD with 10+ GB free | Faster I/O operations |
| **Network** | Stable broadband | Reliable API communication |

### Software Dependencies

The tool requires several Python packages that will be installed automatically:

- **pandas** (≥1.3.0): Data manipulation and analysis
- **openpyxl** (≥3.0.0): Excel file handling
- **python-docx** (≥0.8.0): Word document processing
- **PyPDF2** (≥2.0.0): PDF document processing
- **requests** (≥2.25.0): HTTP requests for API communication
- **matplotlib** (≥3.3.0): Visualization and plotting
- **seaborn** (≥0.11.0): Statistical data visualization

## Pre-Installation Checklist

Before installing, ensure you have:

- [ ] Administrative/sudo privileges (if needed)
- [ ] Python 3.8+ installed
- [ ] Git installed (for cloning repository)
- [ ] LLM API keys (OpenAI, Anthropic, etc.)
- [ ] Sufficient disk space (2+ GB)
- [ ] Stable internet connection

### Check Current Python Installation

```bash
# Check Python version
python --version
# or
python3 --version

# Check pip availability
pip --version
# or
python -m pip --version
```

If Python is not installed or version is below 3.8, install it first:

- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: Use Homebrew (`brew install python`) or download from python.org
- **Linux**: Use system package manager (`apt install python3`)

## Installation Methods

### Method 1: Quick Installation (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/smartebm/robust-rob-assessment-tool.git
cd robust-rob-assessment-tool

# 2. Create virtual environment
python -m venv rob_env

# 3. Activate virtual environment
# On Windows:
rob_env\Scripts\activate
# On macOS/Linux:
source rob_env/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python main.py --version
```

### Method 2: Manual Installation

```bash
# 1. Download source code
wget https://github.com/smartebm/robust-rob-assessment-tool/archive/main.zip
unzip main.zip
cd robust-rob-assessment-tool-main

# 2. Create virtual environment
python -m venv rob_env
source rob_env/bin/activate  # Linux/macOS
# rob_env\Scripts\activate    # Windows

# 3. Install dependencies manually
pip install pandas>=1.3.0
pip install openpyxl>=3.0.0
pip install python-docx>=0.8.0
pip install PyPDF2>=2.0.0
pip install requests>=2.25.0
pip install matplotlib>=3.3.0
pip install seaborn>=0.11.0

# 4. Test installation
python main.py --version
```

### Method 3: Development Installation

```bash
# 1. Clone with development branch
git clone -b develop https://github.com/smartebm/robust-rob-assessment-tool.git
cd robust-rob-assessment-tool

# 2. Create development environment
python -m venv rob_dev_env
source rob_dev_env/bin/activate

# 3. Install with development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# 4. Install in editable mode
pip install -e .
```

## Platform-Specific Instructions

### Windows Installation

#### Prerequisites
```powershell
# Check Windows version
winver

# Install Python from Microsoft Store or python.org
# Ensure "Add Python to PATH" is checked during installation

# Verify installation
python --version
pip --version
```

#### Installation Steps
```powershell
# Open PowerShell or Command Prompt as Administrator (if needed)

# 1. Clone repository
git clone https://github.com/smartebm/robust-rob-assessment-tool.git
cd robust-rob-assessment-tool

# 2. Create virtual environment
python -m venv rob_env

# 3. Activate virtual environment
rob_env\Scripts\activate

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Test installation
python main.py --version
```

#### Windows-Specific Issues
```powershell
# If execution policy prevents script execution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# If long path names cause issues:
git config --system core.longpaths true

# If antivirus blocks installation:
# Add rob_env folder to antivirus exclusions
```

### macOS Installation

#### Prerequisites
```bash
# Check macOS version
sw_vers

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python via Homebrew
brew install python

# Or install Xcode Command Line Tools
xcode-select --install
```

#### Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/smartebm/robust-rob-assessment-tool.git
cd robust-rob-assessment-tool

# 2. Create virtual environment
python3 -m venv rob_env

# 3. Activate virtual environment
source rob_env/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Test installation
python main.py --version
```

#### macOS-Specific Issues
```bash
# If certificate issues occur:
/Applications/Python\ 3.x/Install\ Certificates.command

# If compilation fails for native extensions:
export CPPFLAGS=-I/usr/local/include
export LDFLAGS=-L/usr/local/lib
pip install -r requirements.txt

# For Apple Silicon Macs (M1/M2):
arch -arm64 pip install -r requirements.txt
```

### Linux Installation

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and development tools
sudo apt install python3 python3-pip python3-venv python3-dev
sudo apt install build-essential git

# Clone and install
git clone https://github.com/smartebm/robust-rob-assessment-tool.git
cd robust-rob-assessment-tool

python3 -m venv rob_env
source rob_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python main.py --version
```

#### CentOS/RHEL/Fedora
```bash
# CentOS/RHEL
sudo yum install python3 python3-pip python3-devel gcc git
# or for newer versions:
sudo dnf install python3 python3-pip python3-devel gcc git

# Fedora
sudo dnf install python3 python3-pip python3-devel gcc git

# Continue with standard installation
git clone https://github.com/smartebm/robust-rob-assessment-tool.git
cd robust-rob-assessment-tool

python3 -m venv rob_env
source rob_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python main.py --version
```

#### Arch Linux
```bash
# Install dependencies
sudo pacman -S python python-pip git base-devel

# Continue with standard installation
git clone https://github.com/smartebm/robust-rob-assessment-tool.git
cd robust-rob-assessment-tool

python -m venv rob_env
source rob_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

python main.py --version
```

## Post-Installation Setup

### 1. Create Configuration File

```bash
# Copy template configuration
cp config/config_template.json config/config.json

# Edit configuration with your settings
# Use your preferred text editor:
nano config/config.json
# or
vim config/config.json
# or
code config/config.json  # VS Code
```

### 2. Set Up API Keys

```bash
# Method 1: Edit configuration file directly
# Add your API keys to config/config.json

# Method 2: Use environment variables (recommended)
export OPENAI_API_KEY="your_openai_key_here"
export ANTHROPIC_API_KEY="your_anthropic_key_here"

# Make environment variables permanent
echo 'export OPENAI_API_KEY="your_openai_key_here"' >> ~/.bashrc
echo 'export ANTHROPIC_API_KEY="your_anthropic_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Create Directory Structure

```bash
# Create necessary directories
mkdir -p input/documents
mkdir -p output/results
mkdir -p checkpoints
mkdir -p logs

# Set appropriate permissions (Linux/macOS)
chmod 755 input output checkpoints logs
```

### 4. Test Basic Functionality

```bash
# Test system information
python main.py --system-info

# Test configuration validation
python main.py start -c config/config.json --validate-only

# Test interactive mode
python main.py
```

## Verification and Testing

### Basic Functionality Test

```bash
# 1. Check version
python main.py --version

# 2. Test help system
python main.py --help
python main.py start --help

# 3. Test configuration validation
python main.py start -c config/config.json --validate-only

# 4. Test system detection
python main.py --system-info
```

### Integration Test

```bash
# 1. Create test documents directory
mkdir -p input/test_docs

# 2. Add a small test PDF (or create a simple text file)
echo "This is a test document for ROB assessment." > input/test_docs/test.txt

# 3. Create minimal test configuration
cat > config/test_config.json << EOF
{
  "paths": {
    "input_folder": "input/test_docs",
    "output_folder": "output/test_results"
  },
  "processing": {
    "max_text_length": 1000,
    "eval_optional_items": false
  },
  "parallel": {
    "enabled": false
  },
  "llm_models": [
    {
      "name": "Test Model",
      "api_key": "test_key_placeholder",
      "base_url": "https://api.openai.com/v1",
      "model_name": "gpt-3.5-turbo"
    }
  ]
}
EOF

# 4. Test configuration (will fail on API call, but should validate config)
python main.py start -c config/test_config.json --validate-only
```

### Performance Test

```bash
# Test system resource detection
python -c "
from core.system_detector import SystemCapacityDetector
capacity = SystemCapacityDetector.detect_system_capacity()
print('System Capacity:', capacity)
recommended = SystemCapacityDetector.recommend_parallel_workers({})
print('Recommended Workers:', recommended)
"
```

## Troubleshooting Installation Issues

### Common Installation Problems

#### Problem 1: Python Not Found
```bash
# Symptoms
python: command not found
'python' is not recognized as an internal or external command

# Solutions
# Windows: Add Python to PATH or use py launcher
py --version
py -m pip install -r requirements.txt

# Linux/macOS: Use python3
python3 --version
python3 -m pip install -r requirements.txt
```

#### Problem 2: Permission Denied
```bash
# Symptoms
PermissionError: [Errno 13] Permission denied

# Solutions
# Use virtual environment (recommended)
python -m venv rob_env
source rob_env/bin/activate
pip install -r requirements.txt

# Or install with --user flag
pip install --user -r requirements.txt
```

#### Problem 3: Package Compilation Errors
```bash
# Symptoms
error: Microsoft Visual C++ 14.0 is required
gcc: command not found

# Solutions
# Windows: Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Linux: Install build tools
sudo apt install build-essential python3-dev  # Ubuntu/Debian
sudo yum install gcc python3-devel           # CentOS/RHEL

# macOS: Install Xcode Command Line Tools
xcode-select --install
```

#### Problem 4: SSL Certificate Errors
```bash
# Symptoms
SSL: CERTIFICATE_VERIFY_FAILED

# Solutions
# macOS: Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command

# All platforms: Upgrade certificates
pip install --upgrade certifi

# Corporate networks: Use trusted hosts
pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org
```

### Diagnostic Commands

```bash
# Check Python installation
python --version
python -c "import sys; print(sys.executable)"
python -c "import sys; print(sys.path)"

# Check pip installation
pip --version
pip list

# Check virtual environment
which python  # Should point to rob_env
echo $VIRTUAL_ENV  # Should show rob_env path

# Check package imports
python -c "import pandas; print('pandas OK')"
python -c "import requests; print('requests OK')"
python -c "import openpyxl; print('openpyxl OK')"
```

## Advanced Installation Options

### Docker Installation

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p input output checkpoints logs

# Set environment variables
ENV PYTHONPATH=/app

# Default command
CMD ["python", "main.py", "--help"]
```

```bash
# Build and run Docker container
docker build -t rob-assessment-tool .
docker run -it --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output rob-assessment-tool
```

### Conda Installation

```bash
# Create conda environment
conda create -n rob_env python=3.10
conda activate rob_env

# Install dependencies via conda (when available)
conda install pandas openpyxl matplotlib seaborn requests

# Install remaining dependencies via pip
pip install python-docx PyPDF2

# Clone and test
git clone https://github.com/smartebm/robust-rob-assessment-tool.git
cd robust-rob-assessment-tool
python main.py --version
```

### System-Wide Installation (Not Recommended)

```bash
# Only use if you understand the implications
sudo pip install -r requirements.txt

# Better alternative: use pipx for isolated installation
pip install pipx
pipx install git+https://github.com/smartebm/robust-rob-assessment-tool.git
```

### Offline Installation

```bash
# On connected machine: Download packages
pip download -r requirements.txt -d packages/

# Transfer packages/ directory to offline machine
# On offline machine:
pip install --no-index --find-links packages/ -r requirements.txt
```

## Installation Verification Checklist

After installation, verify these components work:

- [ ] Python version 3.8+ is available
- [ ] Virtual environment is activated
- [ ] All required packages are installed
- [ ] Main script runs without import errors
- [ ] Configuration validation works
- [ ] System information detection works
- [ ] Directory structure is created
- [ ] API keys are configured (if available)
- [ ] Basic functionality test passes

## Next Steps

After successful installation:

1. **Read the Configuration Guide**: Learn how to set up your configuration file
2. **Review Usage Examples**: Understand different ways to use the tool
3. **Test with Sample Data**: Run a small test assessment
4. **Set Up Your Project**: Configure for your specific systematic review
5. **Join the Community**: Connect with other users for support and tips

For detailed usage instructions, see the [Usage Examples](usage_examples.md) and [Configuration Guide](configuration_guide.md).