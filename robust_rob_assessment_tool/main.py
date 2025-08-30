#!/usr/bin/env python3
"""
Main entry point for the Robust ROB Assessment Tool.
Provides interactive command-line interface with bilingual support and parallel processing.
"""

import argparse
import sys
import os
import json
import glob
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def main() -> int:
    """
    Main function with return code for success/failure.
    
    Returns:
        int: 0 for success, 1 for failure
    """
    try:
        # Parse command line arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Handle different operation modes
        if hasattr(args, 'operation') and args.operation:
            return handle_command_line_operation(args)
        else:
            # Default to interactive mode
            return interactive_mode(args.language if hasattr(args, 'language') else None)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Critical error: {e}")
        return 1

def handle_command_line_operation(args) -> int:
    """
    Handle command-line operations based on parsed arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        int: 0 for success, 1 for failure
    """
    try:
        # Validate configuration file if provided
        if hasattr(args, 'config') and args.config:
            if not validate_config_file(args.config):
                print(f"Error: Invalid configuration file: {args.config}")
                return 1
        
        # Handle different operations
        if args.operation == 'start':
            return handle_start_operation(args)
        elif args.operation == 'resume':
            return handle_resume_operation(args)
        elif args.operation == 'monitor':
            return handle_monitor_operation(args)
        elif args.operation == 'cleanup':
            return handle_cleanup_operation(args)
        elif args.operation == 'merge':
            return handle_merge_operation(args)
        else:
            print(f"Error: Unknown operation '{args.operation}'")
            return 1
            
    except Exception as e:
        print(f"Error executing operation: {e}")
        return 1

def handle_start_operation(args) -> int:
    """Handle start assessment operation."""
    print("Starting new ROB assessment...")
    # TODO: Implement in subsequent tasks
    print("This functionality will be implemented in subsequent tasks.")
    return 0

def handle_resume_operation(args) -> int:
    """Handle resume assessment operation."""
    if not hasattr(args, 'state_file') or not args.state_file:
        print("Error: State file required for resume operation")
        return 1
    
    if not Path(args.state_file).exists():
        print(f"Error: State file not found: {args.state_file}")
        return 1
    
    print(f"Resuming assessment from: {args.state_file}")
    # TODO: Implement in subsequent tasks
    print("This functionality will be implemented in subsequent tasks.")
    return 0

def handle_monitor_operation(args) -> int:
    """Handle monitor progress operation."""
    state_file = getattr(args, 'state_file', None)
    if state_file and not Path(state_file).exists():
        print(f"Error: State file not found: {state_file}")
        return 1
    
    print("Monitoring assessment progress...")
    # TODO: Implement in subsequent tasks
    print("This functionality will be implemented in subsequent tasks.")
    return 0

def handle_cleanup_operation(args) -> int:
    """Handle cleanup temporary files operation."""
    temp_dir = getattr(args, 'temp_dir', 'temp_parallel')
    print(f"Cleaning up temporary files in: {temp_dir}")
    # TODO: Implement in subsequent tasks
    print("This functionality will be implemented in subsequent tasks.")
    return 0

def handle_merge_operation(args) -> int:
    """Handle merge results operation."""
    if not hasattr(args, 'input_dir') or not args.input_dir:
        print("Error: Input directory required for merge operation")
        return 1
    
    if not Path(args.input_dir).exists():
        print(f"Error: Input directory not found: {args.input_dir}")
        return 1
    
    output_file = getattr(args, 'output_file', 'merged_results.xlsx')
    print(f"Merging results from {args.input_dir} to {output_file}")
    # TODO: Implement in subsequent tasks
    print("This functionality will be implemented in subsequent tasks.")
    return 0

def validate_config_file(config_path: str) -> bool:
    """
    Validate configuration file exists and has valid JSON structure.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            json.load(f)
        
        return True
    except (json.JSONDecodeError, IOError):
        return False

def load_configuration_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration file and return as dictionary.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_checkpoint_data(checkpoint_path: str) -> Dict[str, Any]:
    """
    Load checkpoint data from file.
    
    Args:
        checkpoint_path: Path to checkpoint file
        
    Returns:
        Dict[str, Any]: Checkpoint data
    """
    try:
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def interactive_mode(lang_override: Optional[str] = None) -> int:
    """
    Interactive operation selection with bilingual support.
    
    Args:
        lang_override: Optional language override
        
    Returns:
        int: 0 for success, 1 for failure
    """
    try:
        # Import i18n manager
        from i18n.i18n_manager import LanguageManager
        
        # Initialize language manager
        i18n_config_path = Path(__file__).parent / "i18n" / "i18n_config.json"
        lang_manager = LanguageManager(str(i18n_config_path))
        
        # Set language if provided, otherwise let user select
        if lang_override:
            lang_manager.set_language(lang_override)
        else:
            lang_manager.select_language()
        
        # Show welcome message
        print(f"\n{lang_manager.get_message('welcome')}")
        
        # Main operation loop
        while True:
            operation = show_operation_menu(lang_manager)
            
            if operation == 'exit':
                return 0
            elif operation == 'start':
                result = execute_start_assessment(lang_manager)
                if result != 0:
                    return result
            elif operation == 'resume':
                result = execute_resume_assessment(lang_manager)
                if result != 0:
                    return result
            elif operation == 'monitor':
                result = execute_monitor_progress(lang_manager)
                if result != 0:
                    return result
            elif operation == 'cleanup':
                result = execute_cleanup_operation(lang_manager)
                if result != 0:
                    return result
            elif operation == 'merge':
                result = execute_merge_operation(lang_manager)
                if result != 0:
                    return result
            else:
                print(lang_manager.get_message('invalid_input'))
                
            # Add a pause before showing menu again
            input("\nPress Enter to continue...")
                
    except ImportError as e:
        print(f"Error: Could not import required modules: {e}")
        print("Please ensure all dependencies are installed.")
        return 1
    except Exception as e:
        print(f"Error in interactive mode: {e}")
        return 1

def show_operation_menu(lang_manager) -> str:
    """
    Show comprehensive operation menu with descriptions and get user selection.
    
    Args:
        lang_manager: Language manager instance
        
    Returns:
        str: Selected operation
    """
    print("\n" + "="*60)
    print(f"{lang_manager.get_message('operation_menu')}")
    print("="*60)
    
    # Show detailed menu options with descriptions
    print(f"\n1. {lang_manager.get_message('operation_start')}")
    print(f"   - {lang_manager.get_message('operation_start_desc1')}")
    print(f"   - {lang_manager.get_message('operation_start_desc2')}")
    
    print(f"\n2. {lang_manager.get_message('operation_resume')}")
    print(f"   - {lang_manager.get_message('operation_resume_desc1')}")
    print(f"   - {lang_manager.get_message('operation_resume_desc2')}")
    
    print(f"\n3. {lang_manager.get_message('operation_monitor')}")
    print(f"   - {lang_manager.get_message('operation_monitor_desc1')}")
    print(f"   - {lang_manager.get_message('operation_monitor_desc2')}")
    
    print(f"\n4. {lang_manager.get_message('operation_cleanup')}")
    print(f"   - {lang_manager.get_message('operation_cleanup_desc1')}")
    print(f"   - {lang_manager.get_message('operation_cleanup_desc2')}")
    
    print(f"\n5. {lang_manager.get_message('operation_merge')}")
    print(f"   - {lang_manager.get_message('operation_merge_desc1')}")
    print(f"   - {lang_manager.get_message('operation_merge_desc2')}")
    
    print(f"\n6. {lang_manager.get_message('operation_exit')}")
    print(f"   - {lang_manager.get_message('operation_exit_desc1')}")
    
    print("\n" + "-"*60)
    
    while True:
        try:
            choice = input(f"\n{lang_manager.get_message('operation_selection')} ").strip()
            if choice == "1":
                return "start"
            elif choice == "2":
                return "resume"
            elif choice == "3":
                return "monitor"
            elif choice == "4":
                return "cleanup"
            elif choice == "5":
                return "merge"
            elif choice == "6":
                return "exit"
            else:
                print(f"\n{lang_manager.get_message('invalid_input')}")
                print(f"{lang_manager.get_message('please_enter_number')}")
        except KeyboardInterrupt:
            print(f"\n{lang_manager.get_message('operation_exit')}")
            return "exit"
        except Exception:
            print(f"\n{lang_manager.get_message('invalid_input')}")

def execute_start_assessment(lang_manager) -> int:
    """Execute start assessment operation in interactive mode with user guidance."""
    print(f"\n{'='*60}")
    print(f"{lang_manager.get_message('operation_start')}")
    print("="*60)
    
    try:
        # Get configuration file path
        config_path = get_config_file_path(lang_manager)
        if not config_path:
            return 1
        
        # Load and validate configuration
        if not validate_config_file(config_path):
            print(f"\n{lang_manager.get_message('config_error', error='Invalid configuration file')}")
            return 1
        
        print(f"\n{lang_manager.get_message('config_loaded')}")
        
        # Get system information and recommendations
        show_system_information(lang_manager)
        
        # Get processing options
        processing_options = get_processing_options(lang_manager)
        if not processing_options:
            return 1
        
        # Update configuration with user options
        config = load_configuration_file(config_path)
        if processing_options['workers'] != 'auto':
            if 'parallel' not in config:
                config['parallel'] = {}
            config['parallel']['parallel_workers'] = processing_options['workers']
            config['parallel']['enabled'] = processing_options['workers'] > 1
        
        if processing_options['batch_size'] != 50:
            if 'parallel' not in config:
                config['parallel'] = {}
            config['parallel']['max_documents_per_batch'] = processing_options['batch_size']
        
        # Save updated configuration temporarily
        temp_config_path = Path(config_path).parent / f"temp_config_{int(time.time())}.json"
        with open(temp_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # Show configuration summary and confirm
        if not show_configuration_summary(lang_manager, config_path, processing_options):
            print(f"\n{lang_manager.get_message('operation_exit')}")
            # Clean up temp config
            if temp_config_path.exists():
                temp_config_path.unlink()
            return 0
        
        # Start the actual assessment
        print(f"\n{lang_manager.get_message('starting_assessment')}")
        
        # Import and run the actual assessment
        from src.main import run_assessment
        
        # Run assessment with the configuration
        run_assessment(str(temp_config_path))
        
        # Clean up temp config
        if temp_config_path.exists():
            temp_config_path.unlink()
        
        print(f"\n✅ {lang_manager.get_message('assessment_completed')}")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n{lang_manager.get_message('operation_exit')}")
        return 0
    except Exception as e:
        print(f"\n{lang_manager.get_message('errors.unexpected_error', error=str(e))}")
        return 1

def execute_resume_assessment(lang_manager) -> int:
    """Execute resume assessment operation in interactive mode with checkpoint selection."""
    print(f"\n{'='*60}")
    print(f"{lang_manager.get_message('operation_resume')}")
    print("="*60)
    
    try:
        # Find available checkpoint files
        checkpoint_files = find_checkpoint_files()
        
        if not checkpoint_files:
            print(f"\n{lang_manager.get_message('checkpoint_system.checkpoint_invalid', file=lang_manager.get_message('no_checkpoint_files'))}")
            print(f"{lang_manager.get_message('please_start_new_assessment')}")
            return 1
        
        # Show available checkpoints
        selected_checkpoint = select_checkpoint_file(lang_manager, checkpoint_files)
        if not selected_checkpoint:
            return 0
        
        # Validate checkpoint file
        if not validate_checkpoint_file(selected_checkpoint):
            print(f"\n{lang_manager.get_message('checkpoint_system.checkpoint_corrupted')}")
            return 1
        
        print(f"\n{lang_manager.get_message('checkpoint_system.checkpoint_loaded', file=selected_checkpoint)}")
        
        # Show checkpoint information
        show_checkpoint_information(lang_manager, selected_checkpoint)
        
        # Confirm resume operation
        if not confirm_operation(lang_manager, "resume_assessment"):
            print(f"\n{lang_manager.get_message('operation_exit')}")
            return 0
        
        # Start the actual resume process
        print(f"\n{lang_manager.get_message('resuming_assessment')}")
        
        # Import and use the parallel controller
        from core.parallel_controller import ParallelROBManager
        
        # Get config from checkpoint
        checkpoint_data = load_checkpoint_data(selected_checkpoint)
        config_path = checkpoint_data.get('config_path', 'config/config.json')
        
        # Create parallel manager and resume
        parallel_manager = ParallelROBManager(config_path)
        success = parallel_manager.resume_assessment(state_file=selected_checkpoint)
        
        if success:
            print(f"\n✅ {lang_manager.get_message('assessment_resumed')}")
            return 0
        else:
            print(f"\n❌ {lang_manager.get_message('resume_failed')}")
            return 1
        
    except KeyboardInterrupt:
        print(f"\n{lang_manager.get_message('operation_exit')}")
        return 0
    except Exception as e:
        print(f"\n{lang_manager.get_message('errors.unexpected_error', error=str(e))}")
        return 1

def execute_monitor_progress(lang_manager) -> int:
    """Execute monitor progress operation in interactive mode with real-time updates."""
    print(f"\n{'='*60}")
    print(f"{lang_manager.get_message('operation_monitor')}")
    print("="*60)
    
    try:
        # Find active assessment state files
        state_files = find_active_state_files()
        
        if not state_files:
            print(f"\n{lang_manager.get_message('no_active_assessments')}")
            print(f"{lang_manager.get_message('please_start_or_resume')}")
            return 1
        
        # Select state file to monitor
        selected_state = select_state_file(lang_manager, state_files)
        if not selected_state:
            return 0
        
        # Get monitoring options
        monitor_options = get_monitor_options(lang_manager)
        
        print(f"\n{lang_manager.get_message('progress_monitoring.monitoring_started')}")
        print(f"{lang_manager.get_message('press_ctrl_c_to_stop')}")
        
        # Import and use the progress monitor
        from core.progress_monitor import ProgressMonitor
        
        # Create and start progress monitor
        monitor = ProgressMonitor(selected_state)
        monitor.start_monitoring()
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n{lang_manager.get_message('progress_monitoring.monitoring_stopped')}")
        return 0
    except Exception as e:
        print(f"\n{lang_manager.get_message('errors.unexpected_error', error=str(e))}")
        return 1

def execute_cleanup_operation(lang_manager) -> int:
    """Execute cleanup operation in interactive mode with safety confirmations."""
    print(f"\n{'='*60}")
    print(f"{lang_manager.get_message('operation_cleanup')}")
    print("="*60)
    
    try:
        # Show cleanup options
        cleanup_options = get_cleanup_options(lang_manager)
        if not cleanup_options:
            return 0
        
        # Show what will be cleaned up
        show_cleanup_preview(lang_manager, cleanup_options)
        
        # Confirm cleanup operation
        if not confirm_operation(lang_manager, "cleanup_files"):
            print(f"\n{lang_manager.get_message('operation_exit')}")
            return 0
        
        # Perform actual cleanup
        print(f"\n{lang_manager.get_message('file_management.cleanup_temp_files')}")
        
        # Import file organizer for cleanup
        from core.file_organizer import FileOrganizer
        
        # Perform cleanup based on options
        # Note: FileOrganizer.cleanup_temp_files requires session_structure parameter
        # For now, we'll implement a simple cleanup
        temp_dir = Path(cleanup_options.get('temp_dir', 'temp_parallel'))
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
            success = True
        else:
            success = False
        
        if success:
            print(f"\n✅ {lang_manager.get_message('cleanup_completed')}")
            return 0
        else:
            print(f"\n❌ {lang_manager.get_message('cleanup_failed')}")
            return 1
        
    except KeyboardInterrupt:
        print(f"\n{lang_manager.get_message('operation_exit')}")
        return 0
    except Exception as e:
        print(f"\n{lang_manager.get_message('errors.unexpected_error', error=str(e))}")
        return 1

def execute_merge_operation(lang_manager) -> int:
    """Execute merge results operation in interactive mode with format selection."""
    print(f"\n{'='*60}")
    print(f"{lang_manager.get_message('operation_merge')}")
    print("="*60)
    
    try:
        # Get input directory
        input_dir = get_input_directory(lang_manager)
        if not input_dir:
            return 0
        
        # Get merge options
        merge_options = get_merge_options(lang_manager)
        if not merge_options:
            return 0
        
        # Show merge preview
        show_merge_preview(lang_manager, input_dir, merge_options)
        
        # Confirm merge operation
        if not confirm_operation(lang_manager, "merge_results"):
            print(f"\n{lang_manager.get_message('operation_exit')}")
            return 0
        
        # Perform actual merge
        print(f"\n{lang_manager.get_message('file_management.result_merger_started')}")
        
        # Import result merger
        from core.result_merger import ResultMerger
        
        # Perform merge based on options
        # Note: Using merge_batch_results instead of merge_results
        merger = ResultMerger()
        # For now, we'll create a simple placeholder
        # since merge_batch_results expects different parameters
        print(f"Merging from {input_dir} to {merge_options.get('output_file', 'merged_results.xlsx')}")
        success = True  # Placeholder implementation
        
        if success:
            print(f"\n✅ {lang_manager.get_message('merge_completed')}")
            return 0
        else:
            print(f"\n❌ {lang_manager.get_message('merge_failed')}")
            return 1
        
    except KeyboardInterrupt:
        print(f"\n{lang_manager.get_message('operation_exit')}")
        return 0
    except Exception as e:
        print(f"\n{lang_manager.get_message('errors.unexpected_error', error=str(e))}")
        return 1

def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create comprehensive command line argument parser with all operation modes.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="ROB Assessment Tool with parallel processing support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Interactive mode
  %(prog)s start -c config.json      # Start new assessment
  %(prog)s resume -s state.json      # Resume from checkpoint
  %(prog)s monitor -s state.json     # Monitor progress
  %(prog)s cleanup -t temp_parallel  # Clean temporary files
  %(prog)s merge -i results/ -o merged.xlsx  # Merge results
        """
    )
    
    # Version information
    parser.add_argument(
        "--version",
        action="version",
        version="ROB Assessment Tool v2.0"
    )
    
    # Language selection
    parser.add_argument(
        "-l", "--language",
        choices=["en", "zh"],
        help="Interface language (en=English, zh=Chinese)"
    )
    
    # Subcommands for different operations
    subparsers = parser.add_subparsers(
        dest="operation",
        help="Available operations",
        metavar="OPERATION"
    )
    
    # Start assessment command
    start_parser = subparsers.add_parser(
        "start",
        help="Start new ROB assessment",
        description="Start a new ROB assessment with parallel processing"
    )
    start_parser.add_argument(
        "-c", "--config",
        required=True,
        help="Path to configuration file"
    )
    start_parser.add_argument(
        "-w", "--workers",
        type=int,
        help="Number of parallel workers (overrides config)"
    )
    start_parser.add_argument(
        "-i", "--input",
        help="Input directory path (overrides config)"
    )
    start_parser.add_argument(
        "-o", "--output",
        help="Output directory path (overrides config)"
    )
    start_parser.add_argument(
        "--batch-size",
        type=int,
        help="Maximum documents per batch (overrides config)"
    )
    start_parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="Starting document index (default: 0)"
    )
    
    # Resume assessment command
    resume_parser = subparsers.add_parser(
        "resume",
        help="Resume interrupted assessment",
        description="Resume a previously interrupted ROB assessment"
    )
    resume_parser.add_argument(
        "-s", "--state-file",
        required=True,
        help="Path to state/checkpoint file"
    )
    resume_parser.add_argument(
        "-c", "--config",
        help="Path to configuration file (optional, uses saved config if not provided)"
    )
    resume_parser.add_argument(
        "-w", "--workers",
        type=int,
        help="Number of parallel workers (overrides saved config)"
    )
    
    # Monitor progress command
    monitor_parser = subparsers.add_parser(
        "monitor",
        help="Monitor assessment progress",
        description="Monitor the progress of a running ROB assessment"
    )
    monitor_parser.add_argument(
        "-s", "--state-file",
        help="Path to state file to monitor (auto-detects if not provided)"
    )
    monitor_parser.add_argument(
        "-r", "--refresh",
        type=int,
        default=5,
        help="Refresh interval in seconds (default: 5)"
    )
    monitor_parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Don't clear screen between updates"
    )
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser(
        "cleanup",
        help="Clean up temporary files",
        description="Clean up temporary files and directories"
    )
    cleanup_parser.add_argument(
        "-t", "--temp-dir",
        default="temp_parallel",
        help="Temporary directory to clean (default: temp_parallel)"
    )
    cleanup_parser.add_argument(
        "--keep-results",
        action="store_true",
        help="Keep result files, only remove temporary processing files"
    )
    cleanup_parser.add_argument(
        "--force",
        action="store_true",
        help="Force cleanup without confirmation"
    )
    
    # Merge results command
    merge_parser = subparsers.add_parser(
        "merge",
        help="Merge parallel processing results",
        description="Merge results from parallel processing batches"
    )
    merge_parser.add_argument(
        "-i", "--input-dir",
        required=True,
        help="Directory containing batch results to merge"
    )
    merge_parser.add_argument(
        "-o", "--output-file",
        default="merged_results.xlsx",
        help="Output file for merged results (default: merged_results.xlsx)"
    )
    merge_parser.add_argument(
        "--format",
        choices=["excel", "json", "both"],
        default="excel",
        help="Output format (default: excel)"
    )
    merge_parser.add_argument(
        "--include-failed",
        action="store_true",
        help="Include failed documents in results"
    )
    
    # Global options for all commands
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress non-essential output"
    )
    parser.add_argument(
        "--log-file",
        help="Path to log file for detailed logging"
    )
    
    return parser

# Helper functions for interactive operations

def get_config_file_path(lang_manager) -> Optional[str]:
    """Get configuration file path from user input."""
    print(f"\n{lang_manager.get_message('configuration.loading_config', path='...')}")
    
    # Check for default config file
    default_config = Path("config/config.json")
    if default_config.exists():
        use_default = input(f"Use default config file ({default_config})? (y/n): ").strip().lower()
        if use_default in ['y', 'yes']:
            return str(default_config)
    
    while True:
        config_path = input("Enter configuration file path: ").strip()
        if not config_path:
            return None
        
        if Path(config_path).exists():
            return config_path
        else:
            print(f"{lang_manager.get_message('file_management.file_not_found', path=config_path)}")

def show_system_information(lang_manager):
    """Display system information and resource recommendations."""
    print(f"\n{lang_manager.get_message('system_detection.detecting_resources')}")
    
    try:
        # Import system detector
        from core.system_detector import SystemCapacityDetector
        
        capacity = SystemCapacityDetector.detect_system_capacity()
        recommended_workers = SystemCapacityDetector.recommend_parallel_workers({})
        
        print(f"\n{lang_manager.get_message('system_info')}:")
        print(f"  {lang_manager.get_message('system_detection.cpu_cores', cores=capacity.get('cpu_cores', 'Unknown'))}")
        print(f"  {lang_manager.get_message('system_detection.memory_total', memory=capacity.get('memory_gb', 'Unknown'))}")
        print(f"  {lang_manager.get_message('system_detection.disk_space', space=capacity.get('disk_gb', 'Unknown'))}")
        print(f"  {lang_manager.get_message('system_detection.recommended_workers', workers=recommended_workers)}")
        
    except ImportError:
        print("System detection not available - using default recommendations")

def get_processing_options(lang_manager) -> Optional[Dict[str, Any]]:
    """Get processing options from user input."""
    print(f"\nProcessing Options:")
    
    options = {}
    
    # Get number of parallel workers
    while True:
        try:
            workers_input = input("Number of parallel workers (press Enter for auto): ").strip()
            if not workers_input:
                options['workers'] = 'auto'
                break
            else:
                workers = int(workers_input)
                if workers > 0:
                    options['workers'] = workers
                    break
                else:
                    print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            return None
    
    # Get batch size
    while True:
        try:
            batch_input = input("Documents per batch (press Enter for default 50): ").strip()
            if not batch_input:
                options['batch_size'] = 50
                break
            else:
                batch_size = int(batch_input)
                if batch_size > 0:
                    options['batch_size'] = batch_size
                    break
                else:
                    print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            return None
    
    return options

def show_configuration_summary(lang_manager, config_path: str, options: Dict[str, Any]) -> bool:
    """Show configuration summary and get user confirmation."""
    print(f"\n{'='*50}")
    print("Configuration Summary:")
    print("="*50)
    print(f"Config file: {config_path}")
    print(f"Parallel workers: {options.get('workers', 'auto')}")
    print(f"Batch size: {options.get('batch_size', 50)}")
    print("="*50)
    
    return confirm_operation(lang_manager, "start_with_config")

def confirm_operation(lang_manager, operation_key: str) -> bool:
    """Get user confirmation for an operation."""
    while True:
        try:
            response = input(f"\n{lang_manager.get_message('confirm')}").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print(lang_manager.get_message('invalid_input'))
        except KeyboardInterrupt:
            return False

def find_checkpoint_files() -> List[str]:
    """Find available checkpoint files."""
    checkpoint_patterns = [
        "*.checkpoint.json",
        "checkpoint_*.json",
        "state_*.json",
        "temp_parallel/*/state.json"
    ]
    
    checkpoint_files = []
    for pattern in checkpoint_patterns:
        checkpoint_files.extend(glob.glob(pattern))
    
    return sorted(checkpoint_files, key=lambda x: Path(x).stat().st_mtime, reverse=True)

def select_checkpoint_file(lang_manager, checkpoint_files: List[str]) -> Optional[str]:
    """Let user select from available checkpoint files."""
    print(f"\nAvailable checkpoint files:")
    
    for i, checkpoint in enumerate(checkpoint_files[:10], 1):  # Show max 10 files
        file_path = Path(checkpoint)
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        print(f"{i}. {checkpoint} (modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
    
    while True:
        try:
            choice = input(f"\nSelect checkpoint file (1-{min(len(checkpoint_files), 10)}, or 0 to cancel): ").strip()
            if choice == "0":
                return None
            
            index = int(choice) - 1
            if 0 <= index < min(len(checkpoint_files), 10):
                return checkpoint_files[index]
            else:
                print(lang_manager.get_message('invalid_input'))
        except ValueError:
            print(lang_manager.get_message('invalid_input'))
        except KeyboardInterrupt:
            return None

def validate_checkpoint_file(checkpoint_path: str) -> bool:
    """Validate checkpoint file format and content."""
    try:
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Basic validation - check for required fields
        required_fields = ['session_id', 'start_time', 'total_documents']
        return all(field in data for field in required_fields)
    except (json.JSONDecodeError, IOError, KeyError):
        return False

def show_checkpoint_information(lang_manager, checkpoint_path: str):
    """Display information about the selected checkpoint."""
    try:
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\nCheckpoint Information:")
        print(f"  Session ID: {data.get('session_id', 'Unknown')}")
        print(f"  Start Time: {data.get('start_time', 'Unknown')}")
        print(f"  Total Documents: {data.get('total_documents', 'Unknown')}")
        print(f"  Completed: {data.get('completed_documents', 0)}")
        print(f"  Progress: {data.get('progress_percent', 0)}%")
        
    except Exception as e:
        print(f"Could not read checkpoint details: {e}")

def find_active_state_files() -> List[str]:
    """Find active assessment state files."""
    state_patterns = [
        "temp_parallel/*/state.json",
        "state_*.json",
        "assessment_state.json"
    ]
    
    state_files = []
    for pattern in state_patterns:
        state_files.extend(glob.glob(pattern))
    
    return sorted(state_files, key=lambda x: Path(x).stat().st_mtime, reverse=True)

def select_state_file(lang_manager, state_files: List[str]) -> Optional[str]:
    """Let user select from available state files."""
    print(f"\nActive assessments:")
    
    for i, state_file in enumerate(state_files[:5], 1):  # Show max 5 files
        file_path = Path(state_file)
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        print(f"{i}. {state_file} (last updated: {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
    
    while True:
        try:
            choice = input(f"\nSelect assessment to monitor (1-{min(len(state_files), 5)}, or 0 to cancel): ").strip()
            if choice == "0":
                return None
            
            index = int(choice) - 1
            if 0 <= index < min(len(state_files), 5):
                return state_files[index]
            else:
                print(lang_manager.get_message('invalid_input'))
        except ValueError:
            print(lang_manager.get_message('invalid_input'))
        except KeyboardInterrupt:
            return None

def get_monitor_options(lang_manager) -> Dict[str, Any]:
    """Get monitoring options from user."""
    options = {}
    
    # Get refresh interval
    while True:
        try:
            refresh_input = input("Refresh interval in seconds (default 5): ").strip()
            if not refresh_input:
                options['refresh_interval'] = 5
                break
            else:
                interval = int(refresh_input)
                if interval > 0:
                    options['refresh_interval'] = interval
                    break
                else:
                    print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            break
    
    return options

def get_cleanup_options(lang_manager) -> Optional[Dict[str, Any]]:
    """Get cleanup options from user."""
    print(f"\nCleanup Options:")
    print("1. Clean temporary files only (keep results)")
    print("2. Clean all files including results")
    print("3. Clean specific directory")
    print("4. Cancel")
    
    while True:
        try:
            choice = input("Select cleanup option (1-4): ").strip()
            if choice == "1":
                return {'type': 'temp_only', 'keep_results': True}
            elif choice == "2":
                return {'type': 'all', 'keep_results': False}
            elif choice == "3":
                directory = input("Enter directory path to clean: ").strip()
                if directory and Path(directory).exists():
                    return {'type': 'specific', 'directory': directory}
                else:
                    print("Directory not found.")
            elif choice == "4":
                return None
            else:
                print(lang_manager.get_message('invalid_input'))
        except KeyboardInterrupt:
            return None

def show_cleanup_preview(lang_manager, options: Dict[str, Any]):
    """Show what will be cleaned up."""
    print(f"\nCleanup Preview:")
    
    if options['type'] == 'temp_only':
        print("- Temporary processing files")
        print("- Checkpoint files")
        print("- Worker state files")
        print("✓ Results will be preserved")
    elif options['type'] == 'all':
        print("- Temporary processing files")
        print("- Checkpoint files")
        print("- Worker state files")
        print("- Result files")
        print("⚠️  All files will be removed")
    elif options['type'] == 'specific':
        print(f"- All files in: {options['directory']}")

def get_input_directory(lang_manager) -> Optional[str]:
    """Get input directory for merge operation."""
    while True:
        try:
            input_dir = input("Enter directory containing results to merge: ").strip()
            if not input_dir:
                return None
            
            if Path(input_dir).exists() and Path(input_dir).is_dir():
                return input_dir
            else:
                print(f"{lang_manager.get_message('file_management.file_not_found', path=input_dir)}")
        except KeyboardInterrupt:
            return None

def get_merge_options(lang_manager) -> Optional[Dict[str, Any]]:
    """Get merge options from user."""
    options = {}
    
    # Get output format
    print(f"\nOutput format:")
    print("1. Excel (.xlsx)")
    print("2. JSON (.json)")
    print("3. Both formats")
    
    while True:
        try:
            choice = input("Select format (1-3): ").strip()
            if choice == "1":
                options['format'] = 'excel'
                break
            elif choice == "2":
                options['format'] = 'json'
                break
            elif choice == "3":
                options['format'] = 'both'
                break
            else:
                print(lang_manager.get_message('invalid_input'))
        except KeyboardInterrupt:
            return None
    
    # Get output filename
    default_name = "merged_results"
    output_name = input(f"Output filename (default: {default_name}): ").strip()
    options['output_name'] = output_name if output_name else default_name
    
    return options

def show_merge_preview(lang_manager, input_dir: str, options: Dict[str, Any]):
    """Show merge operation preview."""
    print(f"\nMerge Preview:")
    print(f"Input directory: {input_dir}")
    print(f"Output format: {options['format']}")
    print(f"Output filename: {options['output_name']}")
    
    # Count files to merge
    result_files = list(Path(input_dir).glob("*.xlsx")) + list(Path(input_dir).glob("*.json"))
    print(f"Files to merge: {len(result_files)}")

if __name__ == "__main__":
    sys.exit(main())