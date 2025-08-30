"""
Progress monitoring system for ROB assessments.

This module provides real-time monitoring and reporting of assessment progress,
including performance metrics, cost tracking, and interactive updates.
"""

import json
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import os
import sys


class ProgressReporter(ABC):
    """Abstract interface for progress reporting components."""
    
    @abstractmethod
    def update_progress(self, progress_data: Dict[str, Any]) -> None:
        """Update progress with new data."""
        pass
    
    @abstractmethod
    def generate_report(self) -> Dict[str, Any]:
        """Generate progress report."""
        pass


class ErrorTracker:
    """Tracks and analyzes errors during processing."""
    
    def __init__(self):
        self.errors = []
        self.error_categories = {}
        self.error_patterns = {}
        
    def add_error(self, document: str, batch_id: str, error_type: str, error_message: str, timestamp: datetime = None) -> None:
        """Add an error to the tracker."""
        if timestamp is None:
            timestamp = datetime.now()
            
        error_entry = {
            "timestamp": timestamp.isoformat(),
            "document": document,
            "batch_id": batch_id,
            "error_type": error_type,
            "error_message": error_message,
            "severity": self._determine_severity(error_type, error_message)
        }
        
        self.errors.append(error_entry)
        
        # Update categories
        if error_type not in self.error_categories:
            self.error_categories[error_type] = []
        self.error_categories[error_type].append(error_entry)
        
        # Update patterns
        pattern_key = f"{error_type}:{self._extract_pattern(error_message)}"
        self.error_patterns[pattern_key] = self.error_patterns.get(pattern_key, 0) + 1
    
    def _determine_severity(self, error_type: str, error_message: str) -> str:
        """Determine error severity level."""
        critical_keywords = ["critical", "fatal", "crash", "abort"]
        warning_keywords = ["warning", "timeout", "retry"]
        
        message_lower = error_message.lower()
        
        if any(keyword in message_lower for keyword in critical_keywords):
            return "critical"
        elif any(keyword in message_lower for keyword in warning_keywords):
            return "warning"
        elif error_type in ["network_error", "api_error"]:
            return "warning"
        else:
            return "error"
    
    def _extract_pattern(self, error_message: str) -> str:
        """Extract error pattern from message."""
        # Simple pattern extraction - first few words
        words = error_message.split()[:3]
        return " ".join(words).lower()
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors."""
        if not self.errors:
            return {"total_errors": 0, "error_rate": 0.0}
        
        severity_counts = {}
        for error in self.errors:
            severity = error["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_errors": len(self.errors),
            "error_categories": {cat: len(errors) for cat, errors in self.error_categories.items()},
            "severity_breakdown": severity_counts,
            "most_common_patterns": sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)[:5],
            "recent_errors": self.errors[-10:] if len(self.errors) > 10 else self.errors
        }
    
    def get_errors_by_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        """Get all errors for a specific batch."""
        return [error for error in self.errors if error["batch_id"] == batch_id]
    
    def get_critical_errors(self) -> List[Dict[str, Any]]:
        """Get all critical errors."""
        return [error for error in self.errors if error["severity"] == "critical"]


class BatchStatus:
    """Represents the status of a processing batch."""
    
    def __init__(self, batch_id: str, total_documents: int):
        self.batch_id = batch_id
        self.total_documents = total_documents
        self.completed_documents = 0
        self.failed_documents = 0
        self.current_document = None
        self.start_time = None
        self.end_time = None
        self.status = "pending"  # pending, running, completed, failed
        self.errors = []
        self.processing_times = []
        self.document_statuses = {}  # document_name -> status
        
    def start_processing(self) -> None:
        """Mark batch as started."""
        self.status = "running"
        self.start_time = datetime.now()
    
    def complete_document(self, document_name: str, processing_time: float) -> None:
        """Mark a document as completed."""
        self.completed_documents += 1
        self.processing_times.append(processing_time)
        self.document_statuses[document_name] = "completed"
        
        if self.completed_documents + self.failed_documents >= self.total_documents:
            self.status = "completed" if self.failed_documents == 0 else "completed_with_errors"
            self.end_time = datetime.now()
    
    def fail_document(self, document_name: str, error: str, error_type: str = "unknown") -> None:
        """Mark a document as failed."""
        self.failed_documents += 1
        error_entry = {
            "document": document_name,
            "error": error,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat()
        }
        self.errors.append(error_entry)
        self.document_statuses[document_name] = "failed"
        
        if self.completed_documents + self.failed_documents >= self.total_documents:
            self.status = "completed_with_errors"
            self.end_time = datetime.now()
    
    def get_progress_percentage(self) -> float:
        """Get completion percentage for this batch."""
        if self.total_documents == 0:
            return 0.0
        return ((self.completed_documents + self.failed_documents) / self.total_documents) * 100
    
    def get_success_percentage(self) -> float:
        """Get success percentage for this batch."""
        if self.total_documents == 0:
            return 0.0
        return (self.completed_documents / self.total_documents) * 100
    
    def get_average_processing_time(self) -> float:
        """Get average processing time per document."""
        if not self.processing_times:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors in this batch."""
        if not self.errors:
            return {"error_count": 0, "error_rate": 0.0}
        
        error_types = {}
        for error in self.errors:
            error_type = error.get("error_type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "error_count": len(self.errors),
            "error_rate": (len(self.errors) / self.total_documents * 100) if self.total_documents > 0 else 0,
            "error_types": error_types,
            "recent_errors": self.errors[-5:] if len(self.errors) > 5 else self.errors
        }


class ProgressMonitor:
    """
    Real-time monitoring and reporting of assessment progress.
    
    This class provides comprehensive progress tracking including batch status,
    performance metrics, ETA calculation, and cost monitoring.
    """
    
    def __init__(self, state_file_path: str, update_interval: int = 5, i18n_manager=None):
        """
        Initialize the progress monitor.
        
        Args:
            state_file_path: Path to the state file for progress tracking
            update_interval: Update interval in seconds
            i18n_manager: Language manager for localized messages
        """
        self.state_file_path = Path(state_file_path)
        self.update_interval = update_interval
        self.i18n_manager = i18n_manager
        self.is_monitoring = False
        self.start_time = None
        self.last_update_time = None
        
        # Progress tracking data
        self.batches = {}  # batch_id -> BatchStatus
        self.total_documents = 0
        self.completed_documents = 0
        self.failed_documents = 0
        self.current_batch = None
        self.current_document = None
        
        # Error tracking
        self.error_tracker = ErrorTracker()
        
        # Performance metrics
        self.processing_times = []
        self.cost_data = {
            "total_cost": 0.0,
            "model_costs": {},
            "token_usage": {"input": 0, "output": 0}
        }
        
        # Cost tracking integration
        self.cost_analyzer = None
        self.cost_reporter = None
        
        # Threading for real-time updates
        self.monitor_thread = None
        self.stop_event = threading.Event()
        
    def _get_message(self, key: str, **kwargs) -> str:
        """Get localized message."""
        if self.i18n_manager:
            return self.i18n_manager.get_message(key, **kwargs)
        return key.format(**kwargs) if kwargs else key
    
    def set_cost_analyzer(self, cost_analyzer) -> None:
        """
        Set the cost analyzer for cost tracking integration.
        
        Args:
            cost_analyzer: CostAnalyzer instance
        """
        self.cost_analyzer = cost_analyzer
        if cost_analyzer:
            try:
                from ..src.cost_reporter import CostReporter
                self.cost_reporter = CostReporter(cost_analyzer)
            except ImportError:
                print("Warning: CostReporter not available")
    
    def update_cost_data(self) -> None:
        """Update cost data from the cost analyzer."""
        if not self.cost_analyzer:
            return
        
        try:
            cost_summary = self.cost_analyzer.get_cost_summary()
            self.cost_data = {
                "total_cost": cost_summary.get('total_cost_usd', 0.0),
                "model_costs": {},
                "token_usage": {
                    "input": 0,
                    "output": 0,
                    "total": cost_summary.get('total_tokens', 0)
                },
                "api_calls": cost_summary.get('total_api_calls', 0),
                "session_id": cost_summary.get('session_id', 'unknown')
            }
            
            # Update model-specific costs
            for model_summary in cost_summary.get('model_summaries', []):
                model_name = model_summary.get('model', 'unknown')
                self.cost_data["model_costs"][model_name] = {
                    "cost": model_summary.get('total_cost_usd', 0.0),
                    "tokens": model_summary.get('total_tokens', 0),
                    "api_calls": model_summary.get('api_calls', 0)
                }
                
                # Update token usage
                self.cost_data["token_usage"]["input"] += model_summary.get('total_input_tokens', 0)
                self.cost_data["token_usage"]["output"] += model_summary.get('total_output_tokens', 0)
                
        except Exception as e:
            print(f"Warning: Failed to update cost data: {e}")
    
    def get_cost_summary_display(self) -> str:
        """
        Get formatted cost summary for display.
        
        Returns:
            Formatted string with cost information
        """
        if not self.cost_data or self.cost_data["total_cost"] == 0:
            return "Cost tracking: Not available"
        
        cost_lines = [
            f"💰 Total Cost: ${self.cost_data['total_cost']:.4f} USD",
            f"🔢 Total Tokens: {self.cost_data['token_usage']['total']:,}",
            f"📞 API Calls: {self.cost_data['api_calls']:,}"
        ]
        
        # Add model breakdown if available
        if self.cost_data["model_costs"]:
            cost_lines.append("📊 Model Breakdown:")
            for model, data in self.cost_data["model_costs"].items():
                cost_lines.append(f"  • {model}: ${data['cost']:.4f} ({data['tokens']:,} tokens)")
        
        return "\n".join(cost_lines)
    
    def get_cost_efficiency_metrics(self) -> Dict[str, float]:
        """
        Get cost efficiency metrics.
        
        Returns:
            Dictionary with efficiency metrics
        """
        if not self.cost_data or self.cost_data["total_cost"] == 0:
            return {}
        
        metrics = {}
        
        # Cost per document
        total_processed = self.completed_documents + self.failed_documents
        if total_processed > 0:
            metrics["cost_per_document"] = self.cost_data["total_cost"] / total_processed
        
        # Cost per token
        if self.cost_data["token_usage"]["total"] > 0:
            metrics["cost_per_token"] = self.cost_data["total_cost"] / self.cost_data["token_usage"]["total"]
        
        # Cost per API call
        if self.cost_data["api_calls"] > 0:
            metrics["cost_per_api_call"] = self.cost_data["total_cost"] / self.cost_data["api_calls"]
        
        # Processing time efficiency
        if self.processing_times and self.start_time:
            elapsed_minutes = (datetime.now() - self.start_time).total_seconds() / 60
            if elapsed_minutes > 0:
                metrics["cost_per_minute"] = self.cost_data["total_cost"] / elapsed_minutes
        
        return metrics
    
    def add_batch(self, batch_id: str, documents: List[str]) -> None:
        """
        Add a new batch to monitor.
        
        Args:
            batch_id: Unique identifier for the batch
            documents: List of document paths in the batch
        """
        self.batches[batch_id] = BatchStatus(batch_id, len(documents))
        self.total_documents += len(documents)
    
    def start_batch(self, batch_id: str) -> None:
        """
        Mark a batch as started.
        
        Args:
            batch_id: Batch identifier
        """
        if batch_id in self.batches:
            self.batches[batch_id].start_processing()
            self.current_batch = batch_id
    
    def update_batch_progress(self, batch_id: str, document_name: str, 
                            processing_time: float = None, error: str = None, error_type: str = None) -> None:
        """
        Update progress for a specific batch.
        
        Args:
            batch_id: Batch identifier
            document_name: Name of the document being processed
            processing_time: Time taken to process the document
            error: Error message if processing failed
            error_type: Type/category of error if processing failed
        """
        if batch_id not in self.batches:
            return
            
        batch = self.batches[batch_id]
        batch.current_document = document_name
        self.current_document = document_name
        
        if error:
            # Categorize error if type not provided
            if error_type is None:
                error_type = self._categorize_error(error)
            
            batch.fail_document(document_name, error, error_type)
            self.failed_documents += 1
            
            # Add to error tracker
            self.error_tracker.add_error(document_name, batch_id, error_type, error)
            
        elif processing_time is not None:
            batch.complete_document(document_name, processing_time)
            self.completed_documents += 1
            self.processing_times.append(processing_time)
    
    def update_cost_data(self, model: str, input_tokens: int, output_tokens: int, cost: float) -> None:
        """
        Update cost tracking data.
        
        Args:
            model: LLM model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost: Cost for this request
        """
        self.cost_data["total_cost"] += cost
        self.cost_data["token_usage"]["input"] += input_tokens
        self.cost_data["token_usage"]["output"] += output_tokens
        
        if model not in self.cost_data["model_costs"]:
            self.cost_data["model_costs"][model] = 0.0
        self.cost_data["model_costs"][model] += cost
    
    def start_monitoring(self) -> None:
        """Start the progress monitoring process."""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.start_time = datetime.now()
        self.last_update_time = self.start_time
        self.stop_event.clear()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        if self.i18n_manager:
            print(self._get_message("progress_monitoring.monitoring_started"))
    
    def stop_monitoring(self) -> None:
        """Stop the progress monitoring process."""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
            
        if self.i18n_manager:
            print(self._get_message("progress_monitoring.monitoring_stopped"))
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop running in separate thread."""
        while not self.stop_event.wait(self.update_interval):
            try:
                self._update_display()
                self._save_state()
            except Exception as e:
                # Log error but continue monitoring
                print(f"Monitoring error: {e}")
    
    def _update_display(self) -> None:
        """Update the real-time progress display."""
        if not self.is_monitoring:
            return
            
        # Clear screen for real-time updates
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Display header
        print("=" * 80)
        print(self._get_message("progress_monitoring.performance_metrics").center(80))
        print("=" * 80)
        
        # Overall progress
        overall_percent = self._calculate_overall_progress()
        print(f"\n{self._get_message('progress_monitoring.overall_progress', 
                                     percent=f'{overall_percent:.1f}',
                                     completed=self.completed_documents,
                                     total=self.total_documents)}")
        
        # Time information
        elapsed = self._get_elapsed_time()
        print(f"{self._get_message('progress_monitoring.elapsed_time', time=elapsed)}")
        
        # ETA calculation
        eta = self.calculate_eta(self.completed_documents, self.total_documents, 
                               self._get_elapsed_seconds())
        if eta:
            eta_str = self._format_duration(eta)
            print(f"{self._get_message('progress_monitoring.estimated_completion', time=eta_str)}")
        
        # Processing rate
        rate = self._calculate_processing_rate()
        if rate > 0:
            print(f"{self._get_message('progress_monitoring.processing_rate', rate=f'{rate:.1f}')}")
        
        # Current document
        if self.current_document:
            print(f"{self._get_message('progress_monitoring.current_document', document=self.current_document)}")
        
        # Batch status
        print(f"\n{'-' * 40}")
        print(self._get_message("batch_status"))
        print(f"{'-' * 40}")
        
        for batch_id, batch in self.batches.items():
            status_icon = self._get_status_icon(batch.status)
            percent = batch.get_progress_percentage()
            batch_msg = self._get_message('progress_monitoring.batch_progress', 
                                        batch_id=batch_id, percent=f'{percent:.1f}')
            print(f"{status_icon} {batch_msg}")
        
        # Performance metrics
        if self.processing_times:
            avg_time = sum(self.processing_times) / len(self.processing_times)
            print(f"\n{self._get_message('progress_monitoring.avg_processing_time', time=f'{avg_time:.1f}')}")
        
        # Cost summary
        self.update_cost_data()  # Update cost data before displaying
        if self.cost_data["total_cost"] > 0:
            print(f"\n{'-' * 40}")
            print("💰 COST ANALYSIS")
            print(f"{'-' * 40}")
            print(f"Total Cost: ${self.cost_data['total_cost']:.4f} USD")
            print(f"Total Tokens: {self.cost_data['token_usage']['total']:,}")
            print(f"API Calls: {self.cost_data['api_calls']:,}")
            
            # Cost efficiency metrics
            efficiency_metrics = self.get_cost_efficiency_metrics()
            if efficiency_metrics:
                print(f"Cost per Document: ${efficiency_metrics.get('cost_per_document', 0):.4f}")
                print(f"Cost per Token: ${efficiency_metrics.get('cost_per_token', 0):.6f}")
            
            # Model breakdown
            if self.cost_data["model_costs"]:
                print("\nModel Breakdown:")
                for model, data in self.cost_data["model_costs"].items():
                    print(f"  • {model}: ${data['cost']:.4f} ({data['tokens']:,} tokens)")
            
            # Cost recommendations (if available)
            if self.cost_analyzer:
                recommendations = self.cost_analyzer.generate_recommendations()
                if recommendations and len(recommendations) > 0:
                    print(f"\n💡 Top Recommendation: {recommendations[0]}")
        
        # Error summary
        if self.failed_documents > 0:
            print(f"\n{self._get_message('warning', message=f'{self.failed_documents} documents failed')}")
        
        print(f"\n{'-' * 80}")
        print(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    def _get_status_icon(self, status: str) -> str:
        """Get status icon for batch status."""
        icons = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌"
        }
        return icons.get(status, "❓")
    
    def _calculate_overall_progress(self) -> float:
        """Calculate overall progress percentage."""
        if self.total_documents == 0:
            return 0.0
        return (self.completed_documents / self.total_documents) * 100
    
    def _calculate_processing_rate(self) -> float:
        """Calculate processing rate in documents per minute."""
        elapsed_seconds = self._get_elapsed_seconds()
        if elapsed_seconds == 0 or self.completed_documents == 0:
            return 0.0
        return (self.completed_documents / elapsed_seconds) * 60
    
    def _get_elapsed_time(self) -> str:
        """Get formatted elapsed time."""
        if not self.start_time:
            return "00:00:00"
        elapsed = datetime.now() - self.start_time
        return self._format_duration(elapsed.total_seconds())
    
    def _get_elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds()
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _save_state(self) -> None:
        """Save current progress state to file."""
        try:
            state_data = {
                "timestamp": datetime.now().isoformat(),
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "total_documents": self.total_documents,
                "completed_documents": self.completed_documents,
                "failed_documents": self.failed_documents,
                "current_batch": self.current_batch,
                "current_document": self.current_document,
                "batches": {
                    batch_id: {
                        "total_documents": batch.total_documents,
                        "completed_documents": batch.completed_documents,
                        "failed_documents": batch.failed_documents,
                        "status": batch.status,
                        "start_time": batch.start_time.isoformat() if batch.start_time else None,
                        "end_time": batch.end_time.isoformat() if batch.end_time else None,
                        "errors": batch.errors,
                        "avg_processing_time": batch.get_average_processing_time()
                    }
                    for batch_id, batch in self.batches.items()
                },
                "cost_data": self.cost_data,
                "performance_metrics": {
                    "avg_processing_time": sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
                    "processing_rate": self._calculate_processing_rate(),
                    "overall_progress": self._calculate_overall_progress()
                }
            }
            
            # Ensure directory exists
            self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write state file
            with open(self.state_file_path, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            # Don't let state saving errors stop monitoring
            print(f"Warning: Could not save progress state: {e}")
    
    def load_state(self) -> bool:
        """
        Load progress state from file.
        
        Returns:
            bool: True if state loaded successfully, False otherwise
        """
        try:
            if not self.state_file_path.exists():
                return False
                
            with open(self.state_file_path, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # Restore basic state
            self.total_documents = state_data.get("total_documents", 0)
            self.completed_documents = state_data.get("completed_documents", 0)
            self.failed_documents = state_data.get("failed_documents", 0)
            self.current_batch = state_data.get("current_batch")
            self.current_document = state_data.get("current_document")
            
            # Restore start time
            if state_data.get("start_time"):
                self.start_time = datetime.fromisoformat(state_data["start_time"])
            
            # Restore batch data
            for batch_id, batch_data in state_data.get("batches", {}).items():
                batch = BatchStatus(batch_id, batch_data["total_documents"])
                batch.completed_documents = batch_data["completed_documents"]
                batch.failed_documents = batch_data["failed_documents"]
                batch.status = batch_data["status"]
                batch.errors = batch_data.get("errors", [])
                
                if batch_data.get("start_time"):
                    batch.start_time = datetime.fromisoformat(batch_data["start_time"])
                if batch_data.get("end_time"):
                    batch.end_time = datetime.fromisoformat(batch_data["end_time"])
                    
                self.batches[batch_id] = batch
            
            # Restore cost data
            self.cost_data = state_data.get("cost_data", {
                "total_cost": 0.0,
                "model_costs": {},
                "token_usage": {"input": 0, "output": 0}
            })
            
            return True
            
        except Exception as e:
            print(f"Warning: Could not load progress state: {e}")
            return False
    
    def calculate_eta(self, completed: int, total: int, elapsed_time: float) -> Optional[float]:
        """
        Calculate estimated time to completion.
        
        Args:
            completed: Number of completed items
            total: Total number of items
            elapsed_time: Elapsed time in seconds
            
        Returns:
            Optional[float]: ETA in seconds, None if cannot calculate
        """
        if completed == 0 or total == 0 or elapsed_time == 0:
            return None
            
        rate = completed / elapsed_time
        remaining = total - completed
        
        if rate > 0:
            return remaining / rate
        return None
    
    def generate_progress_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive progress report.
        
        Returns:
            Dict[str, Any]: Progress report with statistics and metrics
        """
        elapsed_seconds = self._get_elapsed_seconds()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "session_info": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "elapsed_time": self._get_elapsed_time(),
                "elapsed_seconds": elapsed_seconds,
                "is_monitoring": self.is_monitoring
            },
            "overall_progress": {
                "total_documents": self.total_documents,
                "completed_documents": self.completed_documents,
                "failed_documents": self.failed_documents,
                "remaining_documents": self.total_documents - self.completed_documents - self.failed_documents,
                "completion_percentage": self._calculate_overall_progress(),
                "processing_rate": self._calculate_processing_rate()
            },
            "performance_metrics": {
                "average_processing_time": sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
                "total_processing_time": sum(self.processing_times),
                "estimated_completion": self.calculate_eta(self.completed_documents, self.total_documents, elapsed_seconds)
            },
            "batch_status": {
                batch_id: {
                    "total_documents": batch.total_documents,
                    "completed_documents": batch.completed_documents,
                    "failed_documents": batch.failed_documents,
                    "completion_percentage": batch.get_progress_percentage(),
                    "status": batch.status,
                    "average_processing_time": batch.get_average_processing_time(),
                    "error_count": len(batch.errors)
                }
                for batch_id, batch in self.batches.items()
            },
            "cost_summary": self.cost_data,
            "current_status": {
                "current_batch": self.current_batch,
                "current_document": self.current_document
            }
        }
        
        return report
    
    def generate_detailed_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate detailed progress report with batch breakdown and error analysis.
        
        Args:
            output_path: Optional path to save the report as JSON file
            
        Returns:
            Dict[str, Any]: Detailed progress report
        """
        elapsed_seconds = self._get_elapsed_seconds()
        
        # Calculate detailed statistics
        successful_batches = sum(1 for batch in self.batches.values() if batch.status == "completed")
        failed_batches = sum(1 for batch in self.batches.values() if batch.status == "failed")
        running_batches = sum(1 for batch in self.batches.values() if batch.status == "running")
        pending_batches = sum(1 for batch in self.batches.values() if batch.status == "pending")
        
        # Error analysis
        all_errors = []
        error_categories = {}
        for batch in self.batches.values():
            for error in batch.errors:
                all_errors.append(error)
                error_type = self._categorize_error(error["error"])
                error_categories[error_type] = error_categories.get(error_type, 0) + 1
        
        # Performance analysis
        processing_times_by_batch = {}
        for batch_id, batch in self.batches.items():
            if batch.processing_times:
                processing_times_by_batch[batch_id] = {
                    "min": min(batch.processing_times),
                    "max": max(batch.processing_times),
                    "avg": batch.get_average_processing_time(),
                    "count": len(batch.processing_times)
                }
        
        detailed_report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "detailed_progress_report",
                "session_start": self.start_time.isoformat() if self.start_time else None,
                "session_duration": self._get_elapsed_time(),
                "monitoring_active": self.is_monitoring
            },
            
            "executive_summary": {
                "total_documents": self.total_documents,
                "completed_documents": self.completed_documents,
                "failed_documents": self.failed_documents,
                "success_rate": (self.completed_documents / self.total_documents * 100) if self.total_documents > 0 else 0,
                "overall_progress": self._calculate_overall_progress(),
                "estimated_completion": self.calculate_eta(self.completed_documents, self.total_documents, elapsed_seconds),
                "processing_rate": self._calculate_processing_rate()
            },
            
            "batch_analysis": {
                "total_batches": len(self.batches),
                "successful_batches": successful_batches,
                "failed_batches": failed_batches,
                "running_batches": running_batches,
                "pending_batches": pending_batches,
                "batch_success_rate": (successful_batches / len(self.batches) * 100) if self.batches else 0,
                "detailed_batch_status": {
                    batch_id: {
                        "batch_id": batch_id,
                        "status": batch.status,
                        "total_documents": batch.total_documents,
                        "completed_documents": batch.completed_documents,
                        "failed_documents": batch.failed_documents,
                        "success_rate": (batch.completed_documents / batch.total_documents * 100) if batch.total_documents > 0 else 0,
                        "completion_percentage": batch.get_progress_percentage(),
                        "start_time": batch.start_time.isoformat() if batch.start_time else None,
                        "end_time": batch.end_time.isoformat() if batch.end_time else None,
                        "duration": self._calculate_batch_duration(batch),
                        "average_processing_time": batch.get_average_processing_time(),
                        "current_document": batch.current_document,
                        "error_count": len(batch.errors),
                        "errors": batch.errors
                    }
                    for batch_id, batch in self.batches.items()
                }
            },
            
            "performance_analysis": {
                "overall_metrics": {
                    "total_processing_time": sum(self.processing_times),
                    "average_processing_time": sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
                    "min_processing_time": min(self.processing_times) if self.processing_times else 0,
                    "max_processing_time": max(self.processing_times) if self.processing_times else 0,
                    "processing_rate_per_minute": self._calculate_processing_rate(),
                    "throughput_efficiency": self._calculate_throughput_efficiency()
                },
                "batch_performance": processing_times_by_batch,
                "performance_trends": self._analyze_performance_trends()
            },
            
            "error_analysis": {
                "total_errors": len(all_errors),
                "error_rate": (len(all_errors) / self.total_documents * 100) if self.total_documents > 0 else 0,
                "error_categories": error_categories,
                "detailed_errors": all_errors,
                "error_patterns": self._analyze_error_patterns(all_errors),
                "recovery_suggestions": self._generate_recovery_suggestions(error_categories)
            },
            
            "cost_analysis": {
                "total_cost": self.cost_data["total_cost"],
                "cost_per_document": (self.cost_data["total_cost"] / self.completed_documents) if self.completed_documents > 0 else 0,
                "token_usage": self.cost_data["token_usage"],
                "tokens_per_document": {
                    "input": (self.cost_data["token_usage"]["input"] / self.completed_documents) if self.completed_documents > 0 else 0,
                    "output": (self.cost_data["token_usage"]["output"] / self.completed_documents) if self.completed_documents > 0 else 0
                },
                "model_breakdown": self.cost_data["model_costs"],
                "cost_efficiency": self._calculate_cost_efficiency(),
                "projected_total_cost": self._project_total_cost()
            },
            
            "recommendations": self._generate_recommendations()
        }
        
        # Save report to file if path provided
        if output_path:
            self._save_report_to_file(detailed_report, output_path)
        
        return detailed_report
    
    def generate_summary_statistics(self) -> Dict[str, Any]:
        """
        Generate summary statistics for quick overview.
        
        Returns:
            Dict[str, Any]: Summary statistics
        """
        elapsed_seconds = self._get_elapsed_seconds()
        
        return {
            "session_summary": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "elapsed_time": self._get_elapsed_time(),
                "status": "running" if self.is_monitoring else "stopped"
            },
            "progress_summary": {
                "completion_percentage": self._calculate_overall_progress(),
                "documents_completed": self.completed_documents,
                "documents_failed": self.failed_documents,
                "documents_remaining": self.total_documents - self.completed_documents - self.failed_documents,
                "success_rate": (self.completed_documents / (self.completed_documents + self.failed_documents) * 100) if (self.completed_documents + self.failed_documents) > 0 else 0
            },
            "performance_summary": {
                "processing_rate": self._calculate_processing_rate(),
                "average_time_per_document": sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
                "estimated_completion": self.calculate_eta(self.completed_documents, self.total_documents, elapsed_seconds)
            },
            "cost_summary": {
                "total_cost": self.cost_data["total_cost"],
                "cost_per_document": (self.cost_data["total_cost"] / self.completed_documents) if self.completed_documents > 0 else 0
            }
        }
    
    def print_progress_summary(self) -> None:
        """Print a formatted progress summary to console."""
        summary = self.generate_summary_statistics()
        
        print("\n" + "=" * 60)
        print(self._get_message("progress_monitoring.performance_metrics").center(60))
        print("=" * 60)
        
        # Session info
        print(f"\n{self._get_message('progress_monitoring.elapsed_time', time=summary['session_summary']['elapsed_time'])}")
        print(f"Status: {summary['session_summary']['status'].title()}")
        
        # Progress info
        progress = summary['progress_summary']
        progress_msg = self._get_message('progress_monitoring.overall_progress', 
                                        percent=f"{progress['completion_percentage']:.1f}",
                                        completed=progress['documents_completed'],
                                        total=self.total_documents)
        print(f"\n{progress_msg}")
        
        if progress['success_rate'] > 0:
            print(f"Success Rate: {progress['success_rate']:.1f}%")
        
        # Performance info
        perf = summary['performance_summary']
        if perf['processing_rate'] > 0:
            rate_msg = self._get_message('progress_monitoring.processing_rate', rate=f"{perf['processing_rate']:.1f}")
            print(f"{rate_msg}")
        
        if perf['average_time_per_document'] > 0:
            time_msg = self._get_message('progress_monitoring.avg_processing_time', time=f"{perf['average_time_per_document']:.1f}")
            print(f"{time_msg}")
        
        if perf['estimated_completion']:
            eta_str = self._format_duration(perf['estimated_completion'])
            print(f"{self._get_message('progress_monitoring.estimated_completion', time=eta_str)}")
        
        # Cost info
        cost = summary['cost_summary']
        if cost['total_cost'] > 0:
            cost_msg = self._get_message('cost_tracking.total_cost', cost=f"{cost['total_cost']:.4f}")
            print(f"\n{cost_msg}")
            if cost['cost_per_document'] > 0:
                print(f"Cost per document: ${cost['cost_per_document']:.4f}")
        
        print("=" * 60)
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize error message into error type."""
        error_lower = error_message.lower()
        
        if "network" in error_lower or "connection" in error_lower:
            return "network_error"
        elif "timeout" in error_lower:
            return "timeout_error"
        elif "memory" in error_lower:
            return "memory_error"
        elif "file" in error_lower or "path" in error_lower:
            return "file_error"
        elif "api" in error_lower or "authentication" in error_lower:
            return "api_error"
        elif "format" in error_lower or "parsing" in error_lower:
            return "format_error"
        else:
            return "unknown_error"
    
    def _calculate_batch_duration(self, batch: BatchStatus) -> Optional[str]:
        """Calculate duration for a batch."""
        if not batch.start_time:
            return None
        
        end_time = batch.end_time or datetime.now()
        duration = (end_time - batch.start_time).total_seconds()
        return self._format_duration(duration)
    
    def _calculate_throughput_efficiency(self) -> float:
        """Calculate throughput efficiency as percentage of theoretical maximum."""
        if not self.processing_times or self._get_elapsed_seconds() == 0:
            return 0.0
        
        # Theoretical maximum if all documents were processed at minimum time
        min_time = min(self.processing_times)
        theoretical_max = self.total_documents * min_time
        actual_time = self._get_elapsed_seconds()
        
        return (theoretical_max / actual_time * 100) if actual_time > 0 else 0.0
    
    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        if len(self.processing_times) < 2:
            return {"trend": "insufficient_data"}
        
        # Simple trend analysis - compare first and last quartiles
        n = len(self.processing_times)
        first_quartile = self.processing_times[:n//4] if n >= 4 else self.processing_times[:1]
        last_quartile = self.processing_times[-n//4:] if n >= 4 else self.processing_times[-1:]
        
        avg_first = sum(first_quartile) / len(first_quartile)
        avg_last = sum(last_quartile) / len(last_quartile)
        
        if avg_last < avg_first * 0.9:
            trend = "improving"
        elif avg_last > avg_first * 1.1:
            trend = "degrading"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "first_quartile_avg": avg_first,
            "last_quartile_avg": avg_last,
            "improvement_percentage": ((avg_first - avg_last) / avg_first * 100) if avg_first > 0 else 0
        }
    
    def _analyze_error_patterns(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze error patterns to identify common issues."""
        if not errors:
            return {"patterns": "no_errors"}
        
        # Group errors by document patterns
        document_errors = {}
        for error in errors:
            doc_name = error.get("document", "unknown")
            if doc_name not in document_errors:
                document_errors[doc_name] = []
            document_errors[doc_name].append(error["error"])
        
        # Find documents with multiple errors
        problematic_docs = {doc: errs for doc, errs in document_errors.items() if len(errs) > 1}
        
        return {
            "total_unique_documents_with_errors": len(document_errors),
            "documents_with_multiple_errors": len(problematic_docs),
            "most_problematic_documents": sorted(problematic_docs.items(), key=lambda x: len(x[1]), reverse=True)[:5],
            "error_frequency": len(errors) / len(document_errors) if document_errors else 0
        }
    
    def _generate_recovery_suggestions(self, error_categories: Dict[str, int]) -> List[str]:
        """Generate recovery suggestions based on error patterns."""
        suggestions = []
        
        if error_categories.get("network_error", 0) > 0:
            suggestions.append("Check network connectivity and API endpoint availability")
        
        if error_categories.get("timeout_error", 0) > 0:
            suggestions.append("Consider increasing timeout values or reducing batch sizes")
        
        if error_categories.get("memory_error", 0) > 0:
            suggestions.append("Reduce parallel workers or document batch sizes")
        
        if error_categories.get("api_error", 0) > 0:
            suggestions.append("Verify API credentials and rate limits")
        
        if error_categories.get("file_error", 0) > 0:
            suggestions.append("Check file permissions and paths")
        
        if error_categories.get("format_error", 0) > 0:
            suggestions.append("Review document formats and parsing configuration")
        
        return suggestions
    
    def _calculate_cost_efficiency(self) -> Dict[str, float]:
        """Calculate cost efficiency metrics."""
        if self.completed_documents == 0:
            return {"efficiency": 0.0}
        
        cost_per_doc = self.cost_data["total_cost"] / self.completed_documents
        tokens_per_doc = (self.cost_data["token_usage"]["input"] + self.cost_data["token_usage"]["output"]) / self.completed_documents
        
        return {
            "cost_per_document": cost_per_doc,
            "tokens_per_document": tokens_per_doc,
            "cost_per_token": (self.cost_data["total_cost"] / (self.cost_data["token_usage"]["input"] + self.cost_data["token_usage"]["output"])) if (self.cost_data["token_usage"]["input"] + self.cost_data["token_usage"]["output"]) > 0 else 0
        }
    
    def _project_total_cost(self) -> float:
        """Project total cost based on current progress."""
        if self.completed_documents == 0:
            return 0.0
        
        cost_per_doc = self.cost_data["total_cost"] / self.completed_documents
        return cost_per_doc * self.total_documents
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on current performance."""
        recommendations = []
        
        # Performance recommendations
        if self.processing_times:
            avg_time = sum(self.processing_times) / len(self.processing_times)
            if avg_time > 60:  # More than 1 minute per document
                recommendations.append("Consider optimizing document processing or increasing parallel workers")
        
        # Error rate recommendations
        error_rate = (self.failed_documents / self.total_documents * 100) if self.total_documents > 0 else 0
        if error_rate > 10:
            recommendations.append("High error rate detected - review error logs and consider adjusting configuration")
        
        # Cost recommendations
        if self.cost_data["total_cost"] > 0:
            projected_cost = self._project_total_cost()
            if projected_cost > 100:  # Arbitrary threshold
                recommendations.append("High projected cost - consider reviewing model selection and optimization")
        
        # Progress recommendations
        progress = self._calculate_overall_progress()
        if progress < 10 and self._get_elapsed_seconds() > 3600:  # Less than 10% after 1 hour
            recommendations.append("Slow progress detected - consider increasing parallel workers or optimizing configuration")
        
        return recommendations
    
    def _save_report_to_file(self, report: Dict[str, Any], output_path: str) -> None:
        """Save report to JSON file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
            if self.i18n_manager:
                print(self._get_message("cost_tracking.cost_report_generated", path=str(output_file)))
                
        except Exception as e:
            print(f"Warning: Could not save report to file: {e}")