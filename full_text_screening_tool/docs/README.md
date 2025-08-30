# SmartEBM Full-Text Screening Tool - Complete Documentation

An AI-powered full-text screening tool achieving 99.9% specificity across 3,292 full-text records, featuring intelligent prompt generation, keyword-based pre-screening, and seamless integration with systematic review workflows.

## Table of Contents

- [Research-Validated Performance](#research-validated-performance)
- [Key Advantages](#key-advantages)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Usage Workflows](#usage-workflows)
- [PICOS Extraction Workflow](#picos-extraction-workflow)
- [AI-Powered Screening Decisions](#ai-powered-screening-decisions)
- [Advanced Features](#advanced-features)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Technical Architecture](#technical-architecture)
- [Integration with SmartEBM Tools](#integration-with-smartebm-tools)
- [Best Practices](#best-practices)

## Research-Validated Performance

**SmartNMA Framework Validation**: This tool achieved **99.9% specificity** across **3,292 full-text records** in comprehensive validation studies, demonstrating exceptional accuracy in systematic review workflows.

**Key Performance Metrics**:
- **Specificity**: 99.9% (minimal false positives)
- **Validation Scope**: 3,292 full-text research papers
- **Processing Efficiency**: Intelligent keyword-based pre-screening reduces processing time
- **Decision Transparency**: Complete audit trail with detailed reasoning for each screening decision

## Key Advantages

### Intelligent Prompt Generation
Advanced AI-powered system that automatically generates screening prompts tailored to your specific research criteria, adapting to study characteristics and research domains for optimal accuracy.

### Keyword-Based Pre-Screening
Smart filtering mechanism that identifies potentially relevant studies before full AI analysis, significantly reducing processing time while maintaining the validated 99.9% specificity.

### Transparent Documentation
Complete audit trail of all screening decisions with detailed reasoning, supporting reproducible systematic reviews and meeting regulatory compliance requirements for evidence-based medicine.

### PICOS Framework Integration
Structured extraction and evaluation based on Population, Intervention, Comparison, Outcomes, and Study design criteria, ensuring comprehensive and systematic assessment of each full-text article.

### Systematic Review Workflow Integration
Seamlessly connects with other SmartEBM tools and standard systematic review platforms, supporting end-to-end automation from literature search to meta-analysis.

## Core Features

### AI-Powered Full-Text Analysis
- **Multi-Model LLM Support**: Configure multiple language models for consensus-based screening decisions
- **Adaptive Screening Logic**: Intelligent prompt generation that adapts to your specific research criteria
- **Confidence Scoring**: Built-in confidence assessment for screening decisions
- **Quality Assurance**: Automated validation and error detection mechanisms

### Advanced PDF Processing
- **Multi-Format Support**: Handles various PDF formats including scanned documents
- **OCR Integration**: Automatic text extraction with OCR fallback for image-based PDFs
- **Table Recognition**: Optional extraction and analysis of tabular data
- **Page Limiting**: Configurable maximum pages per document for efficiency

### Parallel Processing Architecture
- **Scalable Processing**: Multi-threaded screening for large document collections
- **Resource Management**: Intelligent CPU and memory utilization
- **Fault Tolerance**: Automatic retry and recovery mechanisms
- **Progress Monitoring**: Real-time tracking with estimated completion times

## System Requirements

### Minimum Requirements
- **Python**: 3.8+ (Python 3.10+ recommended for optimal performance)
- **Memory**: 8GB RAM (16GB+ recommended for large document collections)
- **CPU**: 4+ cores (8+ cores recommended for parallel processing)
- **Storage**: 2GB+ available space for temporary files and outputs
- **Network**: Stable internet connection for LLM API access

### API Requirements
- **LLM Services**: OpenAI, Anthropic, or compatible API providers
- **API Keys**: Valid API keys with sufficient quota for your document volume
- **Rate Limits**: Configurable based on your provider's limits
- **Cost Management**: Budget tracking and monitoring capabilities

### Supported Formats
- **Input**: PDF documents (text-based and scanned with OCR)
- **Output**: Excel (.xlsx), CSV, and structured JSON formats
- **Configuration**: JSON-based configuration files

## Installation Guide

### Step 1: Environment Setup

1. **Ensure Python 3.8+ is installed**
   ```bash
   python --version  # Should show 3.8 or higher
   ```

2. **Clone or download the tool**
   ```bash
   git clone <repository-url>
   cd full_text_screening_tool
   ```

3. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies**:
- `openai`: LLM API integration
- `pandas`: Data processing and analysis
- `openpyxl`: Excel file handling
- `PyMuPDF`: PDF text extraction
- `concurrent.futures`: Parallel processing support

### Step 3: Initial Configuration

1. **Create configuration file**
   ```bash
   cp config/config_template.json config/config.json
   ```

2. **Set up directory structure**
   ```bash
   mkdir -p input output prompts
   ```

3. **Verify installation**
   ```bash
   python main.py --help
   ```

## Configuration

### Basic Configuration Setup

Edit `config/config.json` with your specific settings:

```json
{
  "paths": {
    "input_folder_path": "input/pdfs",
    "output_excel_path": "output/screening_results.xlsx",
    "prompt_file_path": "prompts/screening_prompt.txt",
    "positive_prompt_file_path": "prompts/positive_prompt.txt",
    "negative_prompt_file_path": "prompts/negative_prompt.txt"
  },
  "llm_configs": {
    "prompt_llm": {
      "api_key": "your-api-key-here",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4"
    },
    "screening_llms": {
      "Primary_LLM": {
        "api_key": "your-api-key-here",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4-turbo"
      },
      "Secondary_LLM": {
        "api_key": "your-backup-key",
        "base_url": "https://api.anthropic.com/v1",
        "model": "claude-3-sonnet"
      }
    }
  },
  "inclusion_criteria": {
    "Study design": "Randomized controlled trials, clinical trials",
    "Participants": "Adult patients with cardiovascular disease",
    "Intervention": "Statin therapy or lipid-lowering interventions",
    "Comparison": "Placebo, standard care, or other lipid-lowering drugs",
    "Outcomes": "Cardiovascular events, mortality, lipid levels"
  },
  "exclusion_criteria": {
    "Study design": "Case reports, editorials, reviews without original data",
    "Participants": "Pediatric populations, animal studies",
    "Language": "Non-English publications"
  }
}
```

### Advanced Configuration Options

#### Parallel Processing Settings
```json
{
  "mode": {
    "screening_mode": "parallel",
    "enable_cost_analysis": true,
    "enable_progress_monitoring": true
  },
  "parallel_settings": {
    "parallel_screeners": 4,
    "auto_distribute": true,
    "retry_failed_batches": true,
    "max_retries": 3,
    "batch_size": 10
  },
  "resource_management": {
    "max_memory_usage": "8GB",
    "api_calls_per_minute": 60,
    "delay_between_screeners": 2
  }
}
```

#### PDF Processing Configuration
```json
{
  "pdf_processing": {
    "max_pages_per_document": 50,
    "enable_ocr": true,
    "extract_tables": false,
    "text_cleaning": true,
    "language_detection": true
  }
}
```

## Usage Workflows

### Method 1: Interactive Mode (Recommended)

```bash
python main.py
```

**Interactive Features**:
- Language selection (English/Chinese)
- Configuration validation
- Real-time progress monitoring
- Error handling and recovery options
- Cost estimation and tracking

### Method 2: Command Line Interface

```bash
# Start new screening with specific config
python main.py --config config/config.json --lang en

# Resume interrupted screening
python main.py --resume --state-file output/screening_state.json

# Monitor running process
python main.py --monitor --pid 12345

# Clean temporary files
python main.py --cleanup --temp-dir temp_screening
```

### Method 3: Batch Processing Mode

```bash
# Process specific file range
python main.py --start-from 1 --max-files 100

# Process with custom output location
python main.py --output-dir results/batch_001

# Enable debug mode for troubleshooting
python main.py --debug --verbose
```

## PICOS Extraction Workflow

The tool implements a comprehensive two-stage process for full-text screening:

### Stage 1: Structured PICOS Extraction

**Population (P)**: Extracts detailed participant characteristics including:
- Demographics (age, gender, ethnicity)
- Medical conditions and severity
- Inclusion/exclusion criteria used in the study
- Sample size and recruitment settings
- Baseline characteristics and comorbidities

**Intervention (I)**: Captures comprehensive intervention details:
- Specific treatment protocols and dosages
- Duration and frequency of interventions
- Administration methods and delivery settings
- Co-interventions and combination therapies
- Intervention fidelity and adherence measures

**Comparison (C)**: Documents control and comparison groups:
- Placebo characteristics and blinding methods
- Active comparator details and dosing
- Standard care protocols and guidelines
- No-treatment or waitlist control descriptions
- Historical or external control specifications

**Outcomes (O)**: Identifies all measured endpoints:
- Primary outcomes and measurement methods
- Secondary outcomes and exploratory endpoints
- Safety outcomes and adverse events
- Time points and follow-up duration
- Outcome assessment tools and validation

**Study Design (S)**: Determines precise study methodology:
- Randomization methods and allocation concealment
- Blinding procedures (single, double, triple)
- Parallel group vs. crossover designs
- Multicenter vs. single-center studies
- Adaptive designs and interim analyses

### Stage 2: Inclusion Assessment

**Systematic Evaluation**: Each PICOS element is systematically evaluated against your predefined inclusion and exclusion criteria using the complete full-text information.

**Decision Framework**:
- **INCLUDE**: Study meets ALL inclusion criteria and NO exclusion criteria
- **EXCLUDE**: Study fails ANY inclusion criterion OR meets ANY exclusion criterion  
- **UNCLEAR**: Insufficient information (rare in full-text screening)

**Reasoning Documentation**: Each decision includes a detailed explanation citing specific criteria that were met or not met, supporting audit trails and reproducibility.

## AI-Powered Screening Decisions

### Intelligent Prompt Generation

The system automatically generates tailored screening prompts based on your research criteria:

1. **Criteria Analysis**: Analyzes your inclusion/exclusion criteria to understand research focus
2. **Domain Adaptation**: Adapts language and examples to your specific medical/research domain
3. **Prompt Optimization**: Creates prompts optimized for accuracy and consistency
4. **Validation Integration**: Incorporates lessons learned from 99.9% specificity validation

### Multi-Model Consensus Screening

**Dual-Prompt Validation**: Uses subtly different prompt variants to test decision consistency:
- **Comprehensive Evaluation Prompt**: Emphasizes thorough systematic assessment
- **Precision-Focused Prompt**: Emphasizes exact requirement verification
- **Consensus Analysis**: Compares results to identify potential edge cases

**Multi-LLM Support**: Configure multiple language models for enhanced reliability:
- **Primary Screening**: Uses your preferred high-accuracy model
- **Validation Screening**: Secondary model for consensus verification
- **Conflict Resolution**: Automated handling of disagreements between models

### Keyword-Based Pre-Screening

**Intelligent Filtering**: Before full AI analysis, the system:
1. **Extracts Key Terms**: Identifies domain-specific terminology from your criteria
2. **Content Scanning**: Rapidly scans full-text for relevant keywords and concepts
3. **Relevance Scoring**: Assigns preliminary relevance scores based on keyword density
4. **Efficient Processing**: Prioritizes likely-relevant documents for detailed AI analysis

**Performance Benefits**:
- Reduces processing time by 40-60% while maintaining 99.9% specificity
- Identifies obviously irrelevant studies without expensive LLM calls
- Maintains complete audit trail of pre-screening decisions

## 📊 Features in Detail

### Parallel Processing
- **Intelligent Distribution**: Automatically distributes PDF documents across multiple workers
- **Load Balancing**: Optimizes processing based on document size and complexity
- **Fault Tolerance**: Automatic retry of failed processing with error recovery
- **Resource Management**: Monitors memory usage and API rate limits

### PDF Processing
- **Multi-format Support**: Handles various PDF formats and structures
- **Text Extraction**: Uses PyMuPDF with OCR fallback for scanned documents
- **Table Extraction**: Optionally extracts and processes table content
- **Page Limiting**: Configurable maximum pages per document

### Cost Analysis
- **Real-time Tracking**: Monitors API costs during processing
- **Detailed Reports**: Generates comprehensive cost breakdowns
- **Multi-currency**: Supports USD and CNY with automatic conversion
- **Budget Alerts**: Optional cost thresholds and warnings

### Progress Monitoring
- **Real-time Updates**: Live progress indicators and statistics
- **Time Estimation**: Calculates remaining processing time
- **Performance Metrics**: Processing speed and efficiency tracking
- **Visual Dashboard**: Optional GUI for monitoring (if available)

## 📈 Performance Optimization

### Recommended Settings
- **CPU Cores**: Use 50-75% of available CPU cores for parallel workers
- **Memory**: Allocate 2GB+ per worker for optimal performance
- **API Limits**: Configure based on your provider's rate limits
- **Batch Size**: Adjust based on document size and complexity

### Best Practices
1. **Document Preparation**: Ensure PDFs are text-searchable when possible
2. **Screening Criteria**: Be specific and detailed in PICOS criteria
3. **Model Selection**: Use appropriate models for prompt generation vs. screening
4. **Resource Monitoring**: Monitor system resources during large batch processing

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

#### 2. PDF Processing Errors
- Ensure PDFs are not corrupted or password-protected
- Check file permissions and accessibility
- Verify PDF format compatibility

#### 3. API Rate Limits
- Adjust `api_calls_per_minute_limit` in configuration
- Increase delays between API calls
- Consider using multiple API keys

#### 4. Memory Issues
- Reduce `parallel_screeners` count
- Decrease `max_pages_per_document`
- Enable text cleaning and optimization

### Log Files
- Check output directory for detailed error logs
- Enable debug mode for verbose logging
- Review cost analysis reports for API usage patterns

## 📚 Advanced Usage

### Custom Screening Prompts
Create custom screening prompts for specialized domains:
1. Create prompt files for your specific criteria
2. Include positive and negative examples
3. Test with small document sets first
4. Iterate based on screening accuracy

### Multi-Model Consensus
Configure multiple LLMs for consensus-based decisions:
1. Add multiple models in `screening_llms`
2. System will compare outputs
3. Consensus improves accuracy
4. Useful for critical systematic reviews

### Integration with Other Tools
- Export results to reference managers (EndNote, Zotero)
- Import from literature databases
- Connect with systematic review platforms
- Integrate with statistical analysis tools

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for more information.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `docs/` folder
- Review configuration examples
- Contact the development team

## 🔄 Updates

This tool is actively maintained and updated. Check for:
- New LLM model support
- Performance improvements
- Bug fixes and security updates
- Feature enhancements

---

**Note**: This tool requires valid API keys for LLM services. Ensure you have appropriate access and understand the associated costs before large-scale usage.
## Adv
anced Features

### Parallel Processing Architecture

**Intelligent Resource Management**:
- **CPU Utilization**: Automatically detects available cores and optimizes worker allocation
- **Memory Management**: Monitors RAM usage and adjusts batch sizes dynamically
- **API Rate Limiting**: Respects provider limits with intelligent request spacing
- **Load Balancing**: Distributes documents based on size and complexity

**Fault Tolerance**:
- **Checkpoint Recovery**: Automatic saving of progress with resume capability
- **Error Handling**: Graceful handling of API failures, network issues, and corrupted files
- **Retry Logic**: Configurable retry attempts with exponential backoff
- **State Management**: Persistent state tracking for long-running processes

### Cost Analysis and Optimization

**Real-Time Cost Tracking**:
- **Token Usage Monitoring**: Tracks prompt and completion tokens for each document
- **Multi-Currency Support**: Displays costs in USD, EUR, GBP, CNY, and JPY
- **Budget Alerts**: Configurable spending thresholds with automatic notifications
- **Cost Optimization**: Recommendations for model selection and batch sizing

**Detailed Reporting**:
- **Per-Document Costs**: Individual cost breakdown for each screened article
- **Model Comparison**: Cost and performance analysis across different LLMs
- **Efficiency Metrics**: Processing speed and cost-per-document analytics
- **Export Options**: CSV and Excel reports for financial tracking

### Quality Assurance Framework

**Validation Mechanisms**:
- **Response Format Validation**: Ensures all outputs follow required PICOS structure
- **Consistency Checking**: Identifies potential inconsistencies in screening decisions
- **Confidence Scoring**: Built-in assessment of decision reliability
- **Manual Review Integration**: Flags uncertain cases for human review

**Audit Trail**:
- **Complete Documentation**: Full record of all screening decisions and reasoning
- **Timestamp Tracking**: Precise timing information for each processing step
- **Version Control**: Tracks prompt versions and configuration changes
- **Reproducibility**: Complete information needed to reproduce results

## Performance Optimization

### Recommended System Configuration

**For Small Collections (< 100 documents)**:
- **CPU**: 4 cores minimum
- **RAM**: 8GB minimum
- **Parallel Workers**: 2-3 workers
- **Expected Processing**: 10-20 documents per hour

**For Medium Collections (100-1000 documents)**:
- **CPU**: 8+ cores recommended
- **RAM**: 16GB recommended  
- **Parallel Workers**: 4-6 workers
- **Expected Processing**: 30-50 documents per hour

**For Large Collections (1000+ documents)**:
- **CPU**: 12+ cores optimal
- **RAM**: 32GB optimal
- **Parallel Workers**: 6-8 workers
- **Expected Processing**: 50-80 documents per hour

### LLM Model Selection Guide

**For Maximum Accuracy**:
- **Primary**: GPT-4 or Claude-3-Opus for complex screening criteria
- **Secondary**: GPT-4-Turbo for validation and consensus
- **Cost**: Higher per document, but maximum reliability

**For Balanced Performance**:
- **Primary**: GPT-4-Turbo or Claude-3-Sonnet for most screening tasks
- **Secondary**: GPT-3.5-Turbo for validation
- **Cost**: Moderate cost with excellent accuracy

**For High-Volume Processing**:
- **Primary**: GPT-3.5-Turbo or Claude-3-Haiku for straightforward criteria
- **Secondary**: Same model for consistency
- **Cost**: Lower cost per document, suitable for clear-cut criteria

## Troubleshooting

### Common Issues and Solutions

#### Installation Problems

**Import Errors**:
```bash
# Solution: Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

**Permission Errors**:
```bash
# Solution: Check file permissions
chmod +x main.py
chmod -R 755 input output
```

#### Configuration Issues

**API Key Problems**:
- Verify API keys are valid and have sufficient quota
- Check base URLs match your provider's endpoints
- Ensure models specified are available in your account

**Path Configuration**:
- Use absolute paths for input and output directories
- Ensure all specified directories exist and are writable
- Check file permissions for configuration files

#### Processing Errors

**PDF Reading Failures**:
- Verify PDFs are not password-protected or corrupted
- Enable OCR for scanned documents in configuration
- Check available disk space for temporary files

**Memory Issues**:
- Reduce parallel worker count in configuration
- Decrease batch size for large documents
- Enable text cleaning to reduce memory usage

**API Rate Limiting**:
- Increase delays between API calls in configuration
- Reduce parallel worker count
- Consider using multiple API keys for higher throughput

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
python main.py --debug --verbose --log-file debug.log
```

**Debug Features**:
- **Detailed Logging**: Complete trace of all operations
- **API Request/Response**: Full LLM interaction logs
- **Performance Metrics**: Timing and resource usage statistics
- **Error Stack Traces**: Complete error information for diagnosis

## Technical Architecture

### Core Components

**Main Entry Point (`main.py`)**:
- Command-line interface and argument parsing
- Configuration loading and validation
- Process orchestration and error handling
- Interactive mode and user interface

**Full-Text Extractor (`src/fulltext_extractor.py`)**:
- PICOS extraction and screening logic
- LLM client management and API interactions
- Prompt generation and optimization
- Response parsing and validation

**Document Reader (`src/document_reader.py`)**:
- PDF text extraction with multiple fallback methods
- OCR integration for scanned documents
- Text preprocessing and cleaning
- Metadata extraction and validation

**Parallel Controller (`core/parallel_controller.py`)**:
- Multi-threaded processing coordination
- Resource management and load balancing
- Error handling and recovery mechanisms
- Progress monitoring and reporting

### Data Flow Architecture

```
Input PDFs → Document Reader → Text Extraction → PICOS Analysis → Screening Decision → Results Export
     ↓              ↓              ↓              ↓              ↓              ↓
File Validation → OCR Processing → Preprocessing → LLM Processing → Validation → Excel/CSV Output
     ↓              ↓              ↓              ↓              ↓              ↓
Error Handling → Retry Logic → Quality Check → Consensus Check → Audit Trail → Cost Analysis
```

### Integration Points

**Input Interfaces**:
- PDF document collections
- Configuration files (JSON)
- Custom screening criteria
- API credentials and settings

**Output Interfaces**:
- Structured Excel reports with PICOS data
- CSV files for statistical analysis
- JSON exports for programmatic access
- Cost analysis reports

**External Dependencies**:
- OpenAI API or compatible LLM services
- PyMuPDF for PDF processing
- Pandas for data manipulation
- OpenPyXL for Excel file generation

## Integration with SmartEBM Tools

### Upstream Integration

**From Literature Search Tools**:
- **Input Format**: PDF collections from database searches
- **Metadata Preservation**: Study identifiers and search terms
- **Quality Indicators**: Initial relevance scores and source databases

**From Title/Abstract Screening**:
- **Filtered Collections**: Pre-screened document sets
- **Screening History**: Previous screening decisions and confidence scores
- **Inclusion Rationale**: Reasons for advancement to full-text screening

### Downstream Integration

**To Data Extraction Tools**:
- **Included Studies**: Filtered collection of relevant full-text articles
- **PICOS Data**: Structured study characteristics for extraction templates
- **Quality Metadata**: Screening confidence and decision rationale

**To Risk of Bias Assessment**:
- **Study Design Information**: Detailed methodology extracted during screening
- **Quality Indicators**: Initial assessment of study quality and reporting
- **Bias Risk Flags**: Potential bias sources identified during screening

**To Statistical Analysis Tools**:
- **Study Characteristics**: Population and intervention details for subgroup analysis
- **Outcome Information**: Endpoint data for meta-analysis planning
- **Inclusion Criteria**: Systematic documentation for PRISMA reporting

### Workflow Integration Examples

**Complete Systematic Review Pipeline**:
1. **Literature Search** → Database search results (PDFs)
2. **Title/Abstract Screening** → Potentially relevant studies
3. **Full-Text Screening** (This Tool) → Included studies with PICOS data
4. **Data Extraction** → Quantitative data for analysis
5. **Risk of Bias Assessment** → Quality assessment
6. **Statistical Analysis** → Meta-analysis results
7. **GRADE Assessment** → Evidence quality rating

**Quality Assurance Workflow**:
- **Dual Screening**: Independent screening by multiple reviewers
- **Consensus Resolution**: Automated conflict identification and resolution
- **Audit Trail**: Complete documentation for regulatory compliance
- **Reproducibility**: Version-controlled configurations and results

## Best Practices

### Screening Criteria Development

**Specificity Guidelines**:
- Define clear, measurable inclusion criteria for each PICOS element
- Use specific terminology rather than broad categories
- Include examples of borderline cases and how to handle them
- Test criteria with a small sample before full screening

**Exclusion Criteria**:
- Be explicit about what constitutes exclusion
- Consider hierarchical exclusion (primary vs. secondary reasons)
- Document rationale for each exclusion criterion
- Balance specificity with practical screening efficiency

### Quality Control Procedures

**Pre-Screening Validation**:
- Test configuration with 10-20 representative documents
- Validate prompt generation with domain experts
- Check output format and completeness
- Verify cost estimates and processing times

**During Screening**:
- Monitor progress and error rates regularly
- Review uncertain decisions and edge cases
- Track cost accumulation against budget
- Maintain backup configurations and checkpoints

**Post-Screening Review**:
- Conduct sample validation of screening decisions
- Review excluded studies for potential false negatives
- Analyze cost and efficiency metrics
- Document lessons learned for future screenings

### Performance Optimization

**Configuration Tuning**:
- Start with conservative parallel settings and increase gradually
- Monitor system resources during processing
- Adjust batch sizes based on document complexity
- Use appropriate models for your accuracy requirements

**Cost Management**:
- Set realistic budgets based on document volume
- Use cost estimation features before full processing
- Consider model selection based on screening complexity
- Monitor spending in real-time during processing

**Error Prevention**:
- Validate all file paths and permissions before starting
- Test API connectivity and rate limits
- Ensure sufficient disk space for temporary files
- Create backup configurations for critical screenings

---

## Support and Maintenance

### Getting Help

**Documentation Resources**:
- Complete configuration examples in `config/` directory
- Sample screening criteria for common research domains
- Troubleshooting guides for common issues
- Performance optimization recommendations

**Community Support**:
- GitHub issues for bug reports and feature requests
- Discussion forums for methodology questions
- Example configurations and use cases
- Best practices sharing and collaboration

### Updates and Maintenance

**Regular Updates**:
- New LLM model support and optimization
- Performance improvements and bug fixes
- Enhanced integration with other SmartEBM tools
- Security updates and dependency management

**Version Compatibility**:
- Backward compatibility for configuration files
- Migration guides for major version updates
- Deprecation notices for obsolete features
- Testing procedures for new installations

---

**Note**: This tool requires valid API keys for LLM services and may incur costs based on usage. Always test with small document sets first and monitor costs during large-scale processing. The 99.9% specificity validation was achieved under controlled research conditions; actual performance may vary based on your specific criteria and document characteristics.