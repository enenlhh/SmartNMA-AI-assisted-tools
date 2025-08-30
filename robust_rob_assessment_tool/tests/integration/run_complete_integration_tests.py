#!/usr/bin/env python3
"""
Complete system integration test runner for the ROB Assessment Tool.

This script runs comprehensive integration tests to validate the complete system
functionality including all components working together.
"""

import sys
import os
import unittest
import time
import json
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import test modules
from tests.test_complete_system_integration import (
    TestCompleteSystemIntegration,
    TestPerformanceAndScalability
)
from tests.test_integration_workflows import (
    TestEndToEndAssessmentWorkflow,
    TestComponentIntegration
)


class IntegrationTestRunner:
    """Comprehensive integration test runner with detailed reporting."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.start_time = None
        self.results = {}
        self.temp_dirs = []
        
    def setup_test_environment(self):
        """Set up the test environment."""
        print("="*80)
        print("ROB ASSESSMENT TOOL - COMPLETE SYSTEM INTEGRATION TESTS")
        print("="*80)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python version: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        print("="*80)
        
        # Verify project structure
        self.verify_project_structure()
        
        # Set up test environment variables
        os.environ['ROB_TEST_MODE'] = '1'
        os.environ['ROB_INTEGRATION_TEST'] = '1'
        
        self.start_time = time.time()
    
    def verify_project_structure(self):
        """Verify that the project structure is complete."""
        print("\nVerifying project structure...")
        
        required_directories = [
            "src", "core", "i18n", "config", "tests", "docs"
        ]
        
        required_files = [
            "main.py",
            "requirements.txt",
            "src/rob_evaluator.py",
            "src/cost_analyzer.py",
            "src/config_manager.py",
            "core/parallel_controller.py",
            "core/progress_monitor.py",
            "core/state_manager.py",
            "core/resume_manager.py",
            "core/result_merger.py",
            "i18n/i18n_manager.py"
        ]
        
        missing_items = []
        
        # Check directories
        for directory in required_directories:
            if not Path(directory).exists():
                missing_items.append(f"Directory: {directory}")
        
        # Check files
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_items.append(f"File: {file_path}")
        
        if missing_items:
            print("❌ Missing required project components:")
            for item in missing_items:
                print(f"  - {item}")
            print("\nPlease ensure all components are implemented before running integration tests.")
            sys.exit(1)
        else:
            print("✅ Project structure verification passed")
    
    def run_test_suite(self, test_class, suite_name):
        """Run a specific test suite and collect results."""
        print(f"\n{'='*60}")
        print(f"RUNNING {suite_name}")
        print(f"{'='*60}")
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test_class)
        
        # Run tests with custom result collector
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=True
        )
        
        suite_start_time = time.time()
        result = runner.run(suite)
        suite_duration = time.time() - suite_start_time
        
        # Collect results
        self.results[suite_name] = {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
            "success_rate": ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
            "duration": suite_duration,
            "failure_details": result.failures,
            "error_details": result.errors
        }
        
        # Print suite summary
        print(f"\n{suite_name} Summary:")
        print(f"  Tests run: {result.testsRun}")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Success rate: {self.results[suite_name]['success_rate']:.1f}%")
        print(f"  Duration: {suite_duration:.2f} seconds")
        
        return result.wasSuccessful()
    
    def run_all_integration_tests(self):
        """Run all integration test suites."""
        self.setup_test_environment()
        
        # Define test suites to run
        test_suites = [
            (TestCompleteSystemIntegration, "Complete System Integration"),
            (TestEndToEndAssessmentWorkflow, "End-to-End Assessment Workflow"),
            (TestComponentIntegration, "Component Integration"),
            (TestPerformanceAndScalability, "Performance and Scalability")
        ]
        
        all_successful = True
        
        # Run each test suite
        for test_class, suite_name in test_suites:
            try:
                success = self.run_test_suite(test_class, suite_name)
                if not success:
                    all_successful = False
            except Exception as e:
                print(f"\n❌ Error running {suite_name}: {e}")
                all_successful = False
                self.results[suite_name] = {
                    "tests_run": 0,
                    "failures": 0,
                    "errors": 1,
                    "skipped": 0,
                    "success_rate": 0,
                    "duration": 0,
                    "failure_details": [],
                    "error_details": [str(e)]
                }
        
        # Generate final report
        self.generate_final_report(all_successful)
        
        return all_successful
    
    def generate_final_report(self, all_successful):
        """Generate comprehensive final test report."""
        total_duration = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("FINAL INTEGRATION TEST REPORT")
        print("="*80)
        
        # Calculate overall statistics
        total_tests = sum(result["tests_run"] for result in self.results.values())
        total_failures = sum(result["failures"] for result in self.results.values())
        total_errors = sum(result["errors"] for result in self.results.values())
        total_skipped = sum(result["skipped"] for result in self.results.values())
        
        overall_success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nOverall Statistics:")
        print(f"  Total test suites: {len(self.results)}")
        print(f"  Total tests run: {total_tests}")
        print(f"  Total failures: {total_failures}")
        print(f"  Total errors: {total_errors}")
        print(f"  Total skipped: {total_skipped}")
        print(f"  Overall success rate: {overall_success_rate:.1f}%")
        print(f"  Total duration: {total_duration:.2f} seconds")
        
        # Detailed results by suite
        print(f"\nDetailed Results by Test Suite:")
        print("-" * 80)
        
        for suite_name, result in self.results.items():
            status = "✅ PASSED" if result["failures"] == 0 and result["errors"] == 0 else "❌ FAILED"
            print(f"{suite_name:<40} {status}")
            print(f"  Tests: {result['tests_run']:<3} Failures: {result['failures']:<3} Errors: {result['errors']:<3} Success: {result['success_rate']:>5.1f}%")
        
        # Report failures and errors
        if total_failures > 0 or total_errors > 0:
            print(f"\nFailure and Error Details:")
            print("-" * 80)
            
            for suite_name, result in self.results.items():
                if result["failures"] or result["errors"]:
                    print(f"\n{suite_name}:")
                    
                    for test, traceback in result["failure_details"]:
                        print(f"  FAILURE: {test}")
                        print(f"    {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'See full traceback above'}")
                    
                    for test, traceback in result["error_details"]:
                        print(f"  ERROR: {test}")
                        print(f"    {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'See full traceback above'}")
        
        # Performance summary
        print(f"\nPerformance Summary:")
        print("-" * 80)
        
        for suite_name, result in self.results.items():
            avg_time_per_test = result["duration"] / result["tests_run"] if result["tests_run"] > 0 else 0
            print(f"{suite_name:<40} {result['duration']:>6.2f}s ({avg_time_per_test:>5.2f}s/test)")
        
        # Final status
        print("\n" + "="*80)
        if all_successful:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print("The ROB Assessment Tool is ready for production use.")
        else:
            print("❌ SOME INTEGRATION TESTS FAILED!")
            print("Please review the failures above and fix the issues before deployment.")
        print("="*80)
        
        # Save detailed report to file
        self.save_detailed_report(all_successful, total_duration)
    
    def save_detailed_report(self, all_successful, total_duration):
        """Save detailed test report to file."""
        report_data = {
            "test_run_info": {
                "timestamp": datetime.now().isoformat(),
                "duration": total_duration,
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "overall_success": all_successful
            },
            "results": self.results,
            "summary": {
                "total_suites": len(self.results),
                "total_tests": sum(result["tests_run"] for result in self.results.values()),
                "total_failures": sum(result["failures"] for result in self.results.values()),
                "total_errors": sum(result["errors"] for result in self.results.values()),
                "overall_success_rate": ((sum(result["tests_run"] for result in self.results.values()) - 
                                        sum(result["failures"] for result in self.results.values()) - 
                                        sum(result["errors"] for result in self.results.values())) / 
                                       sum(result["tests_run"] for result in self.results.values()) * 100) 
                                      if sum(result["tests_run"] for result in self.results.values()) > 0 else 0
            }
        }
        
        # Create reports directory
        reports_dir = Path("test_reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Save JSON report
        report_file = reports_dir / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Remove traceback details for JSON (they're too verbose)
        clean_results = {}
        for suite_name, result in self.results.items():
            clean_result = result.copy()
            clean_result["failure_details"] = [test_name for test_name, _ in result["failure_details"]]
            clean_result["error_details"] = [test_name for test_name, _ in result["error_details"]]
            clean_results[suite_name] = clean_result
        
        report_data["results"] = clean_results
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed test report saved to: {report_file}")
    
    def cleanup(self):
        """Clean up test environment."""
        # Clean up any temporary directories created during testing
        for temp_dir in self.temp_dirs:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Remove test environment variables
        os.environ.pop('ROB_TEST_MODE', None)
        os.environ.pop('ROB_INTEGRATION_TEST', None)


def main():
    """Main function to run integration tests."""
    runner = IntegrationTestRunner()
    
    try:
        success = runner.run_all_integration_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\nIntegration tests interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\nUnexpected error during integration testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        runner.cleanup()


if __name__ == "__main__":
    sys.exit(main())