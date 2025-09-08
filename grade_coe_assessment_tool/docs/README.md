# GRADE CoE Assessment Tool - Complete Documentation

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Usage Workflows](#usage-workflows)
- [GRADE Framework Integration](#grade-framework-integration)
- [Assessment Workflow](#assessment-workflow)
- [Interactive Report Generation](#interactive-report-generation)
- [Advanced Features](#advanced-features)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Technical Architecture](#technical-architecture)
- [Integration Guide](#integration-guide)
- [Best Practices](#best-practices)

## System Requirements

### Hardware Requirements
- **RAM**: Minimum 4GB, recommended 8GB for large datasets
- **Storage**: At least 1GB free space for analysis results and reports
- **CPU**: Multi-core processor recommended for batch processing

### Software Dependencies
- **Python**: Version 3.8 or higher
- **Required packages**: Listed in `requirements.txt`
- **Web browser**: Modern browser for interactive reports (Chrome, Firefox, Safari, Edge)

### Input Data Requirements
- Network meta-analysis results from R netmeta package
- Standardized file structure with outcome directories
- Risk of bias assessments for included studies
- Analysis settings and configuration files

## Installation Guide

### Step 1: Clone or Download
```bash
# If using git
git clone [repository-url]
cd grade_coe_assessment_tool

# Or download and extract the tool package
```

### Step 2: Install Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt

# For development environment
pip install -r requirements.txt --upgrade
```

### Step 3: Verify Installation
```bash
# Test the installation
python -c "from src.grade_evaluator import GradeEvaluator; print('Installation successful')"
```

## Configuration

### Basic Configuration

The tool uses a `config.json` file for configuration. Create this file in the root directory:

```json
{
    "data_settings": {
        "base_dir": "/path/to/your/nma/results",
        "output_dir": "/path/to/output/directory"
    },
    "mid_params": {
        "harmful_mid": null,
        "benefit_mid": null
    },
    "rob_params": {
        "high_risk_count_threshold": 0.5,
        "high_risk_weight_threshold": 50,
        "very_serious_weight_threshold": 80
    },
    "inconsistency_params": {
        "i2_threshold": 60,
        "i2_very_serious_threshold": 90,
        "ci_overlap_threshold": 0.5
    }
}
```

### Configuration Parameters

#### Data Settings
- **base_dir**: Root directory containing NMA analysis results
- **output_dir**: Directory for saving GRADE assessment results

#### MID Parameters (Minimal Important Difference)
- **harmful_mid**: Threshold for harmful effects (e.g., 1.25 for OR)
- **benefit_mid**: Threshold for beneficial effects (e.g., 0.75 for OR)
- Set to `null` to use default values

#### Risk of Bias Parameters
- **high_risk_count_threshold**: Proportion threshold for high-risk studies (default: 0.5)
- **high_risk_weight_threshold**: Weight percentage threshold for serious concern (default: 50%)
- **very_serious_weight_threshold**: Weight percentage threshold for very serious concern (default: 80%)

#### Inconsistency Parameters
- **i2_threshold**: I² threshold for serious inconsistency (default: 60%)
- **i2_very_serious_threshold**: I² threshold for very serious inconsistency (default: 90%)
- **ci_overlap_threshold**: Confidence interval overlap threshold (default: 0.5)

### Customizable Judgment Thresholds

The tool allows researchers to customize GRADE assessment criteria:

#### Risk of Bias Thresholds
```json
"rob_params": {
    "high_risk_count_threshold": 0.3,  // 30% of studies
    "high_risk_weight_threshold": 40,   // 40% weight threshold
    "very_serious_weight_threshold": 70 // 70% for very serious
}
```

#### Inconsistency Thresholds
```json
"inconsistency_params": {
    "i2_threshold": 50,           // Lower threshold for conservative assessment
    "i2_very_serious_threshold": 85,
    "ci_overlap_threshold": 0.3   // Stricter overlap requirement
}
```

## Usage Workflows

### Interactive Web Interface

1. **Launch the Application**
   ```bash
   streamlit run app.py
   ```

2. **Select Analysis Parameters**
   - Choose outcome from available options
   - Select model type (random or fixed effects)
   - Review configuration settings

3. **Run Assessment**
   - Click "Start GRADE Assessment"
   - Monitor progress in real-time
   - Review results in interactive table

4. **Export Results**
   - Download Excel file with complete assessment
   - Generate interactive HTML report

### Command Line Interface

1. **Basic Usage**
   ```bash
   python run.py
   ```

2. **Programmatic Usage**
   ```python
   from src.grade_evaluator import GradeEvaluator
   
   evaluator = GradeEvaluator(
       base_dir="/path/to/nma/results",
       outcome_name="primary_outcome",
       model_type="random"
   )
   
   results = evaluator.evaluate_grade()
   ```

### Batch Processing

For multiple outcomes:

```python
import os
from src.grade_evaluator import GradeEvaluator, list_available_outcomes

base_dir = "/path/to/nma/results"
outcomes = list_available_outcomes(base_dir)

for outcome_info in outcomes:
    for model in outcome_info['models']:
        evaluator = GradeEvaluator(
            base_dir=base_dir,
            outcome_name=outcome_info['outcome'],
            model_type=model
        )
        results = evaluator.evaluate_grade()
        # Save results
```

## GRADE Framework Integration

### Five-Domain Assessment

The tool implements comprehensive GRADE methodology:

#### 1. Risk of Bias Assessment
- **Methodology**: Weight-based evaluation using study-level ROB assessments
- **Thresholds**: Configurable proportion and weight thresholds
- **Output**: Serious/Very serious/Not serious ratings with detailed reasoning

#### 2. Inconsistency Evaluation
- **Statistical measures**: I² statistics, confidence interval overlap
- **Network-specific**: Considers both direct and indirect evidence
- **Adaptive thresholds**: Customizable based on research context

#### 3. Indirectness Assessment
- **Population**: Evaluates population representativeness
- **Intervention**: Assesses intervention relevance
- **Outcomes**: Reviews outcome measurement appropriateness

#### 4. Imprecision Analysis
- **Sample size**: Calculates effective sample sizes for network evidence
- **Optimal Information Size**: Computes OIS based on minimal important differences
- **Confidence intervals**: Evaluates precision of effect estimates

#### 5. Publication Bias Detection
- **Network geometry**: Assesses network completeness
- **Study distribution**: Evaluates evidence distribution patterns
- **Reporting quality**: Reviews selective reporting indicators

### GRADE Rating Logic

The tool implements standardized GRADE rating progression:

1. **Starting Point**: High certainty for RCTs
2. **Downgrading**: Apply downgrades for each domain concern
3. **Final Rating**: Very low, Low, Moderate, or High certainty

```
High → Moderate → Low → Very Low
 ↓        ↓       ↓
-1      -1      -1    (per domain concern)
```

## Assessment Workflow

### Data Processing Pipeline

1. **Input Validation**
   - Verify file structure and completeness
   - Check data format consistency
   - Validate analysis settings

2. **Evidence Extraction**
   - Parse network meta-analysis results
   - Extract study-level characteristics
   - Compile comparison-specific data

3. **Domain-Specific Assessment**
   - Apply GRADE criteria systematically
   - Generate evidence-based ratings
   - Document assessment reasoning

4. **Result Compilation**
   - Aggregate domain assessments
   - Calculate final certainty ratings
   - Prepare structured output

### Quality Assurance Steps

- **Automated validation**: Built-in consistency checks
- **Transparent reasoning**: Detailed explanation for each judgment
- **Reproducible results**: Standardized assessment criteria
- **Audit trail**: Complete documentation of assessment process

## Interactive Report Generation

### HTML Report Features

The tool generates comprehensive interactive reports:

#### Real-Time Recalculation
- **Dynamic thresholds**: Adjust parameters and see immediate results
- **Interactive tables**: Sort, filter, and explore assessment data
- **Visual indicators**: Color-coded certainty ratings and domain concerns

#### Self-Contained Design
- **Zero dependencies**: Complete functionality without external resources
- **Portable format**: Single HTML file for easy sharing
- **Cross-platform**: Compatible with all modern browsers

#### Report Components

1. **Executive Summary**
   - Overall assessment overview
   - Key findings and recommendations
   - Methodology summary

2. **Detailed Results Table**
   - Comparison-specific assessments
   - Domain-by-domain ratings
   - Supporting evidence and reasoning

3. **Interactive Controls**
   - Threshold adjustment sliders
   - Filter and search capabilities
   - Export functionality

4. **Methodology Documentation**
   - Assessment criteria explanation
   - Parameter settings record
   - Quality assurance information

### Report Customization

```python
# Generate custom report
evaluator.generate_interactive_report(
    output_path="custom_report.html",
    include_methodology=True,
    show_calculations=True,
    theme="professional"
)
```

## Advanced Features

### Custom Assessment Rules

Implement domain-specific assessment logic:

```python
# Custom ROB assessment
def custom_rob_assessment(studies_data, weights_data):
    # Implement custom logic
    return rating, reasoning

evaluator.set_custom_rob_function(custom_rob_assessment)
```

### Integration with External Tools

- **R netmeta**: Direct integration with netmeta package outputs
- **RevMan**: Compatible with Cochrane Review Manager data
- **STATA**: Supports STATA network meta-analysis results

### Validation and Testing

- **Reference standards**: Validated against expert assessments
- **Reproducibility**: Consistent results across runs
- **Performance metrics**: Speed and accuracy benchmarks

## Performance Optimization

### Large Dataset Handling

- **Memory management**: Efficient data processing for large networks
- **Parallel processing**: Multi-core utilization for batch assessments
- **Caching**: Intelligent caching of intermediate results

### Speed Optimization Tips

1. **Pre-process data**: Clean and validate input data beforehand
2. **Batch operations**: Process multiple outcomes together
3. **Configuration tuning**: Optimize parameters for your use case

## Troubleshooting

### Common Issues

#### File Not Found Errors
```
Error: Directory does not exist: /path/to/results
```
**Solution**: Verify the `base_dir` path in configuration and ensure all required files are present.

#### Missing Dependencies
```
ModuleNotFoundError: No module named 'pandas'
```
**Solution**: Install required packages using `pip install -r requirements.txt`

#### Configuration Errors
```
KeyError: 'high_risk_count_threshold'
```
**Solution**: Check `config.json` format and ensure all required parameters are included.

### Data Format Issues

#### Inconsistent File Structure
- Ensure outcome directories follow the expected naming convention
- Verify that all required CSV files are present and properly formatted
- Check that analysis settings files contain necessary parameters

#### ROB Assessment Format
- Risk of bias assessments should use standardized categories: "Low", "High", "Unclear"
- Ensure study names match between ROB data and analysis results
- Verify that all included studies have ROB assessments

### Performance Issues

#### Slow Processing
- Check available system memory
- Reduce batch size for large datasets
- Verify input data quality and completeness

#### Memory Errors
- Process outcomes individually rather than in batch
- Increase system virtual memory
- Optimize data preprocessing steps

## Technical Architecture

### Core Components

#### GradeEvaluator Class
- **Purpose**: Main assessment engine
- **Responsibilities**: Data loading, domain assessment, result compilation
- **Key methods**: `evaluate_grade()`, `evaluate_rob()`, `evaluate_inconsistency()`

#### Assessment Modules
- **ROB Module**: Risk of bias evaluation with weight-based analysis
- **Inconsistency Module**: Statistical inconsistency assessment
- **Imprecision Module**: Sample size and precision analysis
- **Publication Bias Module**: Network completeness evaluation

#### Report Generator
- **HTML Engine**: Interactive report creation
- **Template System**: Customizable report layouts
- **Export Functions**: Multiple output format support

### Data Flow Architecture

```
Input Data → Validation → Domain Assessment → Result Compilation → Report Generation
     ↓            ↓              ↓                ↓                    ↓
NMA Results → Format Check → GRADE Domains → Final Ratings → Interactive HTML
```

### Algorithm Implementation

#### Weight-Based ROB Assessment
1. Calculate study weights from meta-analysis results
2. Identify high-risk studies from ROB assessments
3. Compute weighted proportion of high-risk evidence
4. Apply configurable thresholds for rating determination

#### Network Inconsistency Analysis
1. Extract I² statistics from pairwise comparisons
2. Evaluate confidence interval overlap patterns
3. Assess global network inconsistency measures
4. Generate domain-specific inconsistency ratings

## Integration Guide

### R netmeta Integration

The tool is designed to work seamlessly with R netmeta package outputs:

#### Required Files
- `outcome-nettable.csv`: Network comparison table
- `outcome-original_data.csv`: Original study data
- `outcome-analysis_settings.csv`: Analysis configuration
- `outcome-netpairwise.csv`: Pairwise comparison results
- `outcome-meta_result_random.csv`: Random effects results

#### File Format Requirements
```r
# R code to generate compatible files
library(netmeta)

# Run network meta-analysis
net_result <- netmeta(TE, seTE, treat1, treat2, studlab, data = your_data)

# Export required files
write.csv(nettable(net_result), "outcome-nettable.csv")
write.csv(your_data, "outcome-original_data.csv")
# ... additional exports
```

### Workflow Integration

#### Systematic Review Pipeline
1. **Study selection**: Complete screening and selection process
2. **Data extraction**: Extract outcome data and study characteristics
3. **ROB assessment**: Conduct risk of bias evaluation
4. **Network meta-analysis**: Perform statistical analysis using R netmeta
5. **GRADE assessment**: Use this tool for evidence certainty evaluation
6. **Report generation**: Create final systematic review report

#### Quality Assurance Integration
- **Dual assessment**: Support for independent assessor workflows
- **Consensus building**: Tools for resolving assessment disagreements
- **Audit documentation**: Complete assessment trail for peer review

## Best Practices

### Assessment Methodology

#### Pre-Assessment Preparation
1. **Complete ROB assessment**: Ensure all studies have quality assessments
2. **Validate network geometry**: Check for disconnected networks or sparse data
3. **Define MID values**: Establish clinically important difference thresholds
4. **Configure parameters**: Set appropriate thresholds for your research context

#### During Assessment
1. **Review automated judgments**: Verify that automated assessments align with clinical expertise
2. **Document rationale**: Add context-specific reasoning where appropriate
3. **Consider clinical relevance**: Evaluate statistical findings in clinical context
4. **Maintain consistency**: Apply assessment criteria uniformly across comparisons

#### Post-Assessment Review
1. **Validate results**: Cross-check assessments with clinical experts
2. **Document methodology**: Record assessment approach and parameter choices
3. **Prepare for peer review**: Ensure transparent and reproducible assessment process

### Configuration Recommendations

#### Conservative Assessment
```json
{
    "rob_params": {
        "high_risk_count_threshold": 0.3,
        "high_risk_weight_threshold": 30,
        "very_serious_weight_threshold": 60
    },
    "inconsistency_params": {
        "i2_threshold": 50,
        "i2_very_serious_threshold": 80
    }
}
```

#### Standard Assessment
```json
{
    "rob_params": {
        "high_risk_count_threshold": 0.5,
        "high_risk_weight_threshold": 50,
        "very_serious_weight_threshold": 80
    },
    "inconsistency_params": {
        "i2_threshold": 60,
        "i2_very_serious_threshold": 90
    }
}
```

### Quality Assurance

#### Validation Steps
1. **Cross-validation**: Compare results with manual assessments
2. **Sensitivity analysis**: Test different parameter configurations
3. **Expert review**: Validate assessments with domain experts
4. **Reproducibility testing**: Verify consistent results across runs

#### Documentation Standards
- **Parameter justification**: Document rationale for threshold choices
- **Assessment trail**: Maintain complete record of assessment process
- **Version control**: Track changes in assessment criteria and results
- **Peer review preparation**: Organize documentation for external review

---

## Citation

When using this tool in your research, please cite:

> Lai H, Liu J, Busse J, et,al. Development and Validation of SmartNMA: An Intelligent Agent for Interventional Systematic Reviews and Network Meta-Analysis

## Repository

- **GitHub**: https://github.com/enenlhh/SmartNMA-AI-assisted-tools
- **Contact**: enenlhh@outlook.com
- **Team**: SmartEBM Group at Lanzhou University

## Support and Contact

For technical support, feature requests, or collaboration opportunities, please contact the SmartEBM Group at Lanzhou University.

---

*This documentation is part of the SmartEBM systematic review and meta-analysis toolkit, designed to enhance the efficiency and reliability of evidence synthesis processes.*