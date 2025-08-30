#!/usr/bin/env python3
"""
Parallel Screening System Main Entry
SmartEBM Parallel Literature Screening Tool

Usage:
    python parallel_run.py                    # Use default config
    python parallel_run.py --config custom.json  # Use custom config
    python parallel_run.py --resume           # Resume interrupted task
    python parallel_run.py --monitor          # Monitor only mode
"""

import os
import sys
import argparse
import time
import threading
from pathlib import Path

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(project_root, 'i18n'))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'tools'))

from parallel_controller import ParallelScreeningManager
from progress_monitor import ProgressMonitor, monitor_screening_progress
from result_merger import merge_results_from_state
from i18n.i18n_manager import get_language_manager, get_message, select_language


def create_argument_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="SmartEBM Parallel Literature Screening System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  python parallel_run.py                           # Start new task with default config
  python parallel_run.py --config custom.json     # Use custom config file
  python parallel_run.py --resume                  # Resume interrupted task
  python parallel_run.py --monitor state.json     # Monitor existing task
  python parallel_run.py --merge-only state.json  # Merge results only
  python parallel_run.py --cleanup                 # Clean temporary files

Configuration Guide:
  Users only need to set parallel_screeners count in config.json,
  the system will automatically detect hardware capacity and intelligently distribute records.
        """
    )
    
    parser.add_argument(
        '--config', '-c', 
        default='config/config.json',
        help='Unified configuration file path (default: config/config.json)'
    )
    
    parser.add_argument(
        '--resume', '-r',
        action='store_true',
        help='Resume interrupted parallel screening task'
    )
    
    parser.add_argument(
        '--monitor', '-m',
        metavar='STATE_FILE',
        help='Monitor screening progress of specified state file'
    )
    
    parser.add_argument(
        '--merge-only',
        metavar='STATE_FILE',
        help='Merge results of specified state file only'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean temporary files and state files'
    )
    
    parser.add_argument(
        '--update-interval',
        type=int,
        default=5,
        help='Monitor update interval in seconds (default: 5 seconds)'
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
    state_files = list(Path('.').glob('parallel_screening_state*.json'))
    
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


def run_new_task(config_path):
    """Run new task"""
    try:
        print(get_message("starting_new_task"))
        
        manager = ParallelScreeningManager(config_path)
        success = manager.start_parallel_screening()
        
        return success
        
    except Exception as e:
        print(get_message("system_error", error=str(e)))
        return False


def run_resume_task(config_path):
    """Resume task"""
    try:
        print("🔄 Resuming interrupted parallel screening task...")
        
        # Find state file
        state_file = find_state_file()
        if not state_file:
            print("❌ No state file found, cannot resume task")
            return False
        
        print(f"✓ Found state file: {state_file}")
        
        manager = ParallelScreeningManager(config_path)
        # Resume logic needs to be implemented here
        success = manager.start_parallel_screening()
        
        return success
        
    except Exception as e:
        print(f"❌ Task resume failed: {str(e)}")
        return False


def run_monitor_only(state_file_path, update_interval):
    """Monitor only mode"""
    try:
        if not os.path.exists(state_file_path):
            print(f"❌ State file does not exist: {state_file_path}")
            return False
        
        print(f"📊 Starting task progress monitoring: {state_file_path}")
        monitor_screening_progress(state_file_path, update_interval)
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring failed: {str(e)}")
        return False


def run_merge_only(state_file_path):
    """Merge only mode"""
    try:
        if not os.path.exists(state_file_path):
            print(f"❌ State file does not exist: {state_file_path}")
            return False
        
        print(f"🔄 Starting result merging: {state_file_path}")
        
        # Read output directory config from state file
        import json
        with open(state_file_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Use current directory as output directory
        output_dir = "."
        
        results = merge_results_from_state(
            state_file_path, 
            output_dir,
            final_output_prefix="final_results",
            backup_individual=True
        )
        
        if results.get('xml_merge', {}).get('success') or results.get('excel_merge', {}).get('success'):
            print("✅ Result merging completed!")
            return True
        else:
            print("❌ Result merging failed")
            return False
        
    except Exception as e:
        print(f"❌ Merging failed: {str(e)}")
        return False


def run_cleanup():
    """Clean temporary files"""
    try:
        print(get_message("cleanup_starting"))
        
        # Clean temporary directories
        temp_dirs = ['temp_parallel', 'temp_screening']
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir)
                print(get_message("deleted_temp_dir", dir=temp_dir))
        
        # Clean state files
        state_files = list(Path('.').glob('parallel_screening_state*.json'))
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


def run_with_monitor(task_func, state_file_pattern="parallel_screening_state.json", update_interval=5):
    """Run task with monitoring"""
    
    def monitor_thread():
        """Monitor thread"""
        # Wait for state file to be generated
        max_wait = 30  # Wait max 30 seconds
        wait_count = 0
        
        while wait_count < max_wait:
            if os.path.exists(state_file_pattern):
                break
            time.sleep(1)
            wait_count += 1
        
        if os.path.exists(state_file_pattern):
            try:
                monitor_screening_progress(state_file_pattern, update_interval)
            except:
                pass  # Monitoring failure doesn't affect main task
    
    # Start monitoring thread
    monitor_t = threading.Thread(target=monitor_thread, daemon=True)
    monitor_t.start()
    
    # Execute main task
    return task_func()


def main():
    """Main function"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Adjust config file path (if relative path)
    if not os.path.isabs(args.config):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        args.config = os.path.join(project_root, args.config)
    
    # Check configuration file
    if not os.path.exists(args.config):
        print(f"❌ Configuration file does not exist: {args.config}")
        print("Please create a configuration file first or use --config to specify the correct path")
        return 1
    
    try:
        # Execute different operations based on arguments
        if args.monitor:
            # Monitor only mode
            success = run_monitor_only(args.monitor, args.update_interval)
            
        elif args.merge_only:
            # Merge only mode
            success = run_merge_only(args.merge_only)
            
        elif args.cleanup:
            # Cleanup mode
            success = run_cleanup()
            
        elif args.resume:
            # Resume mode
            success = run_with_monitor(
                lambda: run_resume_task(args.config),
                update_interval=args.update_interval
            )
            
        elif len(sys.argv) == 1 or (len(sys.argv) == 3 and '--lang' in sys.argv):
            # Interactive mode
            mode = interactive_mode(args.lang if args.lang != 'auto' else None)
            
            if mode == 'new':
                success = run_with_monitor(
                    lambda: run_new_task(args.config),
                    update_interval=args.update_interval
                )
            elif mode == 'resume':
                success = run_with_monitor(
                    lambda: run_resume_task(args.config),
                    update_interval=args.update_interval
                )
            elif mode == 'monitor':
                state_file = find_state_file()
                if state_file:
                    success = run_monitor_only(str(state_file), args.update_interval)
                else:
                    print("❌ State file not found")
                    success = False
            elif mode == 'merge':
                state_file = find_state_file()
                if state_file:
                    success = run_merge_only(str(state_file))
                else:
                    print("❌ State file not found")
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
            success = run_with_monitor(
                lambda: run_new_task(args.config),
                update_interval=args.update_interval
            )
        
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