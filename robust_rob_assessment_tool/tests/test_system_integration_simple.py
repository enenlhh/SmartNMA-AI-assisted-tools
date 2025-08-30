#!/usr/bin/env python3
"""
Simplified system integration tests for the ROB Assessment Tool.

This module tests the core integration of system components with a focus on
functionality that can be reliably tested.
"""

import unittest
import tempfile
import json
import shutil
import time
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import core components
from core.parallel_controller import ParallelROBManager
from core.progress_monitor import ProgressMonitor
from core.state_manager import StateManager, AssessmentState
from src.cost_analyzer import CostAnalyzer
from src.config_manager import ConfigManager
from src.pricing_manager import PricingManager
from i18n.i18n_manager import LanguageManager


class TestSystemIntegrationSimple(unittest.TestCase):
    """Simplified system integration tests."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.setup_test_environment()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def setup_test_environment(self):
        """Set up test environment with minimal configuration."""
        # Create directory structure
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        self.temp_work_dir = Path(self.temp_dir) / "temp_parallel"
        self.config_dir = Path(self.temp_dir) / "config"
        self.i18n_dir = Path(self.temp_dir) / "i18n"
        
        for directory in [self.input_dir, self.output_dir, self.temp_work_dir, self.config_dir, self.i18n_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create test documents
        self.test_documents = []
        for i in range(6):  # Create 6 test documents
            doc_path = self.input_dir / f"test_document_{i:03d}.pdf"
            doc_content = f"Test document {i} content for ROB assessment testing."
            doc_path.write_text(doc_content, encoding='utf-8')
            self.test_documents.append(str(doc_path))
        
        # Create configuration files
        self.create_test_configurations()
    
    def create_test_configurations(self):
        """Create minimal test configuration files."""
        # Main configuration
        self.config_path = self.config_dir / "config.json"
        self.main_config = {
            "paths": {
                "input_folder": str(self.input_dir),
                "output_folder": str(self.output_dir),
                "temp_folder": str(self.temp_work_dir),
                "llm_pricing_config": str(self.config_dir / "llm_pricing.json")
            },
            "processing": {
                "llm_output_mode": "json",
                "eval_optional_items": True,
                "max_text_length": 25000
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
                    "name": "gpt-4",
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
                }
            },
            "currency_rates": {
                "USD": 1.0,
                "EUR": 0.85
            },
            "last_updated": "2024-01-01"
        }
        
        pricing_path = self.config_dir / "llm_pricing.json"
        with open(pricing_path, 'w') as f:
            json.dump(self.pricing_config, f, indent=2)
        
        # I18n configuration (matches the structure expected by LanguageManager)
        self.i18n_config = {
            "en": {
                "welcome": "Welcome to ROB Assessment Tool",
                "processing": "Processing...",
                "completed": "Assessment completed successfully",
                "progress_monitoring": {
                    "overall_progress": "Overall progress: {percent}% ({completed}/{total})"
                }
            },
            "zh": {
                "welcome": "欢迎使用ROB评估工具",
                "processing": "处理中...",
                "completed": "评估成功完成",
                "progress_monitoring": {
                    "overall_progress": "总体进度：{percent}% ({completed}/{total})"
                }
            }
        }
        
        i18n_path = self.i18n_dir / "i18n_config.json"
        with open(i18n_path, 'w', encoding='utf-8') as f:
            json.dump(self.i18n_config, f, ensure_ascii=False, indent=2)
        
        self.i18n_path = i18n_path
    
    def test_configuration_loading_integration(self):
        """Test configuration loading and validation integration."""
        print("\nTesting configuration loading integration...")
        
        # Test configuration manager
        config_manager = ConfigManager(str(self.config_path))
        config = config_manager.load_config()
        
        # Verify configuration structure
        self.assertIsNotNone(config.paths)
        self.assertIsNotNone(config.processing)
        self.assertIsNotNone(config.parallel)
        self.assertIsNotNone(config.llm_models)
        self.assertIsNotNone(config.cost_tracking)
        
        # Test pricing manager integration
        pricing_manager = PricingManager(str(self.config_dir / "llm_pricing.json"))
        pricing_manager.load_pricing_config()
        
        # Verify pricing for configured models
        for llm_model in config.llm_models:
            pricing = pricing_manager.get_model_pricing(llm_model.name)
            self.assertIsNotNone(pricing, f"No pricing found for {llm_model.name}")
        
        print("✅ Configuration loading integration passed")
    
    def test_document_discovery_and_batch_distribution(self):
        """Test document discovery and batch distribution."""
        print("\nTesting document discovery and batch distribution...")
        
        # Initialize parallel manager
        parallel_manager = ParallelROBManager(str(self.config_path))
        
        # Test document discovery
        documents = parallel_manager._get_document_list(str(self.input_dir))
        self.assertEqual(len(documents), 6, "Incorrect number of documents discovered")
        
        # Test document validation
        for doc_path in documents:
            self.assertTrue(Path(doc_path).exists(), f"Document not found: {doc_path}")
        
        # Test batch distribution
        batches = parallel_manager.distribute_documents(documents)
        self.assertGreater(len(batches), 0, "No batches created")
        
        # Verify batch distribution
        total_distributed = sum(len(batch.documents) for batch in batches)
        self.assertEqual(total_distributed, len(documents), "Document distribution mismatch")
        
        print("✅ Document discovery and batch distribution passed")
    
    def test_progress_monitoring_integration(self):
        """Test progress monitoring integration."""
        print("\nTesting progress monitoring integration...")
        
        # Initialize components
        progress_monitor = ProgressMonitor(
            str(self.temp_work_dir / "progress.json"),
            update_interval=1
        )
        
        cost_analyzer = CostAnalyzer(
            str(self.config_dir / "llm_pricing.json"),
            session_id="integration_test"
        )
        
        progress_monitor.set_cost_analyzer(cost_analyzer)
        
        # Test progress monitoring setup
        test_batches = ["batch_001", "batch_002"]
        test_documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        
        for batch_id in test_batches:
            progress_monitor.add_batch(batch_id, test_documents)
        
        progress_monitor.start_monitoring()
        
        # Simulate processing
        for batch_id in test_batches:
            progress_monitor.start_batch(batch_id)
            
            for doc in test_documents:
                # Track cost
                cost_analyzer.track_usage("gpt-4", 1000, 500, doc, "test_operation")
                
                # Update progress
                progress_monitor.update_batch_progress(
                    batch_id,
                    doc,
                    processing_time=0.1
                )
        
        # Allow progress updates
        time.sleep(0.2)
        
        # Generate report
        report = progress_monitor.generate_progress_report()
        
        # Verify report structure
        self.assertIn("overall_progress", report)
        self.assertIn("batch_status", report)  # Use correct key name
        
        # Verify cost integration
        cost_summary = cost_analyzer.get_cost_summary()
        self.assertGreater(cost_summary["total_cost_usd"], 0)
        
        progress_monitor.stop_monitoring()
        
        print("✅ Progress monitoring integration passed")
    
    def test_state_management_integration(self):
        """Test state management integration."""
        print("\nTesting state management integration...")
        
        # Initialize state manager
        state_manager = StateManager(str(self.temp_work_dir / "states"))
        
        # Create test assessment state
        test_state = AssessmentState(
            session_id="integration_test_state",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="running",
            config=self.main_config,
            temp_dir=str(self.temp_work_dir),
            output_dir=str(self.output_dir)
        )
        
        # Test state saving
        success, error = state_manager.save_state(test_state)
        self.assertTrue(success, f"Failed to save state: {error}")
        
        # Test state loading
        loaded_state, load_error = state_manager.load_state(test_state.session_id)
        self.assertIsNotNone(loaded_state, f"Failed to load state: {load_error}")
        self.assertEqual(loaded_state.session_id, test_state.session_id)
        
        print("✅ State management integration passed")
    
    def test_multilingual_interface_basic(self):
        """Test basic multilingual interface functionality."""
        print("\nTesting multilingual interface...")
        
        # Initialize i18n manager
        i18n_manager = LanguageManager(str(self.i18n_path))
        
        # Test English interface
        i18n_manager.set_language("en")
        welcome_en = i18n_manager.get_message("welcome")
        self.assertEqual(welcome_en, "Welcome to ROB Assessment Tool")
        
        # Test parameterized message
        progress_en = i18n_manager.get_message(
            "progress_monitoring.overall_progress",
            percent="75",
            completed=3,
            total=4
        )
        self.assertIn("75", progress_en)
        self.assertIn("3", progress_en)
        self.assertIn("4", progress_en)
        
        # Test Chinese interface
        i18n_manager.set_language("zh")
        welcome_zh = i18n_manager.get_message("welcome")
        self.assertEqual(welcome_zh, "欢迎使用ROB评估工具")
        
        # Verify messages are different
        self.assertNotEqual(welcome_en, welcome_zh)
        
        print("✅ Multilingual interface basic test passed")
    
    def test_cost_tracking_integration(self):
        """Test cost tracking integration."""
        print("\nTesting cost tracking integration...")
        
        # Initialize cost analyzer
        cost_analyzer = CostAnalyzer(
            str(self.config_dir / "llm_pricing.json"),
            session_id="cost_integration_test"
        )
        
        # Test cost tracking
        test_documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
        
        for i, doc in enumerate(test_documents):
            input_tokens = 1000 + (i * 100)
            output_tokens = 500 + (i * 50)
            
            cost_analyzer.track_usage(
                "gpt-4",
                input_tokens,
                output_tokens,
                doc,
                "rob_assessment"
            )
        
        # Verify cost tracking
        cost_summary = cost_analyzer.get_cost_summary()
        
        self.assertGreater(cost_summary["total_cost_usd"], 0)
        self.assertGreater(cost_summary["total_tokens"], 0)
        self.assertEqual(cost_summary["total_api_calls"], len(test_documents))
        
        # Test cost report generation (if method exists)
        if hasattr(cost_analyzer, 'generate_cost_report'):
            cost_report = cost_analyzer.generate_cost_report(str(self.output_dir))
            self.assertIsNotNone(cost_report)
        else:
            # Alternative: just verify cost summary is available
            self.assertIn("total_cost_usd", cost_summary)
        
        print("✅ Cost tracking integration passed")
    
    def test_error_handling_basic(self):
        """Test basic error handling integration."""
        print("\nTesting error handling...")
        
        # Initialize progress monitor
        progress_monitor = ProgressMonitor(
            str(self.temp_work_dir / "progress.json"),
            update_interval=1
        )
        
        # Test error tracking
        progress_monitor.add_batch("error_test_batch", ["doc1.pdf", "doc2.pdf"])
        progress_monitor.start_batch("error_test_batch")
        
        # Simulate errors
        progress_monitor.update_batch_progress(
            "error_test_batch",
            "doc1.pdf",
            error="Test API error",
            error_type="api_error"
        )
        
        progress_monitor.update_batch_progress(
            "error_test_batch",
            "doc2.pdf",
            processing_time=0.1  # Successful processing
        )
        
        # Verify error tracking
        error_summary = progress_monitor.error_tracker.get_error_summary()
        self.assertEqual(error_summary["total_errors"], 1)
        self.assertIn("api_error", error_summary["error_categories"])
        
        progress_monitor.stop_monitoring()
        
        print("✅ Error handling basic test passed")
    
    def test_main_entry_point_basic(self):
        """Test basic main entry point functionality."""
        print("\nTesting main entry point...")
        
        # Test importing main module
        main_path = Path(__file__).parent.parent / "main.py"
        self.assertTrue(main_path.exists(), "Main entry point not found")
        
        try:
            # Import main module
            import main
            
            # Test argument parser creation
            parser = main.create_argument_parser()
            self.assertIsNotNone(parser)
            
            # Test basic argument parsing
            args = parser.parse_args(["start", "-c", str(self.config_path)])
            self.assertEqual(args.operation, "start")
            self.assertEqual(args.config, str(self.config_path))
            
        except ImportError as e:
            self.fail(f"Failed to import main module: {e}")
        except SystemExit:
            pass  # Expected for argument parsing
        
        print("✅ Main entry point basic test passed")
    
    def test_complete_workflow_simulation(self):
        """Test a complete workflow simulation."""
        print("\nTesting complete workflow simulation...")
        
        # Initialize all components
        config_manager = ConfigManager(str(self.config_path))
        config = config_manager.load_config()
        
        parallel_manager = ParallelROBManager(str(self.config_path))
        
        progress_monitor = ProgressMonitor(
            str(self.temp_work_dir / "progress.json"),
            update_interval=1
        )
        
        cost_analyzer = CostAnalyzer(
            str(self.config_dir / "llm_pricing.json"),
            session_id="workflow_test"
        )
        
        progress_monitor.set_cost_analyzer(cost_analyzer)
        
        # Step 1: Document discovery
        documents = parallel_manager._get_document_list(str(self.input_dir))
        self.assertEqual(len(documents), 6)
        
        # Step 2: Batch distribution
        batches = parallel_manager.distribute_documents(documents)
        self.assertGreater(len(batches), 0)
        
        # Step 3: Progress monitoring setup
        for batch in batches:
            progress_monitor.add_batch(batch.batch_id, batch.documents)
        
        progress_monitor.start_monitoring()
        
        # Step 4: Simulate processing
        for batch in batches:
            progress_monitor.start_batch(batch.batch_id)
            
            for doc in batch.documents:
                # Simulate cost tracking
                cost_analyzer.track_usage("gpt-4", 1200, 600, Path(doc).name, "assessment")
                
                # Simulate processing
                time.sleep(0.01)  # Brief processing time
                
                # Update progress
                progress_monitor.update_batch_progress(
                    batch.batch_id,
                    Path(doc).name,
                    processing_time=0.01
                )
        
        # Step 5: Verify results
        time.sleep(0.1)  # Allow final updates
        
        final_report = progress_monitor.generate_progress_report()
        self.assertIn("overall_progress", final_report)
        self.assertEqual(final_report["overall_progress"]["total_documents"], 6)
        
        cost_summary = cost_analyzer.get_cost_summary()
        self.assertGreater(cost_summary["total_cost_usd"], 0)
        
        progress_monitor.stop_monitoring()
        
        print("✅ Complete workflow simulation passed")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)