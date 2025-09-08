# SmartEBM Data Extraction Tool

### AI-Powered Systematic Review Data Extraction with Research-Validated Performance

## Key Advantages

**🎯 Research-Validated Accuracy**: 98.0% initial accuracy, 99.5% post-verification accuracy from SmartNMA validation across 153,334 extracted items

**⚡ Scalable Parallel Processing**: Substantial efficiency gains with intelligent multi-core processing, limited only by API rate limits and hardware capacity

**🔄 Sequential Domain-Based Extraction**: Advanced extraction methodology that processes data systematically across research domains for comprehensive coverage

**🛡️ Dual-Stage Verification**: Innovative two-tier validation system ensuring maximum data quality through automated verification and repair mechanisms

**💰 Intelligent Cost Management**: Real-time API cost tracking with optimization strategies and budget controls for large-scale systematic reviews

## Core Features

- **Parallel Processing Architecture**: Hardware-adaptive scaling with automatic resource detection and load balancing
- **Fault Tolerance System**: Checkpoint recovery, auto-retry mechanisms, and seamless resumption from interruption points  
- **Multi-Format PDF Processing**: Advanced document parsing with OCR fallback and structured data validation
- **Real-Time Progress Monitoring**: Live tracking of extraction progress, cost analysis, and performance metrics
- **Multi-Language Interface**: Complete English and Chinese language support for international research teams

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with interactive language selection
python3 main.py

# Run with specific language
python3 main.py --lang en    # English
python3 main.py --lang zh    # Chinese
```

## Documentation

- **📖 [Complete English Documentation](docs/README.md)** - Comprehensive technical guide with architecture details and optimization strategies
- **📖 [完整中文文档](docs/README_zh.md)** - 完整技术指南，包含架构详情和优化策略

## System Requirements

- **Python**: 3.8+ (3.10+ recommended for optimal performance)
- **Memory**: 8GB+ (16GB+ recommended for large-scale systematic reviews)
- **CPU**: 4+ cores (8+ cores for maximum parallel processing efficiency)
- **Storage**: 2GB+ available space for temporary files and results

## Integration with SmartEBM Ecosystem

This tool seamlessly integrates with the complete SmartEBM systematic review workflow:

**Upstream Integration:**
- **[SmartEBM Title & Abstract Screening Tool](../title_and_abstract_screening_tool/README.md)**: Pre-screened study collections with inclusion decisions
- **[SmartEBM Full-Text Screening Tool](../full_text_screening_tool/README.md)**: Included studies with PICOS framework data
- **Manual Study Collections**: Researcher-curated PDF collections for targeted extraction

**Downstream Integration:**
- **[SmartEBM Risk of Bias Assessment Tool](../robust_rob_assessment_tool/README.md)**: Extracted study characteristics for bias evaluation
- **[SmartEBM Data Analysis Tool](../data_analysis_tool/README.md)**: Structured quantitative data for network meta-analysis
- **Statistical Software**: R, Stata, and SPSS compatible output formats

**Related SmartEBM Tools:**
- **[GRADE CoE Assessment Tool](../grade_coe_assessment_tool/README.md)**: Evidence quality assessment using extracted data
- **[Template-Based Extraction Tool](../template_based_extraction_tool/README.md)**: Specialized extraction for specific data schemas

## Citation

If you use this tool in your research, please cite the SmartNMA framework:

> Lai H, Liu J, Busse J, et,al. Development and Validation of SmartNMA: An Intelligent Agent for Interventional Systematic Reviews and Network Meta-Analysis

## Repository

- **GitHub**: https://github.com/enenlhh/SmartNMA-AI-assisted-tools
- **Contact**: enenlhh@outlook.com
- **Team**: SmartEBM Group at Lanzhou University

---

**Transform your systematic review data extraction with research-validated AI efficiency**