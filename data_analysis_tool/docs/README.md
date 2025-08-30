# SmartEBM Data Analysis Agent - Complete Documentation

### No-Code Network Meta-Analysis with Perfect Agreement Validation

This project is developed and maintained by the **SmartEBM (Smart Evidence-Based Medicine) team** at Lanzhou University. Our team specializes in designing **intelligent agents** that embed sophisticated, human-like reasoning workflows into the evidence synthesis process.

This repository contains the **SmartEBM Data Analysis Agent**, our solution for performing complex statistical calculations required for network meta-analysis (NMA) without programming knowledge.

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Installation Guide](#2-installation-guide)
3. [Data Preparation Guide](#3-data-preparation-guide)
4. [R Shiny Interface Workflow](#4-r-shiny-interface-workflow)
5. [Statistical Analysis Capabilities](#5-statistical-analysis-capabilities)
6. [Output Interpretation](#6-output-interpretation)
7. [Advanced Features](#7-advanced-features)
8. [Performance Optimization](#8-performance-optimization)
9. [Troubleshooting](#9-troubleshooting)
10. [Technical Architecture](#10-technical-architecture)
11. [Integration Guide](#11-integration-guide)
12. [Best Practices](#12-best-practices)

## 1. System Requirements

### Hardware Requirements
- **CPU**: 4+ cores recommended (8+ cores for optimal performance)
- **Memory**: 8GB RAM minimum (16GB+ recommended for large datasets)
- **Storage**: 2GB+ available disk space
- **Network**: Stable internet connection for package installation

### Software Requirements
- **R**: Version 4.0+ (download from [CRAN](https://cran.r-project.org/))
- **Python**: Version 3.8+ (3.10+ recommended)
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

### R Package Dependencies
The tool automatically installs required packages including:
- `netmeta`: Core network meta-analysis functionality
- `shiny`: Interactive web interface framework
- `DT`: Interactive data tables
- `plotly`: Interactive visualizations
- `readxl`: Excel file processing
- `writexl`: Excel output generation

## 2. Installation Guide

### Step 1: Install R and Python
1. Download and install R from the [official CRAN website](https://cran.r-project.org/)
2. Ensure R is accessible from your system's command line/terminal
3. Install Python 3.8+ if not already available

### Step 2: Clone the Repository
```bash
git clone https://github.com/smartebm/data-analysis-agent.git
cd data-analysis-agent
```

### Step 3: Install R Dependencies
```bash
Rscript install_packages.R
```

This script will automatically:
- Check for existing package installations
- Install missing dependencies
- Verify successful installation
- Display any installation errors for troubleshooting

### Step 4: Verify Installation
```bash
python run.py --test
```

## 3. Data Preparation Guide

### Data Format Requirements

The analysis tool requires data in **Excel (.xlsx) format** with specific column structures. Each outcome must be in a separate Excel file, with the filename serving as the outcome name.

#### Binary Data Template

| Column | Description | Example |
|--------|-------------|---------|
| `study` | Study identifier | "Smith 2021" |
| `treatment` | Intervention name | "Drug A" |
| `event` | Number of events | 15 |
| `n` | Total participants | 100 |
| `ROB` | Risk of bias | "Low" or "High" |

#### Continuous Data Template

| Column | Description | Example |
|--------|-------------|---------|
| `study` | Study identifier | "Jones 2020" |
| `treatment` | Intervention name | "Therapy B" |
| `n` | Total participants | 85 |
| `mean` | Outcome mean | 12.5 |
| `sd` | Standard deviation | 3.2 |
| `ROB` | Risk of bias | "Low" or "High" |

### Data Quality Guidelines

**Study Identifiers**: Use consistent, unique identifiers across all files (e.g., "FirstAuthor YYYY")

**Treatment Names**: Maintain exact spelling and capitalization across all studies and outcomes

**Missing Data**: Leave cells empty rather than using placeholders like "NA" or "NULL"

**Risk of Bias**: Use only "Low" or "High" values (case-sensitive)

### Template Files

Reference the `data_templates/` folder for example files:
- `Binary_Example.xlsx`: Template for binary outcomes
- `Continuous_Example.xlsx`: Template for continuous outcomes

## 4. R Shiny Interface Workflow

### Launching the Application

```bash
python run.py
```

The application will:
1. Start a local web server
2. Automatically open your default browser
3. Display the analysis interface at `http://localhost:3838`

### Interface Components

#### Data Upload Panel
- **File Selection**: Choose multiple Excel files simultaneously
- **Preview**: Review uploaded data structure and detect issues
- **Validation**: Automatic format checking and error reporting

#### Configuration Panel
- **Data Type**: Select binary or continuous analysis
- **Effect Measures**: Choose appropriate effect size (OR, RR, MD, SMD)
- **Statistical Models**: Configure fixed-effect and/or random-effects analysis
- **Reference Treatment**: Set the baseline comparison treatment

#### Analysis Settings
- **Confidence Intervals**: Set confidence level (default: 95%)
- **Heterogeneity Assessment**: Enable I² and τ² calculations
- **Publication Bias**: Configure Egger's test and funnel plot analysis
- **Node-Splitting**: Enable consistency evaluation

#### Output Configuration
- **Directory Selection**: Choose output folder location
- **File Formats**: Select PDF, Excel, and/or CSV outputs
- **Report Generation**: Enable automated methodology reports

### Workflow Steps

1. **Upload Data Files**: Select all outcome Excel files
2. **Configure Analysis**: Set data type and statistical parameters
3. **Select Output Directory**: Choose result storage location
4. **Review Settings**: Verify configuration in summary panel
5. **Start Analysis**: Click "🚀 Start Analysis" button
6. **Monitor Progress**: Track analysis status in real-time
7. **Review Results**: Access organized outputs in selected directory

## 5. Statistical Analysis Capabilities

### Network Meta-Analysis Models

#### Fixed-Effect (Common-Effect) Model
- **Assumption**: Single true effect size across all studies
- **Use Case**: Low heterogeneity, similar study populations
- **Output**: Precise estimates with narrow confidence intervals

#### Random-Effects Model
- **Assumption**: Distribution of true effects across studies
- **Use Case**: Moderate to high heterogeneity, diverse populations
- **Output**: Conservative estimates accounting for between-study variation

### Effect Measures

#### Binary Outcomes
- **Odds Ratio (OR)**: Standard for case-control and cross-sectional studies
- **Risk Ratio (RR)**: Preferred for cohort studies and RCTs
- **Risk Difference (RD)**: Absolute effect measures

#### Continuous Outcomes
- **Mean Difference (MD)**: Same measurement scale across studies
- **Standardized Mean Difference (SMD)**: Different scales or instruments

### Statistical Assessments

#### Heterogeneity Analysis
- **I² Statistic**: Percentage of variation due to heterogeneity
- **τ² (Tau-squared)**: Between-study variance estimate
- **Q-test**: Statistical test for heterogeneity

#### Consistency Evaluation
- **Node-Splitting**: Direct vs. indirect evidence comparison
- **Inconsistency Factors**: Quantitative inconsistency measures
- **Loop-Specific Analysis**: Closed-loop consistency assessment

#### Publication Bias Assessment
- **Egger's Test**: Statistical test for small-study effects
- **Funnel Plots**: Visual assessment of publication bias
- **Comparison-Adjusted Funnel Plots**: Network-specific bias evaluation

## 6. Output Interpretation

### File Structure

```
Output_Directory/
├── NMA_Methodology_Report.xlsx
├── Outcome_1/
│   ├── Outcome_1-netgraph.pdf
│   ├── Results of Random Effect Model/
│   │   ├── forestplot.pdf
│   │   ├── nettable.xlsx
│   │   ├── league_table.xlsx
│   │   ├── Pscore.txt
│   │   ├── egger_test_results.csv
│   │   └── meta_result_random.csv
│   └── Results of Common Effect Model/
│       └── [similar files]
└── Outcome_2/
    └── [similar structure]
```

### Key Output Files

#### Network Graph (`netgraph.pdf`)
- **Nodes**: Represent treatments (size proportional to sample size)
- **Edges**: Represent direct comparisons (thickness proportional to studies)
- **Layout**: Optimized for clarity and interpretation

#### Forest Plot (`forestplot.pdf`)
- **Effect Estimates**: Point estimates with confidence intervals
- **Reference Treatment**: Baseline comparison (typically placebo/control)
- **Heterogeneity Statistics**: I² and τ² values displayed

#### League Table (`league_table.xlsx`)
- **Upper Triangle**: Effect estimates (treatment vs. comparator)
- **Lower Triangle**: Confidence intervals
- **Diagonal**: Treatment names
- **Color Coding**: Statistical significance indicators

#### Treatment Rankings (`Pscore.txt`)
- **P-Scores**: Probability of being the best treatment (0-1 scale)
- **SUCRA**: Surface Under Cumulative Ranking curve
- **Ranking Probabilities**: Probability matrices for each rank position

#### GRADE Integration File (`meta_result_random.csv`)
- **Structured Data**: Formatted for GRADE assessment tool input
- **Effect Estimates**: Point estimates and confidence intervals
- **Quality Indicators**: Heterogeneity and consistency measures
- **Study Characteristics**: Sample sizes and risk of bias information

### Interpretation Guidelines

#### Effect Size Interpretation
- **Odds Ratio**: OR > 1 favors treatment, OR < 1 favors control
- **Risk Ratio**: RR > 1 increases risk, RR < 1 reduces risk
- **Mean Difference**: Positive values favor treatment (for beneficial outcomes)

#### Confidence Intervals
- **Narrow CIs**: Precise estimates, adequate sample size
- **Wide CIs**: Uncertain estimates, limited data
- **CI Crossing 1.0**: Non-significant effect (for ratios)
- **CI Crossing 0.0**: Non-significant effect (for differences)

#### Heterogeneity Assessment
- **I² < 25%**: Low heterogeneity
- **I² 25-50%**: Moderate heterogeneity
- **I² > 50%**: Substantial heterogeneity
- **I² > 75%**: Considerable heterogeneity

#### Publication Bias Indicators
- **Egger's p < 0.05**: Significant small-study effects
- **Asymmetric Funnel Plot**: Potential publication bias
- **Missing Studies**: Gaps in evidence network

## 7. Advanced Features

### Batch Processing Capabilities

The tool supports simultaneous analysis of multiple outcomes:

#### Multi-Outcome Analysis
- **Parallel Processing**: Simultaneous analysis of all uploaded files
- **Consistent Settings**: Same statistical parameters across outcomes
- **Organized Output**: Separate folders for each outcome
- **Summary Report**: Comprehensive methodology documentation

#### Efficiency Benefits
- **Time Savings**: Eliminates repetitive manual configuration
- **Consistency**: Standardized analysis approach across outcomes
- **Quality Assurance**: Reduced risk of configuration errors

### GRADE Integration Workflow

#### Automated GRADE Preparation
- **Structured Output**: `meta_result_random.csv` formatted for GRADE tool
- **Effect Estimates**: Direct input for certainty assessment
- **Quality Indicators**: Heterogeneity and consistency data included
- **Study Characteristics**: Risk of bias and sample size information

#### Seamless Workflow Integration
1. **Data Analysis**: Complete NMA using this tool
2. **GRADE Assessment**: Import `meta_result_random.csv` to GRADE tool
3. **Evidence Synthesis**: Automated certainty of evidence evaluation
4. **Report Generation**: Comprehensive evidence profiles and summary tables

### Customization Options

#### Statistical Parameters
- **Confidence Levels**: Adjustable from 90% to 99%
- **Significance Thresholds**: Customizable α levels
- **Model Selection**: Automatic or manual fixed/random effects choice

#### Visualization Settings
- **Graph Layouts**: Multiple network visualization algorithms
- **Color Schemes**: Customizable treatment and significance colors
- **Export Formats**: PDF, PNG, SVG options for publications

## 8. Performance Optimization

### Large Dataset Handling

#### Memory Management
- **Efficient Processing**: Optimized algorithms for large networks
- **Memory Monitoring**: Automatic resource usage tracking
- **Batch Processing**: Chunked analysis for memory-intensive operations

#### Processing Speed
- **Parallel Computing**: Multi-core utilization where possible
- **Optimized Algorithms**: Efficient statistical computation methods
- **Caching**: Intermediate result storage for faster re-analysis

### System Resource Guidelines

#### Recommended Specifications by Network Size
- **Small Networks** (≤10 treatments): 4GB RAM, 2 cores
- **Medium Networks** (10-20 treatments): 8GB RAM, 4 cores
- **Large Networks** (20+ treatments): 16GB RAM, 8+ cores

#### Performance Monitoring
- **Progress Tracking**: Real-time analysis status updates
- **Resource Usage**: CPU and memory utilization display
- **Estimated Time**: Completion time predictions

## 9. Troubleshooting

### Common Issues and Solutions

#### Installation Problems

**R Package Installation Failures**
```bash
# Solution: Install packages individually
R -e "install.packages('netmeta', repos='https://cran.r-project.org')"
```

**Python Dependencies Missing**
```bash
# Solution: Install required Python packages
pip install flask pandas openpyxl
```

#### Data Format Issues

**Column Name Errors**
- **Problem**: Incorrect or missing required columns
- **Solution**: Use exact column names from templates (case-sensitive)

**Data Type Mismatches**
- **Problem**: Text in numeric columns
- **Solution**: Ensure numeric data contains only numbers

**Treatment Name Inconsistencies**
- **Problem**: Spelling variations across studies
- **Solution**: Standardize treatment names exactly across all files

#### Analysis Errors

**Network Connectivity Issues**
- **Problem**: Disconnected treatment networks
- **Solution**: Ensure all treatments connect through direct or indirect comparisons

**Insufficient Data**
- **Problem**: Too few studies for reliable analysis
- **Solution**: Minimum 3 studies required, preferably 5+ per comparison

**Convergence Problems**
- **Problem**: Statistical model fails to converge
- **Solution**: Check for extreme outliers or data entry errors

#### Interface Problems

**Browser Compatibility**
- **Supported**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Solution**: Update browser or try alternative browser

**Port Conflicts**
- **Problem**: Port 3838 already in use
- **Solution**: Modify port in `run.py` or close conflicting applications

### Error Message Guide

#### Common Error Messages

**"File format not supported"**
- **Cause**: Non-Excel file uploaded
- **Solution**: Convert to .xlsx format

**"Required columns missing"**
- **Cause**: Incorrect column names in data file
- **Solution**: Check column names against template requirements

**"Network not connected"**
- **Cause**: Isolated treatments with no connecting studies
- **Solution**: Review evidence network structure

**"Insufficient data for analysis"**
- **Cause**: Too few studies or participants
- **Solution**: Verify data completeness and consider study inclusion criteria

### Getting Help

#### Support Resources
- **Documentation**: Complete guides in `docs/` folder
- **Templates**: Example files in `data_templates/` folder
- **Issue Tracking**: GitHub repository for bug reports
- **Community**: SmartEBM team contact information

## 10. Technical Architecture

### R Shiny Framework

#### Application Structure
```
app.R                    # Main Shiny application
├── UI Components        # User interface definitions
├── Server Logic         # Backend processing functions
├── Reactive Functions   # Dynamic content updates
└── Output Handlers      # Result generation and display
```

#### Core Dependencies
- **netmeta**: Network meta-analysis statistical engine
- **shiny**: Web application framework
- **DT**: Interactive data table rendering
- **plotly**: Interactive visualization library

### Statistical Engine

#### Network Meta-Analysis Implementation
- **Algorithm**: Frequentist approach using multivariate random-effects model
- **Estimation**: Restricted maximum likelihood (REML)
- **Inference**: Wald-type confidence intervals and hypothesis tests

#### Computational Methods
- **Matrix Operations**: Efficient sparse matrix computations
- **Optimization**: Newton-Raphson and quasi-Newton algorithms
- **Numerical Stability**: Robust handling of near-singular matrices

### Data Processing Pipeline

#### Input Processing
1. **File Upload**: Multi-file Excel processing
2. **Data Validation**: Format and content checking
3. **Network Construction**: Treatment comparison mapping
4. **Quality Assessment**: Data completeness evaluation

#### Analysis Workflow
1. **Model Fitting**: Fixed and random-effects estimation
2. **Inference**: Confidence intervals and hypothesis tests
3. **Diagnostics**: Heterogeneity and consistency assessment
4. **Visualization**: Graph and plot generation
5. **Output Generation**: Structured result files

## 11. Integration Guide

### SmartEBM Ecosystem Integration

#### Upstream Tools
- **Data Extraction Agent**: Provides structured outcome data
- **Risk of Bias Agent**: Supplies study quality assessments
- **Full-Text Screening**: Ensures appropriate study inclusion

#### Downstream Tools
- **GRADE Assessment Agent**: Uses `meta_result_random.csv` output
- **Report Generation**: Incorporates analysis results and visualizations

#### Data Flow Compatibility
- **Input Formats**: Excel files from extraction tools
- **Output Standards**: GRADE-compatible structured data
- **Metadata Preservation**: Study identifiers and quality indicators

### External Tool Integration

#### Statistical Software
- **R Integration**: Direct use of R statistical functions
- **RevMan Compatibility**: Export formats compatible with Cochrane RevMan
- **STATA Integration**: Data formats readable by STATA network commands

#### Reporting Tools
- **LaTeX**: Publication-quality table and figure exports
- **Word Integration**: Copy-paste friendly formatted outputs
- **Web Publishing**: HTML-compatible visualization exports

### API and Automation

#### Programmatic Access
```r
# R script integration example
source("analysis_functions.R")
results <- run_nma_analysis(
  data_files = c("outcome1.xlsx", "outcome2.xlsx"),
  output_dir = "results/",
  model_type = "random"
)
```

#### Batch Processing Scripts
```python
# Python automation example
from nma_automation import NMAAnalyzer

analyzer = NMAAnalyzer()
analyzer.configure(model="random", ci_level=0.95)
analyzer.process_directory("input_data/", "output_results/")
```

## 12. Best Practices

### Study Selection and Data Quality

#### Inclusion Criteria
- **Study Design**: Randomized controlled trials preferred
- **Population**: Homogeneous patient populations
- **Interventions**: Clearly defined treatment protocols
- **Outcomes**: Standardized measurement methods

#### Data Quality Assurance
- **Double Extraction**: Independent data extraction by multiple reviewers
- **Consistency Checks**: Verify treatment names and outcome definitions
- **Missing Data**: Document and handle systematically
- **Risk of Bias**: Systematic assessment using validated tools

### Network Construction

#### Treatment Definitions
- **Specificity**: Clearly distinguish between similar interventions
- **Consistency**: Use identical names across all studies
- **Hierarchy**: Consider dose-response relationships
- **Combinations**: Handle combination therapies appropriately

#### Network Geometry
- **Connectivity**: Ensure all treatments connect through evidence paths
- **Balance**: Avoid networks dominated by single comparisons
- **Transitivity**: Verify assumption of treatment effect consistency
- **Coherence**: Check for logical treatment relationships

### Statistical Analysis

#### Model Selection
- **Fixed vs. Random**: Choose based on heterogeneity assessment
- **Effect Measures**: Select clinically meaningful measures
- **Reference Treatment**: Use clinically relevant comparator
- **Sensitivity Analysis**: Test robustness of findings

#### Interpretation Guidelines
- **Clinical Significance**: Consider minimal important differences
- **Statistical Significance**: Interpret p-values appropriately
- **Confidence Intervals**: Focus on precision and clinical relevance
- **Ranking Probabilities**: Use cautiously for decision-making

### Reporting Standards

#### PRISMA-NMA Guidelines
- **Flow Diagram**: Document study selection process
- **Network Diagram**: Present evidence structure clearly
- **Results Tables**: Include all relevant statistical measures
- **Assessment of Bias**: Report publication bias and inconsistency

#### Transparency and Reproducibility
- **Protocol Registration**: Pre-specify analysis methods
- **Data Sharing**: Provide analysis datasets when possible
- **Code Availability**: Share analysis scripts and parameters
- **Version Control**: Document software versions and updates

### Quality Assurance

#### Validation Steps
1. **Data Verification**: Cross-check extracted data with source studies
2. **Analysis Replication**: Verify results using alternative software
3. **Expert Review**: Clinical expert evaluation of findings
4. **Sensitivity Analysis**: Test robustness to methodological choices

#### Documentation Requirements
- **Analysis Plan**: Pre-specified statistical analysis protocol
- **Data Dictionary**: Variable definitions and coding schemes
- **Method Documentation**: Detailed analysis procedure description
- **Result Interpretation**: Clinical context and limitations discussion

## Citation

This tool is a direct output of the research conducted by the SmartEBM team. If you use it in your academic work, we kindly ask that you cite our manuscript, which details the design and validation of the broader framework this module is part of:

> Lai H, Liu J, Ma N, et al. Design and Validation of SmartNMA: A Comprehensive Large Language Model-Assisted Framework for Network Meta-Analysis. (Manuscript in preparation).