# SmartEBM Full-Text Screening Tool
### AI-Powered Full-Text Screening with 99.9% Specificity

## Key Advantages

**Research-Validated Performance**: Achieved 99.9% specificity across 3,292 full-text records in SmartNMA validation study, ensuring minimal false positives in systematic review workflows.

**Intelligent Prompt Generation**: Advanced AI-powered screening with keyword-based pre-screening that automatically adapts to study characteristics and research domains for optimal accuracy.

**Transparent Documentation**: Complete audit trail of screening decisions with detailed reasoning, supporting reproducible systematic reviews and regulatory compliance.

**Systematic Review Integration**: Seamlessly integrates with PICOS framework and connects with other SmartEBM tools for end-to-end systematic review automation.

## Core Features

- **AI-Powered Full-Text Analysis**: Multi-model LLM consensus for robust screening decisions
- **PICOS Framework Integration**: Structured extraction of Population, Intervention, Comparison, Outcomes, and Study design
- **Keyword-Based Pre-Screening**: Intelligent filtering reduces processing time while maintaining accuracy
- **Parallel Processing Architecture**: Scalable multi-threaded processing for large document collections
- **Comprehensive PDF Support**: Advanced text extraction with OCR fallback for scanned documents
- **Real-Time Progress Monitoring**: Live tracking with estimated completion times and performance metrics

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Settings**
   ```bash
   cp config/config_template.json config/config.json
   # Edit config.json with your API keys and screening criteria
   ```

3. **Run Interactive Screening**
   ```bash
   python main.py
   ```

## Documentation

For comprehensive installation, configuration, and usage instructions:
- [Complete English Documentation](docs/README.md)
- [完整中文文档](docs/README_zh.md)

## Integration with SmartEBM Ecosystem

This tool seamlessly integrates with the complete SmartEBM systematic review workflow:

**Upstream Integration:**
- **[SmartEBM Title & Abstract Screening Tool](../title_and_abstract_screening_tool/README.md)**: Pre-screened studies requiring full-text evaluation
- **Literature Databases**: Direct PDF collections from systematic searches
- **Reference Managers**: EndNote, Zotero, and Mendeley PDF libraries

**Downstream Integration:**
- **[SmartEBM Data Extraction Tool](../data_extraction_tool/README.md)**: Included studies with PICOS data for systematic extraction
- **[SmartEBM Risk of Bias Assessment Tool](../robust_rob_assessment_tool/README.md)**: Study methodology data for bias evaluation
- **Manual Review**: Uncertain cases flagged for researcher evaluation

**Related SmartEBM Tools:**
- **[Data Analysis Tool](../data_analysis_tool/README.md)**: Network meta-analysis of screening results
- **[GRADE CoE Assessment Tool](../grade_coe_assessment_tool/README.md)**: Evidence quality assessment integration
- **[Template-Based Extraction Tool](../template_based_extraction_tool/README.md)**: Specialized data extraction workflows

## Citation

If you use this tool in your research, please cite the SmartNMA framework:

> Lai H, Liu J, Ma N, et al. Design and Validation of SmartNMA: A Comprehensive Large Language Model-Assisted Framework for Network Meta-Analysis. (Manuscript in preparation).