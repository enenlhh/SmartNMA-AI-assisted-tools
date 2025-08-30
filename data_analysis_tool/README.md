# SmartEBM Data Analysis Agent

### No-Code Network Meta-Analysis with Perfect Agreement Validation

This project is developed and maintained by the **SmartEBM (Smart Evidence-Based Medicine) team** at Lanzhou University. Our team specializes in designing **intelligent agents** that embed sophisticated, human-like reasoning workflows into the evidence synthesis process.

## Key Advantages

**Perfect Agreement Validation**: Achieved perfect agreement with reference standards across all validation datasets in SmartNMA research, ensuring reliable statistical analysis for systematic reviews.

**No-Code Interactive Interface**: Eliminates programming barriers with an intuitive R Shiny web interface, enabling researchers to conduct comprehensive network meta-analyses without statistical software expertise.

**Comprehensive Visualization Suite**: Automatically generates publication-quality network graphs, forest plots, funnel plots, and node-splitting analyses for complete evidence visualization.

**GRADE-Ready Outputs**: Produces structured data files specifically designed for seamless integration with GRADE certainty of evidence assessment workflows.

**Batch Processing Capabilities**: Analyzes multiple outcome files simultaneously, dramatically reducing analysis time for complex systematic reviews with numerous endpoints.

## Core Features

- **Interactive Web Interface**: Browser-based R Shiny application with intuitive parameter configuration
- **Comprehensive NMA Engine**: Fixed-effect and random-effects models for binary and continuous data
- **Rich Visualization Suite**: Automated generation of network graphs, forest plots, and publication-quality figures
- **Automated Reporting**: League tables, treatment rankings (P-Scores), and heterogeneity statistics
- **Batch Processing & GRADE Integration**: Multi-outcome analysis with structured outputs for evidence assessment

## Quick Start

```bash
# Install dependencies
Rscript install_packages.R

# Launch the tool
python run.py
```

## Integration with SmartEBM Ecosystem

This tool seamlessly integrates with the complete SmartEBM systematic review workflow:

**Upstream Integration:**
- **[SmartEBM Data Extraction Tool](../data_extraction_tool/README.md)**: Structured quantitative data ready for network meta-analysis
- **[SmartEBM Risk of Bias Assessment Tool](../robust_rob_assessment_tool/README.md)**: Quality assessment data for sensitivity analysis
- **Manual Data Entry**: Researcher-curated datasets in standardized formats

**Downstream Integration:**
- **[SmartEBM GRADE CoE Assessment Tool](../grade_coe_assessment_tool/README.md)**: Network meta-analysis results for evidence quality evaluation
- **Publication Outputs**: Publication-ready figures, tables, and statistical reports
- **Clinical Guidelines**: Evidence synthesis for guideline development

**Related SmartEBM Tools:**
- **[Title & Abstract Screening Tool](../title_and_abstract_screening_tool/README.md)**: Study selection informing analysis scope
- **[Full-Text Screening Tool](../full_text_screening_tool/README.md)**: PICOS data supporting analysis design
- **[Template-Based Extraction Tool](../template_based_extraction_tool/README.md)**: Specialized data extraction for analysis inputs

## 文档 / Documentation

- **📖 [Complete English Documentation](./docs/README.md)** - Installation, configuration, and advanced usage
- **📖 [完整中文文档](./docs/README_zh.md)** - 安装配置和高级使用指南

## 引用 / Citation

> Lai H, Liu J, Ma N, et al. Design and Validation of SmartNMA: A Comprehensive Large Language Model-Assisted Framework for Network Meta-Analysis. (Manuscript in preparation).