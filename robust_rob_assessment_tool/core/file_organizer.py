"""
File organization utilities for enhanced output management.

This module provides utilities for creating organized directory structures,
managing file naming conventions, and handling cleanup operations.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import logging
from dataclasses import dataclass


@dataclass
class DirectoryStructure:
    """Represents the organized directory structure for outputs."""
    base_output_dir: str
    session_dir: str
    results_dir: str
    temp_dir: str
    logs_dir: str
    backup_dir: str
    timestamp: str


class FileOrganizer:
    """
    Manages file organization and directory structure for ROB assessment outputs.
    
    This class handles:
    - Timestamp-based output organization
    - Clear naming conventions for results and temporary files
    - Automatic directory creation and cleanup utilities
    """
    
    def __init__(self, base_output_dir: str = "output"):
        """
        Initialize the file organizer.
        
        Args:
            base_output_dir: Base directory for all outputs
        """
        self.base_output_dir = Path(base_output_dir)
        self.logger = logging.getLogger(__name__)
        
    def create_session_structure(self, session_id: Optional[str] = None) -> DirectoryStructure:
        """
        Create organized directory structure for a new assessment session.
        
        Args:
            session_id: Optional custom session ID, defaults to timestamp
            
        Returns:
            DirectoryStructure: Object containing all directory paths
        """
        # Generate timestamp-based session identifier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if session_id is None:
            session_id = f"rob_assessment_{timestamp}"
        
        # Create directory structure
        session_dir = self.base_output_dir / session_id
        results_dir = session_dir / "results"
        temp_dir = session_dir / "temp"
        logs_dir = session_dir / "logs"
        backup_dir = session_dir / "backup"
        
        # Create all directories
        directories = [session_dir, results_dir, temp_dir, logs_dir, backup_dir]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")
        
        # Create directory structure object
        structure = DirectoryStructure(
            base_output_dir=str(self.base_output_dir),
            session_dir=str(session_dir),
            results_dir=str(results_dir),
            temp_dir=str(temp_dir),
            logs_dir=str(logs_dir),
            backup_dir=str(backup_dir),
            timestamp=timestamp
        )
        
        # Save directory structure info
        self._save_structure_info(structure)
        
        return structure
    
    def get_result_filename(self, base_name: str, file_type: str, 
                           timestamp: Optional[str] = None) -> str:
        """
        Generate standardized filename for result files.
        
        Args:
            base_name: Base name for the file (e.g., "rob_assessment")
            file_type: File type/extension (e.g., "xlsx", "html", "json")
            timestamp: Optional timestamp, defaults to current time
            
        Returns:
            str: Standardized filename
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{base_name}_{timestamp}.{file_type}"
    
    def get_temp_filename(self, prefix: str, suffix: str = "tmp") -> str:
        """
        Generate standardized filename for temporary files.
        
        Args:
            prefix: Prefix for the temporary file
            suffix: File suffix/extension
            
        Returns:
            str: Standardized temporary filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{prefix}_{timestamp}.{suffix}"
    
    def get_batch_filename(self, batch_id: str, file_type: str) -> str:
        """
        Generate standardized filename for batch result files.
        
        Args:
            batch_id: Unique batch identifier
            file_type: File type/extension
            
        Returns:
            str: Standardized batch filename
        """
        return f"batch_{batch_id}_results.{file_type}"
    
    def organize_batch_results(self, session_structure: DirectoryStructure, 
                              batch_files: List[str]) -> Dict[str, str]:
        """
        Organize batch result files into proper directory structure.
        
        Args:
            session_structure: Directory structure for the session
            batch_files: List of batch result file paths
            
        Returns:
            Dict[str, str]: Mapping of original paths to organized paths
        """
        organized_files = {}
        results_dir = Path(session_structure.results_dir)
        
        # Create subdirectory for batch results
        batch_results_dir = results_dir / "batch_results"
        batch_results_dir.mkdir(exist_ok=True)
        
        for batch_file in batch_files:
            batch_path = Path(batch_file)
            if batch_path.exists():
                # Generate organized filename
                organized_filename = self._get_organized_batch_name(batch_path.name)
                organized_path = batch_results_dir / organized_filename
                
                # Move file to organized location
                shutil.move(str(batch_path), str(organized_path))
                organized_files[batch_file] = str(organized_path)
                
                self.logger.info(f"Organized batch file: {batch_file} -> {organized_path}")
        
        return organized_files
    
    def cleanup_temp_files(self, session_structure: DirectoryStructure, 
                          keep_logs: bool = True) -> List[str]:
        """
        Clean up temporary files while preserving important results.
        
        Args:
            session_structure: Directory structure for the session
            keep_logs: Whether to keep log files
            
        Returns:
            List[str]: List of cleaned up file paths
        """
        cleaned_files = []
        temp_dir = Path(session_structure.temp_dir)
        
        if temp_dir.exists():
            # Clean up temporary files
            for temp_file in temp_dir.rglob("*"):
                if temp_file.is_file():
                    temp_file.unlink()
                    cleaned_files.append(str(temp_file))
            
            # Remove empty directories
            for temp_dir_path in temp_dir.rglob("*"):
                if temp_dir_path.is_dir() and not any(temp_dir_path.iterdir()):
                    temp_dir_path.rmdir()
                    cleaned_files.append(str(temp_dir_path))
        
        # Optionally clean up logs
        if not keep_logs:
            logs_dir = Path(session_structure.logs_dir)
            if logs_dir.exists():
                for log_file in logs_dir.rglob("*.log"):
                    log_file.unlink()
                    cleaned_files.append(str(log_file))
        
        self.logger.info(f"Cleaned up {len(cleaned_files)} temporary files")
        return cleaned_files
    
    def create_backup(self, session_structure: DirectoryStructure, 
                     backup_name: Optional[str] = None) -> str:
        """
        Create backup of session results.
        
        Args:
            session_structure: Directory structure for the session
            backup_name: Optional custom backup name
            
        Returns:
            str: Path to created backup
        """
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        results_dir = Path(session_structure.results_dir)
        backup_dir = Path(session_structure.backup_dir)
        backup_path = backup_dir / backup_name
        
        if results_dir.exists():
            shutil.copytree(results_dir, backup_path, dirs_exist_ok=True)
            self.logger.info(f"Created backup: {backup_path}")
            return str(backup_path)
        else:
            raise FileNotFoundError(f"Results directory not found: {results_dir}")
    
    def get_session_info(self, session_dir: str) -> Dict[str, any]:
        """
        Get information about a session directory.
        
        Args:
            session_dir: Path to session directory
            
        Returns:
            Dict[str, any]: Session information
        """
        session_path = Path(session_dir)
        info_file = session_path / "session_info.json"
        
        if info_file.exists():
            with open(info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._generate_session_info(session_path)
    
    def list_sessions(self) -> List[Dict[str, any]]:
        """
        List all available assessment sessions.
        
        Returns:
            List[Dict[str, any]]: List of session information
        """
        sessions = []
        
        if self.base_output_dir.exists():
            for session_dir in self.base_output_dir.iterdir():
                if session_dir.is_dir():
                    try:
                        session_info = self.get_session_info(str(session_dir))
                        sessions.append(session_info)
                    except Exception as e:
                        self.logger.warning(f"Could not read session info for {session_dir}: {e}")
        
        # Sort by creation time (newest first)
        sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return sessions
    
    def _save_structure_info(self, structure: DirectoryStructure) -> None:
        """Save directory structure information to session directory."""
        info_file = Path(structure.session_dir) / "session_info.json"
        
        info_data = {
            "session_id": Path(structure.session_dir).name,
            "created_at": datetime.now().isoformat(),
            "timestamp": structure.timestamp,
            "directories": {
                "base_output_dir": structure.base_output_dir,
                "session_dir": structure.session_dir,
                "results_dir": structure.results_dir,
                "temp_dir": structure.temp_dir,
                "logs_dir": structure.logs_dir,
                "backup_dir": structure.backup_dir
            }
        }
        
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info_data, f, indent=2, ensure_ascii=False)
    
    def _get_organized_batch_name(self, original_name: str) -> str:
        """Generate organized name for batch result file."""
        # Extract batch ID from filename if possible
        if "batch_" in original_name:
            return original_name
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name_parts = original_name.split('.')
            if len(name_parts) > 1:
                base_name = '.'.join(name_parts[:-1])
                extension = name_parts[-1]
                return f"batch_{base_name}_{timestamp}.{extension}"
            else:
                return f"batch_{original_name}_{timestamp}"
    
    def _generate_session_info(self, session_path: Path) -> Dict[str, any]:
        """Generate session information from directory structure."""
        stat = session_path.stat()
        
        return {
            "session_id": session_path.name,
            "session_dir": str(session_path),
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size_bytes": sum(f.stat().st_size for f in session_path.rglob('*') if f.is_file())
        }


class CleanupUtility:
    """
    Utility class for cleanup operations and maintenance.
    """
    
    def __init__(self, base_output_dir: str = "output"):
        """
        Initialize cleanup utility.
        
        Args:
            base_output_dir: Base directory for outputs
        """
        self.base_output_dir = Path(base_output_dir)
        self.logger = logging.getLogger(__name__)
    
    def cleanup_old_sessions(self, days_old: int = 30, 
                           keep_recent: int = 5) -> List[str]:
        """
        Clean up old session directories.
        
        Args:
            days_old: Remove sessions older than this many days
            keep_recent: Always keep this many most recent sessions
            
        Returns:
            List[str]: List of removed session directories
        """
        if not self.base_output_dir.exists():
            return []
        
        # Get all session directories with their creation times
        sessions = []
        for session_dir in self.base_output_dir.iterdir():
            if session_dir.is_dir():
                stat = session_dir.stat()
                sessions.append((session_dir, stat.st_ctime))
        
        # Sort by creation time (newest first)
        sessions.sort(key=lambda x: x[1], reverse=True)
        
        # Keep recent sessions
        sessions_to_check = sessions[keep_recent:]
        
        # Remove old sessions
        removed_sessions = []
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for session_dir, creation_time in sessions_to_check:
            if creation_time < cutoff_time:
                try:
                    shutil.rmtree(session_dir)
                    removed_sessions.append(str(session_dir))
                    self.logger.info(f"Removed old session: {session_dir}")
                except Exception as e:
                    self.logger.error(f"Failed to remove session {session_dir}: {e}")
        
        return removed_sessions
    
    def cleanup_temp_directories(self) -> List[str]:
        """
        Clean up all temporary directories across sessions.
        
        Returns:
            List[str]: List of cleaned up directories
        """
        cleaned_dirs = []
        
        if not self.base_output_dir.exists():
            return cleaned_dirs
        
        for session_dir in self.base_output_dir.iterdir():
            if session_dir.is_dir():
                temp_dir = session_dir / "temp"
                if temp_dir.exists():
                    try:
                        shutil.rmtree(temp_dir)
                        temp_dir.mkdir()  # Recreate empty temp directory
                        cleaned_dirs.append(str(temp_dir))
                        self.logger.info(f"Cleaned temp directory: {temp_dir}")
                    except Exception as e:
                        self.logger.error(f"Failed to clean temp directory {temp_dir}: {e}")
        
        return cleaned_dirs
    
    def get_disk_usage(self) -> Dict[str, any]:
        """
        Get disk usage information for output directories.
        
        Returns:
            Dict[str, any]: Disk usage information
        """
        if not self.base_output_dir.exists():
            return {"total_size": 0, "sessions": []}
        
        total_size = 0
        session_sizes = []
        
        for session_dir in self.base_output_dir.iterdir():
            if session_dir.is_dir():
                session_size = sum(f.stat().st_size for f in session_dir.rglob('*') if f.is_file())
                total_size += session_size
                
                session_sizes.append({
                    "session_id": session_dir.name,
                    "size_bytes": session_size,
                    "size_mb": round(session_size / (1024 * 1024), 2)
                })
        
        # Sort by size (largest first)
        session_sizes.sort(key=lambda x: x["size_bytes"], reverse=True)
        
        return {
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
            "session_count": len(session_sizes),
            "sessions": session_sizes
        }