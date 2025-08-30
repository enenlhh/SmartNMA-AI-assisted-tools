#!/usr/bin/env python3
"""
Example demonstrating checkpoint and resume functionality.

This example shows how to use the checkpoint and resume features
in the ROB assessment tool.
"""

import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.parallel_controller import ParallelROBManager
from core.resume_manager import ResumeManager


def create_example_config(temp_dir: str) -> str:
    """Create an example configuration file."""
    config = {
        "paths": {
            "input_folder": f"{temp_dir}/input",
            "output_folder": f"{temp_dir}/output",
            "temp_folder": f"{temp_dir}/temp"
        },
        "processing": {
            "llm_output_mode": "json",
            "eval_optional_items": True,
            "max_text_length": 25000,
            "start_index": 0
        },
        "llm_models": {
            "primary": {
                "model": "gpt-4",
                "api_key": "your_api_key_here",
                "base_url": "https://api.openai.com/v1"
            }
        },
        "parallel": {
            "parallel_workers": 2,
            "max_documents_per_batch": 3,
            "checkpoint_interval": 5,
            "retry_attempts": 3,
            "timeout_seconds": 300
        }
    }
    
    config_path = Path(temp_dir) / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return str(config_path)


def create_example_documents(input_dir: str, count: int = 5):
    """Create example PDF documents for testing."""
    input_path = Path(input_dir)
    input_path.mkdir(parents=True, exist_ok=True)
    
    for i in range(count):
        doc_path = input_path / f"example_study_{i+1}.pdf"
        # Create a simple text file (in real usage, these would be PDF files)
        doc_path.write_text(f"""
Example Study {i+1}

This is a sample research paper for ROB assessment testing.

Methods: This study used a randomized controlled trial design...
Results: The primary outcome showed significant improvement...
Conclusion: The intervention was effective...
        """.strip())


def demonstrate_checkpoint_resume():
    """Demonstrate the checkpoint and resume functionality."""
    print("🚀 Checkpoint and Resume Demonstration")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Working directory: {temp_dir}")
        
        # Create example configuration and documents
        config_path = create_example_config(temp_dir)
        create_example_documents(f"{temp_dir}/input", count=6)
        
        print("✅ Created example configuration and documents")
        
        # Initialize parallel manager
        parallel_manager = ParallelROBManager(config_path)
        resume_manager = ResumeManager(config_path)
        
        print(f"✅ Initialized managers")
        print(f"   Session ID: {parallel_manager.session_id}")
        
        # Demonstrate session listing (should be empty initially)
        print("\n📋 Listing available sessions:")
        sessions = resume_manager.list_resumable_sessions()
        print(f"   Found {len(sessions)} resumable sessions")
        
        # Get documents for processing
        try:
            documents = parallel_manager._get_document_list(f"{temp_dir}/input")
            print(f"\n📄 Found {len(documents)} documents to process:")
            for doc in documents:
                print(f"   - {Path(doc).name}")
        except Exception as e:
            print(f"❌ Error getting documents: {e}")
            return
        
        # Create batches (simulate assessment setup)
        print("\n⚙️  Creating processing batches:")
        batches = parallel_manager.distribute_documents(documents)
        print(f"   Created {len(batches)} batches")
        
        for i, batch in enumerate(batches):
            print(f"   Batch {i+1}: {len(batch.documents)} documents")
        
        # Save initial state
        print("\n💾 Saving initial state:")
        if parallel_manager._save_state():
            print("   ✅ State saved successfully")
            session_id = parallel_manager.session_id
        else:
            print("   ❌ Failed to save state")
            return
        
        # Demonstrate session info
        print(f"\n📊 Session information:")
        session_info = resume_manager.parallel_manager.get_session_info(session_id)
        if session_info:
            print(f"   Status: {session_info['status']}")
            print(f"   Total documents: {session_info['total_documents']}")
            print(f"   Total batches: {session_info['total_batches']}")
            print(f"   Progress: {session_info['progress']}%")
        
        # Demonstrate resume preview
        print(f"\n🔍 Resume preview:")
        preview = resume_manager.get_resume_preview(session_id)
        if preview:
            print(f"   Can resume: {preview['can_resume']}")
            print(f"   Remaining documents: {preview['progress']['remaining_documents']}")
            print(f"   Incomplete batches: {preview['batches']['incomplete_batches']}")
            
            if preview['issues']:
                print("   Issues found:")
                for issue in preview['issues']:
                    print(f"     - {issue}")
        
        # List sessions again (should show our session)
        print(f"\n📋 Listing sessions after creation:")
        sessions = resume_manager.list_resumable_sessions()
        print(f"   Found {len(sessions)} resumable sessions")
        
        for session in sessions:
            print(f"   - {session['session_id'][:12]}... ({session['status']})")
        
        # Demonstrate state manager features
        print(f"\n🔧 State manager features:")
        all_states = parallel_manager.state_manager.list_available_states()
        print(f"   Available states: {len(all_states)}")
        
        # Validate state
        assessment_state = parallel_manager.assessment_state
        if assessment_state:
            is_valid, issues = parallel_manager.state_manager.validate_state(assessment_state)
            print(f"   State valid: {is_valid}")
            if issues:
                print("   Validation issues:")
                for issue in issues:
                    print(f"     - {issue}")
        
        print(f"\n✅ Demonstration completed successfully!")
        print(f"\nIn a real scenario, you would:")
        print(f"  1. Start the assessment with: parallel_manager.start_parallel_assessment()")
        print(f"  2. If interrupted, resume with: resume_manager.resume_session('{session_id}')")
        print(f"  3. Monitor progress with the progress monitor")
        print(f"  4. Use the resume CLI for management: python scripts/resume_cli.py")


def demonstrate_cli_usage():
    """Show example CLI usage."""
    print(f"\n🖥️  CLI Usage Examples:")
    print(f"=" * 30)
    
    cli_examples = [
        ("List all resumable sessions", "python scripts/resume_cli.py list"),
        ("Show session details", "python scripts/resume_cli.py info SESSION_ID"),
        ("Resume a session", "python scripts/resume_cli.py resume SESSION_ID"),
        ("Force resume despite issues", "python scripts/resume_cli.py resume SESSION_ID --force"),
        ("Detect completed work", "python scripts/resume_cli.py detect SESSION_ID"),
        ("Clean up failed session", "python scripts/resume_cli.py cleanup SESSION_ID"),
        ("Export session report", "python scripts/resume_cli.py export SESSION_ID"),
        ("Show session logs", "python scripts/resume_cli.py logs SESSION_ID --tail")
    ]
    
    for description, command in cli_examples:
        print(f"\n{description}:")
        print(f"  {command}")


if __name__ == "__main__":
    try:
        demonstrate_checkpoint_resume()
        demonstrate_cli_usage()
        
        print(f"\n🎉 Example completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        sys.exit(1)