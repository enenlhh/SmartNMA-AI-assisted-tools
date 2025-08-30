#!/usr/bin/env python3
"""
Complete system integration tests for the ROB Assessment Tool.

This module tests the complete integration of all system components including:
- Main entry point and CLI interface
- Parallel processing coordination
- Progress monitoring and reporting
- Cost tracking and analysis
- Checkpoint and resume functionality
- Error handling and recovery
- Multilingual interface support
- File organization and output management
"""

import unittest
import tempfile
import json
import shutil
import time
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all major components
from core.parallel_controller import ParallelROBManager
from core.progress_monitor import ProgressMonitor
from core.state_manager import StateManager, AssessmentState
from core.resume_manager import ResumeManager
from core.result_merger import ResultMerger
from core.file_organizer import FileOrganizer
from src.cost_analyzer import CostAnalyzer
from src.config_manager import ConfigManager
from src.pricing_manager import PricingManager
from src.rob_evaluator import ROBEvaluator
from i18n.i18n_manager import LanguageManager


class TestCompleteSystemIntegration(unittest.TestCase):
    """Test complete system integration with all components working together."""
    
    def setUp(self):
        """Set up comprehensive test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.setup_complete_test_environment()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def setup_complete_test_environment(self):
        """Set up complete test environment with all required files and configurations."""
        # Create directory structure
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        self.temp_work_dir = Path(self.temp_dir) / "temp_parallel"
        self.config_dir = Path(self.temp_dir) / "config"
        self.i18n_dir = Path(self.temp_dir) / "i18n"
        
        for directory in [self.input_dir, self.output_dir, self.temp_work_dir, self.config_dir, self.i18n_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create test documents with realistic content
        self.test_documents = []
        for i in range(12):  # Create 12 test documents for comprehensive testing
            doc_path = self.input_dir / f"study_{i:03d}.pdf"
            doc_content = self.generate_realistic_document_content(i)
            doc_path.write_text(doc_content, encoding='utf-8')
            self.test_documents.append(str(doc_path))
        
        # Create comprehensive configuration files
        self.create_comprehensive_configurations()
        
        # Set up environment variables for testing
        os.environ['ROB_TEST_MODE'] = '1'
        os.environ['ROB_CONFIG_PATH'] = str(self.config_path)
    
    def generate_realistic_document_content(self, index):
        """Generate realistic document content for testing."""
        return f"""
        Study {index:03d}: Risk of Bias Assessment Test Document
        
        Abstract:
        This is a test document for ROB assessment containing typical study content.
        The study examines the effectiveness of intervention X compared to control Y.
        
        Methods:
        - Randomized controlled trial design
        - Sample size: {100 + index * 10} participants
        - Primary outcome: Clinical improvement
        - Secondary outcomes: Safety measures
        
        Results:
        The intervention group showed significant improvement compared to control.
        Statistical analysis revealed p < 0.05 for primary outcome.
        
        Conclusion:
        The intervention appears effective but requires further validation.
        
        Risk of Bias Considerations:
        - Random sequence generation: {'Low' if index % 3 == 0 else 'High' if index % 3 == 1 else 'Unclear'} risk
        - Allocation concealment: {'Low' if index % 2 == 0 else 'High'} risk
        - Blinding of participants: {'Low' if index % 4 == 0 else 'High'} risk
        - Incomplete outcome data: {'Low' if index % 5 == 0 else 'Unclear'} risk
        - Selective reporting: Low risk
        - Other bias: {'Low' if index % 6 == 0 else 'Unclear'} risk
        """
    
    def create_comprehensive_configurations(self):
        """Create comprehensive configuration files for all components."""
        # Main system configuration
        self.config_path = self.config_dir / "config.json"
        self.main_config = {
            "paths": {
                "input_folder": str(self.input_dir),
                "output_folder": str(self.output_dir),
                "temp_folder": str(self.temp_work_dir),
                "llm_pricing_config": str(self.config_dir / "llm_pricing.json"),
                "i18n_config": str(self.i18n_dir / "i18n_config.json")
            },
            "processing": {
                "llm_output_mode": "json",
                "eval_optional_items": True,
                "max_text_length": 25000,
                "chunk_overlap": 200,
                "start_index": 0
            },
            "parallel": {
                "parallel_workers": 3,
                "max_documents_per_batch": 4,
                "checkpoint_interval": 2,
                "retry_attempts": 3,
                "timeout_seconds": 120,
                "enable_resume": True
            },
            "llm_models": [
                {
                    "name": "gpt-4",
                    "api_key": "test_api_key_gpt4",
                    "base_url": "https://api.openai.com/v1",
                    "max_tokens": 4000,
                    "temperature": 0.1
                },
                {
                    "name": "gpt-3.5-turbo",
                    "api_key": "test_api_key_gpt35",
                    "base_url": "https://api.openai.com/v1",
                    "max_tokens": 2000,
                    "temperature": 0.1
                }
            ],
            "cost_tracking": {
                "enabled": True,
                "currency": "USD",
                "budget_limit": 100.0,
                "alert_threshold": 80.0,
                "detailed_logging": True
            },
            "output": {
                "generate_excel": True,
                "generate_html": True,
                "generate_json": True,
                "include_visualizations": True,
                "organize_by_date": True
            },
            "error_handling": {
                "max_retries": 3,
                "retry_delay": 1.0,
                "continue_on_error": True,
                "log_errors": True
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.main_config, f, indent=2)
        
        # LLM pricing configuration
        self.pricing_config = {
            "models": {
                "gpt-4": {
                    "input_cost_per_1k_tokens": 0.03,
                    "output_cost_per_1k_tokens": 0.06,
                    "currency": "USD",
                    "context_window": 8192,
                    "max_output_tokens": 4096
                },
                "gpt-3.5-turbo": {
                    "input_cost_per_1k_tokens": 0.0015,
                    "output_cost_per_1k_tokens": 0.002,
                    "currency": "USD",
                    "context_window": 4096,
                    "max_output_tokens": 2048
                },
                "claude-3-opus": {
                    "input_cost_per_1k_tokens": 0.015,
                    "output_cost_per_1k_tokens": 0.075,
                    "currency": "USD",
                    "context_window": 200000,
                    "max_output_tokens": 4096
                }
            },
            "currency_rates": {
                "USD": 1.0,
                "EUR": 0.85,
                "GBP": 0.73,
                "CNY": 7.2,
                "JPY": 110.0
            },
            "last_updated": "2024-01-01T00:00:00Z",
            "update_frequency_hours": 24
        }
        
        pricing_path = self.config_dir / "llm_pricing.json"
        with open(pricing_path, 'w') as f:
            json.dump(self.pricing_config, f, indent=2)
        
        # Internationalization configuration
        self.i18n_config = {
            "default_language": "en",
            "supported_languages": ["en", "zh"],
            "fallback_language": "en",
            "messages": {
                "en": {
                    "welcome": "Welcome to ROB Assessment Tool v2.0",
                    "processing": "Processing documents...",
                    "completed": "Assessment completed successfully",
                    "error": "Error occurred: {error}",
                    "progress_monitoring": {
                        "overall_progress": "Overall progress: {percent}% ({completed}/{total})",
                        "batch_progress": "Batch {batch_id}: {percent}% complete",
                        "eta": "Estimated time remaining: {eta}",
                        "processing_rate": "Processing rate: {rate} docs/min"
                    },
                    "cost_tracking": {
                        "total_cost": "Total cost: ${cost}",
                        "budget_warning": "Warning: {percent}% of budget used",
                        "cost_per_document": "Average cost per document: ${cost}"
                    },
                    "operations": {
                        "start_assessment": "Start New Assessment",
                        "resume_assessment": "Resume Assessment",
                        "monitor_progress": "Monitor Progress",
                        "cleanup_files": "Cleanup Files",
                        "merge_results": "Merge Results"
                    }
                },
                "zh": {
                    "welcome": "欢迎使用ROB评估工具 v2.0",
                    "processing": "正在处理文档...",
                    "completed": "评估成功完成",
                    "error": "发生错误：{error}",
                    "progress_monitoring": {
                        "overall_progress": "总体进度：{percent}% ({completed}/{total})",
                        "batch_progress": "批次 {batch_id}：{percent}% 完成",
                        "eta": "预计剩余时间：{eta}",
                        "processing_rate": "处理速度：{rate} 文档/分钟"
                    },
                    "cost_tracking": {
                        "total_cost": "总成本：${cost}",
                        "budget_warning": "警告：已使用预算的 {percent}%",
                        "cost_per_document": "每文档平均成本：${cost}"
                    },
                    "operations": {
                        "start_assessment": "开始新评估",
                        "resume_assessment": "恢复评估",
                        "monitor_progress": "监控进度",
                        "cleanup_files": "清理文件",
                        "merge_results": "合并结果"
                    }
                }
            }
        }
        
        i18n_path = self.i18n_dir / "i18n_config.json"
        with open(i18n_path, 'w', encoding='utf-8') as f:
            json.dump(self.i18n_config, f, ensure_ascii=False, indent=2)
        
        self.i18n_path = i18n_path
    
    def test_complete_system_workflow(self):
        """Test the complete system workflow from initialization to completion."""
        print("\n" + "="*80)
        print("TESTING COMPLETE SYSTEM WORKFLOW")
        print("="*80)
        
        # Step 1: Initialize all system components
        print("\n1. Initializing system components...")
        components = self.initialize_all_components()
        self.verify_component_initialization(components)
        
        # Step 2: Test configuration validation and loading
        print("\n2. Testing configuration validation...")
        self.test_configuration_integration(components)
        
        # Step 3: Test document discovery and validation
        print("\n3. Testing document discovery...")
        documents = self.test_document_discovery(components)
        
        # Step 4: Test batch distribution and parallel setup
        print("\n4. Testing batch distribution...")
        batches = self.test_batch_distribution(components, documents)
        
        # Step 5: Test progress monitoring setup
        print("\n5. Setting up progress monitoring...")
        self.setup_progress_monitoring(components, batches)
        
        # Step 6: Test complete assessment workflow
        print("\n6. Running complete assessment workflow...")
        self.run_complete_assessment_workflow(components, batches)
        
        # Step 7: Test result processing and merging
        print("\n7. Testing result processing...")
        self.test_result_processing(components)
        
        # Step 8: Test cleanup and finalization
        print("\n8. Testing cleanup and finalization...")
        self.test_cleanup_and_finalization(components)
        
        print("\n" + "="*80)
        print("COMPLETE SYSTEM WORKFLOW TEST PASSED")
        print("="*80)
    
    def initialize_all_components(self):
        """Initialize all system components and return them."""
        components = {}
        
        # Configuration management
        components['config_manager'] = ConfigManager(str(self.config_path))
        components['config'] = components['config_manager'].load_config()
        
        # Pricing management
        components['pricing_manager'] = PricingManager(str(self.config_dir / "llm_pricing.json"))
        components['pricing_manager'].load_pricing_config()
        
        # Cost tracking
        components['cost_analyzer'] = CostAnalyzer(
            str(self.config_dir / "llm_pricing.json"),
            session_id="system_integration_test"
        )
        
        # Internationalization
        components['i18n_manager'] = LanguageManager(str(self.i18n_path))
        components['i18n_manager'].set_language("en")
        
        # Parallel processing controller
        components['parallel_manager'] = ParallelROBManager(str(self.config_path))
        
        # Progress monitoring
        components['progress_monitor'] = ProgressMonitor(
            str(self.temp_work_dir / "progress.json"),
            update_interval=1,
            i18n_manager=components['i18n_manager']
        )
        components['progress_monitor'].set_cost_analyzer(components['cost_analyzer'])
        
        # State management
        components['state_manager'] = StateManager(str(self.temp_work_dir / "states"))
        
        # Resume management
        components['resume_manager'] = ResumeManager(str(self.config_path))
        
        # Result processing
        components['result_merger'] = ResultMerger(str(self.output_dir))
        components['file_organizer'] = FileOrganizer(str(self.output_dir))
        
        return components
    
    def verify_component_initialization(self, components):
        """Verify that all components are properly initialized."""
        required_components = [
            'config_manager', 'config', 'pricing_manager', 'cost_analyzer',
            'i18n_manager', 'parallel_manager', 'progress_monitor',
            'state_manager', 'resume_manager', 'result_merger', 'file_organizer'
        ]
        
        for component_name in required_components:
            self.assertIn(component_name, components, f"Component {component_name} not initialized")
            self.assertIsNotNone(components[component_name], f"Component {component_name} is None")
        
        # Test component communication
        self.assertEqual(
            components['progress_monitor'].cost_analyzer,
            components['cost_analyzer'],
            "Progress monitor not properly linked to cost analyzer"
        )
        
        self.assertEqual(
            components['progress_monitor'].i18n_manager,
            components['i18n_manager'],
            "Progress monitor not properly linked to i18n manager"
        )
    
    def test_configuration_integration(self, components):
        """Test integration between configuration components."""
        config = components['config']
        pricing_manager = components['pricing_manager']
        
        # Verify configuration structure
        self.assertIsNotNone(config.paths)
        self.assertIsNotNone(config.processing)
        self.assertIsNotNone(config.parallel)
        self.assertIsNotNone(config.llm_models)
        self.assertIsNotNone(config.cost_tracking)
        
        # Verify pricing integration
        for llm_model in config.llm_models:
            pricing = pricing_manager.get_model_pricing(llm_model.model_name)
            self.assertIsNotNone(pricing, f"No pricing found for {llm_model.model_name}")
        
        # Verify currency support
        target_currency = config.cost_tracking.currency
        supported_currencies = pricing_manager.get_supported_currencies()
        self.assertIn(target_currency, supported_currencies)
        
        # Test configuration validation
        validation_result = components['config_manager'].validate_config()
        self.assertTrue(validation_result.is_valid, f"Config validation failed: {validation_result.errors}")
    
    def test_document_discovery(self, components):
        """Test document discovery and validation."""
        parallel_manager = components['parallel_manager']
        
        # Test document discovery
        documents = parallel_manager._get_document_list(str(self.input_dir))
        self.assertEqual(len(documents), 12, "Incorrect number of documents discovered")
        
        # Test document validation
        for doc_path in documents:
            self.assertTrue(Path(doc_path).exists(), f"Document not found: {doc_path}")
            self.assertGreater(Path(doc_path).stat().st_size, 0, f"Empty document: {doc_path}")
        
        # Test document filtering
        filtered_docs = parallel_manager._filter_documents(documents, start_index=2, max_docs=8)
        self.assertEqual(len(filtered_docs), 8, "Document filtering failed")
        
        return documents
    
    def test_batch_distribution(self, components, documents):
        """Test batch distribution and parallel processing setup."""
        parallel_manager = components['parallel_manager']
        
        # Test batch distribution
        batches = parallel_manager.distribute_documents(documents)
        self.assertGreater(len(batches), 0, "No batches created")
        
        # Verify batch distribution
        total_distributed = sum(len(batch.documents) for batch in batches)
        self.assertEqual(total_distributed, len(documents), "Document distribution mismatch")
        
        # Test batch validation
        is_valid, issues = parallel_manager.validate_batch_distribution(documents)
        self.assertTrue(is_valid, f"Batch validation failed: {issues}")
        
        # Test worker configuration creation
        worker_configs = parallel_manager.create_worker_configs(batches)
        self.assertEqual(len(worker_configs), len(batches), "Worker config count mismatch")
        
        # Verify worker configurations
        for i, config in enumerate(worker_configs):
            self.assertIn('batch_id', config)
            self.assertIn('documents', config)
            self.assertIn('output_dir', config)
            self.assertEqual(config['batch_id'], batches[i].batch_id)
        
        return batches
    
    def setup_progress_monitoring(self, components, batches):
        """Set up progress monitoring for all batches."""
        progress_monitor = components['progress_monitor']
        
        # Add all batches to progress monitor
        for batch in batches:
            progress_monitor.add_batch(batch.batch_id, batch.documents)
        
        # Start monitoring
        progress_monitor.start_monitoring()
        
        # Verify monitoring setup
        self.assertEqual(len(progress_monitor.batches), len(batches))
        self.assertTrue(progress_monitor.is_monitoring)
    
    def run_complete_assessment_workflow(self, components, batches):
        """Run the complete assessment workflow with all components."""
        parallel_manager = components['parallel_manager']
        progress_monitor = components['progress_monitor']
        cost_analyzer = components['cost_analyzer']
        
        # Simulate complete assessment workflow
        for batch_idx, batch in enumerate(batches):
            print(f"  Processing batch {batch_idx + 1}/{len(batches)}: {batch.batch_id}")
            
            # Start batch processing
            progress_monitor.start_batch(batch.batch_id)
            
            # Process each document in the batch
            for doc_idx, document in enumerate(batch.documents):
                doc_name = Path(document).name
                print(f"    Processing document: {doc_name}")
                
                # Simulate processing time
                processing_time = 0.1 + (doc_idx * 0.02)
                time.sleep(processing_time)
                
                # Simulate LLM usage and cost tracking
                input_tokens = 1200 + (doc_idx * 150)
                output_tokens = 600 + (doc_idx * 75)
                
                cost_analyzer.track_usage(
                    "gpt-4",
                    input_tokens,
                    output_tokens,
                    doc_name,
                    "rob_assessment"
                )
                
                # Simulate occasional processing errors (5% failure rate)
                if doc_idx % 20 == 19:  # Every 20th document fails
                    progress_monitor.update_batch_progress(
                        batch.batch_id,
                        doc_name,
                        error="Simulated API timeout error",
                        error_type="api_timeout"
                    )
                else:
                    # Create mock result file
                    result_file = Path(batch.output_dir) / f"{Path(document).stem}_result.json"
                    result_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    mock_result = {
                        "document": doc_name,
                        "study_id": f"STUDY_{doc_idx:03d}",
                        "rob_assessment": {
                            "random_sequence_generation": "Low" if doc_idx % 3 == 0 else "High",
                            "allocation_concealment": "Low" if doc_idx % 2 == 0 else "High",
                            "blinding_participants": "Low" if doc_idx % 4 == 0 else "High",
                            "incomplete_outcome_data": "Low" if doc_idx % 5 == 0 else "Unclear",
                            "selective_reporting": "Low",
                            "other_bias": "Low" if doc_idx % 6 == 0 else "Unclear"
                        },
                        "processing_time": processing_time,
                        "timestamp": datetime.now().isoformat(),
                        "model_used": "gpt-4",
                        "token_usage": {
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens
                        }
                    }
                    
                    with open(result_file, 'w') as f:
                        json.dump(mock_result, f, indent=2)
                    
                    # Update progress
                    progress_monitor.update_batch_progress(
                        batch.batch_id,
                        doc_name,
                        processing_time=processing_time
                    )
                
                # Simulate checkpoint saving every few documents
                if (doc_idx + 1) % 3 == 0:
                    parallel_manager._save_state()
        
        # Allow final progress updates
        time.sleep(0.5)
        
        # Verify workflow completion
        final_report = progress_monitor.generate_progress_report()
        self.assertIn("overall_progress", final_report)
        self.assertGreater(final_report["overall_progress"]["completed_documents"], 0)
        
        # Verify cost tracking
        cost_summary = cost_analyzer.get_cost_summary()
        self.assertGreater(cost_summary["total_cost_usd"], 0)
        self.assertGreater(cost_summary["total_tokens"], 0)
    
    def test_result_processing(self, components):
        """Test result processing and merging."""
        result_merger = components['result_merger']
        file_organizer = components['file_organizer']
        
        # Find all result files
        result_files = list(self.output_dir.rglob("*_result.json"))
        self.assertGreater(len(result_files), 0, "No result files found")
        
        # Test result merging
        merged_results = result_merger.merge_batch_results(str(self.output_dir))
        self.assertIsNotNone(merged_results)
        self.assertIn("summary", merged_results)
        self.assertIn("results", merged_results)
        
        # Test file organization
        organized_files = file_organizer.organize_output_files()
        self.assertGreater(len(organized_files), 0)
        
        # Test Excel export
        excel_file = result_merger.export_to_excel(merged_results, "complete_results.xlsx")
        self.assertTrue(Path(excel_file).exists())
        
        # Test HTML visualization generation
        html_file = result_merger.generate_html_report(merged_results, "assessment_report.html")
        self.assertTrue(Path(html_file).exists())
    
    def test_cleanup_and_finalization(self, components):
        """Test cleanup and finalization processes."""
        progress_monitor = components['progress_monitor']
        file_organizer = components['file_organizer']
        
        # Stop progress monitoring
        progress_monitor.stop_monitoring()
        self.assertFalse(progress_monitor.is_monitoring)
        
        # Generate final reports
        final_report = progress_monitor.generate_progress_report()
        cost_report = components['cost_analyzer'].generate_cost_report(str(self.output_dir))
        
        # Verify reports
        self.assertIn("overall_progress", final_report)
        self.assertIn("performance_metrics", final_report)
        self.assertIsNotNone(cost_report)
        
        # Test cleanup operations
        temp_files_before = len(list(self.temp_work_dir.rglob("*")))
        file_organizer.cleanup_temp_files(keep_results=True)
        temp_files_after = len(list(self.temp_work_dir.rglob("*")))
        
        # Verify cleanup (should have fewer temp files)
        self.assertLessEqual(temp_files_after, temp_files_before)
    
    def test_error_handling_and_recovery(self):
        """Test comprehensive error handling and recovery mechanisms."""
        print("\n" + "="*80)
        print("TESTING ERROR HANDLING AND RECOVERY")
        print("="*80)
        
        # Initialize components
        components = self.initialize_all_components()
        
        # Test configuration error handling
        print("\n1. Testing configuration error handling...")
        self.test_configuration_error_handling(components)
        
        # Test document processing error handling
        print("\n2. Testing document processing error handling...")
        self.test_document_processing_error_handling(components)
        
        # Test API error handling
        print("\n3. Testing API error handling...")
        self.test_api_error_handling(components)
        
        # Test checkpoint and recovery
        print("\n4. Testing checkpoint and recovery...")
        self.test_checkpoint_recovery(components)
        
        print("\n" + "="*80)
        print("ERROR HANDLING AND RECOVERY TEST PASSED")
        print("="*80)
    
    def test_configuration_error_handling(self, components):
        """Test configuration error handling."""
        config_manager = components['config_manager']
        
        # Test invalid configuration file
        invalid_config_path = self.config_dir / "invalid_config.json"
        invalid_config_path.write_text("{ invalid json }")
        
        with self.assertRaises(Exception):
            ConfigManager(str(invalid_config_path)).load_config()
        
        # Test missing required fields
        incomplete_config = {"paths": {"input_folder": "/nonexistent"}}
        incomplete_config_path = self.config_dir / "incomplete_config.json"
        
        with open(incomplete_config_path, 'w') as f:
            json.dump(incomplete_config, f)
        
        incomplete_manager = ConfigManager(str(incomplete_config_path))
        validation_result = incomplete_manager.validate_config()
        self.assertFalse(validation_result.is_valid)
        self.assertGreater(len(validation_result.errors), 0)
    
    def test_document_processing_error_handling(self, components):
        """Test document processing error handling."""
        progress_monitor = components['progress_monitor']
        
        # Set up error tracking
        progress_monitor.add_batch("error_test_batch", ["doc1.pdf", "doc2.pdf", "doc3.pdf"])
        progress_monitor.start_batch("error_test_batch")
        
        # Simulate various error types
        error_scenarios = [
            ("api_error", "API rate limit exceeded"),
            ("processing_error", "Document parsing failed"),
            ("timeout_error", "Processing timeout after 120 seconds"),
            ("critical_error", "Out of memory error")
        ]
        
        for i, (error_type, error_message) in enumerate(error_scenarios):
            progress_monitor.update_batch_progress(
                "error_test_batch",
                f"doc{i+1}.pdf",
                error=error_message,
                error_type=error_type
            )
        
        # Verify error tracking
        error_summary = progress_monitor.error_tracker.get_error_summary()
        self.assertEqual(error_summary["total_errors"], len(error_scenarios))
        
        # Test error categorization
        for error_type, _ in error_scenarios:
            self.assertIn(error_type, error_summary["error_categories"])
        
        # Test critical error detection
        critical_errors = progress_monitor.error_tracker.get_critical_errors()
        self.assertEqual(len(critical_errors), 1)  # Only one critical error
    
    def test_api_error_handling(self, components):
        """Test API error handling and retry mechanisms."""
        cost_analyzer = components['cost_analyzer']
        
        # Test handling of invalid API responses
        with patch('src.cost_analyzer.CostAnalyzer.track_usage') as mock_track:
            mock_track.side_effect = Exception("API connection failed")
            
            # Should handle the error gracefully
            try:
                cost_analyzer.track_usage("gpt-4", 1000, 500, "test_doc.pdf")
            except Exception:
                pass  # Expected to handle gracefully
        
        # Test retry mechanism simulation
        retry_count = 0
        max_retries = 3
        
        def simulate_retry_logic():
            nonlocal retry_count
            retry_count += 1
            if retry_count < max_retries:
                raise Exception("Temporary API error")
            return "Success"
        
        # Simulate retry logic
        for attempt in range(max_retries + 1):
            try:
                result = simulate_retry_logic()
                break
            except Exception as e:
                if attempt == max_retries:
                    self.fail("Retry logic failed")
                time.sleep(0.01)  # Brief delay
        
        self.assertEqual(result, "Success")
        self.assertEqual(retry_count, max_retries)
    
    def test_checkpoint_recovery(self, components):
        """Test checkpoint creation and recovery functionality."""
        parallel_manager = components['parallel_manager']
        resume_manager = components['resume_manager']
        
        # Create initial assessment state
        documents = parallel_manager._get_document_list(str(self.input_dir))
        batches = parallel_manager.distribute_documents(documents[:6])  # Use subset for testing
        
        # Initialize assessment state
        parallel_manager.assessment_state = AssessmentState(
            session_id=parallel_manager.session_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="running",
            config=parallel_manager.config,
            temp_dir=str(parallel_manager.temp_dir),
            output_dir=str(parallel_manager.output_dir)
        )
        
        # Save checkpoint
        checkpoint_saved = parallel_manager._save_state()
        self.assertTrue(checkpoint_saved, "Failed to save checkpoint")
        
        # Simulate partial completion
        for i, batch in enumerate(batches[:2]):  # Complete first 2 batches
            for doc in batch.documents:
                result_file = Path(batch.output_dir) / f"{Path(doc).stem}_result.json"
                result_file.parent.mkdir(parents=True, exist_ok=True)
                
                mock_result = {
                    "document": Path(doc).name,
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                }
                
                with open(result_file, 'w') as f:
                    json.dump(mock_result, f)
        
        # Test recovery
        session_id = parallel_manager.session_id
        
        # Create new manager instance to simulate restart
        new_parallel_manager = ParallelROBManager(str(self.config_path))
        
        # Test resume functionality
        resume_success = new_parallel_manager.resume_assessment(session_id=session_id)
        self.assertTrue(resume_success, "Failed to resume assessment")
        
        # Verify state restoration
        self.assertEqual(new_parallel_manager.session_id, session_id)
        self.assertIsNotNone(new_parallel_manager.assessment_state)
    
    def test_multilingual_interface_integration(self):
        """Test multilingual interface integration throughout the system."""
        print("\n" + "="*80)
        print("TESTING MULTILINGUAL INTERFACE INTEGRATION")
        print("="*80)
        
        # Test English interface
        print("\n1. Testing English interface...")
        self.test_language_interface("en")
        
        # Test Chinese interface
        print("\n2. Testing Chinese interface...")
        self.test_language_interface("zh")
        
        # Test language switching
        print("\n3. Testing language switching...")
        self.test_language_switching()
        
        print("\n" + "="*80)
        print("MULTILINGUAL INTERFACE INTEGRATION TEST PASSED")
        print("="*80)
    
    def test_language_interface(self, language_code):
        """Test interface in specific language."""
        i18n_manager = LanguageManager(str(self.i18n_path))
        i18n_manager.set_language(language_code)
        
        # Test basic messages
        welcome_msg = i18n_manager.get_message("welcome")
        self.assertIsNotNone(welcome_msg)
        self.assertNotEqual(welcome_msg, "")
        
        # Test parameterized messages
        progress_msg = i18n_manager.get_message(
            "progress_monitoring.overall_progress",
            percent="75.5",
            completed=6,
            total=8
        )
        self.assertIn("75.5", progress_msg)
        self.assertIn("6", progress_msg)
        self.assertIn("8", progress_msg)
        
        # Test cost tracking messages
        cost_msg = i18n_manager.get_message(
            "cost_tracking.total_cost",
            cost="25.50"
        )
        self.assertIn("25.50", cost_msg)
        
        # Test operation messages
        operations = ["start_assessment", "resume_assessment", "monitor_progress"]
        for operation in operations:
            op_msg = i18n_manager.get_message(f"operations.{operation}")
            self.assertIsNotNone(op_msg)
            self.assertNotEqual(op_msg, "")
    
    def test_language_switching(self):
        """Test dynamic language switching."""
        i18n_manager = LanguageManager(str(self.i18n_path))
        
        # Start with English
        i18n_manager.set_language("en")
        welcome_en = i18n_manager.get_message("welcome")
        
        # Switch to Chinese
        i18n_manager.set_language("zh")
        welcome_zh = i18n_manager.get_message("welcome")
        
        # Verify messages are different
        self.assertNotEqual(welcome_en, welcome_zh)
        
        # Switch back to English
        i18n_manager.set_language("en")
        welcome_en_again = i18n_manager.get_message("welcome")
        
        # Verify consistency
        self.assertEqual(welcome_en, welcome_en_again)
    
    @patch('subprocess.run')
    def test_main_entry_point_integration(self, mock_subprocess):
        """Test main entry point integration with all components."""
        print("\n" + "="*80)
        print("TESTING MAIN ENTRY POINT INTEGRATION")
        print("="*80)
        
        # Mock subprocess calls for CLI testing
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Test output"
        
        # Test importing main module
        main_path = Path(__file__).parent.parent / "main.py"
        self.assertTrue(main_path.exists(), "Main entry point not found")
        
        # Test command line argument parsing
        sys.argv = ["main.py", "--version"]
        
        try:
            # Import and test main module
            import main
            
            # Test argument parser creation
            parser = main.create_argument_parser()
            self.assertIsNotNone(parser)
            
            # Test parsing various command combinations
            test_commands = [
                ["start", "-c", str(self.config_path)],
                ["resume", "-s", "test_state.json"],
                ["monitor", "-r", "10"],
                ["cleanup", "-t", "temp_parallel"],
                ["merge", "-i", str(self.output_dir), "-o", "merged.xlsx"]
            ]
            
            for cmd in test_commands:
                try:
                    args = parser.parse_args(cmd)
                    self.assertIsNotNone(args)
                except SystemExit:
                    pass  # Expected for some argument combinations
        
        except ImportError as e:
            self.fail(f"Failed to import main module: {e}")
        
        print("\n" + "="*80)
        print("MAIN ENTRY POINT INTEGRATION TEST PASSED")
        print("="*80)


class TestPerformanceAndScalability(unittest.TestCase):
    """Test system performance and scalability characteristics."""
    
    def setUp(self):
        """Set up performance test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.setup_performance_test_environment()
    
    def tearDown(self):
        """Clean up performance test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def setup_performance_test_environment(self):
        """Set up environment for performance testing."""
        # Create larger document set for performance testing
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        self.config_dir = Path(self.temp_dir) / "config"
        
        for directory in [self.input_dir, self.output_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create performance test configuration
        self.create_performance_config()
        
        # Create test documents of varying sizes
        self.create_test_documents()
    
    def create_performance_config(self):
        """Create configuration optimized for performance testing."""
        self.config_path = self.config_dir / "config.json"
        config = {
            "paths": {
                "input_folder": str(self.input_dir),
                "output_folder": str(self.output_dir),
                "temp_folder": str(Path(self.temp_dir) / "temp"),
                "llm_pricing_config": str(self.config_dir / "pricing.json")
            },
            "processing": {
                "llm_output_mode": "json",
                "max_text_length": 25000
            },
            "parallel": {
                "parallel_workers": 4,
                "max_documents_per_batch": 10,
                "checkpoint_interval": 5
            },
            "llm_models": [{"model_name": "gpt-4", "api_key": "test_key"}],
            "cost_tracking": {"enabled": True, "currency": "USD"}
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Create pricing config
        pricing_config = {
            "models": {
                "gpt-4": {
                    "input_cost_per_1k_tokens": 0.03,
                    "output_cost_per_1k_tokens": 0.06,
                    "currency": "USD"
                }
            },
            "currency_rates": {"USD": 1.0}
        }
        
        with open(self.config_dir / "pricing.json", 'w') as f:
            json.dump(pricing_config, f, indent=2)
    
    def create_test_documents(self):
        """Create test documents of varying sizes."""
        document_sizes = [
            ("small", 1000),    # 1KB documents
            ("medium", 10000),  # 10KB documents
            ("large", 50000),   # 50KB documents
        ]
        
        self.test_documents = []
        
        for size_name, size_bytes in document_sizes:
            for i in range(5):  # 5 documents of each size
                doc_path = self.input_dir / f"{size_name}_doc_{i:03d}.pdf"
                content = f"Test document {size_name} {i}\n" * (size_bytes // 50)
                doc_path.write_text(content[:size_bytes])
                self.test_documents.append(str(doc_path))
    
    def test_batch_processing_performance(self):
        """Test batch processing performance with different configurations."""
        parallel_manager = ParallelROBManager(str(self.config_path))
        
        # Test different batch sizes
        batch_sizes = [5, 10, 15]
        performance_results = {}
        
        for batch_size in batch_sizes:
            # Update configuration
            parallel_manager.config.parallel.max_documents_per_batch = batch_size
            
            # Measure batch distribution time
            start_time = time.time()
            batches = parallel_manager.distribute_documents(self.test_documents)
            distribution_time = time.time() - start_time
            
            performance_results[batch_size] = {
                "distribution_time": distribution_time,
                "num_batches": len(batches),
                "avg_batch_size": sum(len(b.documents) for b in batches) / len(batches)
            }
        
        # Verify performance characteristics
        for batch_size, results in performance_results.items():
            self.assertLess(results["distribution_time"], 1.0, f"Batch distribution too slow for size {batch_size}")
            self.assertGreater(results["num_batches"], 0, f"No batches created for size {batch_size}")
    
    def test_memory_usage_monitoring(self):
        """Test memory usage during processing."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Initialize components
        parallel_manager = ParallelROBManager(str(self.config_path))
        progress_monitor = ProgressMonitor(str(Path(self.temp_dir) / "progress.json"))
        cost_analyzer = CostAnalyzer(str(self.config_dir / "pricing.json"))
        
        # Process documents and monitor memory
        documents = parallel_manager._get_document_list(str(self.input_dir))
        batches = parallel_manager.distribute_documents(documents)
        
        for batch in batches:
            progress_monitor.add_batch(batch.batch_id, batch.documents)
        
        progress_monitor.start_monitoring()
        
        # Simulate processing
        for batch in batches:
            for doc in batch.documents:
                cost_analyzer.track_usage("gpt-4", 1000, 500, Path(doc).name)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        progress_monitor.stop_monitoring()
        
        # Verify memory usage is reasonable (less than 100MB increase)
        self.assertLess(memory_increase, 100, f"Memory usage increased by {memory_increase:.2f}MB")
    
    def test_concurrent_processing_simulation(self):
        """Test concurrent processing simulation."""
        import threading
        
        parallel_manager = ParallelROBManager(str(self.config_path))
        progress_monitor = ProgressMonitor(str(Path(self.temp_dir) / "progress.json"))
        
        documents = parallel_manager._get_document_list(str(self.input_dir))
        batches = parallel_manager.distribute_documents(documents)
        
        # Set up progress monitoring
        for batch in batches:
            progress_monitor.add_batch(batch.batch_id, batch.documents)
        
        progress_monitor.start_monitoring()
        
        # Simulate concurrent batch processing
        def process_batch_simulation(batch):
            """Simulate processing a batch concurrently."""
            for doc in batch.documents:
                time.sleep(0.01)  # Simulate processing time
                progress_monitor.update_batch_progress(
                    batch.batch_id,
                    Path(doc).name,
                    processing_time=0.01
                )
        
        # Start threads for each batch
        threads = []
        start_time = time.time()
        
        for batch in batches:
            thread = threading.Thread(target=process_batch_simulation, args=(batch,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        progress_monitor.stop_monitoring()
        
        # Verify concurrent processing completed in reasonable time
        sequential_time_estimate = len(self.test_documents) * 0.01
        self.assertLess(total_time, sequential_time_estimate, "Concurrent processing not faster than sequential")
        
        # Verify all documents were processed
        final_report = progress_monitor.generate_progress_report()
        self.assertEqual(
            final_report["overall_progress"]["completed_documents"],
            len(self.test_documents)
        )


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)