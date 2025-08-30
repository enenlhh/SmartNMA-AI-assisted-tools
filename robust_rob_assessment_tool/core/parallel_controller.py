"""
Parallel processing controller for ROB assessments.

This module manages parallel processing of ROB assessments with intelligent
resource allocation, document distribution, and process coordination.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os
import glob
import uuid
import time
import math
import subprocess
import sys
from datetime import datetime

from .system_detector import SystemCapacityDetector
from .state_manager import StateManager, AssessmentState, BatchState, DocumentState, StateFormat


@dataclass
class Batch:
    """Represents a batch of documents for parallel processing."""
    batch_id: str
    documents: List[str]
    output_dir: str
    config: Dict[str, Any]
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert batch to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Batch':
        """Create batch from dictionary."""
        # Convert ISO format strings back to datetime objects
        if data.get('start_time'):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)


class ParallelProcessorInterface(ABC):
    """Abstract interface for parallel processing components."""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the processor with configuration."""
        pass
    
    @abstractmethod
    def process_batch(self, batch: Batch) -> Dict[str, Any]:
        """Process a batch of documents."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources after processing."""
        pass


class ParallelROBManager:
    """
    Manages parallel processing of ROB assessments with intelligent resource allocation.
    
    This class coordinates the distribution of documents across multiple parallel workers,
    handles process coordination, and manages checkpoint functionality for resume capability.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the parallel ROB manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.batches: List[Batch] = []
        self.session_id = str(uuid.uuid4())[:8]
        self.temp_dir = Path(self.config.get("paths", {}).get("temp_folder", "temp_parallel"))
        self.output_dir = Path(self.config.get("paths", {}).get("output_folder", "output"))
        
        # Initialize state manager
        self.state_manager = StateManager(
            state_dir=self.temp_dir / "states",
            format=StateFormat.JSON
        )
        self.assessment_state: Optional[AssessmentState] = None
        
        # Ensure directories exist
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Set default parallel processing settings if not present
            if "parallel" not in config:
                config["parallel"] = {}
            
            parallel_config = config["parallel"]
            if "parallel_workers" not in parallel_config:
                parallel_config["parallel_workers"] = SystemCapacityDetector.recommend_parallel_workers(config)
            if "max_documents_per_batch" not in parallel_config:
                parallel_config["max_documents_per_batch"] = 50
            if "checkpoint_interval" not in parallel_config:
                parallel_config["checkpoint_interval"] = 10
            if "retry_attempts" not in parallel_config:
                parallel_config["retry_attempts"] = 3
            if "timeout_seconds" not in parallel_config:
                parallel_config["timeout_seconds"] = 300
                
            return config
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {self.config_path}: {e}")
    
    def _get_document_list(self, input_folder: str) -> List[str]:
        """
        Get list of documents to process from input folder.
        
        Args:
            input_folder: Path to input folder
            
        Returns:
            List[str]: List of document file paths
        """
        input_path = Path(input_folder)
        if not input_path.exists():
            raise FileNotFoundError(f"Input folder not found: {input_folder}")
        
        # Support common document formats
        supported_extensions = ['*.pdf', '*.docx', '*.doc', '*.txt']
        documents = []
        
        for extension in supported_extensions:
            pattern = str(input_path / extension)
            documents.extend(glob.glob(pattern))
        
        # Also check subdirectories
        for extension in supported_extensions:
            pattern = str(input_path / "**" / extension)
            documents.extend(glob.glob(pattern, recursive=True))
        
        # Remove duplicates and sort
        documents = sorted(list(set(documents)))
        
        if not documents:
            raise ValueError(f"No supported documents found in {input_folder}")
        
        return documents
    
    def _calculate_optimal_batch_size(self, total_documents: int, parallel_workers: int) -> int:
        """
        Calculate optimal batch size based on document count and worker count.
        
        Args:
            total_documents: Total number of documents to process
            parallel_workers: Number of parallel workers
            
        Returns:
            int: Optimal batch size
        """
        max_batch_size = self.config["parallel"]["max_documents_per_batch"]
        
        # Aim for roughly equal distribution across workers
        ideal_batch_size = math.ceil(total_documents / parallel_workers)
        
        # Don't exceed maximum batch size
        optimal_batch_size = min(ideal_batch_size, max_batch_size)
        
        # Ensure at least 1 document per batch
        return max(1, optimal_batch_size)
        
    def start_parallel_assessment(self) -> bool:
        """
        Start parallel ROB assessment process.
        
        Returns:
            bool: True if assessment started successfully, False otherwise
        """
        try:
            # Get documents from input folder
            input_folder = self.config["paths"]["input_folder"]
            documents = self._get_document_list(input_folder)
            
            # Validate distribution
            is_valid, issues = self.validate_batch_distribution(documents)
            if not is_valid:
                print("❌ Validation failed:")
                for issue in issues:
                    print(f"  - {issue}")
                return False
            
            # Distribute documents into batches
            batches = self.distribute_documents(documents)
            if not batches:
                print("❌ No batches created - no documents to process")
                return False
            
            # Create worker configurations
            worker_configs = self.create_worker_configs(batches)
            
            # Initialize assessment state
            self.assessment_state = AssessmentState(
                session_id=self.session_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                status="initializing",
                config=self.config,
                total_documents=len(documents),
                temp_dir=str(self.temp_dir),
                output_dir=str(self.output_dir)
            )
            
            # Save initial state
            self._save_state()
            
            print(f"✅ Parallel assessment initialized:")
            print(f"  - Total documents: {len(documents)}")
            print(f"  - Number of batches: {len(batches)}")
            print(f"  - Parallel workers: {self.config['parallel']['parallel_workers']}")
            print(f"  - Session ID: {self.session_id}")
            
            # Update status to running
            self._update_assessment_status("running")
            
            # Start worker processes
            return self._start_worker_processes(worker_configs)
            
        except Exception as e:
            print(f"❌ Failed to start parallel assessment: {e}")
            return False
    
    def resume_assessment(self, session_id: Optional[str] = None, 
                         state_file: Optional[str] = None) -> bool:
        """
        Resume assessment from checkpoint file or session ID.
        
        Args:
            session_id: Session ID to resume (if not providing state_file)
            state_file: Path to the checkpoint state file (legacy support)
            
        Returns:
            bool: True if resume was successful, False otherwise
        """
        try:
            # Load state using new state manager
            if session_id:
                assessment_state, error = self.state_manager.load_state(session_id)
                if not assessment_state:
                    print(f"❌ Failed to load state for session {session_id}: {error}")
                    return False
            elif state_file:
                # Legacy support for old state files
                if not self._load_legacy_state(state_file):
                    return False
                assessment_state = self.assessment_state
            else:
                print("❌ Must provide either session_id or state_file")
                return False
            
            # Validate loaded state
            is_valid, issues = self.state_manager.validate_state(assessment_state)
            if not is_valid:
                print("❌ State validation failed:")
                for issue in issues:
                    print(f"  - {issue}")
                return False
            
            # Set current state
            self.assessment_state = assessment_state
            self.session_id = assessment_state.session_id
            self.config = assessment_state.config
            
            # Convert assessment state batches to internal batch format
            self.batches = self._convert_assessment_batches_to_internal(assessment_state.batches)
            
            # Find incomplete batches
            incomplete_batches = [
                batch for batch in self.batches 
                if batch.status in ["pending", "running", "paused"]
            ]
            
            if not incomplete_batches:
                print("✅ All batches already completed - nothing to resume")
                self._update_assessment_status("completed")
                return True
            
            # Check for completed work and update state
            self._detect_completed_work(incomplete_batches)
            
            print(f"🔄 Resuming assessment:")
            print(f"  - Session ID: {self.session_id}")
            print(f"  - Total batches: {len(self.batches)}")
            print(f"  - Incomplete batches: {len(incomplete_batches)}")
            print(f"  - Overall progress: {assessment_state.get_overall_progress()}%")
            
            # Update assessment status
            self._update_assessment_status("running")
            
            # Create worker configurations for incomplete batches
            worker_configs = self.create_worker_configs(incomplete_batches)
            
            # Start worker processes for incomplete batches
            return self._start_worker_processes(worker_configs)
            
        except Exception as e:
            print(f"❌ Failed to resume assessment: {e}")
            return False
    
    def distribute_documents(self, documents: List[str]) -> List[Batch]:
        """
        Distribute documents across parallel processing batches.
        
        Args:
            documents: List of document paths to process
            
        Returns:
            List[Batch]: List of document batches for parallel processing
        """
        if not documents:
            return []
        
        parallel_workers = self.config["parallel"]["parallel_workers"]
        batch_size = self._calculate_optimal_batch_size(len(documents), parallel_workers)
        
        batches = []
        
        # Create batches by splitting documents
        for i in range(0, len(documents), batch_size):
            batch_documents = documents[i:i + batch_size]
            batch_id = f"{self.session_id}_batch_{len(batches) + 1:03d}"
            
            # Create batch-specific output directory
            batch_output_dir = self.temp_dir / f"batch_{len(batches) + 1:03d}"
            batch_output_dir.mkdir(exist_ok=True)
            
            # Create batch configuration
            batch_config = self._create_batch_config(batch_id, len(batches))
            
            batch = Batch(
                batch_id=batch_id,
                documents=batch_documents,
                output_dir=str(batch_output_dir),
                config=batch_config,
                status="pending"
            )
            
            batches.append(batch)
        
        self.batches = batches
        return batches
    
    def _create_batch_config(self, batch_id: str, batch_index: int) -> Dict[str, Any]:
        """
        Create configuration for a specific batch.
        
        Args:
            batch_id: Unique batch identifier
            batch_index: Index of the batch (0-based)
            
        Returns:
            Dict[str, Any]: Batch-specific configuration
        """
        # Start with base configuration
        batch_config = self.config.copy()
        
        # Add batch-specific settings
        batch_config["batch"] = {
            "batch_id": batch_id,
            "batch_index": batch_index,
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat()
        }
        
        # Modify paths for batch processing
        batch_config["paths"]["checkpoint_file"] = str(
            self.temp_dir / f"{batch_id}_checkpoint.json"
        )
        
        # Disable parallel processing within batch (single-threaded per batch)
        if "parallel" in batch_config:
            batch_config["parallel"]["parallel_workers"] = 1
        
        return batch_config
    
    def create_worker_configs(self, batches: List[Batch]) -> List[Dict[str, Any]]:
        """
        Create configuration files for parallel workers.
        
        Args:
            batches: List of document batches
            
        Returns:
            List[Dict[str, Any]]: List of worker configurations
        """
        worker_configs = []
        
        for batch in batches:
            # Create worker configuration file path
            config_file_path = self.temp_dir / f"{batch.batch_id}_config.json"
            
            # Save batch configuration to file
            try:
                with open(config_file_path, 'w', encoding='utf-8') as f:
                    json.dump(batch.config, f, indent=2, ensure_ascii=False)
                
                # Create worker configuration with necessary information
                worker_config = {
                    "batch_id": batch.batch_id,
                    "config_file": str(config_file_path),
                    "documents": batch.documents,
                    "output_dir": batch.output_dir,
                    "status": batch.status,
                    "worker_script": self._get_worker_script_path(),
                    "log_file": str(self.temp_dir / f"{batch.batch_id}_worker.log"),
                    "pid_file": str(self.temp_dir / f"{batch.batch_id}_worker.pid"),
                    "result_file": str(self.temp_dir / f"{batch.batch_id}_results.json")
                }
                
                worker_configs.append(worker_config)
                
            except Exception as e:
                raise RuntimeError(f"Failed to create worker config for batch {batch.batch_id}: {e}")
        
        return worker_configs
    
    def _get_worker_script_path(self) -> str:
        """
        Get the path to the worker script for batch processing.
        
        Returns:
            str: Path to worker script
        """
        # This will be the main ROB evaluator script that can run in batch mode
        return str(Path(__file__).parent.parent / "src" / "main.py")
    
    def get_batch_summary(self) -> Dict[str, Any]:
        """
        Get summary information about current batches.
        
        Returns:
            Dict[str, Any]: Batch summary information
        """
        if not self.batches:
            return {
                "total_batches": 0,
                "total_documents": 0,
                "status_counts": {},
                "session_id": self.session_id
            }
        
        status_counts = {}
        total_documents = 0
        
        for batch in self.batches:
            status = batch.status
            status_counts[status] = status_counts.get(status, 0) + 1
            total_documents += len(batch.documents)
        
        return {
            "total_batches": len(self.batches),
            "total_documents": total_documents,
            "status_counts": status_counts,
            "session_id": self.session_id,
            "temp_dir": str(self.temp_dir),
            "output_dir": str(self.output_dir),
            "parallel_workers": self.config["parallel"]["parallel_workers"],
            "max_documents_per_batch": self.config["parallel"]["max_documents_per_batch"]
        }
    
    def validate_batch_distribution(self, documents: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that document distribution will work correctly.
        
        Args:
            documents: List of document paths to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        issues = []
        
        # Check if documents exist
        missing_docs = []
        for doc in documents:
            if not Path(doc).exists():
                missing_docs.append(doc)
        
        if missing_docs:
            issues.append(f"Missing documents: {missing_docs[:5]}{'...' if len(missing_docs) > 5 else ''}")
        
        # Check system resources
        resource_warnings = SystemCapacityDetector.validate_configuration(self.config)
        if resource_warnings:
            issues.extend([f"Resource warning: {warning}" for warning in resource_warnings])
        
        # Check output directory permissions
        try:
            test_file = self.temp_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            issues.append(f"Cannot write to temp directory {self.temp_dir}: {e}")
        
        # Check configuration validity
        required_config_keys = ["paths", "processing", "llm_models"]
        for key in required_config_keys:
            if key not in self.config:
                issues.append(f"Missing required configuration section: {key}")
        
        return len(issues) == 0, issues
    
    def _start_worker_processes(self, worker_configs: List[Dict[str, Any]]) -> bool:
        """
        Start worker processes for parallel batch processing.
        
        Args:
            worker_configs: List of worker configurations
            
        Returns:
            bool: True if all workers started successfully
        """
        import subprocess
        import sys
        
        started_processes = []
        
        try:
            for worker_config in worker_configs:
                batch_id = worker_config["batch_id"]
                
                # Prepare command to run worker
                cmd = [
                    sys.executable,
                    worker_config["worker_script"],
                    "--config", worker_config["config_file"],
                    "--batch-mode",
                    "--batch-id", batch_id,
                    "--output-dir", worker_config["output_dir"]
                ]
                
                # Start process
                print(f"🚀 Starting worker for batch {batch_id}...")
                
                with open(worker_config["log_file"], 'w') as log_file:
                    process = subprocess.Popen(
                        cmd,
                        stdout=log_file,
                        stderr=subprocess.STDOUT,
                        cwd=str(Path(__file__).parent.parent)
                    )
                
                # Save PID
                with open(worker_config["pid_file"], 'w') as pid_file:
                    pid_file.write(str(process.pid))
                
                started_processes.append({
                    "batch_id": batch_id,
                    "process": process,
                    "pid": process.pid,
                    "config": worker_config
                })
                
                # Update batch status
                for batch in self.batches:
                    if batch.batch_id == batch_id:
                        batch.status = "running"
                        batch.start_time = datetime.now()
                        break
            
            print(f"✅ Started {len(started_processes)} worker processes")
            
            # Save updated state
            self._save_state()
            
            # Monitor processes (this will be handled by progress monitor in later tasks)
            return True
            
        except Exception as e:
            print(f"❌ Failed to start worker processes: {e}")
            
            # Clean up any started processes
            self._cleanup_processes(started_processes)
            return False
    
    def _cleanup_processes(self, processes: List[Dict[str, Any]]) -> None:
        """
        Clean up worker processes and temporary files.
        
        Args:
            processes: List of process information dictionaries
        """
        for process_info in processes:
            try:
                process = process_info["process"]
                batch_id = process_info["batch_id"]
                
                print(f"🧹 Cleaning up process for batch {batch_id}...")
                
                # Terminate process if still running
                if process.poll() is None:
                    process.terminate()
                    
                    # Wait for graceful termination
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        # Force kill if necessary
                        process.kill()
                        process.wait()
                
                # Clean up PID file
                pid_file = Path(process_info["config"]["pid_file"])
                if pid_file.exists():
                    pid_file.unlink()
                    
            except Exception as e:
                print(f"⚠️  Error cleaning up process for batch {process_info['batch_id']}: {e}")
    
    def _save_state(self) -> bool:
        """
        Save current state to checkpoint file using state manager.
        
        Returns:
            bool: True if state saved successfully
        """
        try:
            # Create or update assessment state
            if not self.assessment_state:
                self.assessment_state = AssessmentState(
                    session_id=self.session_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    status="initializing",
                    config=self.config,
                    temp_dir=str(self.temp_dir),
                    output_dir=str(self.output_dir)
                )
            
            # Convert internal batches to assessment state format
            self.assessment_state.batches = self._convert_internal_batches_to_assessment(self.batches)
            
            # Update counters and status
            self.assessment_state.update_counters()
            self.assessment_state.updated_at = datetime.now()
            
            # Save using state manager
            success, error = self.state_manager.save_state(self.assessment_state)
            
            if not success:
                print(f"⚠️  Failed to save state: {error}")
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to save state: {e}")
            return False
    
    def _load_state(self, state_file: str) -> bool:
        """
        Load state from checkpoint file.
        
        Args:
            state_file: Path to state file
            
        Returns:
            bool: True if state loaded successfully
        """
        try:
            state_path = Path(state_file)
            if not state_path.exists():
                print(f"❌ State file not found: {state_file}")
                return False
            
            with open(state_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # Restore state
            self.session_id = state_data["session_id"]
            self.config = state_data["config"]
            self.temp_dir = Path(state_data["temp_dir"])
            self.output_dir = Path(state_data["output_dir"])
            self.state_file = state_path
            
            # Restore batches
            self.batches = [
                Batch.from_dict(batch_data) 
                for batch_data in state_data["batches"]
            ]
            
            print(f"✅ State loaded from {state_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load state from {state_file}: {e}")
            return False
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """
        Get information about currently running worker processes.
        
        Returns:
            List[Dict[str, Any]]: List of running process information
        """
        running_processes = []
        
        for batch in self.batches:
            if batch.status == "running":
                pid_file = self.temp_dir / f"{batch.batch_id}_worker.pid"
                log_file = self.temp_dir / f"{batch.batch_id}_worker.log"
                
                process_info = {
                    "batch_id": batch.batch_id,
                    "pid_file": str(pid_file),
                    "log_file": str(log_file),
                    "start_time": batch.start_time.isoformat() if batch.start_time else None,
                    "documents_count": len(batch.documents)
                }
                
                # Check if process is actually running
                if pid_file.exists():
                    try:
                        with open(pid_file, 'r') as f:
                            pid = int(f.read().strip())
                        
                        # Check if PID exists
                        import psutil
                        if psutil.pid_exists(pid):
                            process_info["pid"] = pid
                            process_info["is_running"] = True
                        else:
                            process_info["is_running"] = False
                            process_info["status"] = "Process not found"
                    except Exception as e:
                        process_info["is_running"] = False
                        process_info["status"] = f"Error checking PID: {e}"
                else:
                    process_info["is_running"] = False
                    process_info["status"] = "PID file not found"
                
                running_processes.append(process_info)
        
        return running_processes
    
    def stop_all_processes(self) -> bool:
        """
        Stop all running worker processes gracefully.
        
        Returns:
            bool: True if all processes stopped successfully
        """
        running_processes = self.get_running_processes()
        
        if not running_processes:
            print("ℹ️  No running processes to stop")
            return True
        
        print(f"🛑 Stopping {len(running_processes)} worker processes...")
        
        stopped_count = 0
        
        for process_info in running_processes:
            try:
                if process_info.get("is_running") and process_info.get("pid"):
                    import psutil
                    process = psutil.Process(process_info["pid"])
                    
                    # Send termination signal
                    process.terminate()
                    
                    # Wait for graceful termination
                    try:
                        process.wait(timeout=10)
                        stopped_count += 1
                        print(f"✅ Stopped process for batch {process_info['batch_id']}")
                    except psutil.TimeoutExpired:
                        # Force kill if necessary
                        process.kill()
                        process.wait()
                        stopped_count += 1
                        print(f"⚠️  Force killed process for batch {process_info['batch_id']}")
                    
                    # Update batch status
                    for batch in self.batches:
                        if batch.batch_id == process_info["batch_id"]:
                            batch.status = "pending"  # Reset to pending for potential resume
                            batch.start_time = None
                            break
                
            except Exception as e:
                print(f"❌ Failed to stop process for batch {process_info['batch_id']}: {e}")
        
        # Save updated state
        self._save_state()
        
        print(f"✅ Stopped {stopped_count}/{len(running_processes)} processes")
        return stopped_count == len(running_processes)
    
    def _convert_internal_batches_to_assessment(self, batches: List[Batch]) -> List[BatchState]:
        """Convert internal batch format to assessment state format."""
        assessment_batches = []
        
        for batch in batches:
            # Create document states
            document_states = []
            for doc_path in batch.documents:
                doc_state = DocumentState(
                    document_path=doc_path,
                    status="pending"  # Will be updated by completed work detection
                )
                document_states.append(doc_state)
            
            # Create batch state
            batch_state = BatchState(
                batch_id=batch.batch_id,
                status=batch.status,
                documents=document_states,
                start_time=batch.start_time,
                end_time=batch.end_time,
                progress=batch.progress,
                config_file=str(self.temp_dir / f"{batch.batch_id}_config.json"),
                output_dir=batch.output_dir,
                error_message=batch.error_message
            )
            
            assessment_batches.append(batch_state)
        
        return assessment_batches
    
    def _convert_assessment_batches_to_internal(self, assessment_batches: List[BatchState]) -> List[Batch]:
        """Convert assessment state batches to internal batch format."""
        internal_batches = []
        
        for batch_state in assessment_batches:
            # Extract document paths
            document_paths = [doc.document_path for doc in batch_state.documents]
            
            # Create internal batch
            batch = Batch(
                batch_id=batch_state.batch_id,
                documents=document_paths,
                output_dir=batch_state.output_dir or "",
                config=self.config,  # Use current config
                status=batch_state.status,
                start_time=batch_state.start_time,
                end_time=batch_state.end_time,
                progress=batch_state.progress,
                error_message=batch_state.error_message
            )
            
            internal_batches.append(batch)
        
        return internal_batches
    
    def _detect_completed_work(self, batches: List[Batch]) -> None:
        """
        Detect and update completed work by checking result files.
        
        Args:
            batches: List of batches to check for completed work
        """
        print("🔍 Detecting completed work...")
        
        total_detected = 0
        
        for batch in batches:
            batch_detected = 0
            
            # Check for batch result file
            result_file = self.temp_dir / f"{batch.batch_id}_results.json"
            
            if result_file.exists():
                try:
                    # Load and validate results
                    with open(result_file, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                    
                    # Count completed documents in results
                    if isinstance(results, dict) and "results" in results:
                        completed_docs = results["results"]
                        batch_detected = len(completed_docs)
                        
                        # Update batch progress
                        if batch.documents:
                            batch.progress = int((batch_detected / len(batch.documents)) * 100)
                        
                        # If all documents completed, mark batch as completed
                        if batch_detected >= len(batch.documents):
                            batch.status = "completed"
                            batch.end_time = datetime.now()
                            print(f"  ✅ Batch {batch.batch_id}: {batch_detected} documents completed")
                        else:
                            print(f"  🔄 Batch {batch.batch_id}: {batch_detected}/{len(batch.documents)} documents completed")
                    
                except Exception as e:
                    print(f"  ⚠️  Error reading results for batch {batch.batch_id}: {e}")
            
            total_detected += batch_detected
        
        if total_detected > 0:
            print(f"✅ Detected {total_detected} completed documents")
            # Save updated state
            self._save_state()
        else:
            print("ℹ️  No completed work detected")
    
    def _update_assessment_status(self, status: str) -> None:
        """Update assessment status and save state."""
        if self.assessment_state:
            self.assessment_state.status = status
            self.assessment_state.updated_at = datetime.now()
            self._save_state()
    
    def _load_legacy_state(self, state_file: str) -> bool:
        """
        Load state from legacy state file format.
        
        Args:
            state_file: Path to legacy state file
            
        Returns:
            bool: True if state loaded successfully
        """
        try:
            state_path = Path(state_file)
            if not state_path.exists():
                print(f"❌ State file not found: {state_file}")
                return False
            
            with open(state_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # Convert legacy format to new assessment state
            self.session_id = state_data["session_id"]
            self.config = state_data["config"]
            self.temp_dir = Path(state_data["temp_dir"])
            self.output_dir = Path(state_data["output_dir"])
            
            # Convert legacy batches
            self.batches = [
                Batch.from_dict(batch_data) 
                for batch_data in state_data["batches"]
            ]
            
            # Create assessment state
            self.assessment_state = AssessmentState(
                session_id=self.session_id,
                created_at=datetime.fromisoformat(state_data.get("timestamp", datetime.now().isoformat())),
                updated_at=datetime.now(),
                status="paused",
                config=self.config,
                temp_dir=str(self.temp_dir),
                output_dir=str(self.output_dir)
            )
            
            print(f"✅ Legacy state loaded from {state_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load legacy state from {state_file}: {e}")
            return False
    
    def list_available_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available assessment sessions.
        
        Returns:
            List[Dict[str, Any]]: List of available sessions with metadata
        """
        return self.state_manager.list_available_states()
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific session.
        
        Args:
            session_id: Session ID to get info for
            
        Returns:
            Optional[Dict[str, Any]]: Session information or None if not found
        """
        try:
            assessment_state, error = self.state_manager.load_state(session_id, validate=False)
            if not assessment_state:
                return None
            
            return {
                "session_id": assessment_state.session_id,
                "status": assessment_state.status,
                "created_at": assessment_state.created_at.isoformat(),
                "updated_at": assessment_state.updated_at.isoformat(),
                "total_documents": assessment_state.total_documents,
                "completed_documents": assessment_state.completed_documents,
                "failed_documents": assessment_state.failed_documents,
                "progress": assessment_state.get_overall_progress(),
                "total_batches": len(assessment_state.batches),
                "incomplete_batches": len(assessment_state.get_incomplete_batches()),
                "temp_dir": assessment_state.temp_dir,
                "output_dir": assessment_state.output_dir
            }
            
        except Exception as e:
            print(f"❌ Error getting session info: {e}")
            return None
    
    def delete_session(self, session_id: str, create_backup: bool = True) -> bool:
        """
        Delete a session and its associated files.
        
        Args:
            session_id: Session ID to delete
            create_backup: Whether to create backup before deletion
            
        Returns:
            bool: True if deletion successful
        """
        try:
            # Delete state using state manager
            success, error = self.state_manager.delete_state(session_id, create_backup)
            
            if not success:
                print(f"❌ Failed to delete session state: {error}")
                return False
            
            # Clean up associated temporary files
            cleanup_patterns = [
                f"{session_id}_*_config.json",
                f"{session_id}_*_worker.log",
                f"{session_id}_*_worker.pid",
                f"{session_id}_*_results.json",
                f"{session_id}_*_checkpoint.json"
            ]
            
            cleaned_files = 0
            for pattern in cleanup_patterns:
                for file_path in self.temp_dir.glob(pattern):
                    try:
                        file_path.unlink()
                        cleaned_files += 1
                    except Exception as e:
                        print(f"⚠️  Could not delete {file_path}: {e}")
            
            print(f"✅ Session {session_id} deleted ({cleaned_files} files cleaned)")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting session: {e}")
            return False

    def cleanup_session(self, keep_results: bool = True) -> bool:
        """
        Clean up temporary files and processes for current session.
        
        Args:
            keep_results: Whether to keep result files
            
        Returns:
            bool: True if cleanup successful
        """
        try:
            print(f"🧹 Cleaning up session {self.session_id}...")
            
            # Stop any running processes
            self.stop_all_processes()
            
            # Clean up temporary files
            cleanup_patterns = [
                f"{self.session_id}_*_config.json",
                f"{self.session_id}_*_worker.log",
                f"{self.session_id}_*_worker.pid",
                f"state_{self.session_id}.json"
            ]
            
            if not keep_results:
                cleanup_patterns.extend([
                    f"{self.session_id}_*_results.json",
                    f"{self.session_id}_*_checkpoint.json"
                ])
            
            cleaned_files = 0
            for pattern in cleanup_patterns:
                for file_path in self.temp_dir.glob(pattern):
                    try:
                        file_path.unlink()
                        cleaned_files += 1
                    except Exception as e:
                        print(f"⚠️  Could not delete {file_path}: {e}")
            
            # Clean up empty batch directories
            for batch in self.batches:
                batch_dir = Path(batch.output_dir)
                if batch_dir.exists() and not any(batch_dir.iterdir()):
                    try:
                        batch_dir.rmdir()
                    except Exception:
                        pass  # Directory not empty or other issue
            
            print(f"✅ Cleaned up {cleaned_files} temporary files")
            return True
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False