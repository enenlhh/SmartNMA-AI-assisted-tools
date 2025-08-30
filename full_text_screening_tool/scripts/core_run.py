#!/usr/bin/env python3
"""
SmartEBM Full-Text Screening System Main Entry Point

Usage:
    python core_run.py                    # Use default configuration
    python core_run.py --config custom.json  # Use custom configuration
    python core_run.py --resume           # Resume interrupted task
    python core_run.py --monitor          # Monitor mode only
"""

import os
import sys
import argparse
import time
import glob
from pathlib import Path

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'i18n'))
sys.path.insert(0, os.path.join(current_dir, 'src'))

from i18n.i18n_manager import get_language_manager, get_message, select_language
from src.fulltext_extractor import FullTextExtractor
from src.utils import load_config, validate_config, create_output_directory


def create_argument_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="SmartEBM Full-Text Screening System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  python core_run.py                           # Start new task with default config
  python core_run.py --config custom.json     # Use custom config file
  python core_run.py --resume                  # Resume interrupted task
  python core_run.py --cleanup                 # Clean temporary files

Configuration Guide:
  Configure your LLM settings and screening criteria in config.json,
  then run the system for automatic full-text document screening.
        """
    )
    
    parser.add_argument(
        '--config', '-c', 
        default='config/config.json',
        help='Configuration file path (default: config/config.json)'
    )
    
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Resume interrupted full-text screening task'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean temporary files and state files'
    )
    
    parser.add_argument(
        '--lang', '-l',
        choices=['en', 'zh', 'auto'],
        default='auto',
        help='Interface language: en (English), zh (Chinese), auto (interactive selection)'
    )
    
    return parser


def find_state_file():
    """Find the latest state file"""
    state_files = list(Path('.').glob('fulltext_screening_state*.json'))
    
    if not state_files:
        # Also check for parallel state files
        state_files = list(Path('.').glob('parallel_fulltext_state*.json'))
    
    if not state_files:
        return None
    
    # Return the latest state file
    return max(state_files, key=lambda p: p.stat().st_mtime)


def interactive_mode(lang_override=None):
    """Interactive mode"""
    # First let user select language (unless preset)
    if lang_override and lang_override in ['en', 'zh']:
        get_language_manager().set_language(lang_override)
        selected_lang = lang_override
    else:
        selected_lang = select_language()
    
    print("=" * 60)
    print(get_message("system_title"))
    print("=" * 60)
    
    print(f"\n{get_message('operation_selection')}")
    print(f"1. {get_message('operation_1')}")
    print(f"2. {get_message('operation_2')}")
    print(f"3. {get_message('operation_3')}")
    print(f"4. {get_message('operation_4')}")
    print(f"5. {get_message('operation_5')}")
    print(f"6. {get_message('operation_6')}")
    
    while True:
        choice = input(f"\n{get_message('operation_prompt')}").strip()
        
        if choice == '1':
            return 'new'
        elif choice == '2':
            return 'resume'
        elif choice == '3':
            return 'monitor'
        elif choice == '4':
            return 'merge'
        elif choice == '5':
            return 'cleanup'
        elif choice == '6':
            return 'exit'
        else:
            print(get_message('invalid_option'))


def validate_fulltext_config(config):
    """Validate full-text configuration structure"""
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


def detect_system_resources():
    """Detect system resources and provide recommendations"""
    import psutil
    import multiprocessing
    
    print(f"\n{get_message('system_detection')}")
    print("=" * 50)
    
    # CPU information
    cpu_cores = multiprocessing.cpu_count()
    print(get_message("cpu_cores", cores=cpu_cores))
    
    # Memory information
    memory = psutil.virtual_memory()
    total_memory_gb = memory.total / (1024**3)
    available_memory_gb = memory.available / (1024**3)
    print(get_message("total_memory", memory=f"{total_memory_gb:.1f}"))
    print(get_message("available_memory", memory=f"{available_memory_gb:.1f}"))
    
    # Disk space
    disk = psutil.disk_usage('.')
    available_disk_gb = disk.free / (1024**3)
    print(get_message("available_disk", space=f"{available_disk_gb:.1f}"))
    
    # Calculate recommendations
    # For full-text screening, be more conservative due to PDF processing
    safe_cpu_threads = max(1, cpu_cores - 1)  # Leave one core free
    recommended_threads = min(safe_cpu_threads, max(1, int(available_memory_gb / 2)))  # 2GB per thread
    max_safe_threads = min(safe_cpu_threads, max(1, int(available_memory_gb / 1.5)))  # 1.5GB per thread minimum
    
    print(get_message("recommended_threads", count=recommended_threads))
    print(get_message("max_safe_threads", count=max_safe_threads))
    
    return {
        'cpu_cores': cpu_cores,
        'total_memory_gb': total_memory_gb,
        'available_memory_gb': available_memory_gb,
        'available_disk_gb': available_disk_gb,
        'recommended_threads': recommended_threads,
        'max_safe_threads': max_safe_threads,
        'safe_cpu_threads': safe_cpu_threads
    }


def validate_and_adjust_config(config, system_info):
    """Validate configuration against system resources and offer adjustments"""
    processing = config.get('processing', {})
    parallel_settings = config.get('parallel_settings', {})
    
    # Get current thread configuration
    current_threads = parallel_settings.get('parallel_screeners', 1)
    mode = config.get('mode', {}).get('screening_mode', 'single')
    
    if mode == 'single':
        return config, True  # No validation needed for single mode
    
    warnings = []
    suggestions = []
    
    # Check CPU cores
    if current_threads > system_info['safe_cpu_threads']:
        warnings.append(get_message("exceed_cpu_cores", 
                                  requested=current_threads, 
                                  safe=system_info['safe_cpu_threads']))
        suggestions.append(get_message("recommend_cpu_threads", 
                                     count=system_info['recommended_threads']))
    
    # Check memory
    estimated_memory = current_threads * 2.0  # Estimate 2GB per thread for full-text
    if estimated_memory > system_info['available_memory_gb']:
        warnings.append(get_message("exceed_memory",
                                  estimated=estimated_memory,
                                  available=system_info['available_memory_gb']))
        memory_safe_threads = max(1, int(system_info['available_memory_gb'] / 2))
        suggestions.append(get_message("recommend_memory_threads", 
                                     count=memory_safe_threads))
    
    # Check disk space
    if system_info['available_disk_gb'] < 2.0:
        warnings.append(get_message("insufficient_disk"))
    
    # Display warnings and suggestions
    if warnings:
        print(f"\n{get_message('config_warning')}")
        for warning in warnings:
            print(f"  • {warning}")
        
        if suggestions:
            print(f"\n{get_message('suggestion')}")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
            
            # Offer to adjust
            recommended_count = system_info['recommended_threads']
            adjust_choice = input(f"\n{get_message('adjust_to_recommended', count=recommended_count)}")
            
            if adjust_choice.lower() == 'y':
                config['parallel_settings']['parallel_screeners'] = recommended_count
                print(get_message("adjusted_to", count=recommended_count))
                return config, True
            else:
                continue_choice = input(f"{get_message('continue_anyway')}")
                if continue_choice.lower() != 'y':
                    print(get_message("execution_cancelled"))
                    return config, False
    
    return config, True


def run_new_task(config_path):
    """Run new task"""
    try:
        print(get_message("starting_new_task"))
        
        # Load configuration
        if not os.path.exists(config_path):
            print(get_message("system_error", error=f"Configuration file not found: {config_path}"))
            return False
        
        config = load_config(config_path)
        validate_fulltext_config(config)
        print(get_message("config_loaded"))
        
        # Detect system resources
        system_info = detect_system_resources()
        
        # Validate and adjust configuration
        config, should_continue = validate_and_adjust_config(config, system_info)
        if not should_continue:
            return False
        
        # Extract configuration values
        paths = config['paths']
        processing = config.get('processing', {})
        llm_configs = config['llm_configs']
        inclusion_criteria = config['inclusion_criteria']
        exclusion_criteria = config.get('exclusion_criteria', {})
        
        # Validate input folder
        input_folder_path = paths['input_folder_path']
        if not os.path.exists(input_folder_path):
            print(get_message("system_error", error=f"Input folder not found: {input_folder_path}"))
            return False
        
        # Check for PDF files
        pdf_files = glob.glob(os.path.join(input_folder_path, "*.pdf"))
        print(f"\n{get_message('analyzing_input', filename=input_folder_path)}")
        print(get_message("detected_documents", count=len(pdf_files)))
        
        if len(pdf_files) == 0:
            print(get_message("system_error", error="No PDF files found in input folder"))
            return False
        
        # Display processing plan
        mode = config.get('mode', {}).get('screening_mode', 'single')
        if mode == 'parallel':
            threads = config.get('parallel_settings', {}).get('parallel_screeners', 1)
            print(f"\n📋 {get_message('batch_processing')}")
            print(f"  • Processing mode: Parallel ({threads} threads)")
            print(f"  • Total documents: {len(pdf_files)}")
            print(f"  • Documents per thread: ~{len(pdf_files) // threads}")
        
        # Confirm to start screening
        start_choice = input(f"\n{get_message('start_screening')}")
        if start_choice.lower() != 'y':
            print(get_message("operation_interrupted"))
            return False
        
        # Create output directory
        output_excel_path = paths['output_excel_path']
        create_output_directory(output_excel_path)
        
        # Initialize extractor
        print(f"\n{get_message('starting_system')}")
        print(get_message("prompt_generation"))
        
        extractor = FullTextExtractor(
            screening_llm_configs=llm_configs['screening_llms'],
            prompt_llm_config=llm_configs.get('prompt_llm'),
            positive_prompt_path=paths.get('positive_prompt_file_path'),
            negative_prompt_path=paths.get('negative_prompt_file_path'),
            config=config
        )
        
        print(get_message("prompt_loaded"))
        
        # Process documents
        print(f"\n{get_message('processing_documents')}")
        result_path = extractor.process_documents(
            folder_path=input_folder_path,
            inclusion_criteria=inclusion_criteria,
            output_path=output_excel_path,
            exclusion_criteria=exclusion_criteria,
            prompt_file_path=paths.get('prompt_file_path')
        )
        
        print(f"\n{get_message('task_completed')}")
        print(get_message("results_saved", path=result_path))
        
        return True
        
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        return False


def run_resume_task(config_path):
    """Resume task"""
    try:
        print(get_message("resuming_task"))
        
        # Find state file
        state_file = find_state_file()
        if not state_file:
            print(get_message("no_state_file"))
            return False
        
        print(get_message("state_file_found", file=state_file))
        
        # For now, just restart the new task
        # TODO: Implement proper resume logic
        return run_new_task(config_path)
        
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        return False


def run_monitor_only(state_file_path, update_interval):
    """Monitor only mode"""
    try:
        if not os.path.exists(state_file_path):
            print(get_message("system_error", error=f"State file does not exist: {state_file_path}"))
            return False
        
        print(f"📊 Starting task progress monitoring: {state_file_path}")
        
        # Import progress monitor
        from src.progress_monitor import monitor_fulltext_screening_progress
        monitor_fulltext_screening_progress(state_file_path, update_interval)
        
        return True
        
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        return False


def run_cleanup():
    """Clean temporary files"""
    try:
        print(get_message("cleanup_started"))
        
        # Clean temporary directories
        temp_dirs = ['temp_fulltext', 'temp_screening']
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                print(get_message("deleted_temp_dir", dir=temp_dir))
        
        # Clean state files
        state_files = list(Path('.').glob('fulltext_screening_state*.json'))
        for state_file in state_files:
            choice = input(get_message("delete_state_file", file=state_file))
            if choice.lower() == 'y':
                state_file.unlink()
                print(get_message("deleted_state_file", file=state_file))
        
        print(get_message("cleanup_completed"))
        return True
        
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        return False


def main():
    """Main function"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Adjust config file path (if relative path)
    if not os.path.isabs(args.config):
        # Get the parent directory of scripts (project root)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        args.config = os.path.join(project_root, args.config)
    
    # Check configuration file
    if not os.path.exists(args.config):
        print(f"❌ Configuration file does not exist: {args.config}")
        print("Please create a configuration file first or use --config to specify the correct path")
        return 1
    
    try:
        # Execute different operations based on arguments
        if args.cleanup:
            # Cleanup mode
            success = run_cleanup()
            
        elif args.resume:
            # Resume mode
            success = run_resume_task(args.config)
            
        elif len(sys.argv) == 1 or (len(sys.argv) == 3 and '--lang' in sys.argv):
            # Interactive mode
            mode = interactive_mode(args.lang if args.lang != 'auto' else None)
            
            if mode == 'new':
                success = run_new_task(args.config)
            elif mode == 'resume':
                success = run_resume_task(args.config)
            elif mode == 'monitor':
                state_file = find_state_file()
                if state_file:
                    success = run_monitor_only(str(state_file), args.update_interval)
                else:
                    print(get_message("no_state_file"))
                    success = False
            elif mode == 'merge':
                print(get_message("system_error", error="Merge mode not yet implemented"))
                success = False
            elif mode == 'cleanup':
                success = run_cleanup()
            elif mode == 'exit':
                print(get_message("goodbye"))
                return 0
            else:
                success = False
                
        else:
            # Default new task mode
            success = run_new_task(args.config)
        
        if success:
            print(f"\n{get_message('operation_completed')}")
            return 0
        else:
            print(f"\n{get_message('operation_failed')}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n\n{get_message('operation_interrupted')}")
        return 1
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())