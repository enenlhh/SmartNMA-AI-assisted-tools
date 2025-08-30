#!/usr/bin/env python3
"""
Test runner for ROB Assessment Tool testing framework.

Runs all unit tests and integration tests with comprehensive reporting,
performance validation, and resource usage monitoring.
"""

import unittest
import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import importlib.util

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestResult:
    """Container for test execution results."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
        self.failures = []
        self.errors = []
        self.execution_time = 0.0
    
    def finalize(self):
        """Finalize test results."""
        self.end_time = datetime.now()
        self.execution_time = (self.end_time - self.start_time).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary dictionary."""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "error_tests": self.error_tests,
            "skipped_tests": self.skipped_tests,
            "success_rate": (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
            "failures": [str(failure) for failure in self.failures],
            "errors": [str(error) for error in self.errors]
        }


class CustomTestResult(unittest.TestResult):
    """Custom test result class for detailed reporting."""
    
    def __init__(self, test_result: TestResult):
        super().__init__()
        self.test_result = test_result
        self.current_test = None
    
    def startTest(self, test):
        """Called when a test starts."""
        super().startTest(test)
        self.current_test = test
        print(f"  Running: {test._testMethodName}")
    
    def addSuccess(self, test):
        """Called when a test passes."""
        super().addSuccess(test)
        self.test_result.passed_tests += 1
        print(f"    ✅ PASSED")
    
    def addError(self, test, err):
        """Called when a test has an error."""
        super().addError(test, err)
        self.test_result.error_tests += 1
        self.test_result.errors.append(f"{test}: {err[1]}")
        print(f"    ❌ ERROR: {err[1]}")
    
    def addFailure(self, test, err):
        """Called when a test fails."""
        super().addFailure(test, err)
        self.test_result.failed_tests += 1
        self.test_result.failures.append(f"{test}: {err[1]}")
        print(f"    ❌ FAILED: {err[1]}")
    
    def addSkip(self, test, reason):
        """Called when a test is skipped."""
        super().addSkip(test, reason)
        self.test_result.skipped_tests += 1
        print(f"    ⏭️  SKIPPED: {reason}")


class TestRunner:
    """Main test runner class."""
    
    def __init__(self, test_dir: str = None):
        """Initialize test runner."""
        self.test_dir = Path(test_dir) if test_dir else Path(__file__).parent
        self.test_modules = []
        self.results = TestResult()
    
    def discover_tests(self, pattern: str = "test_*.py") -> List[str]:
        """Discover test modules matching the pattern."""
        test_files = list(self.test_dir.glob(pattern))
        test_modules = []
        
        for test_file in test_files:
            if test_file.name == "run_tests.py":  # Skip this file
                continue
            
            module_name = test_file.stem
            test_modules.append(module_name)
        
        return sorted(test_modules)
    
    def load_test_module(self, module_name: str) -> unittest.TestSuite:
        """Load tests from a specific module."""
        try:
            module_path = self.test_dir / f"{module_name}.py"
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Load tests from module
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            return suite
        
        except Exception as e:
            print(f"❌ Failed to load test module {module_name}: {e}")
            return unittest.TestSuite()
    
    def run_test_suite(self, suite: unittest.TestSuite, module_name: str) -> None:
        """Run a test suite and collect results."""
        print(f"\n📋 Running tests from {module_name}")
        print("-" * 60)
        
        # Count tests in suite
        test_count = suite.countTestCases()
        self.results.total_tests += test_count
        
        if test_count == 0:
            print("  No tests found in module")
            return
        
        # Run tests with custom result handler
        custom_result = CustomTestResult(self.results)
        suite.run(custom_result)
        
        # Print module summary
        module_passed = custom_result.testsRun - len(custom_result.failures) - len(custom_result.errors)
        print(f"\n  Module Summary: {module_passed}/{custom_result.testsRun} tests passed")
    
    def run_all_tests(self, test_pattern: str = "test_*.py", 
                     include_integration: bool = True) -> TestResult:
        """Run all discovered tests."""
        print("🚀 Starting ROB Assessment Tool Test Suite")
        print("=" * 80)
        
        # Discover test modules
        test_modules = self.discover_tests(test_pattern)
        
        if not include_integration:
            # Filter out integration tests
            test_modules = [m for m in test_modules if "integration" not in m]
        
        print(f"📁 Discovered {len(test_modules)} test modules:")
        for module in test_modules:
            print(f"  • {module}")
        
        # Run each test module
        for module_name in test_modules:
            suite = self.load_test_module(module_name)
            self.run_test_suite(suite, module_name)
        
        # Finalize results
        self.results.finalize()
        
        return self.results
    
    def print_summary(self) -> None:
        """Print comprehensive test summary."""
        print("\n" + "=" * 80)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 80)
        
        summary = self.results.get_summary()
        
        print(f"⏱️  Execution Time: {summary['execution_time']:.2f} seconds")
        print(f"📈 Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"💥 Errors: {summary['error_tests']}")
        print(f"⏭️  Skipped: {summary['skipped_tests']}")
        print(f"📊 Success Rate: {summary['success_rate']:.1f}%")
        
        # Print failures and errors if any
        if summary['failures']:
            print(f"\n❌ FAILURES ({len(summary['failures'])}):")
            for i, failure in enumerate(summary['failures'], 1):
                print(f"  {i}. {failure}")
        
        if summary['errors']:
            print(f"\n💥 ERRORS ({len(summary['errors'])}):")
            for i, error in enumerate(summary['errors'], 1):
                print(f"  {i}. {error}")
        
        # Overall result
        if summary['failed_tests'] == 0 and summary['error_tests'] == 0:
            print(f"\n🎉 ALL TESTS PASSED! ({summary['passed_tests']}/{summary['total_tests']})")
        else:
            print(f"\n💥 SOME TESTS FAILED! ({summary['passed_tests']}/{summary['total_tests']} passed)")
    
    def save_results(self, output_file: str) -> None:
        """Save test results to JSON file."""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(self.results.get_summary(), f, indent=2)
            
            print(f"📄 Test results saved to: {output_path}")
        
        except Exception as e:
            print(f"⚠️  Failed to save test results: {e}")


def run_performance_validation():
    """Run performance validation tests."""
    print("\n🔍 Running Performance Validation Tests")
    print("-" * 60)
    
    # Test import performance
    start_time = time.time()
    
    try:
        from core.parallel_controller import ParallelROBManager
        from core.progress_monitor import ProgressMonitor
        from src.cost_analyzer import CostAnalyzer
        from i18n.i18n_manager import LanguageManager
        
        import_time = time.time() - start_time
        print(f"✅ Module imports: {import_time:.3f}s")
        
        if import_time > 2.0:
            print("⚠️  Warning: Module import time is high")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test basic functionality performance
    try:
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test configuration loading performance
            start_time = time.time()
            
            config_path = Path(temp_dir) / "test_config.json"
            test_config = {
                "paths": {"input_folder": temp_dir, "output_folder": temp_dir},
                "processing": {"llm_output_mode": "json"},
                "llm_models": [{"model_name": "gpt-4", "api_key": "test"}]
            }
            
            with open(config_path, 'w') as f:
                json.dump(test_config, f)
            
            manager = ParallelROBManager(str(config_path))
            config_time = time.time() - start_time
            
            print(f"✅ Configuration loading: {config_time:.3f}s")
            
            if config_time > 1.0:
                print("⚠️  Warning: Configuration loading time is high")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance validation error: {e}")
        return False


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="ROB Assessment Tool Test Runner")
    parser.add_argument(
        "--pattern", 
        default="test_*.py",
        help="Test file pattern (default: test_*.py)"
    )
    parser.add_argument(
        "--no-integration",
        action="store_true",
        help="Skip integration tests"
    )
    parser.add_argument(
        "--output",
        help="Output file for test results (JSON format)"
    )
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance validation tests"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Set up test runner
    runner = TestRunner()
    
    # Run performance validation if requested
    if args.performance:
        perf_success = run_performance_validation()
        if not perf_success:
            print("⚠️  Performance validation failed, continuing with tests...")
    
    # Run tests
    results = runner.run_all_tests(
        test_pattern=args.pattern,
        include_integration=not args.no_integration
    )
    
    # Print summary
    runner.print_summary()
    
    # Save results if requested
    if args.output:
        runner.save_results(args.output)
    
    # Exit with appropriate code
    if results.failed_tests > 0 or results.error_tests > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()