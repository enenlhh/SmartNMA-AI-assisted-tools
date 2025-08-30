# GRADE CoE Assessment Tool

### Automated GRADE Evidence Evaluation for Network Meta-Analysis with Perfect Agreement Validation

## Key Advantages

**Automated GRADE Domain Evaluation**: Systematically processes raw NMA output files with comprehensive rule-based assessment across all five GRADE domains, achieving perfect agreement with reference standards in SmartNMA validation studies.

**Interactive Self-Contained Reporting**: Generates single, portable `report.html` files with real-time recalculation capabilities and zero dependencies, enabling seamless sharing and presentation of evidence quality assessments.

**Transparent Reasoning Process**: Provides clear natural language explanations for every automated judgment, ensuring methodological transparency and facilitating peer review processes.

**Configurable Logic Framework**: Researcher-controlled thresholds through `config.json` configuration, allowing customization of judgment criteria while maintaining standardized GRADE methodology.

## Core Features

- **Perfect Agreement Validation**: Validated against reference standards with 100% agreement across comprehensive test datasets
- **Five-Domain Assessment**: Automated evaluation of risk of bias, inconsistency, indirectness, imprecision, and publication bias
- **Interactive Web Interface**: Streamlit-based GUI for intuitive operation and real-time result visualization  
- **Batch Processing**: Efficient evaluation of multiple outcomes and model types within systematic review projects
- **Standardized Output**: GRADE-compliant assessment tables ready for systematic review reporting

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run interactive interface
python app.py

# Or run command-line version
python run.py
```

## Integration with SmartEBM Ecosystem

This tool seamlessly integrates with the complete SmartEBM systematic review workflow:

**Upstream Integration:**
- **[SmartEBM Data Analysis Tool](../data_analysis_tool/README.md)**: Network meta-analysis results for GRADE domain evaluation
- **[SmartEBM Risk of Bias Assessment Tool](../robust_rob_assessment_tool/README.md)**: Study quality data for risk of bias domain assessment
- **[SmartEBM Data Extraction Tool](../data_extraction_tool/README.md)**: Study characteristics for indirectness and applicability evaluation

**Downstream Integration:**
- **Clinical Guidelines**: GRADE evidence profiles for guideline development
- **Systematic Review Reports**: Evidence quality tables for PRISMA reporting
- **Publication Outputs**: GRADE summary of findings tables for manuscripts

**Related SmartEBM Tools:**
- **[Title & Abstract Screening Tool](../title_and_abstract_screening_tool/README.md)**: Study selection informing evidence base
- **[Full-Text Screening Tool](../full_text_screening_tool/README.md)**: PICOS data supporting GRADE evaluation
- **[Template-Based Extraction Tool](../template_based_extraction_tool/README.md)**: Specialized GRADE-relevant data extraction

## 文档 / Documentation

- **📖 [Complete English Documentation](./docs/README.md)** - Installation, configuration, and advanced usage
- **📖 [完整中文文档](./docs/README_zh.md)** - 安装配置和高级使用指南

## 引用 / Citation

> Lai H, Liu J, Ma N, et al. Design and Validation of SmartNMA: A Comprehensive Large Language Model-Assisted Framework for Network Meta-Analysis. (Manuscript in preparation).