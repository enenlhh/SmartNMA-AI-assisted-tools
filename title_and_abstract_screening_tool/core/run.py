"""
Systematic Review Screening Tool
Main execution script

Usage: python run.py
"""

import os
import sys
import traceback

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.extractor import SystematicReviewExtractor
from src.utils import load_config, validate_config, create_output_directory, check_file_exists

def main():
    """Main execution function"""
    try:
        print("=== Systematic Review Screening Tool ===")
        print("Loading configuration...")
        
        # Try to load configuration (support both .json and .js)
        config_path = None
        
        # 首先检查环境变量
        env_config = os.environ.get('CONFIG_PATH')
        if env_config and os.path.exists(env_config):
            config_path = env_config
        elif os.path.exists("config.json"):
            config_path = "config.json"
        elif os.path.exists("config.js"):
            config_path = "config.js"
        else:
            print("Error: Configuration file not found.")
            print("Please create either 'config.json' or 'config.js' file with your settings.")
            print("Recommended: Use 'config.json' for better compatibility.")
            return
        
        config = load_config(config_path)
        validate_config(config)
        print(f"✓ Configuration loaded successfully from {config_path}")
        
        # Extract configuration values
        paths = config['paths']
        processing = config.get('processing', {})
        
        # Handle different configuration formats for backward compatibility
        if 'study_designs' in config:
            # New format with study_designs section
            excluded_designs = config['study_designs'].get('excluded_study_designs', [])
            included_designs = config['study_designs'].get('included_study_designs', [])
        else:
            # Legacy format with top-level keys
            excluded_designs = config.get('excluded_study_designs', [])
            included_designs = config.get('included_study_designs', [])
        
        llm_configs = config['llm_configs']
        inclusion_criteria = config['inclusion_criteria']
        exclusion_criteria = config.get('exclusion_criteria', {})
        
        # Validate input file
        input_xml_path = paths['input_xml_path']
        check_file_exists(input_xml_path, "Input XML file")
        
        # Create output directory
        output_xml_path = paths['output_xml_path']
        create_output_directory(output_xml_path)
        
        # Initialize extractor
        print("Initializing XML extractor...")
        extractor = SystematicReviewExtractor(
            screening_llm_configs=llm_configs['screening_llms'],
            prompt_llm_config=llm_configs.get('prompt_llm'),
            positive_prompt_path=paths.get('positive_prompt_file_path'),
            negative_prompt_path=paths.get('negative_prompt_file_path')
        )
        
        # Parse XML file (automatic format detection)
        print(f"Parsing XML file: {input_xml_path}")
        parsed_records, tree, root = extractor.parse_xml(input_xml_path)
        
        # Display detection results
        print(f"Successfully parsed {len(parsed_records)} records")
        
        # Handle record skipping if configured
        skip_records_count = processing.get('skip_records_count', 0)
        if skip_records_count > 0:
            print(f"Will skip first {skip_records_count} records, starting from record {skip_records_count+1}...")
            records_to_process = parsed_records[skip_records_count:]
        else:
            records_to_process = parsed_records
        
        # Set excluded study designs
        extractor.set_excluded_study_designs(excluded_designs)
        extractor.set_included_study_designs(included_designs)
        
        # Process records
        print("Starting record processing...")
        extractor.process_records(
            records_to_process, 
            inclusion_criteria, 
            output_xml_path, 
            tree,
            exclusion_criteria=exclusion_criteria,
            prompt_file_path=paths.get('prompt_file_path')
        )
        
        print("\n=== Processing Complete ===")
        print(f"Results saved to: {output_xml_path}")
        print(f"Excel results saved to: {output_xml_path.replace('.xml', '_results.xlsx')}")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        print("Partial results may have been saved.")
    except Exception as e:
        print(f"\nError occurred during execution: {str(e)}")
        print(f"Error details:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
