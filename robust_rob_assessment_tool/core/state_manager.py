"""
State persistence and management system for ROB assessments.

This module provides comprehensive state saving, loading, validation, and recovery
functionality for checkpoint and resume operations in parallel ROB assessments.
"""

import json
import pickle
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StateFormat(Enum):
    """Supported state file formats."""
    JSON = "json"
    PICKLE = "pickle"


class StateValidationError(Exception):
    """Raised when state validation fails."""
    pass


class StateCorruptionError(Exception):
    """Raised when state file is corrupted."""
    pass


@dataclass
class DocumentState:
    """State information for a single document."""
    document_path: str
    status: str  # "pending", "processing", "completed", "failed", "skipped"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result_file: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentState':
        """Create from dictionary."""
        if data.get('start_time'):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)


@dataclass
class BatchState:
    """State information for a processing batch."""
    batch_id: str
    status: str  # "pending", "running", "completed", "failed", "paused"
    documents: List[DocumentState] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: int = 0  # Percentage completion
    worker_pid: Optional[int] = None
    config_file: Optional[str] = None
    output_dir: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        data['documents'] = [doc.to_dict() for doc in self.documents]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchState':
        """Create from dictionary."""
        if data.get('start_time'):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        
        documents = []
        for doc_data in data.get('documents', []):
            documents.append(DocumentState.from_dict(doc_data))
        data['documents'] = documents
        
        return cls(**data)
    
    def get_completed_documents(self) -> List[DocumentState]:
        """Get list of completed documents."""
        return [doc for doc in self.documents if doc.status == "completed"]
    
    def get_failed_documents(self) -> List[DocumentState]:
        """Get list of failed documents."""
        return [doc for doc in self.documents if doc.status == "failed"]
    
    def get_pending_documents(self) -> List[DocumentState]:
        """Get list of pending documents."""
        return [doc for doc in self.documents if doc.status == "pending"]
    
    def update_progress(self) -> None:
        """Update progress percentage based on document states."""
        if not self.documents:
            self.progress = 0
            return
        
        completed = len([doc for doc in self.documents 
                        if doc.status in ["completed", "skipped"]])
        self.progress = int((completed / len(self.documents)) * 100)


@dataclass
class AssessmentState:
    """Complete state information for an assessment session."""
    session_id: str
    created_at: datetime
    updated_at: datetime
    status: str  # "initializing", "running", "paused", "completed", "failed"
    config: Dict[str, Any]
    batches: List[BatchState] = field(default_factory=list)
    total_documents: int = 0
    completed_documents: int = 0
    failed_documents: int = 0
    temp_dir: Optional[str] = None
    output_dir: Optional[str] = None
    cost_tracking: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['batches'] = [batch.to_dict() for batch in self.batches]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssessmentState':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        batches = []
        for batch_data in data.get('batches', []):
            batches.append(BatchState.from_dict(batch_data))
        data['batches'] = batches
        
        return cls(**data)
    
    def update_counters(self) -> None:
        """Update document counters based on batch states."""
        self.total_documents = 0
        self.completed_documents = 0
        self.failed_documents = 0
        
        for batch in self.batches:
            self.total_documents += len(batch.documents)
            self.completed_documents += len(batch.get_completed_documents())
            self.failed_documents += len(batch.get_failed_documents())
    
    def get_overall_progress(self) -> int:
        """Get overall progress percentage."""
        if self.total_documents == 0:
            return 0
        return int((self.completed_documents / self.total_documents) * 100)
    
    def get_incomplete_batches(self) -> List[BatchState]:
        """Get list of incomplete batches."""
        return [batch for batch in self.batches 
                if batch.status in ["pending", "running", "paused"]]


class StateManager:
    """
    Manages state persistence, validation, and recovery for ROB assessments.
    
    This class provides comprehensive functionality for saving and loading
    assessment state, validating state integrity, and recovering from corruption.
    """
    
    def __init__(self, state_dir: Union[str, Path], format: StateFormat = StateFormat.JSON):
        """
        Initialize state manager.
        
        Args:
            state_dir: Directory for storing state files
            format: State file format (JSON or PICKLE)
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.format = format
        self.backup_dir = self.state_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def save_state(self, state: AssessmentState, 
                   create_backup: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Save assessment state to file.
        
        Args:
            state: Assessment state to save
            create_backup: Whether to create backup of existing state
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            # Update timestamp
            state.updated_at = datetime.now()
            
            # Generate state file path
            state_file = self._get_state_file_path(state.session_id)
            
            # Create backup if requested and file exists
            if create_backup and state_file.exists():
                backup_success, backup_error = self._create_backup(state_file)
                if not backup_success:
                    self.logger.warning(f"Failed to create backup: {backup_error}")
            
            # Save state based on format
            if self.format == StateFormat.JSON:
                success, error = self._save_json_state(state, state_file)
            else:
                success, error = self._save_pickle_state(state, state_file)
            
            if success:
                # Create checksum file for integrity verification
                self._create_checksum_file(state_file)
                self.logger.info(f"State saved successfully: {state_file}")
            
            return success, error
            
        except Exception as e:
            error_msg = f"Unexpected error saving state: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def load_state(self, session_id: str, 
                   validate: bool = True) -> Tuple[Optional[AssessmentState], Optional[str]]:
        """
        Load assessment state from file.
        
        Args:
            session_id: Session ID to load
            validate: Whether to validate state integrity
            
        Returns:
            Tuple[Optional[AssessmentState], Optional[str]]: (state, error_message)
        """
        try:
            state_file = self._get_state_file_path(session_id)
            
            if not state_file.exists():
                return None, f"State file not found: {state_file}"
            
            # Validate file integrity if requested
            if validate:
                is_valid, validation_error = self._validate_file_integrity(state_file)
                if not is_valid:
                    # Try to recover from backup
                    recovery_state, recovery_error = self._attempt_recovery(session_id)
                    if recovery_state:
                        self.logger.warning(f"Recovered state from backup: {validation_error}")
                        return recovery_state, None
                    else:
                        return None, f"State validation failed: {validation_error}"
            
            # Load state based on format
            if self.format == StateFormat.JSON:
                state, error = self._load_json_state(state_file)
            else:
                state, error = self._load_pickle_state(state_file)
            
            if state:
                self.logger.info(f"State loaded successfully: {state_file}")
            
            return state, error
            
        except Exception as e:
            error_msg = f"Unexpected error loading state: {e}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def validate_state(self, state: AssessmentState) -> Tuple[bool, List[str]]:
        """
        Validate assessment state for consistency and completeness.
        
        Args:
            state: Assessment state to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        issues = []
        
        try:
            # Basic field validation
            if not state.session_id:
                issues.append("Missing session_id")
            
            if not state.config:
                issues.append("Missing configuration")
            
            if not state.batches:
                issues.append("No batches defined")
            
            # Validate batch consistency
            for i, batch in enumerate(state.batches):
                batch_issues = self._validate_batch_state(batch, i)
                issues.extend(batch_issues)
            
            # Validate document counts
            state.update_counters()
            calculated_total = sum(len(batch.documents) for batch in state.batches)
            if state.total_documents != calculated_total:
                issues.append(f"Document count mismatch: {state.total_documents} vs {calculated_total}")
            
            # Validate paths
            if state.temp_dir and not Path(state.temp_dir).exists():
                issues.append(f"Temp directory not found: {state.temp_dir}")
            
            if state.output_dir and not Path(state.output_dir).exists():
                issues.append(f"Output directory not found: {state.output_dir}")
            
            # Validate configuration
            config_issues = self._validate_config(state.config)
            issues.extend(config_issues)
            
        except Exception as e:
            issues.append(f"Validation error: {e}")
        
        return len(issues) == 0, issues
    
    def _validate_batch_state(self, batch: BatchState, batch_index: int) -> List[str]:
        """Validate individual batch state."""
        issues = []
        
        if not batch.batch_id:
            issues.append(f"Batch {batch_index}: Missing batch_id")
        
        if not batch.documents:
            issues.append(f"Batch {batch.batch_id}: No documents")
        
        # Validate document states
        for j, doc in enumerate(batch.documents):
            if not doc.document_path:
                issues.append(f"Batch {batch.batch_id}, Doc {j}: Missing document_path")
            
            if doc.status not in ["pending", "processing", "completed", "failed", "skipped"]:
                issues.append(f"Batch {batch.batch_id}, Doc {j}: Invalid status '{doc.status}'")
            
            # Check if completed documents have result files
            if doc.status == "completed" and not doc.result_file:
                issues.append(f"Batch {batch.batch_id}, Doc {j}: Completed but no result file")
        
        return issues
    
    def _validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration structure."""
        issues = []
        
        required_sections = ["paths", "processing", "llm_models"]
        for section in required_sections:
            if section not in config:
                issues.append(f"Missing config section: {section}")
        
        # Validate paths section
        if "paths" in config:
            required_paths = ["input_folder", "output_folder"]
            for path_key in required_paths:
                if path_key not in config["paths"]:
                    issues.append(f"Missing path config: {path_key}")
        
        return issues
    
    def list_available_states(self) -> List[Dict[str, Any]]:
        """
        List all available state files with metadata.
        
        Returns:
            List[Dict[str, Any]]: List of state file information
        """
        states = []
        
        # Find state files based on format
        if self.format == StateFormat.JSON:
            pattern = "state_*.json"
        else:
            pattern = "state_*.pkl"
        
        for state_file in self.state_dir.glob(pattern):
            try:
                # Extract session ID from filename
                session_id = state_file.stem.replace("state_", "")
                
                # Get file metadata
                stat = state_file.stat()
                
                state_info = {
                    "session_id": session_id,
                    "file_path": str(state_file),
                    "file_size": stat.st_size,
                    "modified_time": datetime.fromtimestamp(stat.st_mtime),
                    "format": self.format.value
                }
                
                # Try to load basic info without full validation
                try:
                    if self.format == StateFormat.JSON:
                        with open(state_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    else:
                        with open(state_file, 'rb') as f:
                            data = pickle.load(f)
                    
                    state_info.update({
                        "status": data.get("status", "unknown"),
                        "total_documents": data.get("total_documents", 0),
                        "completed_documents": data.get("completed_documents", 0),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at")
                    })
                    
                except Exception:
                    state_info["status"] = "corrupted"
                
                states.append(state_info)
                
            except Exception as e:
                self.logger.warning(f"Error reading state file {state_file}: {e}")
        
        # Sort by modification time (newest first)
        states.sort(key=lambda x: x["modified_time"], reverse=True)
        
        return states
    
    def delete_state(self, session_id: str, create_backup: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Delete state file for given session.
        
        Args:
            session_id: Session ID to delete
            create_backup: Whether to create backup before deletion
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            state_file = self._get_state_file_path(session_id)
            
            if not state_file.exists():
                return False, f"State file not found: {state_file}"
            
            # Create backup if requested
            if create_backup:
                backup_success, backup_error = self._create_backup(state_file)
                if not backup_success:
                    self.logger.warning(f"Failed to create backup: {backup_error}")
            
            # Delete state file
            state_file.unlink()
            
            # Delete checksum file if exists
            checksum_file = self._get_checksum_file_path(session_id)
            if checksum_file.exists():
                checksum_file.unlink()
            
            self.logger.info(f"State deleted: {state_file}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting state: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def cleanup_old_states(self, max_age_days: int = 30, 
                          keep_backups: bool = True) -> Tuple[int, List[str]]:
        """
        Clean up old state files.
        
        Args:
            max_age_days: Maximum age in days for state files
            keep_backups: Whether to keep backup files
            
        Returns:
            Tuple[int, List[str]]: (deleted_count, list_of_errors)
        """
        deleted_count = 0
        errors = []
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        try:
            # Clean up main state files
            if self.format == StateFormat.JSON:
                pattern = "state_*.json"
            else:
                pattern = "state_*.pkl"
            
            for state_file in self.state_dir.glob(pattern):
                try:
                    if state_file.stat().st_mtime < cutoff_time:
                        session_id = state_file.stem.replace("state_", "")
                        
                        # Create backup before deletion
                        if keep_backups:
                            self._create_backup(state_file)
                        
                        # Delete state and checksum files
                        state_file.unlink()
                        checksum_file = self._get_checksum_file_path(session_id)
                        if checksum_file.exists():
                            checksum_file.unlink()
                        
                        deleted_count += 1
                        self.logger.info(f"Cleaned up old state: {state_file}")
                        
                except Exception as e:
                    errors.append(f"Error deleting {state_file}: {e}")
            
            # Clean up old backups if not keeping them
            if not keep_backups:
                for backup_file in self.backup_dir.glob("*"):
                    try:
                        if backup_file.stat().st_mtime < cutoff_time:
                            backup_file.unlink()
                            deleted_count += 1
                    except Exception as e:
                        errors.append(f"Error deleting backup {backup_file}: {e}")
        
        except Exception as e:
            errors.append(f"Error during cleanup: {e}")
        
        return deleted_count, errors
    
    def _get_state_file_path(self, session_id: str) -> Path:
        """Get path for state file."""
        if self.format == StateFormat.JSON:
            return self.state_dir / f"state_{session_id}.json"
        else:
            return self.state_dir / f"state_{session_id}.pkl"
    
    def _get_checksum_file_path(self, session_id: str) -> Path:
        """Get path for checksum file."""
        return self.state_dir / f"state_{session_id}.checksum"
    
    def _save_json_state(self, state: AssessmentState, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Save state in JSON format."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)
            return True, None
        except Exception as e:
            return False, f"JSON save error: {e}"
    
    def _save_pickle_state(self, state: AssessmentState, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Save state in pickle format."""
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
            return True, None
        except Exception as e:
            return False, f"Pickle save error: {e}"
    
    def _load_json_state(self, file_path: Path) -> Tuple[Optional[AssessmentState], Optional[str]]:
        """Load state from JSON format."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            state = AssessmentState.from_dict(data)
            return state, None
        except Exception as e:
            return None, f"JSON load error: {e}"
    
    def _load_pickle_state(self, file_path: Path) -> Tuple[Optional[AssessmentState], Optional[str]]:
        """Load state from pickle format."""
        try:
            with open(file_path, 'rb') as f:
                state = pickle.load(f)
            return state, None
        except Exception as e:
            return None, f"Pickle load error: {e}"
    
    def _create_checksum_file(self, state_file: Path) -> None:
        """Create checksum file for integrity verification."""
        try:
            # Calculate SHA-256 checksum
            sha256_hash = hashlib.sha256()
            with open(state_file, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            checksum = sha256_hash.hexdigest()
            
            # Save checksum
            checksum_file = self._get_checksum_file_path(
                state_file.stem.replace("state_", "")
            )
            with open(checksum_file, 'w') as f:
                f.write(checksum)
                
        except Exception as e:
            self.logger.warning(f"Failed to create checksum: {e}")
    
    def _validate_file_integrity(self, state_file: Path) -> Tuple[bool, Optional[str]]:
        """Validate file integrity using checksum."""
        try:
            session_id = state_file.stem.replace("state_", "")
            checksum_file = self._get_checksum_file_path(session_id)
            
            if not checksum_file.exists():
                return True, None  # No checksum file, assume valid
            
            # Read stored checksum
            with open(checksum_file, 'r') as f:
                stored_checksum = f.read().strip()
            
            # Calculate current checksum
            sha256_hash = hashlib.sha256()
            with open(state_file, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            current_checksum = sha256_hash.hexdigest()
            
            if stored_checksum == current_checksum:
                return True, None
            else:
                return False, "Checksum mismatch - file may be corrupted"
                
        except Exception as e:
            return False, f"Checksum validation error: {e}"
    
    def _create_backup(self, state_file: Path) -> Tuple[bool, Optional[str]]:
        """Create backup of state file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{state_file.stem}_{timestamp}{state_file.suffix}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(state_file, backup_path)
            
            # Also backup checksum file if exists
            session_id = state_file.stem.replace("state_", "")
            checksum_file = self._get_checksum_file_path(session_id)
            if checksum_file.exists():
                backup_checksum_path = self.backup_dir / f"{checksum_file.stem}_{timestamp}{checksum_file.suffix}"
                shutil.copy2(checksum_file, backup_checksum_path)
            
            return True, None
            
        except Exception as e:
            return False, f"Backup creation error: {e}"
    
    def _attempt_recovery(self, session_id: str) -> Tuple[Optional[AssessmentState], Optional[str]]:
        """Attempt to recover state from backup files."""
        try:
            # Find most recent backup
            backup_pattern = f"state_{session_id}_*"
            backup_files = list(self.backup_dir.glob(backup_pattern + ".*"))
            
            if not backup_files:
                return None, "No backup files found"
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Try to load from most recent backup
            for backup_file in backup_files:
                try:
                    if self.format == StateFormat.JSON and backup_file.suffix == ".json":
                        state, error = self._load_json_state(backup_file)
                    elif self.format == StateFormat.PICKLE and backup_file.suffix == ".pkl":
                        state, error = self._load_pickle_state(backup_file)
                    else:
                        continue
                    
                    if state:
                        self.logger.info(f"Recovered state from backup: {backup_file}")
                        return state, None
                        
                except Exception as e:
                    self.logger.warning(f"Failed to load backup {backup_file}: {e}")
                    continue
            
            return None, "All backup recovery attempts failed"
            
        except Exception as e:
            return None, f"Recovery error: {e}"