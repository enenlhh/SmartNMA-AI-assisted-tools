#!/usr/bin/env python3
"""
Example usage of Template-Based Extraction Tool
This script demonstrates how to use the tool with custom configuration
"""

import os
from main import TemplateExtractor

def example_usage():
    """Example of how to use the extraction tool"""
    
    # Custom configuration
    custom_config = {
        "paths": {
            "pdf_folder": "./input",
            "template_xlsx": "./template.xlsx",
            "output_xlsx": "./output/my_results.xlsx"
        },
        "llm": {
            "api_key": os.getenv("OPENAI_API_KEY", "your-api-key-here"),
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4-turbo",
            "temperature": 0.1,
            "max_tokens": 4000
        },
        "runtime": {
            "chunk_field_size": 15,        # Process fewer fields per batch
            "max_chars_per_doc": 25000,    # Shorter document limit
            "debug_dir": "./my_debug",     # Custom debug directory
            "use_repair_call": True
        }
    }
    
    # Create and run extractor
    extractor = TemplateExtractor(custom_config)
    extractor.run_extraction()

if __name__ == "__main__":
    example_usage()