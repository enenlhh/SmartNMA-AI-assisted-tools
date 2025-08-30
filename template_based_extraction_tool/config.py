"""
Configuration file for Template-Based Extraction Tool
Modify these settings according to your needs
"""

import os

# Default configuration
DEFAULT_CONFIG = {
    "paths": {
        "pdf_folder": "./input",              # Input PDF folder path
        "template_xlsx": "./template.xlsx",   # Template Excel file path
        "output_xlsx": "./output/results.xlsx"  # Output Excel file path
    },
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
        "temperature": 0.0,
        "max_tokens": 6000,
        "timeout": 120,
        "max_retries": 5
    },
    "runtime": {
        "chunk_field_size": 20,        # Maximum fields per batch
        "max_chars_per_doc": 30000,    # Text truncation to avoid excessive length
        "debug_dir": "./debug_tables", # Save original output and repair text
        "use_repair_call": True        # Whether to make repair call on parsing failure
    }
}

def get_config():
    """Get configuration with environment variable overrides"""
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables if available
    if os.getenv("PDF_FOLDER"):
        config["paths"]["pdf_folder"] = os.getenv("PDF_FOLDER")
    if os.getenv("TEMPLATE_XLSX"):
        config["paths"]["template_xlsx"] = os.getenv("TEMPLATE_XLSX")
    if os.getenv("OUTPUT_XLSX"):
        config["paths"]["output_xlsx"] = os.getenv("OUTPUT_XLSX")
    
    return config