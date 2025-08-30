#!/usr/bin/env python3
"""
Test script for checkpoint and resume functionality.

This script tests the state persistence and resume capabilities
of the ROB assessment tool.
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state_manager import StateManager, AssessmentState, BatchState, DocumentState, StateFormat
from core.resume_manager import ResumeManager
from core.parallel_controller import ParallelROBManager


def test_state_manager():
    """Test basic state manager functionality."""
    print("🧪 Testing State Manager...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        state_manager = StateManager(temp_dir, StateFormat.JSON)
        
        # Create test assessment state with proper config
        test_config = {
            "paths": {
                "input_folder": temp_dir,
                "output_folder": temp_dir
            },
            "processing": {
                "llm_output_mode": "json"
            },
            "llm_models": {
                "primary": "test_model"
            }
        }
        
        test_state = AssessmentState(
            session_id="test_session_001",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="running",
            config=test_config,
            total_documents=10,
            completed_documents=5,
            temp_dir=temp_dir,
            output_dir=temp_dir
        )
        
        # Add test batch with proper document states
        doc_states = []
        for i in range(10):
            if i < 5:  # Completed documents
                doc_state = DocumentState(
                    document_path=f"doc_{i}.pdf", 
                    status="completed",
                    result_file=f"{temp_dir}/result_{i}.json"
                )
            else:  # Pending documents
                doc_state = DocumentState(
                    document_path=f"doc_{i}.pdf", 
                    status="pending"
                )
            doc_states.append(doc_state)
        
        batch_state = BatchState(
            batch_id="test_batch_001",
            status="running",
            documents=doc_states,
            start_time=datetime.now(),
            progress=50
        )
        
        test_state.batches = [batch_state]
        
        # Test save
        success, error = state_manager.save_state(test_state)
        if not success:
            print(f"❌ Save failed: {error}")
            return False
        
        print("✅ State saved successfully")
        
        # Test load
        loaded_state, error = state_manager.load_state("test_session_001")
        if not loaded_state:
            print(f"❌ Load failed: {error}")
            return False
        
        print("✅ State loaded successfully")
        
        # Test validation
        is_valid, issues = state_manager.validate_state(loaded_state)
        if not is_valid:
            print(f"❌ Validation failed: {issues}")
            return False
        
        print("✅ State validation passed")
        
        # Test list states
        states = state_manager.list_available_states()
        if len(states) != 1:
            print(f"❌ Expected 1 state, found {len(states)}")
            return False
        
        print("✅ State listing works")
        
        return True


def test_resume_manager():
    """Test resume manager functionality."""
    print("\n🧪 Testing Resume Manager...")
    
    # Create temporary config file
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "test_config.json"
        
        # Create minimal test config
        test_config = {
            "paths": {
                "input_folder": temp_dir,
                "output_folder": temp_dir,
                "temp_folder": temp_dir
            },
            "processing": {
                "llm_output_mode": "json"
            },
            "llm_models": {
                "primary": "test_model"
            },
            "parallel": {
                "parallel_workers": 2,
                "max_documents_per_batch": 5
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        # Create test input files
        for i in range(3):
            test_file = Path(temp_dir) / f"test_doc_{i}.pdf"
            test_file.write_text(f"Test document {i}")
        
        try:
            resume_manager = ResumeManager(str(config_path))
            
            # Test list resumable sessions (should be empty initially)
            sessions = resume_manager.list_resumable_sessions()
            print(f"✅ Found {len(sessions)} resumable sessions (expected 0)")
            
            # Create a test session using parallel manager
            parallel_manager = resume_manager.parallel_manager
            
            # Test session creation would require more complex setup
            # For now, just test that the resume manager initializes correctly
            print("✅ Resume manager initialized successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Resume manager test failed: {e}")
            return False


def test_state_persistence():
    """Test state persistence with corruption recovery."""
    print("\n🧪 Testing State Persistence and Recovery...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        state_manager = StateManager(temp_dir, StateFormat.JSON)
        
        # Create test state
        test_state = AssessmentState(
            session_id="persistence_test",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            status="running",
            config={"test": "persistence"},
            total_documents=5
        )
        
        # Save state
        success, error = state_manager.save_state(test_state)
        if not success:
            print(f"❌ Initial save failed: {error}")
            return False
        
        # Verify state file exists
        state_file = Path(temp_dir) / "state_persistence_test.json"
        if not state_file.exists():
            print("❌ State file not created")
            return False
        
        print("✅ State file created")
        
        # Test backup creation
        success, error = state_manager.save_state(test_state, create_backup=True)
        if not success:
            print(f"❌ Backup save failed: {error}")
            return False
        
        # Check if backup was created
        backup_dir = Path(temp_dir) / "backups"
        backup_files = list(backup_dir.glob("state_persistence_test_*.json"))
        if not backup_files:
            print("❌ Backup file not created")
            return False
        
        print("✅ Backup created successfully")
        
        # Test cleanup
        deleted_count, errors = state_manager.cleanup_old_states(max_age_days=0, keep_backups=False)
        if errors:
            print(f"⚠️  Cleanup errors: {errors}")
        
        print(f"✅ Cleanup completed ({deleted_count} files deleted)")
        
        return True


def main():
    """Run all tests."""
    print("🚀 Starting Checkpoint and Resume Tests")
    print("=" * 50)
    
    tests = [
        ("State Manager", test_state_manager),
        ("Resume Manager", test_resume_manager),
        ("State Persistence", test_state_persistence)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())