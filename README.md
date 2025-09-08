# SmartNMA: An Intelligent Agent for Interventional Systematic Reviews and Network Meta-Analysis

> **An AI-powered intelligent agent designed to facilitate the workflows of systematic reviews and network meta-analyses while augmenting human expertise.**

## Overview

SmartNMA is a comprehensive LLM-driven intelligent agent engineered to automate and enhance the production of systematic reviews and network meta-analyses (NMAs). Developed by the **SmartEBM Group at Lanzhou University**, SmartNMA addresses key limitations in evidence synthesis through adaptive mechanisms that enhance transparency, efficiency, and reliability.

### Key Features

- **Six Integrated Modules**: Complete workflow coverage from literature screening to evidence assessment
- **Intelligent Automation**: LLMs for linguistic tasks, algorithms for procedural standardization
- **Adaptive Mechanisms**: Intelligent prompt generation, task decomposition, confidence grading
- **Transparent Documentation**: Detailed reasoning chains and evidence for all decisions
- **High Accuracy**: Validated across 68,006 records and 233 studies with 96.4%+ accuracy
- **Efficiency**: Complete NMA workflow in approximately 30 hours including manual verification

## System Architecture

SmartNMA comprises six integrated modules corresponding to critical NMA workflow steps:

### LLM-Based Modules
1. **Title-Abstract Screening** - AI-powered initial literature screening
2. **Full-Text Screening** - Comprehensive full-text evaluation with PICOS extraction
3. **Data Extraction** - Systematic extraction using domain-based decomposition
4. **Risk of Bias Assessment** - Automated quality assessment using ROBUST-RCT framework

### Algorithmic Modules
5. **Data Analysis** - Frequentist network meta-analysis with standardized outputs
6. **Certainty of Evidence Assessment** - Automated GRADE approach implementation

## Installation

### Prerequisites

- Python 3.8+ (3.12.4 recommended)
- 8GB+ RAM (16GB+ recommended for large reviews)
- Stable internet connection for LLM API access

### Quick Start

```bash
# Clone the repository
git clone https://github.com/enenlhh/SmartNMA-AI-assisted-tools.git
cd SmartNMA-AI-assisted-tools

# Install dependencies
pip install -r requirements.txt

# Configure your API keys in each module's config file
```

### Individual Module Usage

Each module can be used independently. Navigate to the specific tool directory:

```bash
# Example: Use title-abstract screening
cd title_and_abstract_screening_tool
pip install -r requirements.txt
python main.py

# Example: Use data extraction
cd data_extraction_tool
pip install -r requirements.txt
python main.py
```

## Configuration

### API Setup

Each module requires LLM API configuration. SmartNMA supports multiple LLM providers:

- **Claude 3.5 Sonnet** (recommended)
- **GPT-4.1** / **GPT-4.1-mini**
- **Gemini-2.5-Pro**
- **DeepSeek-R1**

Configure your API keys in the respective module's configuration files.

## Performance Metrics

SmartNMA has been validated across nine full systematic reviews with NMAs:

| Module | Records/Studies | Sensitivity | Specificity | Accuracy |
|--------|----------------|-------------|-------------|----------|
| Title-Abstract Screening | 68,006 records | 100% | 99.0% | 96.4% |
| Full-Text Screening | 3,292 records | 100% | 99.9% | 98.8% |
| Data Extraction | 153,334 items | - | - | 98.0% → 99.5%* |
| Risk of Bias Assessment | 3,276 assessments | - | - | 97.5% → 97.4%* |
| Data Analysis | All datasets | - | - | 100% |
| CoE Assessment | All datasets | - | - | 100% |

*After manual verification

### Resource Requirements

For a typical systematic review (10,000 title-abstract records, 300 full-text records, 100 included studies):

- **Total Time**: ~30 hours (including manual verification)
- **Token Consumption**: ~57.4 million tokens
- **Estimated Cost**: $30-288 USD (depending on LLM model)

## Available Modules

- [Title & Abstract Screening Tool](title_and_abstract_screening_tool/)
- [Full-Text Screening Tool](full_text_screening_tool/)
- [Data Extraction Tool](data_extraction_tool/)
- [Risk of Bias Assessment Tool](robust_rob_assessment_tool/)
- [Data Analysis Tool](data_analysis_tool/)
- [GRADE CoE Assessment Tool](grade_coe_assessment_tool/)
- [Template-Based Extraction Tool](template_based_extraction_tool/)

## Citation

If you use SmartNMA in your research, please cite our paper:

```bibtex
@article{lai2025smartnma,
  title={Development and Validation of SmartNMA: An Intelligent Agent for Interventional Systematic Reviews and Network Meta-Analysis},
  author={Lai, Honghao and Liu, Jiayi and Busse, Jason W and Estill, Janne and Zhou, Qi and Brignardello-Petersen, Romina and Bala, Malgorzata M and da Costa, Bruno R and Li, Sheyu and Wang, Qi and others},
  journal={[Journal Name]},
  year={2025},
  publisher={[Publisher]}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

### Getting Help

- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/enenlhh/SmartNMA-AI-assisted-tools/issues)
- **Email**: Contact the development team at enenlhh@outlook.com

### Acknowledgments

**SmartEBM Group at Lanzhou University**

**Lead Developers:**
- Honghao Lai (enenlhh@outlook.com) - Technical Lead & Architecture
- Long Ge - Project Supervisor & Methodology

**Funding:**
- Fundamental Research Funds for Central Universities of Lanzhou University (lzujbky-2024-oy11)
- Traditional Chinese Medicine Innovation Team and Talent Support Program (ZYYCXTD-D-202401)

---

**SmartNMA** - Advancing Evidence-Based Medicine through Intelligent Automation

*Developed by the SmartEBM Group at Lanzhou University*