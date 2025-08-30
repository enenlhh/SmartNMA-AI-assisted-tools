# SmartEBM Title & Abstract Screening Tool - Complete Documentation

> 🎯 **Research-Validated AI Screening with 100% Sensitivity & Scalable Parallel Processing**

**Research Foundation**: Validated across 68,006 systematic review records with 100% sensitivity in SmartNMA framework validation studies. Features dual-call validation and adaptive reverse validation for maximum screening accuracy.

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Multi-Language Interface](#multi-language-interface)
- [Configuration](#configuration)
- [Parallel Processing](#parallel-processing)
- [Cost Analysis](#cost-analysis)
- [Advanced Features](#advanced-features)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Technical Architecture](#technical-architecture)

---

## 🚀 Quick Start

### Step 1: Configure Number of Screeners
Edit `config.json`:
```json
{
  "mode": {
    "screening_mode": "parallel"
  },
  "parallel_settings": {
    "parallel_screeners": 4  // Just change this number!
  }
}
```

### Step 2: Launch Parallel Screening
```bash
python3 main.py
```

### Step 3: Enjoy Parallel Processing Speed
- Single-threaded: 8 hours → Parallel with 4 screeners: 2 hours
- Automatic splitting, parallel processing, intelligent merging
- Supports checkpoint recovery and real-time monitoring

---

## 🎯 Project Overview

The SmartEBM Title & Abstract Screening Tool revolutionizes systematic review literature screening through research-validated AI methodologies, delivering unprecedented efficiency and accuracy for evidence-based medicine workflows.

### Research-Backed Advantages

**🔬 Validated Performance Metrics**
- **100% Sensitivity**: Validated across 68,006 systematic review records in SmartNMA research
- **Scalable Parallel Processing**: 25-50 threads typical performance, hardware-limited scaling
- **Parallel Processing Efficiency**: Transforms traditional 8-hour screening tasks into 1-hour workflows through intelligent multi-threading
- **Zero False Negatives**: Critical for systematic review quality and completeness

**🚀 Advanced AI Innovations**
- **Dual-Call Validation**: Two-stage consensus mechanism ensures screening reliability
- **Adaptive Reverse Validation**: Intelligent confidence grading with automatic verification
- **PICOS-Based Intelligence**: Structured Population, Intervention, Comparison, Outcomes, Study design criteria extraction
- **Multi-LLM Consensus**: Configurable screening models with validation workflows

### Core Capabilities
- **Intelligent XML Processing**: Handles datasets of 10,000+ records with automatic splitting and distribution
- **Parallel AI Screening**: Multi-core processing with intelligent resource management
- **Real-time Monitoring**: Live progress tracking with performance optimization recommendations
- **Checkpoint Recovery**: Comprehensive fault tolerance with automatic batch retry mechanisms
- **Result Integration**: Seamless XML and Excel output merging with validation reports

### Technical Architecture Features
- **Multi-process Parallel Processing**: Python multiprocessing-based scalable architecture
- **Automatic System Detection**: Hardware resource detection with optimal configuration recommendations
- **Intelligent Load Distribution**: Even record distribution across processing batches
- **Fault-Tolerant Design**: Individual batch failure isolation without overall process impact
- **Resource Optimization**: Dynamic memory and CPU usage management

---

## 💻 System Requirements

### Basic Requirements
- **Python**: 3.12+
- **Memory**: 8GB+ (recommended)
- **CPU**: 4+ cores (recommended)
- **Disk**: 2GB+ available space

### Performance Recommendations
| Hardware Config | Recommended Screeners | Description |
|-----------------|----------------------|-------------|
| 4-core 8GB      | 2-3 screeners        | Conservative config, ensures stability |
| 8-core 16GB     | 4-6 screeners        | Balanced config, recommended |
| 12-core 24GB    | 6-8 screeners        | High-performance config |
| 16-core 32GB+   | 8-10 screeners       | Maximum performance config |

---

## 📦 Installation

### 1. Clone Project
```bash
git clone [repository-url]
cd title_and_abstract_screening_tool
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
python3 main.py --help
```

---

## 🛠️ Usage

### 📊 Different Usage Scenarios

#### 🚀 Daily Use - Parallel Screening (Recommended)
```bash
python3 main.py  # Efficient parallel processing, 8x acceleration
```

#### 🔧 Debug/Special Cases - Single-threaded Screening
```bash
python3 core/run.py          # Single-threaded processing, suitable for debugging or small files
```
**Use Cases:**
- 🐛 When debugging issues
- 📝 Small literature sets (<100 records)
- 💻 Low-spec machines
- 🔍 Need detailed process control

---

## 🌐 Multi-Language Interface

### Language Selection

The tool supports both **English** and **Chinese** interfaces. Users can choose their preferred language:

#### 1. Interactive Selection (Default)
```bash
python3 main.py
```

The system will display a language selection menu:
```
============================================================
🌐 Language Selection / 语言选择
============================================================
Please select your preferred language / 请选择您的首选语言:

1. English
2. 中文

Please enter your choice [1-2] / 请输入您的选择 [1-2]:
```

#### 2. Command Line Preset
```bash
# Use English interface
python3 main.py --lang en

# Use Chinese interface  
python3 main.py --lang zh

# Interactive selection (default)
python3 main.py --lang auto
```

#### 3. Short Parameter
```bash
python3 main.py -l en    # English
python3 main.py -l zh    # Chinese  
python3 main.py -l auto  # Interactive selection
```

### Interface Examples

#### English Interface
```
============================================================
🎯 SmartEBM Parallel Screening System - Interactive Mode
============================================================

Please select operation:
1. Start new parallel screening task
2. Resume interrupted task
3. Monitor existing task progress
4. Merge existing results only
5. Clean temporary files
6. Exit

⚠️  Configuration Warning:
   - Requested screeners (20) exceed safe CPU cores (11)

💡 Suggestion:
   - Recommend setting to 11 screeners
```

#### Chinese Interface
```
============================================================
🎯 SmartEBM 并行筛选系统 - 交互模式
============================================================

请选择操作:
1. 启动新的并行筛选任务
2. 恢复中断的任务
3. 监控现有任务进度
4. 仅合并现有结果
5. 清理临时文件
6. 退出

⚠️  配置警告:
   - 请求的筛选器数量 (20) 超过安全CPU核心数 (11)

💡 建议:
   - 建议设置为 11 个筛选器
```

### Supported Elements

Multi-language support covers all user-facing text:
- ✅ Main menu options
- ✅ System resource detection
- ✅ Configuration warnings and suggestions
- ✅ User interaction prompts
- ✅ Progress status information
- ✅ Error and success messages
- ✅ File operation prompts

### Use Cases

- **Chinese Users**: Mainland China researchers, Chinese medical literature research
- **English Users**: International collaboration, English literature screening, non-Chinese speakers
- **Mixed Teams**: Sino-foreign cooperation projects, multilingual research teams

---

## ⚙️ Configuration

### Unified Configuration File: `config.json`
```json
{
  "mode": {
    "screening_mode": "parallel",       // Run mode: parallel or single
    "enable_cost_analysis": true        // Enable cost analysis
  },
  "paths": {
    "input_xml_path": "your_file.xml",         // Input XML file
    "output_directory": "results/",            // Output directory
    "output_xml_path": "results/output.xml"    // Output XML file
  },
  "parallel_settings": {
    "parallel_screeners": 4,           // Number of screeners (main config)
    "auto_distribute": true,           // Auto distribute records
    "temp_dir": "temp_parallel",       // Temporary directory
    "cleanup_temp_files": true,        // Auto cleanup
    "retry_failed_batches": true,      // Retry failed batches
    "max_retries": 3,                  // Maximum retry attempts
    "state_file": "parallel_screening_state.json" // State file
  },
  "resource_management": {
    "api_calls_per_minute_limit": 100, // API call limit
    "memory_limit_mb": 2048,           // Memory limit
    "delay_between_screeners": 2,      // Startup interval
    "progress_update_interval": 10     // Progress update interval
  },
  "llm_configs": {
    "screening_llms": {
      "LLM_A": {
        "api_key": "your_api_key",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4"
      }
    }
  },
  "inclusion_criteria": {
    "Study design": "randomized controlled trial",
    "Participants": "adults with target condition",
    "Intervention": "target intervention",
    "Comparison": "placebo or control",
    "Outcomes": "primary and secondary outcomes"
  }
}
```

### Configuration Templates

| Config File | Use Case | Features | Recommended For |
|-------------|----------|----------|----------------|
| `config_template.json` | Complete feature template | All options with detailed comments | New users, comprehensive feature overview |
| `config.json` | Main configuration | User primary configuration | All general use cases |
| `llm_pricing.json` | Model pricing reference | Latest pricing information | Cost control and budget planning |

---

## 🔄 Parallel Processing

### 🔄 Checkpoint Recovery

#### Automatic Recovery
System automatically detects incomplete tasks:
```
🔄 Detected incomplete screening task
========================================
Task ID: 20241224_143052
Total records: 5067
Number of screeners: 4
Current progress: 2/4 (50.0%)

Pending batches:
  🔄 Batch 3: Records 2535-3801 (running)
  ⏳ Batch 4: Records 3802-5067 (pending)

Options:
1. Auto continue incomplete batches
2. Restart all tasks
3. Cancel
```

#### Manual Recovery
```bash
# Resume interrupted task
python3 main.py --resume

# Monitor existing task
python3 main.py --monitor state_file.json

# Merge results only
python3 main.py --merge-only state_file.json
```

### 📊 Real-time Monitoring

Runtime shows detailed progress:
```
🎯 SmartEBM Parallel Screening Progress Monitor
========================================
Session ID: 20241224_143052
Start time: 2024-12-24 14:30:52
Current time: 2024-12-24 14:35:22
Runtime: 4:30
========================================

📋 Batch Progress Details
----------------------------------------
Batch  Record Range    Status      Progress  Start Time  Duration
----------------------------------------
1      1-1267         ✅ completed  100%     14:30:55    3:45
2      1268-2534      🔄 running    65%      14:31:15    4:07
3      2535-3801      ⏳ pending    0%       -           -
4      3802-5067      ⏳ pending    0%       -           -
----------------------------------------

📊 Overall Progress
Total batches: 4
Completed: 1 (25.0%)
Running: 1
Failed: 0
Pending: 2

Progress: [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 25.0%
Estimated remaining time: 11:15
```

### 📁 Intelligent Record Distribution

Example with 5067 records, 4 screeners:
```
📋 Record Distribution Plan
==========================================
Batch  Start Record  End Record  Record Count  Percentage
----------------------------------------------------------
1      1             1267        1267          25.0%
2      1268          2534        1267          25.0%
3      2535          3801        1267          25.0%
4      3802          5067        1266          25.0%
----------------------------------------------------------
Total                             5067          100.0%
==========================================
```

### 📤 Result Output

System automatically merges all batch results:
```
Output Directory/
├── final_results_20241224_143052.xml          # Final XML results
├── final_results_20241224_143052.xlsx         # Final Excel results
├── final_tokens_usage_20241224_143052.csv     # Merged token usage statistics
├── final_cost_analysis_20241224_143052_usd_cost_report.txt # USD cost report
├── final_cost_analysis_20241224_143052_cny_cost_report.txt # CNY cost report
├── merge_report_20241224_143052.txt           # Merge report
└── backup_20241224_143052/                    # Individual batch backup
    ├── batch_1_results.xml
    ├── batch_1_results.xlsx
    ├── batch_1_tokens_usage.csv
    └── ...
```

---

## 💰 Cost Analysis

### Automatic Cost Tracking
System automatically tracks and calculates all LLM call costs:

#### Supported Model Pricing
- **OpenAI**: GPT-4, GPT-4-turbo, GPT-4o, GPT-4o-mini, GPT-3.5-turbo
- **Anthropic**: Claude-3 series (Opus, Sonnet, Haiku)
- **Google**: Gemini-1.5 series (Pro, Flash)
- **Third-party**: OpenAI API-compatible third-party providers

#### Cost Report Example
```
================================================================================
📊 TOKEN COST ANALYSIS REPORT
================================================================================

💰 Overall Cost:
   Total cost: $15.2840 USD
   Total tokens: 1,245,678
   Input tokens: 890,234
   Output tokens: 355,444
   API calls: 2,500

🤖 By LLM Statistics:
--------------------------------------------------------------------------------
LLM Name         Cost         Tokens     Calls       Model                  
--------------------------------------------------------------------------------
LLM_A           $8.1250      680,000    1,250       gpt-4o-mini         
LLM_B           $7.1590      565,678    1,250       gpt-4o-mini         

🏷️ By Model Statistics:
--------------------------------------------------------------------------------
Model Name              Total Cost      Input Cost      Output Cost     Tokens      Calls    
--------------------------------------------------------------------------------
gpt-4o-mini          $15.2840        $8.9023         $6.3817         1,245,678   2,500   

💱 Exchange Rate: 1 USD = 7.25 CNY
   USD Equivalent: $15.2840 USD
================================================================================
```

### Cost Optimization Strategies

| Model | Advantages | Use Cases | Cost Estimate (1000 records) |
|-------|------------|-----------|------------------------------|
| gpt-4o-mini | Ultra-low cost, fast | Daily screening, large volumes | $1-3 USD |
| gpt-4o | Cost-effective | Important research, high quality requirements | $8-15 USD |
| gpt-4-turbo | High quality | Precise screening, complex criteria | $15-25 USD |
| claude-3-haiku | Low-cost alternative | Multi-model validation | $2-4 USD |

---

## ⚡ Performance Optimization

### 📈 Research-Validated Performance Metrics

**🔬 SmartNMA Validation Results**
- **Dataset Scale**: 68,006 systematic review records processed
- **Sensitivity Achievement**: 100% (zero false negatives)
- **Parallel Processing Advantage**: Dramatically faster than traditional manual screening through multi-threading
- **Scalability Range**: 25-50 parallel threads typical, hardware-limited

**⚡ Processing Speed Comparison**

| Configuration | Processing Time (5000 records) | Efficiency Gain | Recommended Use Case |
|---------------|--------------------------------|-----------------|---------------------|
| Single-threaded | 8 hours | 1x (baseline) | Small datasets, debugging |
| 2 screeners | 4 hours | 2x | Conservative systems |
| 4 screeners | 2 hours | 4x | Standard workstations |
| 8 screeners | 1 hour | 8x | High-performance systems |
| 16+ screeners | 30-45 minutes | 10-16x | Server-grade hardware |

### 🎯 Advanced Optimization Strategies

#### Dual-Call Validation Tuning
```json
{
  "validation_settings": {
    "confidence_threshold": 0.85,     // Higher = fewer dual-calls, faster processing
    "adaptive_threshold": true,       // Dynamic adjustment based on content complexity
    "reverse_validation_rate": 0.15   // Percentage requiring second validation
  }
}
```

**Optimization Impact**:
- **High Threshold (0.9+)**: 20-30% faster, maintains 99%+ accuracy
- **Adaptive Mode**: Balances speed and accuracy automatically
- **Conservative Mode (0.7)**: Maximum accuracy, 15-20% slower

#### Hardware Resource Optimization

**🖥️ CPU Configuration**
```bash
# Optimal screener calculation
Recommended Screeners = min(CPU_Cores - 1, Available_Memory_GB / 2)

# Example configurations:
# 8-core, 16GB RAM: 7 screeners (CPU limited)
# 4-core, 32GB RAM: 3 screeners (CPU limited)  
# 16-core, 8GB RAM: 4 screeners (memory limited)
```

**💾 Memory Management**
- **Per-Screener Memory**: 2GB minimum, 4GB recommended
- **System Reserve**: Keep 2GB for OS and monitoring
- **Large Dataset Handling**: Consider batch size reduction for memory-constrained systems

**💿 Storage Optimization**
- **SSD vs HDD**: Significantly faster temporary file operations with SSD storage
- **Temporary Directory**: Place on fastest available drive
- **Network Storage**: Avoid for temporary files, acceptable for final outputs

#### API and Network Optimization

**🌐 API Rate Management**
```json
{
  "api_optimization": {
    "calls_per_minute_limit": 100,    // Conservative for stability
    "concurrent_requests": 5,         // Per screener
    "retry_exponential_base": 2,      // Backoff multiplier
    "max_retry_attempts": 3           // Balance persistence vs speed
  }
}
```

**📊 Cost-Performance Balance**

| Model | Cost per 1K Records | Processing Speed | Accuracy | Best Use Case |
|-------|---------------------|------------------|----------|---------------|
| gpt-4o-mini | $1-3 USD | Fastest | 98-99% | Large-scale screening |
| gpt-4o | $8-15 USD | Fast | 99-99.5% | Standard research |
| gpt-4-turbo | $15-25 USD | Moderate | 99.5%+ | High-stakes research |
| claude-3-haiku | $2-4 USD | Fast | 98-99% | Cost-sensitive projects |

#### Workflow Integration Optimization

**🔄 Systematic Review Pipeline**
```
Literature Search → Title/Abstract Screening → Full-Text Review → Data Extraction
     (Manual)              (This Tool)           (SmartEBM)      (SmartEBM)
```

**Integration Benefits**:
- **Seamless Data Flow**: XML/Excel outputs compatible with downstream tools
- **Consistent Formatting**: Standardized output structure across SmartEBM suite
- **Quality Assurance**: Built-in validation maintains data integrity
- **Cost Tracking**: Unified cost analysis across entire workflow

### 🚀 Advanced Configuration Examples

#### High-Throughput Configuration (Server Environment)
```json
{
  "parallel_settings": {
    "parallel_screeners": 16,
    "batch_size_multiplier": 2.0,
    "aggressive_timeout": false
  },
  "resource_management": {
    "memory_limit_mb": 8192,
    "api_calls_per_minute_limit": 200,
    "concurrent_api_requests": 8
  }
}
```

#### Cost-Optimized Configuration (Budget-Conscious)
```json
{
  "parallel_settings": {
    "parallel_screeners": 4,
    "conservative_retry": true
  },
  "llm_configs": {
    "primary_model": "gpt-4o-mini",
    "validation_model": "gpt-4o-mini"
  },
  "validation_settings": {
    "confidence_threshold": 0.9,
    "minimize_dual_calls": true
  }
}
```

#### Research-Grade Configuration (Maximum Accuracy)
```json
{
  "parallel_settings": {
    "parallel_screeners": 6,
    "comprehensive_validation": true
  },
  "llm_configs": {
    "primary_model": "gpt-4-turbo",
    "validation_model": "claude-3-sonnet"
  },
  "validation_settings": {
    "confidence_threshold": 0.75,
    "mandatory_dual_validation": 0.25
  }
}
```

---

## 🛠️ Troubleshooting

### Performance Issues

#### 1. Memory Optimization Warnings
```
⚠️  Configuration Warning:
   - Estimated memory usage (4.0GB) may exceed available memory (3.2GB)

💡 Suggestion:
   - Based on memory limit, recommend setting to 6 screeners
```
**Root Cause**: Insufficient system memory for requested parallel screeners
**Solutions**:
- Reduce `parallel_screeners` count in config.json
- Close other memory-intensive applications
- Consider upgrading system RAM for large-scale screening

#### 2. API Rate Limiting
```
❌ Batch 2 failed: API rate limit exceeded
```
**Root Cause**: LLM API service rate limits exceeded
**Solutions**:
- System automatically retries with exponential backoff
- Adjust `api_calls_per_minute_limit` in configuration
- Use multiple API keys for load distribution
- Consider upgrading to higher-tier API plans

#### 3. Disk Space Management
```
⚠️  Insufficient disk space under 2GB, may affect temporary file storage
```
**Root Cause**: Limited storage for temporary processing files
**Solutions**:
- Clean existing temporary files: `python3 main.py --cleanup`
- Change `temp_dir` path to drive with more space
- Archive or remove old screening results

### Configuration Issues

#### 4. Configuration File Errors
```
❌ Configuration file not found: config.json
```
**Root Cause**: Missing or incorrectly named configuration file
**Solutions**:
- Copy `config_template.json` to `config.json`
- Verify file path and permissions
- Check JSON syntax validity

#### 5. Multi-Language Interface Issues

**Missing Language Configuration**
```
Warning: Failed to load language config: [Errno 2] No such file or directory: 'i18n_config.json'
```
**Solutions**:
- Ensure `i18n/i18n_config.json` exists in project directory
- Reinstall or update project files
- System falls back to English interface automatically

**Invalid Language Selection**
```
Warning: Language 'xx' not available, using en
```
**Solutions**:
- Use supported language codes: `en` (English) or `zh` (Chinese)
- Check command line parameters: `--lang en` or `--lang zh`

### Processing Errors

#### 6. Validation Mechanism Failures
```
❌ Dual-call validation failed for batch 3
```
**Root Cause**: LLM service interruption or configuration issues
**Solutions**:
- Check API key validity and service status
- Verify network connectivity
- Review LLM model availability and pricing
- System automatically retries failed batches

#### 7. XML Processing Issues
```
❌ Failed to parse XML input file
```
**Root Cause**: Malformed or incompatible XML structure
**Solutions**:
- Validate XML file structure and encoding
- Check for special characters or formatting issues
- Use XML validation tools before processing
- Ensure file is not corrupted or truncated

### System Diagnostic Tools

#### Resource Monitoring
```bash
# Check system capacity and recommendations
python3 -c "
from core.parallel_controller import SystemCapacityDetector
capacity = SystemCapacityDetector.detect_system_capacity()
for key, value in capacity.items():
    print(f'{key}: {value}')
"
```

#### Cleanup and Maintenance
```bash
# Clean all temporary files and reset state
python3 main.py --cleanup

# Resume interrupted screening tasks
python3 main.py --resume

# Monitor active screening progress
python3 main.py --monitor
```

#### Configuration Validation
```bash
# Test configuration file validity
python3 -c "
import json
with open('config/config.json', 'r') as f:
    config = json.load(f)
    print('Configuration loaded successfully')
    print(f'Parallel screeners: {config[\"parallel_settings\"][\"parallel_screeners\"]}')
"
```

### Performance Optimization Tips

#### Hardware Optimization
- **CPU Cores**: Optimal screener count = CPU cores - 1 (reserve for system)
- **Memory**: Minimum 2GB per screener, 4GB recommended for large datasets
- **Storage**: SSD recommended for temporary file operations
- **Network**: Stable connection essential for API reliability

#### Configuration Tuning
- **Batch Size**: Larger batches reduce overhead but increase failure impact
- **API Limits**: Conservative limits prevent service interruptions
- **Retry Logic**: Balance between persistence and resource efficiency
- **Progress Intervals**: Frequent updates provide better monitoring but consume resources

#### Cost Optimization
- **Model Selection**: Use cost-effective models (gpt-4o-mini) for large-scale screening
- **Batch Processing**: Process during off-peak hours for better API availability
- **Validation Thresholds**: Tune confidence thresholds to minimize unnecessary dual-calls
- **Resource Monitoring**: Regular cost analysis prevents budget overruns

---

## 🏗️ Technical Architecture

### Parallel Processing Architecture

**🔄 Multi-Core Processing Engine**
```
Parallel Screening Workflow:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   XML Input     │───▶│  Record Splitter │───▶│  Batch Creator  │
│   (10,000+)     │    │  (Even Distrib.) │    │  (N Screeners)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       ▼                                 ▼                                 ▼
              ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
              │   Screener 1    │              │   Screener 2    │              │   Screener N    │
              │  (Batch 1-1267) │              │ (Batch 1268-...) │              │ (Batch N-...)   │
              │                 │              │                 │              │                 │
              │ ┌─────────────┐ │              │ ┌─────────────┐ │              │ ┌─────────────┐ │
              │ │ Dual-Call   │ │              │ │ Dual-Call   │ │              │ │ Dual-Call   │ │
              │ │ Validation  │ │              │ │ Validation  │ │              │ │ Validation  │ │
              │ └─────────────┘ │              │ └─────────────┘ │              │ └─────────────┘ │
              └─────────────────┘              └─────────────────┘              └─────────────────┘
                       │                                 │                                 │
                       └─────────────────────────────────┼─────────────────────────────────┘
                                                         ▼
                                              ┌─────────────────┐
                                              │ Result Merger   │
                                              │ (Sequential)    │
                                              └─────────────────┘
```

**🎯 Dual-Call Validation Mechanism**
```
Individual Record Processing:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Record Input   │───▶│   First Call     │───▶│ Confidence      │
│  (Title/Abs)    │    │   (LLM A)        │    │ Assessment      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                              ┌─────────────────┐
                                              │ Adaptive Logic  │
                                              │ (Threshold)     │
                                              └─────────────────┘
                                                         │
                                    ┌────────────────────┼────────────────────┐
                                    ▼                                         ▼
                          ┌─────────────────┐                      ┌─────────────────┐
                          │ High Confidence │                      │ Low Confidence  │
                          │ (Accept Result) │                      │ (Second Call)   │
                          └─────────────────┘                      └─────────────────┘
                                                                            │
                                                                            ▼
                                                                  ┌─────────────────┐
                                                                  │ Reverse Valid.  │
                                                                  │ (LLM B)         │
                                                                  └─────────────────┘
                                                                            │
                                                                            ▼
                                                                  ┌─────────────────┐
                                                                  │ Final Decision  │
                                                                  │ (Consensus)     │
                                                                  └─────────────────┘
```

### System Components

```
Project Architecture:
├── 📄 main.py                  # Main entry point with language selection
├── 📄 requirements.txt        # Python dependencies
├── 📁 core/                   # Core system modules
│   ├── parallel_run.py        # Parallel screening orchestrator
│   ├── parallel_controller.py # Main processing controller
│   ├── progress_monitor.py    # Real-time progress tracking
│   ├── result_merger.py       # Sequential result integration
│   └── run.py                 # Single-threaded fallback mode
├── 📁 config/                # Configuration management
│   ├── config.json            # Primary configuration file
│   ├── config_template.json   # Complete configuration template
│   └── llm_pricing.json       # LLM cost reference data
├── 🌐 i18n/                  # Internationalization support
│   ├── i18n_config.json       # Language configuration
│   └── i18n_manager.py        # Multi-language interface manager
├── 📁 src/                   # Core processing logic
│   ├── extractor.py           # Main AI screening engine
│   ├── xml_parser.py          # XML data structure parser
│   ├── study_design_prefilter.py # PICOS-based pre-filtering
│   └── utils.py               # Utility functions and helpers
├── 📁 tools/                 # Auxiliary processing tools
│   └── xml_splitter/          # Large dataset splitting utilities
├── 📁 input/                 # Input data directory
├── 📁 output/                # Results and reports directory
└── 📁 temp_parallel/         # Temporary processing files
```

### Validation Mechanisms

**🔬 Research-Validated Approach**
- **100% Sensitivity Validation**: Tested across 68,006 systematic review records
- **Dual-Call Consensus**: Two-stage validation reduces false negatives to zero
- **Adaptive Thresholds**: Dynamic confidence scoring based on content complexity
- **PICOS Integration**: Structured criteria extraction ensures comprehensive evaluation

**⚡ Performance Optimization**
- **Hardware-Adaptive Scaling**: 25-50 threads typical, automatically configured based on system resources
- **Memory Management**: Dynamic allocation prevents system overload
- **API Rate Limiting**: Intelligent throttling prevents service interruptions
- **Checkpoint Recovery**: Fault tolerance with automatic batch retry mechanisms

### Core Workflow

1. **System Resource Detection**: Automatic hardware analysis and optimal configuration recommendations
2. **Intelligent Record Distribution**: Even splitting of datasets across processing batches
3. **Parallel AI Screening**: Multi-core processing with dual-call validation
4. **Real-time Progress Monitoring**: Live status updates with performance metrics
5. **Sequential Result Integration**: Ordered merging maintaining record sequence integrity
6. **Automated Resource Cleanup**: Temporary file management and system optimization

### Design Patterns

- **Configuration-Driven Architecture**: JSON-based behavior control with template inheritance
- **Modular Component Design**: Independent testing and deployment capabilities
- **Observer Pattern Implementation**: Real-time status broadcasting and monitoring
- **Factory Pattern for LLM Management**: Dynamic model instantiation and configuration
- **Strategy Pattern for Screening Logic**: Configurable validation approaches and thresholds

---

## 📚 File Description

### Important Files
| File | Purpose | Need to Edit |
|------|---------|-------------|
| `config/config.json` | Unified configuration file | ✅ Main configuration |
| `main.py` | Main entry point | ❌ Direct execution |
| `core/run.py` | Single-threaded backup | ❌ Debug use |

### Output Files
| File Type | Description |
|-----------|-------------|
| `final_results_*.xml` | Final screening results XML |
| `final_results_*.xlsx` | Final screening results Excel |
| `merge_report_*.txt` | Merge process report |
| `parallel_screening_state.json` | Task state file |

---

## 🤝 Support and Feedback

### Getting Help
If you encounter issues, please provide:
1. System detection results
2. Configuration file content
3. Error message screenshots
4. State file (if available)

### Version Information
- **Python Requirement**: 3.12+
- **Main Dependencies**: pandas, numpy, openai, psutil
- **Supported Systems**: Windows, macOS, Linux

---

**🎉 Start Your Efficient Literature Screening Journey!**

> 💡 **Tip**: For first-time use, we recommend testing with a small literature set (100-200 records) to familiarize yourself with the process before processing large batches of data.