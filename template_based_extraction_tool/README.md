# SmartEBM Template-Based Extraction Tool

### Simplified Template-Driven PDF Data Extraction with Intelligent Auto-Repair

## Key Advantages

**4-Row Template Simplicity**: Revolutionary template design requiring only four Excel rows (field names, descriptions, example 1, example 2) to define complex extraction schemas - dramatically reducing setup complexity compared to traditional rule-based systems.

**Automatic Repair Mechanism**: Intelligent LLM-powered auto-repair system that automatically detects and corrects parsing failures, ensuring robust data extraction even from challenging PDF formats and layouts.

**Smart Field Batching**: Adaptive processing that automatically batches fields into optimal groups (≤20 fields per batch) to maximize LLM performance while maintaining extraction accuracy and preventing token limit issues.

**Structured Output Validation**: Built-in validation system that ensures consistent, standardized Excel output with proper column alignment and data integrity checks across all processed documents.

**SmartNMA Framework Integration**: Seamlessly integrates within the broader SmartEBM ecosystem, providing specialized template-driven extraction capabilities that complement the comprehensive systematic review workflow.

## Core Features

- **Template-Driven Configuration**: Define extraction fields using intuitive 4-row Excel templates
- **Batch PDF Processing**: Automated processing of entire PDF document folders
- **Intelligent Field Management**: Automatic batching for optimal LLM performance
- **Robust Error Recovery**: Auto-repair mechanism for parsing failures
- **Multi-Format PDF Support**: Handles various PDF layouts with fallback extraction methods
- **Structured Data Output**: Standardized Excel results with consistent formatting

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your template.xlsx with 4 rows:
# Row 1: Field names
# Row 2: Field descriptions  
# Row 3: Example values 1
# Row 4: Example values 2

# Run extraction
python main.py
```

## Integration with SmartEBM Ecosystem

This tool seamlessly integrates with the complete SmartEBM systematic review workflow:

**Upstream Integration:**
- **[SmartEBM Full-Text Screening Tool](../full_text_screening_tool/README.md)**: Included studies requiring specialized template-based extraction
- **[SmartEBM Data Extraction Tool](../data_extraction_tool/README.md)**: Complementary extraction for specific data schemas
- **Manual Study Collections**: Researcher-curated PDF collections with defined extraction templates

**Downstream Integration:**
- **[SmartEBM Data Analysis Tool](../data_analysis_tool/README.md)**: Template-extracted data for specialized network meta-analysis
- **[SmartEBM Risk of Bias Assessment Tool](../robust_rob_assessment_tool/README.md)**: Extracted methodology data for bias evaluation
- **Statistical Software**: Structured Excel outputs compatible with R, Stata, and SPSS

**Related SmartEBM Tools:**
- **[Title & Abstract Screening Tool](../title_and_abstract_screening_tool/README.md)**: Study selection informing extraction scope
- **[GRADE CoE Assessment Tool](../grade_coe_assessment_tool/README.md)**: Template-extracted data supporting evidence quality evaluation

## 文档 / Documentation

- **📖 [Complete English Documentation](./docs/README.md)** - Installation, configuration, and advanced usage
- **📖 [完整中文文档](./docs/README_zh.md)** - 安装配置和高级使用指南

## 引用 / Citation

> Lai H, Liu J, Ma N, et al. Design and Validation of SmartNMA: A Comprehensive Large Language Model-Assisted Framework for Network Meta-Analysis. (Manuscript in preparation).