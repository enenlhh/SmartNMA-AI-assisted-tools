#!/usr/bin/env python3
"""
Unit tests for ParallelROBManager and related components.

Tests parallel processing controller functionality including document distribution,
batch management, worker coordination, and state management.
"""

import unittest
import tempfile
import json
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.parallel_controller import ParallelROBManager, Batch, ParallelProcessorInterface
from core.state_manager import StateManager, AssessmentState, BatchState, DocumentState


class TestBatch(unittest.TestCase):
    """Test the Batch data class."""
    
    def test_batch_creation(self):
        """Test basic batch creation."""
        batch = Batch(
            batch_id="test_batch_001",
            documents=["doc1.pdf", "doc2.pdf"],
            output_dir="/tmp/output",
            config={"test": "config"}
        )
        
        self.assertEqual(batch.batch_id, "test_batch_001")
        self.assertEqual(len(batch.documents), 2)
        self.assertEqual(batch.status, "pending")
        self.assertIsNone(batch.start_time)
    
    def test_batch_serialization(self):
        """Test batch to_dict and from_dict methods."""
        original_batch = Batch(
            batch_id="test_batch_002",
            documents=["doc1.pdf"],
            output_dir="/tmp/output",
            config={"test": "config"},
            status="running",
            start_time=datetime.now()
        )
        
        # Test serialization
        batch_dict = original_batch.to_dict()
        self.assertIn("batch_id", batch_dict)
        self.assertIn("start_time", batch_dict)
        self.assertIsInstance(batch_dict["start_time"], str)
        
        # Test deserialization
        restored_batch = Batch.from_dict(batch_dict)
        self.assertEqual(restored_batch.batch_id, original_batch.batch_id)
        self.assertEqual(restored_batch.status, original_batch.status)
        self.assertIsInstance(restored_batch.start_time, datetime)


class TestParallelROBManager(unittest.TestCase):
    """Test the ParallelROBManager class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Create test configuration
        self.test_config = {
            "paths": {
                "input_folder": str(Path(self.temp_dir) / "input"),
                "output_folder": str(Path(self.temp_dir) / "output"),
                "temp_folder": str(Path(self.temp_dir) / "temp"),
                "llm_pricing_config": str(Path(self.temp_dir) / "pricing.json")
            },
            "processing": {
                "llm_output_mode": "json",
                "eval_optional_items": True,
                "max_text_length": 25000
            },
            "parallel": {
                "parallel_workers": 2,
                "max_documents_per_batch": 5,
                "checkpoint_interval": 10,
                "retry_attempts": 3,
                "timeout_seconds": 300
            },
            "llm_models": {
                "primary": "gpt-4"
            }
        }
        
        # Save configuration
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f, indent=2)
        
        # Create input directory and test files
        input_dir = Path(self.temp_dir) / "input"
        input_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(10):
            test_file = input_dir / f"test_doc_{i:03d}.pdf"
            test_file.write_text(f"Test document {i}")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_manager_initialization(self):
        """Test ParallelROBManager initialization."""
        manager = ParallelROBManager(str(self.config_path))
        
        self.assertEqual(manager.config_path, self.config_path)
        self.assertIsNotNone(manager.config)
        self.assertIsNotNone(manager.session_id)
        self.assertEqual(len(manager.batches), 0)
        self.assertIsInstance(manager.state_manager, StateManager)
    
    def test_config_loading(self):
        """Test configuration loading and validation."""
        manager = ParallelROBManager(str(self.config_path))
        
        # Check that default parallel settings are applied
        self.assertIn("parallel", manager.config)
        self.assertIn("parallel_workers", manager.config["parallel"])
        self.assertGreater(manager.config["parallel"]["parallel_workers"], 0)
    
    def test_document_list_retrieval(self):
        """Test getting document list from input folder."""
        manager = ParallelROBManager(str(self.config_path))
        
        documents = manager._get_document_list(self.test_config["paths"]["input_folder"])
        
        self.assertEqual(len(documents), 10)
        self.assertTrue(all(doc.endswith('.pdf') for doc in documents))
        self.assertTrue(all(Path(doc).exists() for doc in documents))
    
    def test_batch_size_calculation(self):
        """Test optimal batch size calculation."""
        manager = ParallelROBManager(str(self.config_path))
        
        # Test with 10 documents and 2 workers
        batch_size = manager._calculate_optimal_batch_size(10, 2)
        self.assertGreater(batch_size, 0)
        self.assertLessEqual(batch_size, manager.config["parallel"]["max_documents_per_batch"])
        
        # Test with more documents than max batch size
        large_batch_size = manager._calculate_optimal_batch_size(100, 2)
        self.assertEqual(large_batch_size, manager.config["parallel"]["max_documents_per_batch"])
    
    def test_document_distribution(self):
        """Test document distribution into batches."""
        manager = ParallelROBManager(str(self.config_path))
        
        documents = manager._get_document_list(self.test_config["paths"]["input_folder"])
        batches = manager.distribute_documents(documents)
        
        self.assertGreater(len(batches), 0)
        
        # Check that all documents are distributed
        total_distributed = sum(len(batch.documents) for batch in batches)
        self.assertEqual(total_distributed, len(documents))
        
        # Check batch properties
        for batch in batches:
            self.assertIsInstance(batch, Batch)
            self.assertTrue(batch.batch_id.startswith(manager.session_id))
            self.assertEqual(batch.status, "pending")
            self.assertIsNotNone(batch.config)
    
    def test_worker_config_creation(self):
        """Test worker configuration creation."""
        manager = ParallelROBManager(str(self.config_path))
        
        documents = manager._get_document_list(self.test_config["paths"]["input_folder"])
        batches = manager.distribute_documents(documents)
        worker_configs = manager.create_worker_configs(batches)
        
        self.assertEqual(len(worker_configs), len(batches))
        
        for i, config in enumerate(worker_configs):
            self.assertIn("batch_id", config)
            self.assertIn("config_file", config)
            self.assertIn("documents", config)
            self.assertIn("output_dir", config)
            self.assertIn("worker_script", config)
            
            # Check that config file was created
            self.assertTrue(Path(config["config_file"]).exists())
    
    def test_batch_validation(self):
        """Test batch distribution validation."""
        manager = ParallelROBManager(str(self.config_path))
        
        documents = manager._get_document_list(self.test_config["paths"]["input_folder"])
        is_valid, issues = manager.validate_batch_distribution(documents)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
        
        # Test with non-existent documents
        fake_documents = ["non_existent.pdf"]
        is_valid, issues = manager.validate_batch_distribution(fake_documents)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
    
    def test_batch_summary(self):
        """Test batch summary generation."""
        manager = ParallelROBManager(str(self.config_path))
        
        # Test empty summary
        summary = manager.get_batch_summary()
        self.assertEqual(summary["total_batches"], 0)
        self.assertEqual(summary["total_documents"], 0)
        
        # Test with batches
        documents = manager._get_document_list(self.test_config["paths"]["input_folder"])
        manager.distribute_documents(documents)
        
        summary = manager.get_batch_summary()
        self.assertGreater(summary["total_batches"], 0)
        self.assertEqual(summary["total_documents"], len(documents))
        self.assertIn("status_counts", summary)
        self.assertIn("session_id", summary)
    
    @patch('subprocess.Popen')
    def test_worker_process_management(self, mock_popen):
        """Test worker process starting and management."""
        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        manager = ParallelROBManager(str(self.config_path))
        documents = manager._get_document_list(self.test_config["paths"]["input_folder"])
        batches = manager.distribute_documents(documents)
        worker_configs = manager.create_worker_configs(batches)
        
        # Test starting processes
        result = manager._start_worker_processes(worker_configs)
        
        # Should succeed with mocked processes
        self.assertTrue(result)
        
        # Check that Popen was called for each worker
        self.assertEqual(mock_popen.call_count, len(worker_configs))
    
    def test_state_management(self):
        """Test state saving and loading."""
        manager = ParallelROBManager(str(self.config_path))
        
        # Create some batches
        documents = manager._get_document_list(self.test_config["paths"]["input_folder"])
        manager.distribute_documents(documents)
        
        # Initialize assessment state
        manager.assessment_state = AssessmentState(
            session_id=manager.session_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="initializing",
            config=manager.config,
            temp_dir=str(manager.temp_dir),
            output_dir=str(manager.output_dir)
        )
        
        # Test state saving
        result = manager._save_state()
        self.assertTrue(result)
        
        # Test state loading
        loaded_state, error = manager.state_manager.load_state(manager.session_id)
        self.assertIsNotNone(loaded_state)
        self.assertIsNone(error)
        self.assertEqual(loaded_state.session_id, manager.session_id)


class TestParallelProcessorInterface(unittest.TestCase):
    """Test the ParallelProcessorInterface abstract class."""
    
    def test_interface_methods(self):
        """Test that interface methods are abstract."""
        with self.assertRaises(TypeError):
            # Should not be able to instantiate abstract class
            ParallelProcessorInterface()
    
    def test_concrete_implementation(self):
        """Test concrete implementation of interface."""
        class TestProcessor(ParallelProcessorInterface):
            def initialize(self, config):
                return True
            
            def process_batch(self, batch):
                return {"status": "completed"}
            
            def cleanup(self):
                pass
        
        processor = TestProcessor()
        self.assertTrue(processor.initialize({}))
        result = processor.process_batch(Mock())
        self.assertEqual(result["status"], "completed")


if __name__ == '__main__':
    unittest.main()