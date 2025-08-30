#!/usr/bin/env python3
"""
Integration tests for end-to-end ROB assessment workflows.

Tests complete assessment workflows including parallel processing coordination,
state management, progress monitoring, and cost tracking integration.
"""

import unittest
import tempfile
import json
import shutil
import time
import threading
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.parallel_controller import ParallelROBManager
from core.progress_monitor import ProgressMonitor
from core.state_manager import StateManager, AssessmentState
from core.resume_manager import ResumeManager
from src.cost_analyzer import CostAnalyzer
from src.config_manager import ConfigManager
from src.pricing_manager import PricingManager
from i18n.i18n_manager import LanguageManager


class TestEndToEndAssessmentWorkflow(unittest.TestCase):
    """Test complete end-to-end assessment workflows."""
    
    def setUp(self):
        """Set up test environment with complete configuration."""
        self.temp_dir = tempfile.mkdtemp()
        self.setup_test_environment()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def setup_test_environment(self):
        """Set up complete test environment with all required files."""
        # Create directory structure
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        self.temp_work_dir = Path(self.temp_dir) / "temp"
        self.config_dir = Path(self.temp_dir) / "config"
        
        for directory in [self.input_dir, self.output_dir, self.temp_work_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create test documents
        self.test_documents = []
        for i in range(8):  # Create 8 test documents
            doc_path = self.input_dir / f"test_document_{i:03d}.pdf"
            doc_path.write_text(f"Test document {i} content for ROB assessment")
            self.test_documents.append(str(doc_path))
        
        # Create configuration files
        self.create_test_configurations()
    
    def create_test_configurations(self):
        """Create test configuration files."""
        # Main configuration
        self.config_path = self.config_dir / "config.json"
        self.main_config = {
            "paths": {
                "input_folder": str(self.input_dir),
                "output_folder": str(self.output_dir),
                "temp_folder": str(self.temp_work_dir),
                "llm_pricing_config": str(self.config_dir / "pricing.json")
            },
            "processing": {
                "llm_output_mode": "json",
                "eval_optional_items": True,
                "max_text_length": 25000,
                "chunk_overlap": 200
            },
            "parallel": {
                "parallel_workers": 2,
                "max_documents_per_batch": 3,
                "checkpoint_interval": 2,
                "retry_attempts": 2,
                "timeout_seconds": 60
            },
            "llm_models": [
                {
                    "model_name": "gpt-4",
                    "api_key": "test_api_key",
                    "base_url": "https://api.openai.com/v1"
                }
            ],
            "cost_tracking": {
                "enabled": True,
                "currency": "USD",
                "budget_limit": 50.0
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.main_config, f, indent=2)
        
        # Pricing configuration
        self.pricing_config = {
            "models": {
                "gpt-4": {
                    "input_cost_per_1k_tokens": 0.03,
                    "output_cost_per_1k_tokens": 0.06,
                    "currency": "USD"
                },
                "gpt-3.5-turbo": {
                    "input_cost_per_1k_tokens": 0.0015,
                    "output_cost_per_1k_tokens": 0.002,
                    "currency": "USD"
                }
            },
            "currency_rates": {
                "USD": 1.0,
                "EUR": 0.85,
                "CNY": 7.2
            },
            "last_updated": "2024-01-01"
        }
        
        pricing_path = self.config_dir / "pricing.json"
        with open(pricing_path, 'w') as f:
            json.dump(self.pricing_config, f, indent=2)
        
        # I18n configuration
        self.i18n_config = {
            "en": {
                "welcome": "Welcome to ROB Assessment Tool",
                "processing": "Processing...",
                "completed": "Assessment completed successfully",
                "error": "Error occurred: {error}",
                "progress_monitoring": {
                    "overall_progress": "Overall progress: {percent}% ({completed}/{total})",
                    "batch_progress": "Batch {batch_id}: {percent}% complete"
                }
            },
            "zh": {
                "welcome": "欢迎使用ROB评估工具",
                "processing": "处理中...",
                "completed": "评估成功完成",
                "error": "发生错误：{error}",
                "progress_monitoring": {
                    "overall_progress": "总体进度：{percent}% ({completed}/{total})",
                    "batch_progress": "批次 {batch_id}：{percent}% 完成"
                }
            }
        }
        
        i18n_path = self.config_dir / "i18n.json"
        with open(i18n_path, 'w', encoding='utf-8') as f:
            json.dump(self.i18n_config, f, ensure_ascii=False, indent=2)
        
        self.i18n_path = i18n_path
    
    def test_complete_assessment_workflow(self):
        """Test complete assessment workflow from start to finish."""
        # Initialize all components
        config_manager = ConfigManager(str(self.config_path))
        config = config_manager.load_config()
        
        pricing_manager = PricingManager(str(self.config_dir / "pricing.json"))
        pricing_manager.load_pricing_config()
        
        cost_analyzer = CostAnalyzer(str(self.config_dir / "pricing.json"), "integration_test")
        
        i18n_manager = LanguageManager(str(self.i18n_path))
        
        parallel_manager = ParallelROBManager(str(self.config_path))
        
        progress_monitor = ProgressMonitor(
            str(self.temp_work_dir / "progress.json"),
            update_interval=1,
            i18n_manager=i18n_manager
        )
        progress_monitor.set_cost_analyzer(cost_analyzer)
        
        # Test workflow steps
        self.run_assessment_workflow(parallel_manager, progress_monitor, cost_analyzer)
    
    def run_assessment_workflow(self, parallel_manager, progress_monitor, cost_analyzer):
        """Run the complete assessment workflow."""
        # Step 1: Validate configuration and documents
        documents = parallel_manager._get_document_list(str(self.input_dir))
        self.assertEqual(len(documents), 8)
        
        is_valid, issues = parallel_manager.validate_batch_distribution(documents)
        self.assertTrue(is_valid, f"Validation failed: {issues}")
        
        # Step 2: Distribute documents into batches
        batches = parallel_manager.distribute_documents(documents)
        self.assertGreater(len(batches), 0)
        
        # Verify batch distribution
        total_distributed = sum(len(batch.documents) for batch in batches)
        self.assertEqual(total_distributed, len(documents))
        
        # Step 3: Set up progress monitoring
        for batch in batches:
            progress_monitor.add_batch(batch.batch_id, batch.documents)
        
        progress_monitor.start_monitoring()
        
        # Step 4: Simulate assessment processing
        self.simulate_assessment_processing(batches, progress_monitor, cost_analyzer)
        
        # Step 5: Verify results
        self.verify_assessment_results(progress_monitor, cost_analyzer)
        
        # Step 6: Clean up
        progress_monitor.stop_monitoring()
    
    def simulate_assessment_processing(self, batches, progress_monitor, cost_analyzer):
        """Simulate the assessment processing workflow."""
        for batch in batches:
            progress_monitor.start_batch(batch.batch_id)
            
            for i, document in enumerate(batch.documents):
                # Simulate processing time
                processing_time = 0.1 + (i * 0.05)  # Variable processing time
                time.sleep(processing_time)
                
                # Simulate cost tracking
                input_tokens = 1000 + (i * 100)
                output_tokens = 500 + (i * 50)
                cost_analyzer.track_usage(
                    "gpt-4", 
                    input_tokens, 
                    output_tokens, 
                    Path(document).name,
                    "core_assessment"
                )
                
                # Simulate occasional failures (10% failure rate)
                if i % 10 == 9:  # Every 10th document fails
                    progress_monitor.update_batch_progress(
                        batch.batch_id, 
                        Path(document).name,
                        error="Simulated processing error",
                        error_type="processing_error"
                    )
                else:
                    progress_monitor.update_batch_progress(
                        batch.batch_id, 
                        Path(document).name,
                        processing_time=processing_time
                    )
                
                # Create mock result file
                result_file = Path(batch.output_dir) / f"{Path(document).stem}_result.json"
                result_file.parent.mkdir(parents=True, exist_ok=True)
                
                mock_result = {
                    "document": Path(document).name,
                    "assessment_result": "completed" if i % 10 != 9 else "failed",
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
                
                with open(result_file, 'w') as f:
                    json.dump(mock_result, f, indent=2)
        
        # Allow progress monitor to update
        time.sleep(0.2)
    
    def verify_assessment_results(self, progress_monitor, cost_analyzer):
        """Verify the assessment results."""
        # Check progress monitoring results
        report = progress_monitor.generate_progress_report()
        
        self.assertIn("overall_progress", report)
        self.assertIn("batch_details", report)
        self.assertIn("performance_metrics", report)
        
        overall = report["overall_progress"]
        self.assertEqual(overall["total_documents"], 8)
        self.assertGreater(overall["completed_documents"], 0)
        
        # Check cost tracking results
        cost_summary = cost_analyzer.get_cost_summary()
        
        self.assertGreater(cost_summary["total_cost_usd"], 0)
        self.assertGreater(cost_summary["total_tokens"], 0)
        self.assertGreater(cost_summary["total_api_calls"], 0)
        
        # Check that recommendations are generated
        recommendations = cost_analyzer.generate_recommendations()
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
    
    @patch('subprocess.Popen')
    def test_parallel_processing_coordination(self, mock_popen):
        """Test parallel processing coordination and state management."""
        # Mock subprocess for worker processes
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process
        
        parallel_manager = ParallelROBManager(str(self.config_path))
        
        # Test parallel processing setup
        documents = parallel_manager._get_document_list(str(self.input_dir))
        batches = parallel_manager.distribute_documents(documents)
        worker_configs = parallel_manager.create_worker_configs(batches)
        
        # Test worker process coordination
        result = parallel_manager._start_worker_processes(worker_configs)
        self.assertTrue(result)
        
        # Verify that processes were started
        self.assertEqual(mock_popen.call_count, len(worker_configs))
        
        # Test state management during parallel processing
        state_saved = parallel_manager._save_state()
        self.assertTrue(state_saved)
        
        # Verify state can be loaded
        loaded_state, error = parallel_manager.state_manager.load_state(parallel_manager.session_id)
        self.assertIsNotNone(loaded_state)
        self.assertIsNone(error)
    
    def test_checkpoint_and_resume_workflow(self):
        """Test checkpoint creation and resume functionality."""
        # Initialize resume manager
        resume_manager = ResumeManager(str(self.config_path))
        
        # Create initial assessment state
        parallel_manager = resume_manager.parallel_manager
        documents = parallel_manager._get_document_list(str(self.input_dir))
        batches = parallel_manager.distribute_documents(documents)
        
        # Initialize assessment state
        parallel_manager.assessment_state = AssessmentState(
            session_id=parallel_manager.session_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="initializing",
            config=parallel_manager.config,
            temp_dir=str(parallel_manager.temp_dir),
            output_dir=str(parallel_manager.output_dir)
        )
        
        # Save initial state (checkpoint)
        success = parallel_manager._save_state()
        self.assertTrue(success)
        
        # Simulate partial completion
        for i, batch in enumerate(batches[:2]):  # Complete first 2 batches
            for doc in batch.documents:
                # Create mock result files
                result_file = Path(batch.output_dir) / f"{Path(doc).stem}_result.json"
                result_file.parent.mkdir(parents=True, exist_ok=True)
                
                mock_result = {"status": "completed", "document": Path(doc).name}
                with open(result_file, 'w') as f:
                    json.dump(mock_result, f)
        
        # Test resume functionality
        session_id = parallel_manager.session_id
        
        # Create new manager instance to simulate restart
        new_parallel_manager = ParallelROBManager(str(self.config_path))
        
        # Test resume
        resume_success = new_parallel_manager.resume_assessment(session_id=session_id)
        self.assertTrue(resume_success)
        
        # Verify state was restored
        self.assertEqual(new_parallel_manager.session_id, session_id)
        self.assertGreater(len(new_parallel_manager.batches), 0)
    
    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        parallel_manager = ParallelROBManager(str(self.config_path))
        
        progress_monitor = ProgressMonitor(
            str(self.temp_work_dir / "progress.json"),
            update_interval=1
        )
        
        # Test handling of missing documents
        fake_documents = [str(self.input_dir / "non_existent.pdf")]
        is_valid, issues = parallel_manager.validate_batch_distribution(fake_documents)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        
        # Test error tracking in progress monitor
        progress_monitor.add_batch("test_batch", ["doc1.pdf", "doc2.pdf"])
        progress_monitor.start_batch("test_batch")
        
        # Simulate various error types
        error_types = [
            ("api_error", "API connection failed"),
            ("processing_error", "Document parsing failed"),
            ("timeout_error", "Processing timeout"),
            ("critical_error", "Critical system failure")
        ]
        
        for i, (error_type, error_message) in enumerate(error_types):
            progress_monitor.update_batch_progress(
                "test_batch",
                f"doc{i}.pdf",
                error=error_message,
                error_type=error_type
            )
        
        # Verify error tracking
        error_summary = progress_monitor.error_tracker.get_error_summary()
        self.assertEqual(error_summary["total_errors"], len(error_types))
        self.assertIn("api_error", error_summary["error_categories"])
        
        # Test critical error detection
        critical_errors = progress_monitor.error_tracker.get_critical_errors()
        self.assertEqual(len(critical_errors), 1)
    
    def test_performance_and_resource_validation(self):
        """Test performance monitoring and resource usage validation."""
        parallel_manager = ParallelROBManager(str(self.config_path))
        
        progress_monitor = ProgressMonitor(
            str(self.temp_work_dir / "progress.json"),
            update_interval=1
        )
        
        cost_analyzer = CostAnalyzer(str(self.config_dir / "pricing.json"))
        progress_monitor.set_cost_analyzer(cost_analyzer)
        
        # Set up monitoring
        documents = parallel_manager._get_document_list(str(self.input_dir))
        batches = parallel_manager.distribute_documents(documents)
        
        for batch in batches:
            progress_monitor.add_batch(batch.batch_id, batch.documents)
        
        progress_monitor.start_monitoring()
        
        # Simulate processing with performance metrics
        start_time = time.time()
        
        for batch in batches:
            progress_monitor.start_batch(batch.batch_id)
            
            for i, document in enumerate(batch.documents):
                processing_time = 0.05 + (i * 0.01)  # Increasing processing time
                time.sleep(processing_time)
                
                # Track cost
                cost_analyzer.track_usage("gpt-4", 1500, 750, Path(document).name)
                
                # Update progress
                progress_monitor.update_batch_progress(
                    batch.batch_id,
                    Path(document).name,
                    processing_time=processing_time
                )
        
        total_time = time.time() - start_time
        
        # Generate performance report
        report = progress_monitor.generate_progress_report()
        
        # Verify performance metrics
        self.assertIn("performance_metrics", report)
        metrics = report["performance_metrics"]
        
        if "avg_processing_time" in metrics:
            self.assertGreater(metrics["avg_processing_time"], 0)
        
        if "processing_rate" in metrics:
            self.assertGreater(metrics["processing_rate"], 0)
        
        # Verify cost efficiency metrics
        efficiency_metrics = progress_monitor.get_cost_efficiency_metrics()
        if efficiency_metrics:
            self.assertIn("cost_per_document", efficiency_metrics)
            self.assertGreater(efficiency_metrics["cost_per_document"], 0)
        
        progress_monitor.stop_monitoring()
    
    def test_multilingual_interface_integration(self):
        """Test multilingual interface integration throughout workflow."""
        i18n_manager = LanguageManager(str(self.i18n_path))
        
        # Test English interface
        i18n_manager.set_language("en")
        welcome_en = i18n_manager.get_message("welcome")
        self.assertEqual(welcome_en, "Welcome to ROB Assessment Tool")
        
        progress_en = i18n_manager.get_message(
            "progress_monitoring.overall_progress",
            percent="75.5",
            completed=6,
            total=8
        )
        self.assertEqual(progress_en, "Overall progress: 75.5% (6/8)")
        
        # Test Chinese interface
        i18n_manager.set_language("zh")
        welcome_zh = i18n_manager.get_message("welcome")
        self.assertEqual(welcome_zh, "欢迎使用ROB评估工具")
        
        progress_zh = i18n_manager.get_message(
            "progress_monitoring.overall_progress",
            percent="75.5",
            completed=6,
            total=8
        )
        self.assertEqual(progress_zh, "总体进度：75.5% (6/8)")
        
        # Test integration with progress monitor
        progress_monitor = ProgressMonitor(
            str(self.temp_work_dir / "progress.json"),
            i18n_manager=i18n_manager
        )
        
        # Should use localized messages
        self.assertEqual(progress_monitor.i18n_manager, i18n_manager)


class TestComponentIntegration(unittest.TestCase):
    """Test integration between different system components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_pricing_integration(self):
        """Test integration between configuration and pricing managers."""
        # Create test configurations
        config_path = Path(self.temp_dir) / "config.json"
        pricing_path = Path(self.temp_dir) / "pricing.json"
        
        config_data = {
            "paths": {
                "input_folder": str(Path(self.temp_dir) / "input"),
                "output_folder": str(Path(self.temp_dir) / "output"),
                "llm_pricing_config": str(pricing_path)
            },
            "processing": {"llm_output_mode": "json"},
            "llm_models": [
                {"model_name": "gpt-4", "api_key": "test_key"},
                {"model_name": "gpt-3.5-turbo", "api_key": "test_key"}
            ],
            "cost_tracking": {
                "enabled": True,
                "currency": "EUR",
                "budget_limit": 100.0
            }
        }
        
        pricing_data = {
            "models": {
                "gpt-4": {
                    "input_cost_per_1k_tokens": 0.03,
                    "output_cost_per_1k_tokens": 0.06,
                    "currency": "USD"
                },
                "gpt-3.5-turbo": {
                    "input_cost_per_1k_tokens": 0.0015,
                    "output_cost_per_1k_tokens": 0.002,
                    "currency": "USD"
                }
            },
            "currency_rates": {
                "USD": 1.0,
                "EUR": 0.85,
                "CNY": 7.2
            }
        }
        
        # Create input directory
        Path(self.temp_dir, "input").mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        with open(pricing_path, 'w') as f:
            json.dump(pricing_data, f, indent=2)
        
        # Test integration
        config_manager = ConfigManager(str(config_path))
        config = config_manager.load_config()
        
        pricing_manager = PricingManager(config.paths.llm_pricing_config)
        pricing_config = pricing_manager.load_pricing_config()
        
        # Verify integration
        self.assertIsNotNone(pricing_config)
        
        # Test that configured models have pricing
        for llm_model in config.llm_models:
            pricing = pricing_manager.get_model_pricing(llm_model.model_name)
            self.assertIsNotNone(pricing, f"No pricing found for {llm_model.model_name}")
        
        # Test currency compatibility
        target_currency = config.cost_tracking.currency
        supported_currencies = pricing_manager.get_supported_currencies()
        self.assertIn(target_currency, supported_currencies)
    
    def test_state_progress_integration(self):
        """Test integration between state management and progress monitoring."""
        state_dir = Path(self.temp_dir) / "states"
        progress_file = Path(self.temp_dir) / "progress.json"
        
        state_manager = StateManager(str(state_dir))
        progress_monitor = ProgressMonitor(str(progress_file))
        
        # Create test assessment state
        test_state = AssessmentState(
            session_id="integration_test",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="initializing",
            config={"test": "config"},
            temp_dir=str(self.temp_dir),
            output_dir=str(self.temp_dir)
        )
        
        # Save state
        success, error = state_manager.save_state(test_state)
        self.assertTrue(success)
        
        # Set up progress monitoring
        progress_monitor.add_batch("batch_001", ["doc1.pdf", "doc2.pdf"])
        progress_monitor.start_batch("batch_001")
        
        # Update progress
        progress_monitor.update_batch_progress("batch_001", "doc1.pdf", processing_time=1.5)
        
        # Save progress state
        progress_monitor._save_state()
        
        # Verify both states exist
        self.assertTrue(progress_file.exists())
        
        # Load and verify progress state
        new_monitor = ProgressMonitor(str(progress_file))
        load_success = new_monitor.load_state()
        self.assertTrue(load_success)
        
        self.assertEqual(new_monitor.completed_documents, 1)
        self.assertIn("batch_001", new_monitor.batches)


if __name__ == '__main__':
    unittest.main()