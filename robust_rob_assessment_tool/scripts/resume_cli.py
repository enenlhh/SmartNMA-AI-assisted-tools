#!/usr/bin/env python3
"""
Command-line interface for ROB assessment resume functionality.

This script provides easy-to-use commands for resuming interrupted ROB assessments,
checking session status, and managing assessment state.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.resume_manager import ResumeManager
from i18n.i18n_manager import LanguageManager


def setup_language_manager() -> LanguageManager:
    """Set up language manager for CLI messages."""
    try:
        i18n_config_path = Path(__file__).parent.parent / "i18n" / "i18n_config.json"
        return LanguageManager(str(i18n_config_path))
    except Exception:
        # Fallback to English if i18n setup fails
        class FallbackLanguageManager:
            def get_message(self, key: str, **kwargs) -> str:
                return key.replace("_", " ").title()
        return FallbackLanguageManager()


def print_session_table(sessions: list, lang_manager: LanguageManager) -> None:
    """Print sessions in a formatted table."""
    if not sessions:
        print(lang_manager.get_message("no_sessions_found"))
        return
    
    # Table headers
    headers = [
        "Session ID",
        "Status", 
        "Progress",
        "Documents",
        "Updated"
    ]
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    
    rows = []
    for session in sessions:
        row = [
            session["session_id"][:12],  # Truncate session ID
            session.get("status", "unknown"),
            f"{session.get('progress', 0)}%" if 'progress' in session else "N/A",
            f"{session.get('completed_documents', 0)}/{session.get('total_documents', 0)}",
            session.get("updated_at", "")[:16] if session.get("updated_at") else "N/A"
        ]
        rows.append(row)
        
        # Update column widths
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print table
    separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"
    
    print(separator)
    header_row = "|" + "|".join(f" {header:<{col_widths[i]}} " for i, header in enumerate(headers)) + "|"
    print(header_row)
    print(separator)
    
    for row in rows:
        data_row = "|" + "|".join(f" {str(cell):<{col_widths[i]}} " for i, cell in enumerate(row)) + "|"
        print(data_row)
    
    print(separator)


def cmd_list_sessions(args: argparse.Namespace, resume_manager: ResumeManager, 
                     lang_manager: LanguageManager) -> int:
    """List all resumable sessions."""
    try:
        sessions = resume_manager.list_resumable_sessions()
        
        print(f"\n{lang_manager.get_message('resumable_sessions')}:")
        print_session_table(sessions, lang_manager)
        
        if sessions:
            print(f"\n{lang_manager.get_message('total_sessions')}: {len(sessions)}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error listing sessions: {e}")
        return 1


def cmd_session_info(args: argparse.Namespace, resume_manager: ResumeManager,
                    lang_manager: LanguageManager) -> int:
    """Show detailed information about a session."""
    try:
        session_id = args.session_id
        
        # Get session info
        session_info = resume_manager.parallel_manager.get_session_info(session_id)
        if not session_info:
            print(f"❌ Session {session_id} not found")
            return 1
        
        # Get resume preview
        preview = resume_manager.get_resume_preview(session_id)
        
        print(f"\n📊 Session Information: {session_id}")
        print("=" * 50)
        
        # Basic info
        print(f"Status: {session_info['status']}")
        print(f"Created: {session_info['created_at']}")
        print(f"Updated: {session_info['updated_at']}")
        print(f"Progress: {session_info['progress']}%")
        
        # Document counts
        print(f"\nDocuments:")
        print(f"  Total: {session_info['total_documents']}")
        print(f"  Completed: {session_info['completed_documents']}")
        print(f"  Failed: {session_info['failed_documents']}")
        print(f"  Remaining: {session_info['total_documents'] - session_info['completed_documents']}")
        
        # Batch info
        print(f"\nBatches:")
        print(f"  Total: {session_info['total_batches']}")
        print(f"  Incomplete: {session_info['incomplete_batches']}")
        
        # Resume preview
        if preview:
            if preview.get("estimated_time_remaining"):
                print(f"\nEstimated time remaining: {preview['estimated_time_remaining']}")
            
            if preview.get("issues"):
                print(f"\n⚠️  Resume Issues:")
                for issue in preview["issues"]:
                    print(f"  - {issue}")
            else:
                print(f"\n✅ Ready to resume")
        
        # Paths
        print(f"\nPaths:")
        print(f"  Temp dir: {session_info.get('temp_dir', 'N/A')}")
        print(f"  Output dir: {session_info.get('output_dir', 'N/A')}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error getting session info: {e}")
        return 1


def cmd_resume_session(args: argparse.Namespace, resume_manager: ResumeManager,
                      lang_manager: LanguageManager) -> int:
    """Resume a session."""
    try:
        session_id = args.session_id
        force = args.force
        
        print(f"🔄 Resuming session {session_id}...")
        
        # Attempt resume
        success, error = resume_manager.resume_session(session_id, force=force)
        
        if success:
            print(f"✅ Session {session_id} resumed successfully")
            return 0
        else:
            print(f"❌ Failed to resume session: {error}")
            if not force and "issues found" in str(error):
                print("\n💡 Use --force to resume despite issues")
            return 1
            
    except Exception as e:
        print(f"❌ Error resuming session: {e}")
        return 1


def cmd_detect_completed(args: argparse.Namespace, resume_manager: ResumeManager,
                        lang_manager: LanguageManager) -> int:
    """Detect completed work for a session."""
    try:
        session_id = args.session_id
        
        print(f"🔍 Detecting completed work for session {session_id}...")
        
        completed_count, error = resume_manager.detect_and_update_completed_work(session_id)
        
        if error:
            print(f"❌ Error: {error}")
            return 1
        
        print(f"✅ Found {completed_count} completed documents")
        return 0
        
    except Exception as e:
        print(f"❌ Error detecting completed work: {e}")
        return 1


def cmd_cleanup_session(args: argparse.Namespace, resume_manager: ResumeManager,
                       lang_manager: LanguageManager) -> int:
    """Clean up a failed session."""
    try:
        session_id = args.session_id
        keep_results = not args.delete_results
        
        # Confirm cleanup
        if not args.yes:
            response = input(f"Are you sure you want to clean up session {session_id}? (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("Cleanup cancelled")
                return 0
        
        print(f"🧹 Cleaning up session {session_id}...")
        
        success, error = resume_manager.cleanup_failed_session(session_id, keep_results=keep_results)
        
        if success:
            print(f"✅ Session {session_id} cleaned up successfully")
            return 0
        else:
            print(f"❌ Failed to clean up session: {error}")
            return 1
            
    except Exception as e:
        print(f"❌ Error cleaning up session: {e}")
        return 1


def cmd_export_report(args: argparse.Namespace, resume_manager: ResumeManager,
                     lang_manager: LanguageManager) -> int:
    """Export session report."""
    try:
        session_id = args.session_id
        output_file = args.output
        
        print(f"📄 Exporting report for session {session_id}...")
        
        success, result = resume_manager.export_session_report(session_id, output_file)
        
        if success:
            print(f"✅ Report exported to: {result}")
            return 0
        else:
            print(f"❌ Failed to export report: {result}")
            return 1
            
    except Exception as e:
        print(f"❌ Error exporting report: {e}")
        return 1


def cmd_show_logs(args: argparse.Namespace, resume_manager: ResumeManager,
                 lang_manager: LanguageManager) -> int:
    """Show session logs."""
    try:
        session_id = args.session_id
        
        print(f"📋 Logs for session {session_id}:")
        print("=" * 40)
        
        logs = resume_manager.get_session_logs(session_id)
        
        if "error" in logs:
            print(f"❌ Error: {logs['error']}")
            return 1
        
        log_files = logs.get("log_files", [])
        
        if not log_files:
            print("No log files found")
            return 0
        
        for i, log_file in enumerate(log_files, 1):
            if "error" in log_file:
                print(f"\n{i}. {log_file['file_path']}")
                print(f"   Error: {log_file['error']}")
                continue
            
            print(f"\n{i}. {log_file['file_path']}")
            print(f"   Size: {log_file.get('file_size', 0)} bytes")
            print(f"   Modified: {log_file.get('modified_time', 'N/A')}")
            
            if args.tail and log_file.get("last_lines"):
                print("   Last lines:")
                for line in log_file["last_lines"]:
                    print(f"     {line}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error showing logs: {e}")
        return 1


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="ROB Assessment Resume Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                           # List all resumable sessions
  %(prog)s info SESSION_ID                # Show session details
  %(prog)s resume SESSION_ID              # Resume a session
  %(prog)s resume SESSION_ID --force      # Force resume despite issues
  %(prog)s detect SESSION_ID              # Detect completed work
  %(prog)s cleanup SESSION_ID             # Clean up failed session
  %(prog)s export SESSION_ID              # Export session report
  %(prog)s logs SESSION_ID --tail         # Show session logs
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        default="config/config.json",
        help="Path to configuration file (default: config/config.json)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all resumable sessions")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show detailed session information")
    info_parser.add_argument("session_id", help="Session ID to show info for")
    
    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume a session")
    resume_parser.add_argument("session_id", help="Session ID to resume")
    resume_parser.add_argument("--force", action="store_true", 
                              help="Force resume despite issues")
    
    # Detect command
    detect_parser = subparsers.add_parser("detect", help="Detect completed work")
    detect_parser.add_argument("session_id", help="Session ID to check")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up failed session")
    cleanup_parser.add_argument("session_id", help="Session ID to clean up")
    cleanup_parser.add_argument("--delete-results", action="store_true",
                               help="Also delete any completed results")
    cleanup_parser.add_argument("--yes", "-y", action="store_true",
                               help="Skip confirmation prompt")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export session report")
    export_parser.add_argument("session_id", help="Session ID to export")
    export_parser.add_argument("--output", "-o", help="Output file path")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show session logs")
    logs_parser.add_argument("session_id", help="Session ID to show logs for")
    logs_parser.add_argument("--tail", action="store_true",
                            help="Show last lines of each log file")
    
    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Check if config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("Please provide a valid configuration file path with --config")
        return 1
    
    try:
        # Initialize managers
        resume_manager = ResumeManager(str(config_path))
        lang_manager = setup_language_manager()
        
        # Execute command
        command_map = {
            "list": cmd_list_sessions,
            "info": cmd_session_info,
            "resume": cmd_resume_session,
            "detect": cmd_detect_completed,
            "cleanup": cmd_cleanup_session,
            "export": cmd_export_report,
            "logs": cmd_show_logs
        }
        
        command_func = command_map.get(args.command)
        if command_func:
            return command_func(args, resume_manager, lang_manager)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())