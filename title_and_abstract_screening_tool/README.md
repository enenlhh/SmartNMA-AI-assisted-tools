# SmartEBM Title & Abstract Screening Tool

> 🎯 **Research-Validated AI Screening with 100% Sensitivity & Scalable Parallel Processing**

## Key Advantages

**🔬 Research-Backed Performance**
- **100% Sensitivity** - Validated across 68,006 systematic review records
- **Scalable Parallel Processing** - 25-50 threads typical, hardware-limited scaling
- **Parallel Processing Efficiency** - Transforms 8-hour tasks into 1-hour workflows through multi-threading

**🚀 Advanced AI Innovations**
- **Dual-Call Validation** - Two-stage consensus screening for maximum accuracy
- **Adaptive Reverse Validation** - Intelligent confidence grading and verification
- **PICOS-Based Intelligence** - Structured criteria extraction and evaluation

**⚡ Production-Ready Features**
- **Fault-Tolerant Design** - Checkpoint recovery and automatic batch retry
- **Real-Time Monitoring** - Live progress tracking with resource optimization
- **Cost-Effective Processing** - Comprehensive LLM cost analysis and optimization

## Core Features

- **Intelligent XML Processing** - Handles 10,000+ record datasets with automatic splitting
- **Multi-LLM Consensus** - Configurable screening models with validation workflows
- **Bilingual Interface** - Native English and Chinese language support
- **Resource Management** - Automatic hardware detection and optimal configuration
- **Integration Ready** - Seamless workflow integration within SmartEBM ecosystem

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch with interactive setup
python3 main.py

# Configure parallel screeners (recommended: 4-8 based on hardware)
# Edit config.json: "parallel_screeners": 4
```

## Documentation

- **📖 [Complete Documentation](docs/README.md)** - Installation, configuration, and advanced usage
- **📖 [中文完整文档](docs/README_zh.md)** - 安装配置和高级使用指南

## Integration with SmartEBM Ecosystem

This tool seamlessly integrates with the complete SmartEBM systematic review workflow:

**Upstream Integration:**
- **Literature Search Results**: XML/CSV files from database searches (PubMed, Embase, Cochrane)
- **Reference Manager Exports**: EndNote, Zotero, and Mendeley compatible formats
- **Manual Study Lists**: Researcher-curated study collections for targeted screening

**Downstream Integration:**
- **[SmartEBM Full-Text Screening Tool](../full_text_screening_tool/README.md)**: Filtered studies for comprehensive full-text evaluation
- **[SmartEBM Data Extraction Tool](../data_extraction_tool/README.md)**: Included studies ready for systematic data extraction
- **Quality Assurance**: Screening confidence scores and decision audit trails

**Related SmartEBM Tools:**
- **[Data Analysis Tool](../data_analysis_tool/README.md)**: Network meta-analysis of extracted data
- **[Risk of Bias Assessment Tool](../robust_rob_assessment_tool/README.md)**: Quality assessment of included studies
- **[GRADE CoE Assessment Tool](../grade_coe_assessment_tool/README.md)**: Evidence certainty evaluation

## Citation

If you use this tool in your research, please cite the SmartNMA framework:

> Lai H, Liu J, Ma N, et al. Design and Validation of SmartNMA: A Comprehensive Large Language Model-Assisted Framework for Network Meta-Analysis. (Manuscript in preparation).

---

**Transform your systematic review workflow with research-validated AI screening.**