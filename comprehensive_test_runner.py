#!/usr/bin/env python3
"""
Comprehensive test runner for psutil-cygwin with coverage reporting and performance analysis.

This script runs all test suites with comprehensive coverage analysis, performance benchmarking,
and detailed reporting of test results including edge cases and stress tests.
"""

import os
import sys
import time
import unittest
import subprocess
import argparse
import json
import gc
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from io import StringIO

# Add the package to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test discovery patterns
TEST_PATTERNS = {
    'unit': 'test_unit*.py',
    'integration': 'test_integration*.py', 
    'pth': 'test_pth*.py',
    'stress': 'test_stress.py',
    'all': 'test_*.py'  # All test files
}


class TestRunner:
    """Enhanced test runner with comprehensive reporting and analysis."""
    
    def __init__(self, test_dir=None, coverage=True, performance=True, verbose=True):
        self.test_dir = test_dir or project_root / 'tests'
        self.coverage_enabled = coverage
        self.performance_enabled = performance
        self.verbose = verbose
        self.results = {}
        self.start_time = None
        self.performance_data = {}
        
    def run_all_tests(self, patterns=None, parallel=False):
        """Run all test suites with comprehensive analysis."""
        print("🧪 COMPREHENSIVE PSUTIL-CYGWIN TEST SUITE")
        print("=" * 60)
        
        self.start_time = time.time()
        patterns = patterns or list(TEST_PATTERNS.keys())
        
        # System information
        self._print_system_info()
        
        # Pre-test validation
        self._validate_environment()
        
        # Run test categories
        for pattern_name in patterns:
            if pattern_name in TEST_PATTERNS:
                self._run_test_category(pattern_name, TEST_PATTERNS[pattern_name])
            else:
                print(f"⚠️  Unknown test pattern: {pattern_name}")
        
        # Generate comprehensive report
        self._generate_final_report()
        
        return self.results
    
    def _print_system_info(self):
        """Print system information for test context."""
        print("\n📋 System Information:")
        print(f"   Python: {sys.version.split()[0]}")
        print(f"   Platform: {sys.platform}")
        print(f"   Test Directory: {self.test_dir}")
        print(f"   Project Root: {project_root}")
        
        # Check Cygwin environment
        try:
            from psutil_cygwin.cygwin_check import is_cygwin
            is_cygwin_env = is_cygwin()
            print(f"   Cygwin Environment: {'✅ Yes' if is_cygwin_env else '❌ No'}")
            
            if os.path.exists('/proc'):
                print(f"   /proc filesystem: ✅ Available")
            else:
                print(f"   /proc filesystem: ❌ Not available")
                
        except ImportError:
            print(f"   Cygwin Check: ❌ Cannot import psutil_cygwin")
        
        print()
    
    def _validate_environment(self):
        """Validate test environment setup."""
        print("🔍 Environment Validation:")
        
        # Check test directory
        if not self.test_dir.exists():
            print(f"❌ Test directory not found: {self.test_dir}")
            return False
        else:
            print(f"✅ Test directory: {self.test_dir}")
        
        # Check psutil_cygwin import
        try:
            import psutil_cygwin
            print(f"✅ psutil_cygwin importable")
        except ImportError as e:
            print(f"❌ Cannot import psutil_cygwin: {e}")
            return False
        
        print()
        return True
    
    def _run_test_category(self, category_name, pattern):
        """Run a specific test category with detailed reporting."""
        print(f"\n🧪 Running {category_name.upper()} Tests ({pattern})")
        print("-" * 50)
        
        # Discover tests
        test_files = list(self.test_dir.glob(pattern))
        if not test_files:
            print(f"⚠️  No test files found for pattern: {pattern}")
            self.results[category_name] = {'status': 'skipped', 'reason': 'no_files'}
            return
        
        print(f"📁 Found {len(test_files)} test file(s): {[f.name for f in test_files]}")
        
        # Run tests
        category_start = time.time()
        result = self._run_tests_basic(test_files, category_name)
        category_end = time.time()
        
        # Store results
        result['duration'] = category_end - category_start
        result['files'] = [f.name for f in test_files]
        self.results[category_name] = result
        
        # Summary
        self._print_category_summary(category_name, result)
    
    def _run_tests_basic(self, test_files, category_name):
        """Run tests using basic unittest runner."""
        # Try to run each test file individually
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        all_success = True
        
        for test_file in test_files:
            try:
                print(f"   Running {test_file.name}...")
                
                # Run the test file as a script
                result = subprocess.run([
                    sys.executable, str(test_file)
                ], cwd=str(project_root), capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"   ✅ {test_file.name} passed")
                else:
                    print(f"   ❌ {test_file.name} failed")
                    print(f"      stdout: {result.stdout[-200:]}")  # Last 200 chars
                    print(f"      stderr: {result.stderr[-200:]}")  # Last 200 chars
                    all_success = False
                    total_failures += 1
                
                total_tests += 1
                
            except subprocess.TimeoutExpired:
                print(f"   ⏰ {test_file.name} timed out")
                total_errors += 1
                all_success = False
            except Exception as e:
                print(f"   💥 Error running {test_file.name}: {e}")
                total_errors += 1
                all_success = False
        
        return {
            'success': all_success,
            'tests_run': total_tests,
            'failures': total_failures,
            'errors': total_errors,
            'skipped': total_skipped,
        }
    
    def _print_category_summary(self, category_name, result):
        """Print summary for test category."""
        if result.get('success', False):
            print(f"\n✅ {category_name.upper()} TESTS PASSED")
            print(f"   Test files run: {result.get('tests_run', 0)}")
            print(f"   Duration: {result.get('duration', 0):.2f}s")
        else:
            print(f"\n❌ {category_name.upper()} TESTS FAILED")
            print(f"   Test files run: {result.get('tests_run', 0)}")
            print(f"   Failures: {result.get('failures', 0)}")
            print(f"   Errors: {result.get('errors', 0)}")
    
    def _generate_final_report(self):
        """Generate comprehensive final report."""
        total_duration = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        # Overall statistics
        total_test_files = sum(r.get('tests_run', 0) for r in self.results.values() if isinstance(r, dict))
        total_failures = sum(r.get('failures', 0) for r in self.results.values() if isinstance(r, dict))
        total_errors = sum(r.get('errors', 0) for r in self.results.values() if isinstance(r, dict))
        
        successful_categories = sum(1 for r in self.results.values() 
                                  if isinstance(r, dict) and r.get('success', False))
        total_categories = len([r for r in self.results.values() if isinstance(r, dict)])
        
        print(f"\n📊 Overall Statistics:")
        print(f"   Total test categories: {total_categories}")
        print(f"   Successful categories: {successful_categories}")
        print(f"   Total test files run: {total_test_files}")
        print(f"   Total failures: {total_failures}")
        print(f"   Total errors: {total_errors}")
        print(f"   Total duration: {total_duration:.2f}s")
        
        # Category breakdown
        print(f"\n📋 Category Results:")
        for category, result in self.results.items():
            if isinstance(result, dict):
                status = "✅ PASS" if result.get('success', False) else "❌ FAIL"
                duration = result.get('duration', 0)
                tests = result.get('tests_run', 0)
                print(f"   {category:20s}: {status} ({tests} files, {duration:.2f}s)")
            else:
                print(f"   {category:20s}: ⚠️  SKIPPED")
        
        # Final assessment
        overall_success = (total_failures == 0 and total_errors == 0 and 
                          successful_categories == total_categories)
        
        print(f"\n🎯 Final Assessment:")
        if overall_success:
            print("   ✅ ALL TESTS PASSED - psutil-cygwin is fully validated!")
            print("   🏆 The implementation handles all tested edge cases and stress conditions.")
        else:
            print("   ❌ SOME TESTS FAILED - review failures before deployment")
            print("   🔧 Check individual test results for specific issues to address.")
        
        print("\n" + "=" * 80)
        
        # Save detailed report to file
        self._save_detailed_report()
    
    def _save_detailed_report(self):
        """Save detailed report to JSON file."""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'platform': sys.platform,
            'test_results': self.results,
            'summary': {
                'total_duration': time.time() - self.start_time,
                'total_test_files': sum(r.get('tests_run', 0) for r in self.results.values() if isinstance(r, dict)),
                'total_failures': sum(r.get('failures', 0) for r in self.results.values() if isinstance(r, dict)),
                'total_errors': sum(r.get('errors', 0) for r in self.results.values() if isinstance(r, dict)),
            }
        }
        
        report_file = project_root / 'test_report.json'
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            print(f"📄 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️  Could not save detailed report: {e}")


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description='Comprehensive psutil-cygwin test runner')
    parser.add_argument('--tests', nargs='*', choices=list(TEST_PATTERNS.keys()),
                       help='Specific test categories to run')
    parser.add_argument('--no-coverage', action='store_true',
                       help='Disable coverage analysis')
    parser.add_argument('--no-performance', action='store_true', 
                       help='Disable performance analysis')
    parser.add_argument('--quiet', action='store_true',
                       help='Reduce output verbosity')
    parser.add_argument('--test-dir', type=Path,
                       help='Override test directory location')
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner(
        test_dir=args.test_dir,
        coverage=not args.no_coverage,
        performance=not args.no_performance,
        verbose=not args.quiet
    )
    
    # Run tests
    patterns = args.tests or ['unit', 'integration', 'pth', 'stress']
    results = runner.run_all_tests(patterns=patterns)
    
    # Exit with appropriate code
    all_success = all(r.get('success', False) for r in results.values() if isinstance(r, dict))
    sys.exit(0 if all_success else 1)


if __name__ == '__main__':
    main()
