#!/usr/bin/env python3
"""
System performance validation script for the ROB Assessment Tool.

This script validates system performance, cost tracking accuracy, and
scalability with various document types and sizes.
"""

import sys
import os
import json
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import core components
from core.parallel_controller import ParallelROBManager
from core.progress_monitor import ProgressMonitor
from src.cost_analyzer import CostAnalyzer
from src.config_manager import ConfigManager
from src.pricing_manager import PricingManager


class SystemPerformanceValidator:
    """System performance validation and optimization testing."""
    
    def __init__(self):
        """Initialize the performance validator."""
        self.temp_dir = None
        self.results = {}
        
    def setup_test_environment(self):
        """Set up test environment for performance validation."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create directory structure
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        self.config_dir = Path(self.temp_dir) / "config"
        
        for directory in [self.input_dir, self.output_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create test configuration
        self.create_test_config()
        
        # Create test documents
        self.create_test_documents()
        
        print(f"✅ Test environment set up in: {self.temp_dir}")
    
    def create_test_config(self):
        """Create test configuration files."""
        # Main configuration
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
            "llm_models": [
                {
                    "name": "gpt-4",
                    "model_name": "gpt-4",
                    "api_key": "test_key",
                    "base_url": "https://api.openai.com/v1"
                }
            ],
            "cost_tracking": {"enabled": True, "currency": "USD"}
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Pricing configuration
        pricing_config = {
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
            "currency_rates": {"USD": 1.0, "EUR": 0.85}
        }
        
        with open(self.config_dir / "pricing.json", 'w') as f:
            json.dump(pricing_config, f, indent=2)
    
    def create_test_documents(self):
        """Create test documents of varying sizes."""
        document_configs = [
            ("small", 1000, 5),    # 5 small documents (1KB each)
            ("medium", 10000, 5),  # 5 medium documents (10KB each)
            ("large", 25000, 3),   # 3 large documents (25KB each)
        ]
        
        self.test_documents = []
        
        for size_name, size_bytes, count in document_configs:
            for i in range(count):
                doc_path = self.input_dir / f"{size_name}_doc_{i:03d}.pdf"
                
                # Create realistic document content
                content = f"""
                Study Title: {size_name.title()} ROB Assessment Test Document {i:03d}
                
                Abstract:
                This is a test document for ROB assessment performance validation.
                Document size category: {size_name}
                Document index: {i:03d}
                
                Methods:
                - Study design: Randomized controlled trial
                - Sample size: {100 + i * 50} participants
                - Primary outcome: Clinical effectiveness
                - Secondary outcomes: Safety and tolerability
                
                Risk of Bias Assessment:
                - Random sequence generation: {'Low' if i % 2 == 0 else 'High'} risk
                - Allocation concealment: {'Low' if i % 3 == 0 else 'Unclear'} risk
                - Blinding of participants: {'Low' if i % 4 == 0 else 'High'} risk
                - Incomplete outcome data: Low risk
                - Selective reporting: Low risk
                - Other bias: {'Low' if i % 5 == 0 else 'Unclear'} risk
                
                Results:
                The study showed significant results with statistical significance.
                Effect size was moderate to large across all measured outcomes.
                
                Conclusion:
                The intervention shows promise for clinical implementation.
                Further research is recommended to validate these findings.
                
                """ + ("Additional content padding. " * (size_bytes // 100))
                
                # Truncate to desired size
                content = content[:size_bytes]
                doc_path.write_text(content, encoding='utf-8')
                self.test_documents.append(str(doc_path))
        
        print(f"✅ Created {len(self.test_documents)} test documents")
    
    def validate_batch_processing_performance(self):
        """Validate batch processing performance."""
        print("\n" + "="*60)
        print("VALIDATING BATCH PROCESSING PERFORMANCE")
        print("="*60)
        
        parallel_manager = ParallelROBManager(str(self.config_path))
        
        # Test different batch sizes
        batch_sizes = [5, 10, 15]
        performance_results = {}
        
        for batch_size in batch_sizes:
            print(f"\nTesting batch size: {batch_size}")
            
            # Update configuration by reloading with modified config
            config_data = json.loads(self.config_path.read_text())
            config_data["parallel"]["max_documents_per_batch"] = batch_size
            self.config_path.write_text(json.dumps(config_data, indent=2))
            
            # Reinitialize manager with updated config
            parallel_manager = ParallelROBManager(str(self.config_path))
            
            # Measure batch distribution time
            start_time = time.time()
            batches = parallel_manager.distribute_documents(self.test_documents)
            distribution_time = time.time() - start_time
            
            performance_results[batch_size] = {
                "distribution_time": distribution_time,
                "num_batches": len(batches),
                "avg_batch_size": sum(len(b.documents) for b in batches) / len(batches) if batches else 0
            }
            
            print(f"  Distribution time: {distribution_time:.4f}s")
            print(f"  Number of batches: {len(batches)}")
            print(f"  Average batch size: {performance_results[batch_size]['avg_batch_size']:.1f}")
            
            # Validate performance
            if distribution_time > 1.0:
                print(f"  ⚠️  Warning: Distribution time ({distribution_time:.4f}s) exceeds 1.0s")
            else:
                print(f"  ✅ Distribution time within acceptable limits")
        
        self.results['batch_processing'] = performance_results
        print("\n✅ Batch processing performance validation completed")
    
    def validate_cost_tracking_accuracy(self):
        """Validate cost tracking accuracy."""
        print("\n" + "="*60)
        print("VALIDATING COST TRACKING ACCURACY")
        print("="*60)
        
        cost_analyzer = CostAnalyzer(str(self.config_dir / "pricing.json"), "accuracy_test")
        
        # Test cases with known expected costs
        test_cases = [
            {
                "model": "gpt-4",
                "input_tokens": 1000,
                "output_tokens": 500,
                "expected_cost": (1000 * 0.03 / 1000) + (500 * 0.06 / 1000)  # $0.06
            },
            {
                "model": "gpt-3.5-turbo",
                "input_tokens": 2000,
                "output_tokens": 1000,
                "expected_cost": (2000 * 0.0015 / 1000) + (1000 * 0.002 / 1000)  # $0.005
            }
        ]
        
        print(f"\nTesting cost calculation accuracy with {len(test_cases)} test cases...")
        
        for i, test_case in enumerate(test_cases):
            cost_analyzer.track_usage(
                test_case["model"],
                test_case["input_tokens"],
                test_case["output_tokens"],
                f"test_doc_{i}.pdf",
                "accuracy_test"
            )
            
            print(f"  Test case {i+1}: {test_case['model']}")
            print(f"    Input tokens: {test_case['input_tokens']}")
            print(f"    Output tokens: {test_case['output_tokens']}")
            print(f"    Expected cost: ${test_case['expected_cost']:.6f}")
        
        # Verify total cost accuracy
        cost_summary = cost_analyzer.get_cost_summary()
        expected_total = sum(case["expected_cost"] for case in test_cases)
        
        print(f"\nCost Summary:")
        print(f"  Expected total cost: ${expected_total:.6f}")
        print(f"  Actual total cost: ${cost_summary['total_cost_usd']:.6f}")
        print(f"  Difference: ${abs(cost_summary['total_cost_usd'] - expected_total):.6f}")
        
        # Validate accuracy (allow for small floating point differences)
        accuracy_threshold = 0.000001
        if abs(cost_summary['total_cost_usd'] - expected_total) < accuracy_threshold:
            print("  ✅ Cost calculation accuracy validated")
        else:
            print("  ❌ Cost calculation accuracy validation failed")
        
        self.results['cost_tracking'] = {
            "expected_total": expected_total,
            "actual_total": cost_summary['total_cost_usd'],
            "accuracy_validated": abs(cost_summary['total_cost_usd'] - expected_total) < accuracy_threshold
        }
        
        print("\n✅ Cost tracking accuracy validation completed")
    
    def validate_system_integration(self):
        """Validate complete system integration."""
        print("\n" + "="*60)
        print("VALIDATING SYSTEM INTEGRATION")
        print("="*60)
        
        # Initialize all components
        parallel_manager = ParallelROBManager(str(self.config_path))
        progress_monitor = ProgressMonitor(str(Path(self.temp_dir) / "progress.json"))
        cost_analyzer = CostAnalyzer(str(self.config_dir / "pricing.json"), "integration_test")
        
        progress_monitor.set_cost_analyzer(cost_analyzer)
        
        print(f"\nTesting with {len(self.test_documents)} documents...")
        
        # Step 1: Document discovery
        start_time = time.time()
        documents = parallel_manager._get_document_list(str(self.input_dir))
        discovery_time = time.time() - start_time
        
        print(f"  Document discovery: {len(documents)} documents in {discovery_time:.4f}s")
        
        # Step 2: Batch distribution
        start_time = time.time()
        batches = parallel_manager.distribute_documents(documents)
        distribution_time = time.time() - start_time
        
        print(f"  Batch distribution: {len(batches)} batches in {distribution_time:.4f}s")
        
        # Step 3: Progress monitoring setup
        for batch in batches:
            progress_monitor.add_batch(batch.batch_id, batch.documents)
        
        progress_monitor.start_monitoring()
        
        # Step 4: Simulate processing workflow
        start_time = time.time()
        
        for batch_idx, batch in enumerate(batches):
            progress_monitor.start_batch(batch.batch_id)
            
            for doc_idx, doc in enumerate(batch.documents):
                doc_name = Path(doc).name
                
                # Simulate processing time based on document size
                doc_size = Path(doc).stat().st_size
                processing_time = 0.01 + (doc_size / 1000000)  # Base time + size factor
                
                # Simulate cost tracking
                input_tokens = 1000 + (doc_size // 100)
                output_tokens = 500 + (doc_size // 200)
                
                cost_analyzer.track_usage("gpt-4", input_tokens, output_tokens, doc_name, "integration")
                
                # Simulate processing delay
                time.sleep(min(processing_time, 0.05))  # Cap at 50ms for testing
                
                # Update progress
                progress_monitor.update_batch_progress(
                    batch.batch_id,
                    doc_name,
                    processing_time=processing_time
                )
        
        processing_time = time.time() - start_time
        
        # Step 5: Generate final reports
        time.sleep(0.1)  # Allow final updates
        
        final_report = progress_monitor.generate_progress_report()
        cost_summary = cost_analyzer.get_cost_summary()
        
        progress_monitor.stop_monitoring()
        
        # Validate results
        print(f"\nIntegration Results:")
        print(f"  Total processing time: {processing_time:.4f}s")
        print(f"  Documents processed: {final_report['overall_progress']['completed_documents']}")
        print(f"  Total cost: ${cost_summary['total_cost_usd']:.6f}")
        print(f"  API calls: {cost_summary['total_api_calls']}")
        
        # Validation checks
        integration_success = True
        
        if final_report['overall_progress']['completed_documents'] != len(documents):
            print("  ❌ Not all documents were processed")
            integration_success = False
        else:
            print("  ✅ All documents processed successfully")
        
        if cost_summary['total_cost_usd'] <= 0:
            print("  ❌ Cost tracking not working")
            integration_success = False
        else:
            print("  ✅ Cost tracking working correctly")
        
        if cost_summary['total_api_calls'] != len(documents):
            print("  ❌ API call count mismatch")
            integration_success = False
        else:
            print("  ✅ API call count matches document count")
        
        self.results['system_integration'] = {
            "processing_time": processing_time,
            "documents_processed": final_report['overall_progress']['completed_documents'],
            "total_cost": cost_summary['total_cost_usd'],
            "api_calls": cost_summary['total_api_calls'],
            "success": integration_success
        }
        
        if integration_success:
            print("\n✅ System integration validation completed successfully")
        else:
            print("\n❌ System integration validation failed")
    
    def generate_validation_report(self):
        """Generate comprehensive validation report."""
        print("\n" + "="*80)
        print("SYSTEM PERFORMANCE VALIDATION REPORT")
        print("="*80)
        
        print(f"\nValidation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Test environment: {self.temp_dir}")
        print(f"Test documents: {len(self.test_documents)}")
        
        # Batch processing results
        if 'batch_processing' in self.results:
            print(f"\nBatch Processing Performance:")
            for batch_size, results in self.results['batch_processing'].items():
                print(f"  Batch size {batch_size}:")
                print(f"    Distribution time: {results['distribution_time']:.4f}s")
                print(f"    Number of batches: {results['num_batches']}")
                print(f"    Average batch size: {results['avg_batch_size']:.1f}")
        
        # Cost tracking results
        if 'cost_tracking' in self.results:
            print(f"\nCost Tracking Accuracy:")
            ct_results = self.results['cost_tracking']
            print(f"  Expected total: ${ct_results['expected_total']:.6f}")
            print(f"  Actual total: ${ct_results['actual_total']:.6f}")
            print(f"  Accuracy validated: {'✅ Yes' if ct_results['accuracy_validated'] else '❌ No'}")
        
        # System integration results
        if 'system_integration' in self.results:
            print(f"\nSystem Integration:")
            si_results = self.results['system_integration']
            print(f"  Processing time: {si_results['processing_time']:.4f}s")
            print(f"  Documents processed: {si_results['documents_processed']}")
            print(f"  Total cost: ${si_results['total_cost']:.6f}")
            print(f"  API calls: {si_results['api_calls']}")
            print(f"  Integration success: {'✅ Yes' if si_results['success'] else '❌ No'}")
        
        # Overall validation status
        overall_success = all([
            self.results.get('cost_tracking', {}).get('accuracy_validated', False),
            self.results.get('system_integration', {}).get('success', False)
        ])
        
        print(f"\n" + "="*80)
        if overall_success:
            print("🎉 OVERALL VALIDATION STATUS: PASSED")
            print("The ROB Assessment Tool has passed all performance validation tests.")
        else:
            print("❌ OVERALL VALIDATION STATUS: FAILED")
            print("Some validation tests failed. Please review the results above.")
        print("="*80)
        
        return overall_success
    
    def cleanup(self):
        """Clean up test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"\n🧹 Cleaned up test environment: {self.temp_dir}")
    
    def run_validation(self):
        """Run complete system performance validation."""
        try:
            print("🚀 Starting ROB Assessment Tool Performance Validation")
            print("="*80)
            
            # Setup
            self.setup_test_environment()
            
            # Run validation tests
            self.validate_batch_processing_performance()
            self.validate_cost_tracking_accuracy()
            self.validate_system_integration()
            
            # Generate report
            success = self.generate_validation_report()
            
            return success
            
        except Exception as e:
            print(f"\n❌ Validation failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()


def main():
    """Main function to run performance validation."""
    validator = SystemPerformanceValidator()
    
    try:
        success = validator.run_validation()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\nUnexpected error during validation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())