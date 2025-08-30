"""
Full Text Screening Tool
Main execution script for full-text screening with internationalization support

Usage: python run_fulltext.py
"""

import os
import sys
import traceback
import glob

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'i18n'))

from src.fulltext_extractor import FullTextExtractor
from src.utils import load_config, validate_config, create_output_directory
from i18n.i18n_manager import get_language_manager, get_message, select_language

def main():
    """主执行函数 / Main execution function for full-text screening"""
    try:
        # 选择语言 / Select language
        selected_lang = select_language()
        
        print("=" * 60)
        print(get_message("system_title"))
        print("=" * 60)
        print(get_message("config_loading"))
        
        # Load configuration
        config_path = "config/config.json"
        if not os.path.exists(config_path):
            print(get_message("system_error", error=f"Configuration file not found: {config_path}"))
            print("Please ensure the config/config.json file exists with your settings.")
            return
        
        config = load_config(config_path)
        validate_fulltext_config(config)
        print(get_message("config_loaded"))
        
        # Extract configuration values
        paths = config['paths']
        processing = config.get('processing', {})
        llm_configs = config['llm_configs']
        inclusion_criteria = config['inclusion_criteria']
        exclusion_criteria = config.get('exclusion_criteria', {})
        
        # Validate input folder
        input_folder_path = paths['input_folder_path']
        if not os.path.exists(input_folder_path):
            raise FileNotFoundError(get_message("system_error", error=f"Input folder not found: {input_folder_path}"))
        
        # Check PDF files and display count
        pdf_files = glob.glob(os.path.join(input_folder_path, "*.pdf"))
        print(get_message("analyzing_input", filename=input_folder_path))
        print(get_message("detected_documents", count=len(pdf_files)))
        
        if len(pdf_files) == 0:
            print(get_message("system_error", error="No PDF files found in input folder"))
            return 1
        
        # Create output directory
        output_excel_path = paths['output_excel_path']
        create_output_directory(output_excel_path)
        
        # Initialize extractor
        print(get_message("starting_system"))
        extractor = FullTextExtractor(
            screening_llm_configs=llm_configs['screening_llms'],
            prompt_llm_config=llm_configs.get('prompt_llm'),
            positive_prompt_path=paths.get('positive_prompt_file_path'),
            negative_prompt_path=paths.get('negative_prompt_file_path'),
            config=config  # 传递完整配置
        )
        
        # Process documents
        print(get_message("processing_documents"))
        result_path = extractor.process_documents(
            folder_path=input_folder_path,
            inclusion_criteria=inclusion_criteria,
            output_path=output_excel_path,
            exclusion_criteria=exclusion_criteria,
            prompt_file_path=paths.get('prompt_file_path')
        )
        
        print("\n" + "=" * 60)
        print(get_message("task_completed"))
        print(get_message("results_saved", path=result_path))
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n" + get_message("task_interrupted"))
        print("Partial results may have been saved.")
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        traceback.print_exc()
        return 1
    
    return 0

def validate_fulltext_config(config):
    """验证全文配置结构 / Validate full-text configuration structure"""
    required_sections = ['paths', 'llm_configs', 'inclusion_criteria']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate paths for full-text screening
    required_paths = ['input_folder_path', 'output_excel_path']
    for path_key in required_paths:
        if path_key not in config['paths']:
            raise ValueError(f"Missing required path: {path_key}")
    
    # Validate LLM configs
    if 'screening_llms' not in config['llm_configs']:
        raise ValueError("Missing screening_llms configuration")
    
    if len(config['llm_configs']['screening_llms']) < 1:
        raise ValueError("At least one screening LLM must be configured")
    
    return True

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
