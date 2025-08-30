"""
Resume functionality for ROB assessments.

This module provides high-level resume functionality with completed work detection,
state restoration, and progress continuation for interrupted ROB assessments.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from .state_manager import StateManager, AssessmentState, BatchState, DocumentState
from .parallel_controller import ParallelROBManager

logger = logging.getLogger(__name__)


class ResumeManager:
    """
    Manages resume functionality for ROB assessments.
    
    This class provides high-level methods for resuming interrupted assessments,
    detecting completed work, and restoring processing state.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize resume manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.parallel_manager = ParallelROBManager(str(config_path))
        self.state_manager = self.parallel_manager.state_manager
        
        # Configure logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def list_resumable_sessions(self) -> List[Dict[str, Any]]:
        """
        List all sessions that can be resumed.
        
        Returns:
            List[Dict[str, Any]]: List of resumable sessions with metadata
        """
        all_sessions = self.state_manager.list_available_states()
        resumable_sessions = []
        
        for session_info in all_sessions:
            # Only include sessions that are not completed
            if session_info.get("status") not in ["completed"]:
                # Add resumability information
                session_info["is_resumable"] = True
                session_info["resume_reason"] = self._get_resume_reason(session_info)
                resumable_sessions.append(session_info)
        
        return resumable_sessions
    
    def _get_resume_reason(self, session_info: Dict[str, Any]) -> str:
        """Get human-readable reason why session can be resumed."""
        status = session_info.get("status", "unknown")
        
        if status == "running":
            return "Assessment was interrupted while running"
        elif status == "paused":
            return "Assessment was manually paused"
        elif status == "failed":
            return "Assessment failed and can be retried"
        elif status == "initializing":
            return "Assessment was interrupted during initialization"
        else:
            return f"Assessment in {status} state"
    
    def get_resume_preview(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get preview information for resuming a session.
        
        Args:
            session_id: Session ID to preview
            
        Returns:
            Optional[Dict[str, Any]]: Resume preview information or None if not found
        """
        try:
            # Load assessment state
            assessment_state, error = self.state_manager.load_state(session_id, validate=True)
            if not assessment_state:
                return None
            
            # Analyze current state
            incomplete_batches = assessment_state.get_incomplete_batches()
            
            # Calculate work remaining
            total_docs = assessment_state.total_documents
            completed_docs = assessment_state.completed_documents
            remaining_docs = total_docs - completed_docs
            
            # Estimate time remaining (if we have timing data)
            estimated_time = self._estimate_remaining_time(assessment_state)
            
            # Check for potential issues
            issues = self._check_resume_issues(assessment_state)
            
            preview = {
                "session_id": session_id,
                "status": assessment_state.status,
                "created_at": assessment_state.created_at.isoformat(),
                "updated_at": assessment_state.updated_at.isoformat(),
                "progress": {
                    "total_documents": total_docs,
                    "completed_documents": completed_docs,
                    "remaining_documents": remaining_docs,
                    "progress_percentage": assessment_state.get_overall_progress()
                },
                "batches": {
                    "total_batches": len(assessment_state.batches),
                    "incomplete_batches": len(incomplete_batches),
                    "batch_details": [
                        {
                            "batch_id": batch.batch_id,
                            "status": batch.status,
                            "documents_count": len(batch.documents),
                            "completed_count": len(batch.get_completed_documents()),
                            "progress": batch.progress
                        }
                        for batch in incomplete_batches
                    ]
                },
                "estimated_time_remaining": estimated_time,
                "issues": issues,
                "can_resume": len(issues) == 0
            }
            
            return preview
            
        except Exception as e:
            self.logger.error(f"Error getting resume preview: {e}")
            return None
    
    def _estimate_remaining_time(self, assessment_state: AssessmentState) -> Optional[str]:
        """Estimate remaining processing time based on completed work."""
        try:
            completed_batches = [
                batch for batch in assessment_state.batches 
                if batch.status == "completed" and batch.start_time and batch.end_time
            ]
            
            if not completed_batches:
                return None
            
            # Calculate average processing time per document
            total_time = 0
            total_docs = 0
            
            for batch in completed_batches:
                if batch.start_time and batch.end_time:
                    batch_time = (batch.end_time - batch.start_time).total_seconds()
                    batch_docs = len(batch.documents)
                    total_time += batch_time
                    total_docs += batch_docs
            
            if total_docs == 0:
                return None
            
            avg_time_per_doc = total_time / total_docs
            remaining_docs = assessment_state.total_documents - assessment_state.completed_documents
            estimated_seconds = avg_time_per_doc * remaining_docs
            
            # Format time estimate
            if estimated_seconds < 60:
                return f"{int(estimated_seconds)} seconds"
            elif estimated_seconds < 3600:
                return f"{int(estimated_seconds / 60)} minutes"
            else:
                hours = int(estimated_seconds / 3600)
                minutes = int((estimated_seconds % 3600) / 60)
                return f"{hours}h {minutes}m"
                
        except Exception as e:
            self.logger.warning(f"Error estimating time: {e}")
            return None
    
    def _check_resume_issues(self, assessment_state: AssessmentState) -> List[str]:
        """Check for potential issues that might prevent successful resume."""
        issues = []
        
        try:
            # Check if directories still exist
            if assessment_state.temp_dir and not Path(assessment_state.temp_dir).exists():
                issues.append(f"Temporary directory not found: {assessment_state.temp_dir}")
            
            if assessment_state.output_dir and not Path(assessment_state.output_dir).exists():
                issues.append(f"Output directory not found: {assessment_state.output_dir}")
            
            # Check configuration validity
            config = assessment_state.config
            if not config:
                issues.append("Configuration is missing")
            else:
                # Check required config sections
                required_sections = ["paths", "processing", "llm_models"]
                for section in required_sections:
                    if section not in config:
                        issues.append(f"Missing configuration section: {section}")
                
                # Check input folder
                if "paths" in config and "input_folder" in config["paths"]:
                    input_folder = Path(config["paths"]["input_folder"])
                    if not input_folder.exists():
                        issues.append(f"Input folder not found: {input_folder}")
            
            # Check for running processes that might conflict
            temp_dir = Path(assessment_state.temp_dir) if assessment_state.temp_dir else None
            if temp_dir:
                pid_files = list(temp_dir.glob(f"{assessment_state.session_id}_*_worker.pid"))
                if pid_files:
                    issues.append(f"Found {len(pid_files)} potentially running worker processes")
            
            # Check batch consistency
            for batch in assessment_state.batches:
                if not batch.documents:
                    issues.append(f"Batch {batch.batch_id} has no documents")
                
                # Check if batch output directory exists
                if batch.output_dir and not Path(batch.output_dir).exists():
                    issues.append(f"Batch output directory not found: {batch.output_dir}")
        
        except Exception as e:
            issues.append(f"Error checking resume issues: {e}")
        
        return issues
    
    def resume_session(self, session_id: str, 
                      force: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Resume an assessment session.
        
        Args:
            session_id: Session ID to resume
            force: Whether to force resume despite issues
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            # Get resume preview to check for issues
            preview = self.get_resume_preview(session_id)
            if not preview:
                return False, f"Session {session_id} not found or invalid"
            
            # Check for issues
            if preview["issues"] and not force:
                issues_str = "\n".join(f"  - {issue}" for issue in preview["issues"])
                return False, f"Resume issues found:\n{issues_str}\n\nUse force=True to resume anyway"
            
            # Perform the resume
            print(f"🔄 Resuming session {session_id}...")
            print(f"  - Progress: {preview['progress']['progress_percentage']}%")
            print(f"  - Remaining: {preview['progress']['remaining_documents']} documents")
            
            if preview["issues"]:
                print("⚠️  Resuming despite issues:")
                for issue in preview["issues"]:
                    print(f"    - {issue}")
            
            # Use parallel manager to resume
            success = self.parallel_manager.resume_assessment(session_id=session_id)
            
            if success:
                return True, None
            else:
                return False, "Resume operation failed"
                
        except Exception as e:
            error_msg = f"Error resuming session: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def detect_and_update_completed_work(self, session_id: str) -> Tuple[int, Optional[str]]:
        """
        Detect completed work for a session and update state.
        
        Args:
            session_id: Session ID to check
            
        Returns:
            Tuple[int, Optional[str]]: (completed_count, error_message)
        """
        try:
            # Load assessment state
            assessment_state, error = self.state_manager.load_state(session_id)
            if not assessment_state:
                return 0, f"Failed to load session: {error}"
            
            # Set up parallel manager with this session
            self.parallel_manager.assessment_state = assessment_state
            self.parallel_manager.session_id = assessment_state.session_id
            self.parallel_manager.config = assessment_state.config
            self.parallel_manager.batches = self.parallel_manager._convert_assessment_batches_to_internal(
                assessment_state.batches
            )
            
            # Detect completed work
            incomplete_batches = [
                batch for batch in self.parallel_manager.batches
                if batch.status in ["pending", "running", "paused"]
            ]
            
            if incomplete_batches:
                self.parallel_manager._detect_completed_work(incomplete_batches)
                
                # Count newly detected completed documents
                updated_state = self.parallel_manager.assessment_state
                if updated_state:
                    updated_state.update_counters()
                    return updated_state.completed_documents, None
            
            return assessment_state.completed_documents, None
            
        except Exception as e:
            error_msg = f"Error detecting completed work: {e}"
            self.logger.error(error_msg)
            return 0, error_msg
    
    def cleanup_failed_session(self, session_id: str, 
                              keep_results: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Clean up a failed session.
        
        Args:
            session_id: Session ID to clean up
            keep_results: Whether to keep any completed results
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            # Load session info
            session_info = self.parallel_manager.get_session_info(session_id)
            if not session_info:
                return False, f"Session {session_id} not found"
            
            print(f"🧹 Cleaning up failed session {session_id}...")
            
            # Stop any running processes
            self.parallel_manager.session_id = session_id
            self.parallel_manager.stop_all_processes()
            
            # Delete session
            success = self.parallel_manager.delete_session(session_id, create_backup=True)
            
            if success:
                print(f"✅ Session {session_id} cleaned up successfully")
                return True, None
            else:
                return False, "Failed to delete session"
                
        except Exception as e:
            error_msg = f"Error cleaning up session: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_session_logs(self, session_id: str) -> Dict[str, Any]:
        """
        Get log information for a session.
        
        Args:
            session_id: Session ID to get logs for
            
        Returns:
            Dict[str, Any]: Log information
        """
        try:
            # Load assessment state to get temp directory
            assessment_state, error = self.state_manager.load_state(session_id, validate=False)
            if not assessment_state or not assessment_state.temp_dir:
                return {"error": "Session not found or no temp directory"}
            
            temp_dir = Path(assessment_state.temp_dir)
            log_files = []
            
            # Find log files for this session
            for log_file in temp_dir.glob(f"{session_id}_*_worker.log"):
                try:
                    stat = log_file.stat()
                    
                    # Read last few lines of log
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        last_lines = lines[-10:] if len(lines) > 10 else lines
                    
                    log_info = {
                        "file_path": str(log_file),
                        "file_size": stat.st_size,
                        "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "last_lines": [line.strip() for line in last_lines]
                    }
                    
                    log_files.append(log_info)
                    
                except Exception as e:
                    log_files.append({
                        "file_path": str(log_file),
                        "error": f"Could not read log: {e}"
                    })
            
            return {
                "session_id": session_id,
                "log_files": log_files,
                "total_log_files": len(log_files)
            }
            
        except Exception as e:
            return {"error": f"Error getting logs: {e}"}
    
    def export_session_report(self, session_id: str, 
                             output_file: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Export detailed session report.
        
        Args:
            session_id: Session ID to export
            output_file: Output file path (optional)
            
        Returns:
            Tuple[bool, Optional[str]]: (success, file_path_or_error)
        """
        try:
            # Get session info and preview
            session_info = self.parallel_manager.get_session_info(session_id)
            preview = self.get_resume_preview(session_id)
            logs = self.get_session_logs(session_id)
            
            if not session_info:
                return False, f"Session {session_id} not found"
            
            # Create report
            report = {
                "session_id": session_id,
                "generated_at": datetime.now().isoformat(),
                "session_info": session_info,
                "resume_preview": preview,
                "logs_summary": {
                    "total_log_files": logs.get("total_log_files", 0),
                    "log_files": [
                        {
                            "file_path": log["file_path"],
                            "file_size": log.get("file_size", 0),
                            "modified_time": log.get("modified_time")
                        }
                        for log in logs.get("log_files", [])
                        if "error" not in log
                    ]
                }
            }
            
            # Determine output file path
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"session_report_{session_id}_{timestamp}.json"
            
            output_path = Path(output_file)
            
            # Write report
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return True, str(output_path)
            
        except Exception as e:
            error_msg = f"Error exporting report: {e}"
            self.logger.error(error_msg)
            return False, error_msg