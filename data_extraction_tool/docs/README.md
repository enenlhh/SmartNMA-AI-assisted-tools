# SmartEBM Data Extraction Tool - Complete Documentation

### Research-Validated AI-Powered Data Extraction with Advanced Parallel Processing Architecture

## 📋 Table of Contents
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Configuration Guide](#configuration-guide)
- [Parallel Processing Architecture](#parallel-processing-architecture)
- [Resource Management](#resource-management)
- [Cost Analysis and Optimization](#cost-analysis-and-optimization)
- [Performance Optimization](#performance-optimization)
- [Multi-Language Interface](#multi-language-interface)
- [Technical Architecture](#technical-architecture)
- [Integration Guide](#integration-guide)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Research Validation Overview

**SmartNMA Framework Validation Results:**
- **Validation Scope**: 153,334 extracted data items across systematic review studies
- **Initial Accuracy**: 98.0% accuracy on first-pass extraction
- **Post-Verification Accuracy**: 99.5% accuracy after dual-stage verification
- **Parallel Processing Efficiency**: Substantial speed improvement over traditional manual extraction methods through multi-threading
- **Innovation**: Sequential domain-based extraction with intelligent dual-stage verification

## 💻 System Requirements

### Minimum Requirements
- **Python**: 3.8+ (3.10+ strongly recommended for optimal performance)
- **Memory**: 4GB+ (8GB+ recommended for production use)
- **CPU**: 2+ cores (4+ cores recommended for parallel processing)
- **Storage**: 2GB+ available space for temporary files and results
- **Network**: Stable internet connection for LLM API access

### Performance Optimization Recommendations

| Hardware Configuration | Recommended Workers | Expected Performance | Use Case |
|------------------------|--------------------|--------------------|----------|
| 2-core 4GB RAM        | 1 worker           | Baseline performance, stable | Small studies (<50 documents) |
| 4-core 8GB RAM        | 2-3 workers        | Significant performance boost | Medium studies (50-200 documents) |
| 8-core 16GB RAM       | 4-6 workers        | Substantial performance boost | Large studies (200-500 documents) |
| 12+ core 24GB+ RAM    | 6-8 workers        | Maximum parallel performance | Very large studies (500+ documents) |

**Performance Limiting Factors:**
- **API Rate Limits**: Most LLM providers limit requests per minute
- **Memory Usage**: Each worker requires ~1-2GB RAM for document processing
- **Network Bandwidth**: Concurrent API calls require stable internet connection
- **Storage I/O**: Temporary file operations during parallel processing

---

## 📦 Installation Guide

### 1. Environment Setup
```bash
# Clone the repository
git clone [repository-url]
cd data_extraction_tool

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python3 -c "import pandas, openpyxl, PyPDF2; print('Dependencies installed successfully')"
```

### 3. Configuration Setup
```bash
# Copy configuration template
cp config/config_template.json config/config.json

# Edit configuration with your settings
# Add your LLM API keys and adjust parallel processing settings
```

### 4. Verify Installation
```bash
# Test basic functionality
python3 main.py --help

# Run system resource detection
python3 main.py --detect-resources
```

### 5. Initial Test Run
```bash
# Place test PDFs in input/pdfs/ directory
# Run a small test extraction
python3 main.py --test-mode
```

---

## ⚙️ Configuration Guide

### Core Configuration File: `config/config.json`

The tool uses a comprehensive JSON configuration system that controls all aspects of the extraction process:

```json
{
  "mode": {
    "extraction_mode": "table",         // Extraction format: "table" or "json"
    "enable_cost_analysis": true,       // Enable real-time cost tracking
    "enable_parallel_processing": true, // Enable multi-worker processing
    "sequential_domain_extraction": true // Enable domain-based extraction
  },
  "paths": {
    "input_folder": "input/pdfs",              // PDF input directory
    "output_folder": "output",                 // Results output directory
    "output_filename": "extraction_results.xlsx", // Final results file
    "temp_dir": "temp_parallel"                // Temporary processing directory
  },
  "parallel_settings": {
    "parallel_workers": 3,              // Number of concurrent workers
    "auto_distribute": true,            // Automatic document distribution
    "cleanup_temp_files": true,         // Auto-cleanup temporary files
    "retry_failed_batches": true,       // Retry failed processing batches
    "max_retries": 3,                   // Maximum retry attempts per batch
    "batch_size_optimization": true     // Dynamic batch size adjustment
  },
  "resource_management": {
    "api_calls_per_minute_limit": 100,  // API rate limiting
    "memory_limit_mb": 2048,            // Memory usage limit per worker
    "delay_between_workers": 2,         // Worker startup delay (seconds)
    "progress_update_interval": 5,      // Progress reporting interval
    "auto_resource_detection": true     // Automatic hardware detection
  },
  "llm_configs": {
    "primary": {
      "api_key": "your_api_key_here",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4o-mini",
      "temperature": 0.1,
      "max_tokens": 4000
    },
    "verification": {
      "api_key": "your_api_key_here",
      "base_url": "https://api.openai.com/v1", 
      "model": "gpt-4o",
      "temperature": 0.0,
      "max_tokens": 2000
    }
  },
  "cost_control": {
    "max_budget_usd": 100.0,           // Maximum spending limit
    "warning_threshold_percent": 80,    // Budget warning threshold
    "track_token_usage": true,         // Detailed token tracking
    "cost_optimization": true,         // Enable cost optimization strategies
    "model_selection_strategy": "adaptive" // Adaptive model selection
  },
  "extraction_strategy": {
    "dual_stage_verification": true,    // Enable two-stage verification
    "domain_based_processing": true,    // Sequential domain extraction
    "confidence_threshold": 0.85,      // Minimum confidence for auto-acceptance
    "fallback_model": "gpt-4o",        // Fallback for low-confidence extractions
    "quality_assurance_sampling": 0.1  // QA sampling rate (10%)
  }
}
```

### Configuration Sections Explained

#### Extraction Strategy Configuration
- **Sequential Domain-Based Extraction**: Processes data systematically across research domains (demographics, interventions, outcomes, etc.)
- **Dual-Stage Verification**: First-pass extraction followed by verification and repair stage
- **Confidence Thresholding**: Automatic quality assessment with fallback processing for low-confidence results

#### Performance Recommendations by Study Size

| Study Size | Recommended Workers | Memory Allocation | Expected Processing Time |
|------------|--------------------|--------------------|-------------------------|
| Small (<50 docs) | 1-2 workers | 4GB total | 1-2 hours |
| Medium (50-200 docs) | 2-4 workers | 8GB total | 2-4 hours |
| Large (200-500 docs) | 4-6 workers | 16GB total | 4-8 hours |
| Very Large (500+ docs) | 6-8 workers | 24GB+ total | 8+ hours |

---

## 🔄 Parallel Processing Architecture

### Research-Validated Performance Scaling

Based on SmartNMA framework validation, the parallel processing system delivers substantial efficiency improvements through multi-threading:

| Processing Method | Time (100 documents) | Processing Approach | Resource Usage |
|-------------------|---------------------|-------------------|----------------|
| Traditional Manual | 25-30 hours | Sequential human review | Human labor intensive |
| Single-threaded AI | 5-6 hours | Sequential AI processing | 1 CPU core, 2GB RAM |
| 2-worker parallel | 2.5-3 hours | Parallel AI processing | 2 CPU cores, 4GB RAM |
| 4-worker parallel | 1.3-1.7 hours | Multi-threaded processing | 4 CPU cores, 8GB RAM |
| Optimal parallel (6-8 workers) | 1-1.3 hours | Maximum parallel efficiency | 6-8 CPU cores, 12-16GB RAM |

### Intelligent Resource Management

**Automatic Resource Detection:**
```bash
# System automatically detects optimal configuration
python3 main.py --detect-resources

# Sample output:
# 🖥️  System Resources Detected:
# CPU Cores: 8 (6 recommended for parallel processing)
# Available RAM: 16GB (12GB recommended allocation)
# Optimal Workers: 6
# Expected Performance: Maximum parallel processing efficiency
```

**Dynamic Load Balancing:**
- Automatic document distribution across workers
- Real-time performance monitoring and adjustment
- Intelligent batch size optimization based on document complexity
- Adaptive API rate limiting to prevent service interruptions

### Advanced Checkpoint Recovery System

The system implements comprehensive fault tolerance with automatic state preservation:

```bash
# Resume from any interruption point
python3 main.py --resume

# Monitor active processing
python3 main.py --monitor extraction_state_[timestamp].json

# Merge completed batches only
python3 main.py --merge-only extraction_state_[timestamp].json

# Detailed recovery information
python3 main.py --recovery-info extraction_state_[timestamp].json
```

**Recovery Capabilities:**
- **Granular Checkpointing**: Progress saved after each document
- **Batch-Level Recovery**: Resume from failed batch without losing completed work
- **State Validation**: Automatic verification of checkpoint integrity
- **Partial Result Merging**: Combine results from multiple interrupted sessions

---

## 🎛️ Resource Management

### Hardware Resource Optimization

**CPU Utilization Strategy:**
- **Multi-Core Scaling**: Linear performance scaling up to 6-8 workers
- **Process Isolation**: Each worker operates in isolated process space
- **Load Balancing**: Dynamic work distribution based on processing speed
- **Thermal Management**: Automatic throttling to prevent system overheating

**Memory Management:**
- **Per-Worker Allocation**: Configurable memory limits (default: 2GB per worker)
- **Document Caching**: Intelligent PDF caching to reduce I/O overhead
- **Garbage Collection**: Automatic memory cleanup between document processing
- **Memory Monitoring**: Real-time memory usage tracking and alerts

**Storage Optimization:**
- **Temporary File Management**: Automatic cleanup of processing artifacts
- **Result Streaming**: Progressive result writing to prevent memory overflow
- **Compression**: Automatic compression of intermediate results
- **Disk Space Monitoring**: Alerts for insufficient storage space

### API Resource Management

**Rate Limiting Strategy:**
```json
{
  "api_management": {
    "calls_per_minute": 100,           // Conservative rate limiting
    "burst_allowance": 20,             // Burst capacity for short peaks
    "backoff_strategy": "exponential", // Retry strategy for rate limits
    "timeout_seconds": 30,             // Request timeout
    "connection_pooling": true         // Reuse connections for efficiency
  }
}
```

**Model Selection Strategy:**
- **Primary Model**: Fast, cost-effective model for initial extraction (gpt-4o-mini)
- **Verification Model**: High-accuracy model for quality assurance (gpt-4o)
- **Fallback Model**: Alternative provider for redundancy
- **Adaptive Selection**: Automatic model switching based on document complexity

---

## 💰 Cost Analysis and Optimization

### Comprehensive Cost Tracking

The system provides detailed cost analysis across multiple dimensions:

```
💰 SmartEBM Data Extraction - Cost Analysis Report
================================================================
📊 Processing Summary:
   Documents Processed: 150
   Total API Calls: 1,847
   Processing Time: 2.3 hours
   
💵 Cost Breakdown:
   Primary Model (gpt-4o-mini): $12.45 USD (78% of total)
   Verification Model (gpt-4o): $3.21 USD (20% of total)
   Fallback Processing: $0.34 USD (2% of total)
   Total Cost: $16.00 USD / ¥115.20 CNY
   
📈 Efficiency Metrics:
   Cost per Document: $0.107 USD
   Cost per Data Item: $0.0043 USD
   Traditional Manual Cost Equivalent: $750 USD (47x savings)
   
⚡ Performance Analysis:
   Average Processing Speed: 65 documents/hour
   Accuracy Rate: 98.2% (initial), 99.6% (post-verification)
   API Efficiency: 94% (minimal retries)
```

### Cost Optimization Strategies

#### Model Selection Optimization
| Model | Use Case | Cost per 1K tokens | Recommended For |
|-------|----------|-------------------|-----------------|
| gpt-4o-mini | Primary extraction | $0.15 input / $0.60 output | Large-scale studies, budget-conscious |
| gpt-4o | Verification & complex docs | $5.00 input / $15.00 output | High-stakes research, complex documents |
| deepseek-chat | Chinese documents | $0.14 input / $0.28 output | Chinese language studies |
| claude-3-haiku | Alternative primary | $0.25 input / $1.25 output | Backup option, specific use cases |

#### Budget Management Features
```json
{
  "cost_control": {
    "max_budget_usd": 100.0,
    "daily_limit_usd": 25.0,
    "warning_thresholds": [50, 75, 90],
    "auto_pause_at_limit": true,
    "cost_per_document_alert": 0.50,
    "optimization_suggestions": true
  }
}
```

**Real-Time Cost Monitoring:**
- Live cost tracking during processing
- Projected total cost estimation
- Budget alerts and automatic pausing
- Cost-per-document analysis
- Model efficiency recommendations

---

## ⚡ Performance Optimization

### Sequential Domain-Based Extraction

**Research Innovation**: The SmartNMA framework introduces sequential domain-based extraction, processing data systematically across research domains for comprehensive coverage:

1. **Study Characteristics Domain**: Basic study information, design, setting
2. **Population Domain**: Participant demographics, inclusion/exclusion criteria
3. **Intervention Domain**: Treatment details, dosing, administration
4. **Outcomes Domain**: Primary/secondary outcomes, measurement methods
5. **Results Domain**: Statistical results, effect sizes, confidence intervals
6. **Quality Domain**: Risk of bias indicators, study limitations

**Benefits:**
- **Systematic Coverage**: Ensures no critical data domains are missed
- **Quality Consistency**: Maintains extraction quality across all data types
- **Verification Efficiency**: Enables targeted verification of specific domains
- **Error Reduction**: Reduces cognitive load by focusing on one domain at a time

### Dual-Stage Verification System

**Stage 1 - Initial Extraction:**
- Fast, comprehensive data extraction using primary model
- Confidence scoring for each extracted data point
- Automatic flagging of low-confidence extractions

**Stage 2 - Verification and Repair:**
- Targeted re-extraction of low-confidence data points
- Cross-validation using verification model
- Automatic repair of inconsistent or incomplete data
- Final quality assurance scoring

**Performance Impact:**
- **Accuracy Improvement**: 98.0% → 99.5% accuracy (SmartNMA validation)
- **Cost Efficiency**: Selective verification reduces overall API costs
- **Time Optimization**: Focused verification faster than full re-extraction

### Optimization Recommendations

#### For Large-Scale Studies (500+ documents)
```json
{
  "optimization_config": {
    "parallel_workers": 6,
    "batch_size": 25,
    "primary_model": "gpt-4o-mini",
    "verification_sampling": 0.15,
    "aggressive_caching": true,
    "memory_allocation": "16GB"
  }
}
```

#### For High-Accuracy Requirements
```json
{
  "quality_config": {
    "parallel_workers": 3,
    "verification_rate": 1.0,
    "primary_model": "gpt-4o",
    "confidence_threshold": 0.95,
    "manual_review_sampling": 0.05
  }
}
```

---

## 🌐 Multi-Language Interface

### Language Selection

#### Interactive Selection (Default)
```bash
python3 main.py
```

#### Command Line Preset
```bash
python3 main.py --lang zh    # Chinese interface
python3 main.py --lang en    # English interface
```

### Language Selection and Localization

#### Interactive Language Selection (Default)
```bash
python3 main.py
# System presents language selection menu:
# 🌐 Language Selection / 语言选择
# [1] English
# [2] 中文 (Chinese)
# Please select / 请选择: 
```

#### Command Line Language Specification
```bash
python3 main.py --lang en    # English interface
python3 main.py --lang zh    # Chinese interface (中文界面)
```

#### Localization Features
- **Complete Interface Translation**: All prompts, messages, and outputs
- **Cultural Adaptation**: Date formats, number formatting, terminology
- **Technical Term Consistency**: Standardized systematic review terminology
- **Error Message Localization**: Troubleshooting guidance in selected language
- **Report Generation**: Results and analysis reports in chosen language

---

## 🏗️ Technical Architecture

### System Architecture Overview

```
SmartEBM Data Extraction Tool Architecture
├── 🎯 Main Controller (main.py)
│   ├── Interactive language selection
│   ├── Configuration validation
│   └── Workflow orchestration
│
├── 🔄 Core Processing Engine
│   ├── 📊 Parallel Controller (core/parallel_controller.py)
│   │   ├── Worker process management
│   │   ├── Document distribution
│   │   └── Load balancing
│   │
│   ├── 📈 Progress Monitor (core/progress_monitor.py)
│   │   ├── Real-time progress tracking
│   │   ├── Performance metrics
│   │   └── Status reporting
│   │
│   ├── 🔧 Resource Detector (core/resource_detector.py)
│   │   ├── Hardware capability detection
│   │   ├── Optimal configuration suggestions
│   │   └── Performance predictions
│   │
│   └── 💰 Cost Analyzer (core/cost_analyzer.py)
│       ├── Real-time cost tracking
│       ├── Budget management
│       └── Optimization recommendations
│
├── 🧠 Extraction Engine (src/)
│   ├── 📄 Document Processor (src/core/file_reader.py)
│   │   ├── Multi-format PDF parsing
│   │   ├── OCR fallback processing
│   │   └── Text preprocessing
│   │
│   ├── 🎯 Data Processor (src/core/data_processor.py)
│   │   ├── Sequential domain extraction
│   │   ├── Dual-stage verification
│   │   └── Quality assurance
│   │
│   └── 📊 Output Generator (src/utils/excel_writer.py)
│       ├── Structured Excel output
│       ├── Data validation
│       └── Format standardization
│
└── 🌐 Support Systems
    ├── 🗣️ Internationalization (i18n/)
    ├── ⚙️ Configuration Management (config/)
    └── 📁 File Organization (tools/)
```

### Core Processing Workflow

1. **Initialization Phase**
   - System resource detection and optimization
   - Configuration validation and setup
   - API connectivity verification

2. **Document Distribution Phase**
   - Intelligent document batching
   - Worker process initialization
   - Load balancing optimization

3. **Parallel Extraction Phase**
   - Sequential domain-based processing
   - Real-time progress monitoring
   - Automatic error handling and retry

4. **Verification Phase**
   - Dual-stage verification system
   - Quality assurance sampling
   - Confidence-based validation

5. **Result Consolidation Phase**
   - Batch result merging
   - Data validation and cleanup
   - Final report generation

### Innovation Highlights

**Sequential Domain-Based Extraction:**
- Systematic processing across research domains
- Reduced cognitive load and improved accuracy
- Targeted verification for specific data types

**Intelligent Resource Management:**
- Automatic hardware detection and optimization
- Dynamic load balancing and scaling
- Predictive performance modeling

**Dual-Stage Verification System:**
- Initial extraction with confidence scoring
- Selective verification of low-confidence data
- Automated repair and quality enhancement

---

## 🔗 Integration Guide

### SmartEBM Ecosystem Integration

The Data Extraction Tool is designed for seamless integration within the complete SmartEBM systematic review workflow:

#### Upstream Integration (Input Sources)
```
Literature Screening → Full-Text Screening → Data Extraction
```

**Compatible Input Formats:**
- **PDF Documents**: Direct processing from screening tool outputs
- **Study Lists**: Excel/CSV files with study identifiers
- **Metadata Integration**: Automatic incorporation of screening decisions
- **Quality Indicators**: Integration of screening confidence scores

#### Downstream Integration (Output Destinations)
```
Data Extraction → Risk of Bias Assessment → Meta-Analysis
```

**Structured Output Formats:**
- **Excel Workbooks**: Multi-sheet structured data for analysis tools
- **CSV Files**: Standardized format for statistical software
- **JSON Export**: API-compatible format for automated workflows
- **XML Output**: PRISMA-compliant systematic review formats

### Workflow Integration Examples

#### Complete SmartEBM Workflow
```bash
# 1. Literature screening (previous step)
# Results: included_studies.xlsx

# 2. Data extraction (this tool)
python3 main.py --input included_studies.xlsx --output extracted_data.xlsx

# 3. Risk of bias assessment (next step)
# Input: extracted_data.xlsx
```

#### Integration with External Tools

**EndNote/Zotero Integration:**
```bash
# Export PDFs from reference manager
# Place in input/pdfs/ directory
python3 main.py --source-manager endnote
```

**RevMan Integration:**
```bash
# Generate RevMan-compatible output
python3 main.py --output-format revman --output revman_data.csv
```

**R/Stata Integration:**
```bash
# Generate statistical software-ready output
python3 main.py --output-format stata --statistical-ready
```

### API Integration

**Programmatic Access:**
```python
from src.main import DataExtractionTool

# Initialize extraction tool
extractor = DataExtractionTool(config_path="config/config.json")

# Process documents programmatically
results = extractor.extract_batch(
    input_files=["study1.pdf", "study2.pdf"],
    extraction_schema="systematic_review",
    parallel_workers=4
)

# Access structured results
for study_id, data in results.items():
    print(f"Study: {study_id}")
    print(f"Participants: {data['population']['sample_size']}")
    print(f"Intervention: {data['intervention']['description']}")
```

---

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. Resource Management Issues

**Insufficient Memory Warning:**
```
⚠️  Resource Warning: Estimated memory usage (12.0GB) exceeds available memory (8.0GB)
Recommendation: Reduce parallel_workers from 6 to 4
```
**Solutions:**
- Reduce `parallel_workers` in configuration
- Increase system RAM or use swap space
- Enable `memory_optimization` mode in config
- Process documents in smaller batches

**CPU Overutilization:**
```
⚠️  CPU Warning: System load average (8.5) exceeds recommended threshold (6.0)
```
**Solutions:**
- Reduce worker count to match CPU cores
- Enable `thermal_management` in configuration
- Add delays between worker startup
- Monitor system temperature

#### 2. API and Network Issues

**API Rate Limit Exceeded:**
```
❌ API Error: Rate limit exceeded (429 Too Many Requests)
Implementing exponential backoff... Retry in 32 seconds
```
**Solutions:**
- System automatically implements retry logic
- Reduce `api_calls_per_minute_limit` in config
- Distribute processing across multiple API keys
- Consider upgrading API plan for higher limits

**Network Connectivity Issues:**
```
❌ Network Error: Connection timeout after 30 seconds
```
**Solutions:**
- Check internet connectivity and stability
- Increase `timeout_seconds` in configuration
- Enable `connection_pooling` for efficiency
- Consider using local LLM models for offline processing

#### 3. Configuration and Setup Issues

**Invalid Configuration:**
```
❌ Configuration Error: Missing required field 'llm_configs.primary.api_key'
```
**Solutions:**
- Verify all required fields in config.json
- Use configuration template as reference
- Validate API keys with test calls
- Check file permissions and accessibility

**Model Access Issues:**
```
❌ Model Error: Model 'gpt-4o-mini' not accessible with provided API key
```
**Solutions:**
- Verify API key has access to specified model
- Check account billing and usage limits
- Try alternative models (gpt-3.5-turbo, claude-3-haiku)
- Contact API provider for access verification

#### 4. Processing and Quality Issues

**Low Extraction Accuracy:**
```
⚠️  Quality Warning: Extraction confidence below threshold (0.75 < 0.85)
Triggering verification stage for 23 documents
```
**Solutions:**
- Enable dual-stage verification
- Use higher-quality models for complex documents
- Adjust confidence thresholds
- Implement manual review sampling

**Incomplete Extractions:**
```
⚠️  Completeness Warning: 15% of expected data fields are empty
```
**Solutions:**
- Review extraction schema for completeness
- Enable domain-based sequential extraction
- Increase model temperature for creativity
- Add fallback extraction strategies

### Performance Optimization Troubleshooting

#### Slow Processing Speed
**Diagnostic Steps:**
1. Check system resource utilization
2. Monitor API response times
3. Analyze document complexity distribution
4. Review parallel processing efficiency

**Optimization Strategies:**
- Increase parallel workers (if resources allow)
- Optimize document batching strategy
- Enable aggressive caching
- Use faster models for initial extraction

#### High Processing Costs
**Cost Analysis:**
1. Review model selection strategy
2. Analyze token usage patterns
3. Evaluate verification necessity
4. Consider batch processing optimization

**Cost Reduction Strategies:**
- Use cost-effective models for primary extraction
- Implement selective verification
- Optimize prompt engineering
- Enable cost-aware processing modes

---

## 📚 Best Practices

### Study Design Considerations

#### For Systematic Reviews
```json
{
  "systematic_review_config": {
    "extraction_mode": "comprehensive",
    "verification_rate": 1.0,
    "quality_assurance": "high",
    "documentation_level": "detailed",
    "reproducibility_features": true
  }
}
```

#### For Rapid Reviews
```json
{
  "rapid_review_config": {
    "extraction_mode": "targeted",
    "verification_rate": 0.2,
    "quality_assurance": "standard",
    "speed_optimization": true,
    "cost_optimization": true
  }
}
```

#### For Meta-Analyses
```json
{
  "meta_analysis_config": {
    "extraction_mode": "statistical_focus",
    "numerical_precision": "high",
    "effect_size_extraction": true,
    "confidence_intervals": true,
    "heterogeneity_assessment": true
  }
}
```

### Quality Assurance Recommendations

#### Pre-Processing Quality Checks
1. **Document Quality Assessment**: Verify PDF readability and completeness
2. **Extraction Schema Validation**: Ensure schema matches research questions
3. **Pilot Testing**: Run small batches to validate extraction accuracy
4. **Model Selection Testing**: Compare models on representative documents

#### During Processing Monitoring
1. **Real-Time Quality Monitoring**: Watch confidence scores and error rates
2. **Resource Utilization Tracking**: Monitor CPU, memory, and API usage
3. **Cost Tracking**: Keep extraction costs within budget parameters
4. **Progress Validation**: Verify extraction completeness at regular intervals

#### Post-Processing Validation
1. **Statistical Validation**: Check extracted numerical data for consistency
2. **Completeness Assessment**: Verify all required fields are populated
3. **Cross-Validation**: Sample manual verification of automated extractions
4. **Integration Testing**: Ensure outputs work with downstream analysis tools

### Performance Optimization Guidelines

#### Hardware Optimization
- **CPU**: Use 6-8 cores for optimal parallel processing
- **RAM**: Allocate 2GB per worker plus 4GB system overhead
- **Storage**: Use SSD storage for temporary files and results
- **Network**: Ensure stable, high-bandwidth internet for API calls

#### Configuration Optimization
- **Batch Size**: Optimize based on document complexity and system resources
- **Model Selection**: Balance cost, speed, and accuracy requirements
- **Verification Strategy**: Use selective verification for cost efficiency
- **Caching**: Enable aggressive caching for repeated processing

### Security and Privacy Considerations

#### Data Protection
- **Local Processing**: All document processing occurs locally
- **API Security**: Secure transmission of text excerpts to LLM services
- **Temporary File Management**: Automatic cleanup of sensitive temporary files
- **Access Control**: Implement appropriate file system permissions

#### Compliance Considerations
- **HIPAA Compliance**: Ensure PHI is properly handled if processing medical studies
- **GDPR Compliance**: Consider data protection requirements for European studies
- **Institutional Requirements**: Verify compliance with institutional data policies
- **API Terms of Service**: Ensure LLM provider terms allow research use

---

## 📞 Support and Resources

### Technical Support

**Documentation Resources:**
- **Configuration Templates**: Complete examples in `config/` directory
- **Troubleshooting Guide**: Comprehensive issue resolution above
- **Performance Tuning**: Optimization recommendations for different use cases
- **Integration Examples**: Sample workflows with other SmartEBM tools

**Community Support:**
- **GitHub Issues**: Report bugs and request features
- **User Forums**: Community discussions and best practices
- **Video Tutorials**: Step-by-step setup and usage guides
- **Webinar Series**: Regular training sessions for new users

### Research and Citation

**Academic Citation:**
```
[SmartNMA Framework Citation]
SmartEBM Data Extraction Tool: AI-Powered Systematic Review Data Extraction
with Sequential Domain-Based Processing and Dual-Stage Verification.
Validation results: 98.0% initial accuracy, 99.5% post-verification accuracy
across 153,334 extracted data items.
```

**Research Validation:**
- **Peer Review**: SmartNMA framework published in [journal name]
- **Validation Scope**: 153,334 data items across multiple systematic reviews
- **Performance Metrics**: Comprehensive accuracy and efficiency validation
- **Reproducibility**: Open-source implementation with detailed documentation

### Getting Started Checklist

#### Initial Setup
- [ ] Install Python 3.8+ and required dependencies
- [ ] Configure LLM API keys and test connectivity
- [ ] Set up input/output directory structure
- [ ] Run system resource detection and optimization
- [ ] Complete test extraction with sample documents

#### Production Deployment
- [ ] Optimize configuration for study size and requirements
- [ ] Set up appropriate budget and cost controls
- [ ] Configure quality assurance and verification settings
- [ ] Establish backup and recovery procedures
- [ ] Train team members on tool usage and troubleshooting

#### Quality Assurance
- [ ] Validate extraction accuracy with pilot studies
- [ ] Establish quality control sampling procedures
- [ ] Set up monitoring and alerting for processing issues
- [ ] Document extraction procedures for reproducibility
- [ ] Plan integration with downstream analysis workflows

---

**Transform your systematic review data extraction with research-validated AI efficiency and accuracy. The SmartEBM Data Extraction Tool delivers substantial speed improvements through parallel processing with 99.5% accuracy, enabling faster, more reliable evidence synthesis for better healthcare decisions.**