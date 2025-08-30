#!/usr/bin/env python3
"""
Unit tests for ProgressMonitor and related components.

Tests progress monitoring functionality including real-time updates,
performance metrics, cost tracking integration, and error handling.
"""

import unittest
import tempfile
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.progress_monitor import ProgressMonitor, BatchStatus, ErrorTracker, ProgressReporter


class TestErrorTracker(unittest.TestCase):
    """Test the ErrorTracker class."""
    
    def setUp(self):
        """Set up test environment."""
        self.error_tracker = ErrorTracker()
    
    def test_error_addition(self):
        """Test adding errors to tracker."""
        self.error_tracker.add_error(
            document="test_doc.pdf",
            batch_id="batch_001",
            error_type="api_error",
            error_message="Connection timeout"
        )
        
        self.assertEqual(len(self.error_tracker.errors), 1)
        self.assertIn("api_error", self.error_tracker.error_categories)
        self.assertEqual(len(self.error_tracker.error_categories["api_error"]), 1)
    
    def test_error_severity_determination(self):
        """Test error severity classification."""
        # Test critical error
        self.error_tracker.add_error("doc1.pdf", "batch_001", "system_error", "Critical system failure")
        critical_errors = self.error_tracker.get_critical_errors()
        self.assertEqual(len(critical_errors), 1)
        
        # Test warning
        self.error_tracker.add_error("doc2.pdf", "batch_001", "api_error", "Warning: rate limit approaching")
        
        # Test regular error
        self.error_tracker.add_error("doc3.pdf", "batch_001", "processing_error", "Document parsing failed")
        
        summary = self.error_tracker.get_error_summary()
        self.assertIn("severity_breakdown", summary)
        self.assertGreater(summary["total_errors"], 0)
    
    def test_error_patterns(self):
        """Test error pattern extraction."""
        # Add similar errors
        for i in range(3):
            self.error_tracker.add_error(
                f"doc_{i}.pdf", "batch_001", "api_error", "Connection timeout occurred"
            )
        
        summary = self.error_tracker.get_error_summary()
        patterns = summary["most_common_patterns"]
        
        self.assertGreater(len(patterns), 0)
        # Should find the common "connection timeout" pattern
        pattern_found = any("connection timeout" in pattern[0].lower() for pattern in patterns)
        self.assertTrue(pattern_found)
    
    def test_batch_specific_errors(self):
        """Test getting errors for specific batch."""
        self.error_tracker.add_error("doc1.pdf", "batch_001", "error1", "Error in batch 1")
        self.error_tracker.add_error("doc2.pdf", "batch_002", "error2", "Error in batch 2")
        self.error_tracker.add_error("doc3.pdf", "batch_001", "error3", "Another error in batch 1")
        
        batch_001_errors = self.error_tracker.get_errors_by_batch("batch_001")
        batch_002_errors = self.error_tracker.get_errors_by_batch("batch_002")
        
        self.assertEqual(len(batch_001_errors), 2)
        self.assertEqual(len(batch_002_errors), 1)


class TestBatchStatus(unittest.TestCase):
    """Test the BatchStatus class."""
    
    def setUp(self):
        """Set up test environment."""
        self.batch_status = BatchStatus("test_batch", 10)
    
    def test_batch_initialization(self):
        """Test batch status initialization."""
        self.assertEqual(self.batch_status.batch_id, "test_batch")
        self.assertEqual(self.batch_status.total_documents, 10)
        self.assertEqual(self.batch_status.completed_documents, 0)
        self.assertEqual(self.batch_status.status, "pending")
    
    def test_batch_processing_lifecycle(self):
        """Test complete batch processing lifecycle."""
        # Start processing
        self.batch_status.start_processing()
        self.assertEqual(self.batch_status.status, "running")
        self.assertIsNotNone(self.batch_status.start_time)
        
        # Complete some documents
        self.batch_status.complete_document("doc1.pdf", 2.5)
        self.batch_status.complete_document("doc2.pdf", 3.0)
        
        self.assertEqual(self.batch_status.completed_documents, 2)
        self.assertEqual(len(self.batch_status.processing_times), 2)
        self.assertEqual(self.batch_status.get_progress_percentage(), 20.0)
        
        # Fail a document
        self.batch_status.fail_document("doc3.pdf", "Processing error", "processing_error")
        
        self.assertEqual(self.batch_status.failed_documents, 1)
        self.assertEqual(len(self.batch_status.errors), 1)
        
        # Complete remaining documents
        for i in range(4, 11):
            self.batch_status.complete_document(f"doc{i}.pdf", 2.0)
        
        self.assertEqual(self.batch_status.status, "completed_with_errors")
        self.assertIsNotNone(self.batch_status.end_time)
    
    def test_progress_calculations(self):
        """Test progress percentage calculations."""
        # No progress initially
        self.assertEqual(self.batch_status.get_progress_percentage(), 0.0)
        self.assertEqual(self.batch_status.get_success_percentage(), 0.0)
        
        # Complete half the documents
        for i in range(5):
            self.batch_status.complete_document(f"doc{i}.pdf", 2.0)
        
        self.assertEqual(self.batch_status.get_progress_percentage(), 50.0)
        self.assertEqual(self.batch_status.get_success_percentage(), 50.0)
        
        # Fail the remaining documents
        for i in range(5, 10):
            self.batch_status.fail_document(f"doc{i}.pdf", "Error", "test_error")
        
        self.assertEqual(self.batch_status.get_progress_percentage(), 100.0)
        self.assertEqual(self.batch_status.get_success_percentage(), 50.0)
    
    def test_performance_metrics(self):
        """Test performance metric calculations."""
        # No processing times initially
        self.assertEqual(self.batch_status.get_average_processing_time(), 0.0)
        
        # Add processing times
        processing_times = [1.5, 2.0, 2.5, 3.0, 1.8]
        for i, time_taken in enumerate(processing_times):
            self.batch_status.complete_document(f"doc{i}.pdf", time_taken)
        
        avg_time = self.batch_status.get_average_processing_time()
        expected_avg = sum(processing_times) / len(processing_times)
        self.assertAlmostEqual(avg_time, expected_avg, places=2)
    
    def test_error_summary(self):
        """Test error summary generation."""
        # No errors initially
        summary = self.batch_status.get_error_summary()
        self.assertEqual(summary["error_count"], 0)
        self.assertEqual(summary["error_rate"], 0.0)
        
        # Add some errors
        self.batch_status.fail_document("doc1.pdf", "API Error", "api_error")
        self.batch_status.fail_document("doc2.pdf", "Processing Error", "processing_error")
        self.batch_status.fail_document("doc3.pdf", "Another API Error", "api_error")
        
        summary = self.batch_status.get_error_summary()
        self.assertEqual(summary["error_count"], 3)
        self.assertEqual(summary["error_rate"], 30.0)  # 3 out of 10 documents
        self.assertIn("api_error", summary["error_types"])
        self.assertEqual(summary["error_types"]["api_error"], 2)


class TestProgressMonitor(unittest.TestCase):
    """Test the ProgressMonitor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "progress_state.json"
        
        # Create mock i18n manager
        self.mock_i18n = Mock()
        self.mock_i18n.get_message.return_value = "Test message"
        
        self.monitor = ProgressMonitor(
            str(self.state_file),
            update_interval=1,
            i18n_manager=self.mock_i18n
        )
    
    def tearDown(self):
        """Clean up test environment."""
        if self.monitor.is_monitoring:
            self.monitor.stop_monitoring()
        
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_monitor_initialization(self):
        """Test progress monitor initialization."""
        self.assertEqual(self.monitor.state_file_path, self.state_file)
        self.assertEqual(self.monitor.update_interval, 1)
        self.assertEqual(self.monitor.total_documents, 0)
        self.assertFalse(self.monitor.is_monitoring)
    
    def test_batch_management(self):
        """Test batch addition and management."""
        documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        self.monitor.add_batch("batch_001", documents)
        
        self.assertIn("batch_001", self.monitor.batches)
        self.assertEqual(self.monitor.total_documents, 3)
        
        batch = self.monitor.batches["batch_001"]
        self.assertEqual(batch.total_documents, 3)
        self.assertEqual(batch.status, "pending")
    
    def test_batch_progress_updates(self):
        """Test batch progress updates."""
        documents = ["doc1.pdf", "doc2.pdf"]
        self.monitor.add_batch("batch_001", documents)
        self.monitor.start_batch("batch_001")
        
        # Update progress for successful document
        self.monitor.update_batch_progress("batch_001", "doc1.pdf", processing_time=2.5)
        
        self.assertEqual(self.monitor.completed_documents, 1)
        batch = self.monitor.batches["batch_001"]
        self.assertEqual(batch.completed_documents, 1)
        
        # Update progress for failed document
        self.monitor.update_batch_progress("batch_001", "doc2.pdf", error="Processing failed", error_type="processing_error")
        
        self.assertEqual(self.monitor.failed_documents, 1)
        self.assertEqual(batch.failed_documents, 1)
        self.assertEqual(len(self.monitor.error_tracker.errors), 1)
    
    def test_cost_tracking_integration(self):
        """Test cost tracking integration."""
        # Mock cost analyzer
        mock_cost_analyzer = Mock()
        mock_cost_analyzer.get_cost_summary.return_value = {
            'total_cost_usd': 5.25,
            'total_tokens': 10000,
            'total_api_calls': 15,
            'session_id': 'test_session',
            'model_summaries': [
                {
                    'model': 'gpt-4',
                    'total_cost_usd': 3.50,
                    'total_tokens': 6000,
                    'api_calls': 10,
                    'total_input_tokens': 4000,
                    'total_output_tokens': 2000
                }
            ]
        }
        
        self.monitor.set_cost_analyzer(mock_cost_analyzer)
        self.monitor.update_cost_data()
        
        self.assertEqual(self.monitor.cost_data["total_cost"], 5.25)
        self.assertEqual(self.monitor.cost_data["token_usage"]["total"], 10000)
        self.assertIn("gpt-4", self.monitor.cost_data["model_costs"])
    
    def test_eta_calculation(self):
        """Test ETA calculation."""
        # Test with no progress
        eta = self.monitor.calculate_eta(0, 10, 60)
        self.assertIsNone(eta)
        
        # Test with some progress
        eta = self.monitor.calculate_eta(5, 10, 60)  # 5 out of 10 in 60 seconds
        self.assertIsNotNone(eta)
        self.assertAlmostEqual(eta, 60.0, places=1)  # Should take another 60 seconds
        
        # Test with all completed
        eta = self.monitor.calculate_eta(10, 10, 60)
        self.assertIsNone(eta)
    
    def test_progress_report_generation(self):
        """Test comprehensive progress report generation."""
        # Set up some test data
        documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        self.monitor.add_batch("batch_001", documents)
        self.monitor.start_batch("batch_001")
        self.monitor.start_monitoring()
        
        # Simulate some progress
        self.monitor.update_batch_progress("batch_001", "doc1.pdf", processing_time=2.0)
        self.monitor.update_batch_progress("batch_001", "doc2.pdf", error="Failed", error_type="test_error")
        
        # Generate report
        report = self.monitor.generate_progress_report()
        
        self.assertIn("timestamp", report)
        self.assertIn("session_info", report)
        self.assertIn("overall_progress", report)
        self.assertIn("batch_details", report)
        self.assertIn("performance_metrics", report)
        
        # Check specific values
        overall = report["overall_progress"]
        self.assertEqual(overall["total_documents"], 3)
        self.assertEqual(overall["completed_documents"], 1)
        self.assertEqual(overall["failed_documents"], 1)
    
    def test_monitoring_lifecycle(self):
        """Test monitoring start/stop lifecycle."""
        self.assertFalse(self.monitor.is_monitoring)
        
        # Start monitoring
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.is_monitoring)
        self.assertIsNotNone(self.monitor.start_time)
        self.assertIsNotNone(self.monitor.monitor_thread)
        
        # Let it run briefly
        time.sleep(0.1)
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.is_monitoring)
    
    def test_state_persistence(self):
        """Test state saving and loading."""
        # Set up some data
        documents = ["doc1.pdf", "doc2.pdf"]
        self.monitor.add_batch("batch_001", documents)
        self.monitor.start_batch("batch_001")
        self.monitor.update_batch_progress("batch_001", "doc1.pdf", processing_time=1.5)
        
        # Save state
        self.monitor._save_state()
        self.assertTrue(self.state_file.exists())
        
        # Create new monitor and load state
        new_monitor = ProgressMonitor(str(self.state_file))
        success = new_monitor.load_state()
        
        self.assertTrue(success)
        self.assertEqual(new_monitor.total_documents, 2)
        self.assertEqual(new_monitor.completed_documents, 1)
        self.assertIn("batch_001", new_monitor.batches)
    
    @patch('os.system')
    def test_display_update(self, mock_system):
        """Test display update functionality."""
        # Set up some data
        documents = ["doc1.pdf", "doc2.pdf"]
        self.monitor.add_batch("batch_001", documents)
        self.monitor.start_batch("batch_001")
        self.monitor.start_time = datetime.now() - timedelta(minutes=5)
        self.monitor.update_batch_progress("batch_001", "doc1.pdf", processing_time=2.0)
        
        # Test display update (should not raise exceptions)
        try:
            self.monitor._update_display()
            # If we get here, the display update worked
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Display update failed: {e}")
    
    def test_cost_efficiency_metrics(self):
        """Test cost efficiency metrics calculation."""
        # Set up cost data
        self.monitor.cost_data = {
            "total_cost": 10.50,
            "token_usage": {"total": 21000},
            "api_calls": 25
        }
        self.monitor.completed_documents = 5
        self.monitor.start_time = datetime.now() - timedelta(minutes=10)
        
        metrics = self.monitor.get_cost_efficiency_metrics()
        
        self.assertIn("cost_per_document", metrics)
        self.assertIn("cost_per_token", metrics)
        self.assertIn("cost_per_api_call", metrics)
        self.assertIn("cost_per_minute", metrics)
        
        self.assertAlmostEqual(metrics["cost_per_document"], 2.10, places=2)
        self.assertAlmostEqual(metrics["cost_per_token"], 0.0005, places=6)


class TestProgressReporter(unittest.TestCase):
    """Test the ProgressReporter abstract interface."""
    
    def test_abstract_interface(self):
        """Test that ProgressReporter is abstract."""
        with self.assertRaises(TypeError):
            ProgressReporter()
    
    def test_concrete_implementation(self):
        """Test concrete implementation of ProgressReporter."""
        class TestReporter(ProgressReporter):
            def __init__(self):
                self.progress_data = {}
            
            def update_progress(self, progress_data):
                self.progress_data = progress_data
            
            def generate_report(self):
                return {"status": "test_report", "data": self.progress_data}
        
        reporter = TestReporter()
        test_data = {"completed": 5, "total": 10}
        
        reporter.update_progress(test_data)
        report = reporter.generate_report()
        
        self.assertEqual(report["status"], "test_report")
        self.assertEqual(report["data"], test_data)


if __name__ == '__main__':
    unittest.main()