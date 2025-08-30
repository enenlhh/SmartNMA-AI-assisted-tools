#!/usr/bin/env python3
"""
单线程全文筛选工具
SmartEBM Full-Text Screening Tool - Single Thread Mode

用法:
    python run.py                    # 使用默认配置
    python run.py --config custom.json  # 使用自定义配置
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

def create_argument_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="SmartEBM Full-Text Screening Tool - Single Thread Mode",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config', '-c', 
        default='config/config.json',
        help='Configuration file path (default: config/config.json)'
    )
    
    parser.add_argument(
        '--lang', '-l',
        choices=['en', 'zh'],
        default='zh',
        help='Interface language: en (English), zh (Chinese)'
    )
    
    return parser


def main():
    """Main function for single-thread mode"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        print("=== SmartEBM Full-Text Screening Tool (Single Thread) ===")
        
        # Import and run the original fulltext processing
        sys.path.insert(0, project_root)
        from scripts.run_fulltext import main as fulltext_main
        
        # Change working directory to project root
        os.chdir(project_root)
        
        # Run single-threaded processing
        result = fulltext_main()
        
        return result
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are properly installed")
        print("Run: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Get the project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    sys.exit(main())