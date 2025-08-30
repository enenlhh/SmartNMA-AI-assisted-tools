"""
Utility functions for the systematic review screening tool
"""

import json
import os

def load_config(config_path):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单清理：只移除BOM
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # 直接解析JSON，不做过多处理
        config = json.loads(content)
        return config
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error:")
        print(f"Line {e.lineno}, Column {e.colno}")
        print(f"Error: {e.msg}")
        
        # 显示原始文件的问题行
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if e.lineno <= len(lines):
                problem_line = lines[e.lineno-1].rstrip()
                print(f"Problematic line: {repr(problem_line)}")
                
                # 显示字符的十六进制表示
                if e.colno <= len(problem_line):
                    char_at_pos = problem_line[e.colno-1] if e.colno > 0 else ''
                    print(f"Character at position {e.colno}: {repr(char_at_pos)} (hex: {char_at_pos.encode('utf-8').hex() if char_at_pos else 'N/A'})")
        except Exception as debug_e:
            print(f"Debug error: {debug_e}")
        
        raise ValueError(f"JSON parsing error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error loading configuration file: {str(e)}")

def validate_config(config):
    """Validate configuration structure"""
    required_sections = ['paths', 'llm_configs', 'inclusion_criteria']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate paths
    required_paths = ['input_xml_path', 'output_xml_path']
    for path_key in required_paths:
        if path_key not in config['paths']:
            raise ValueError(f"Missing required path: {path_key}")
    
    # Validate LLM configs
    if 'screening_llms' not in config['llm_configs']:
        raise ValueError("Missing screening_llms configuration")
    
    if len(config['llm_configs']['screening_llms']) < 1:
        raise ValueError("At least one screening LLM must be configured")
    
    return True

def create_output_directory(output_path):
    """Create output directory if it doesn't exist"""
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

def check_file_exists(file_path, file_description):
    """Check if file exists and provide helpful error message"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_description} not found: {file_path}")
    return True
