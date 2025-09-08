# SmartEBM Risk of Bias Assessment Tool

### Advanced ROBUST-RCT Integration with Scalable Parallel Processing

An AI-powered systematic review tool that achieves 97.5% accuracy for high-confidence bias assessments through innovative two-step decomposition and confidence-based classification, validated across 3,276 assessments in the SmartNMA research framework.

## Key Advantages

**ROBUST-RCT Framework Integration**: Advanced two-step decomposition methodology that breaks down complex bias assessment into manageable components, enabling more accurate and consistent evaluations compared to traditional single-step approaches.

**97.5% High-Confidence Accuracy**: Research-validated performance across 3,276 bias assessments, with confidence-based classification that automatically identifies assessments requiring manual review versus those suitable for automated processing.

**Scalable Parallel Processing**: Hardware and API rate-limited parallel processing architecture that maximizes efficiency while respecting system constraints, enabling assessment of large study collections with optimal resource utilization.

**Confidence-Based Quality Control**: Intelligent confidence scoring system that categorizes assessment reliability, allowing researchers to focus manual review efforts on uncertain cases while trusting high-confidence automated assessments.

## Core Features

- Two-step bias domain decomposition with ROBUST-RCT methodology
- Multi-LLM validation approach for enhanced reliability
- Automated confidence scoring and quality categorization
- Scalable parallel processing with intelligent resource management
- Comprehensive reporting with visual confidence indicators
- Checkpoint recovery system for uninterrupted large-scale assessments

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Assessment**
   ```bash
   cp config/config_template.json config/config.json
   # Edit config.json with your API keys and assessment criteria
   ```

3. **Run Assessment**
   ```bash
   python main.py
   # Follow interactive prompts for guided setup
   ```

## Integration with SmartEBM Ecosystem

This tool seamlessly integrates with the complete SmartEBM systematic review workflow:

**Upstream Integration:**
- **[SmartEBM Data Extraction Tool](../data_extraction_tool/README.md)**: Study characteristics and methodology data for bias assessment
- **[SmartEBM Full-Text Screening Tool](../full_text_screening_tool/README.md)**: Study design information from PICOS extraction
- **Manual Study Collections**: Researcher-provided study PDFs for targeted assessment

**Downstream Integration:**
- **[SmartEBM Data Analysis Tool](../data_analysis_tool/README.md)**: Bias assessment results for sensitivity analysis
- **[SmartEBM GRADE CoE Assessment Tool](../grade_coe_assessment_tool/README.md)**: Risk of bias domain evaluation for evidence quality
- **Systematic Review Reporting**: PRISMA-compliant bias assessment tables

**Related SmartEBM Tools:**
- **[Title & Abstract Screening Tool](../title_and_abstract_screening_tool/README.md)**: Initial study selection for bias assessment
- **[Template-Based Extraction Tool](../template_based_extraction_tool/README.md)**: Specialized bias-related data extraction

## Documentation / 文档

For detailed documentation, please refer to the files in the [docs](docs/) folder:
有关详细文档，请参阅[docs](docs/)文件夹中的文件：
- **📖 [Complete English Documentation](docs/README.md)** - Installation, configuration, and advanced usage
- **📖 [完整中文文档](docs/README_zh.md)** - 安装配置和高级使用指南

## Citation

If you use this tool in your research, please cite the SmartNMA framework:

> Lai H, Liu J, Busse J, et,al. Development and Validation of SmartNMA: An Intelligent Agent for Interventional Systematic Reviews and Network Meta-Analysis

## Repository

- **GitHub**: https://github.com/enenlhh/SmartNMA-AI-assisted-tools
- **Contact**: enenlhh@outlook.com
- **Team**: SmartEBM Group at Lanzhou University