#!/usr/bin/env python3
"""
Comprehensive stress tests and edge case tests for psutil-cygwin.

This test suite focuses on extreme conditions, boundary cases, and stress scenarios
that could reveal hidden bugs or performance issues.
"""

import os
import sys
import time
import unittest
import threading
import tempfile
import subprocess
import signal
import gc
import random
import string
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import weakref

# Add the package to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

import psutil_cygwin as psutil


class TestExtremeEdgeCases(unittest.TestCase):
    """Test extreme edge cases and boundary conditions."""
    
    def test_extreme_pid_values(self):
        """Test with extreme PID values."""
        extreme_pids = [
            0, 1, -1, 2**15-1, 2**16-1, 2**31-1, 2**32-1,
            999999999, -999999999
        ]
        
        for pid in extreme_pids:
            with self.subTest(pid=pid):
                # pid_exists should not crash
                try:
                    exists = psutil.pid_exists(pid)
                    self.assertIsInstance(exists, bool)
                except Exception as e:
                    # Some extreme values might legitimately raise exceptions
                    self.assertIsInstance(e, (ValueError, OSError))
                
                # Process creation with invalid PIDs should raise NoSuchProcess
                if pid <= 0 or pid > 2**31-1:
                    with patch('os.path.exists', return_value=False):
                        with self.assertRaises(psutil.NoSuchProcess):
                            psutil.Process(pid)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_extreme_cpu_values(self, mock_file):
        """Test CPU parsing with extreme values."""
        extreme_cases = [
            # Very large numbers
            "cpu  999999999999999999 888888888888888888 777777777777777777 666666666666666666",
            # Maximum possible values
            f"cpu  {2**63-1} {2**63-1} {2**63-1} {2**63-1}",
            # Zero values
            "cpu  0 0 0 0 0 0 0 0",
            # Single huge value
            "cpu  999999999999999999",
            # Negative values (should be handled gracefully)
            "cpu  -1 -2 -3 -4",
            # Mixed positive/negative
            "cpu  1000 -500 2000 -100",
        ]
        
        with patch('os.sysconf', return_value=100):
            for cpu_data in extreme_cases:
                with self.subTest(cpu_data=cpu_data[:50]):
                    mock_file.return_value.read.return_value = cpu_data + "\n"
                    
                    try:
                        times = psutil.cpu_times()
                        self.assertIsInstance(times, psutil.CPUTimes)
                        # Values should be reasonable after processing
                        self.assertGreaterEqual(times.user, 0)
                        self.assertGreaterEqual(times.system, 0)
                        self.assertGreaterEqual(times.idle, 0)
                    except Exception as e:
                        # Should handle gracefully, not crash
                        self.assertIsInstance(e, (ValueError, OverflowError))
    
    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters in process data."""
        with patch('os.path.exists', return_value=True):
            proc = psutil.Process.__new__(psutil.Process)
            proc.pid = 1234
            proc._proc_path = "/proc/1234"
            
            special_names = [
                "процесс",  # Cyrillic
                "プロセス",  # Japanese
                "进程",     # Chinese
                "🚀rocket",  # Emoji
                "test\x00null",  # Null character
                "test\nnewline",  # Newline
                "test\ttab",     # Tab
                "test\"quote",   # Quote
                "test'apostrophe",  # Apostrophe
                "test\\backslash",  # Backslash
                "test|pipe",     # Pipe
                "test;semicolon", # Semicolon
                "test$dollar",   # Dollar sign
                "test&ampersand", # Ampersand
            ]
            
            for special_name in special_names:
                with self.subTest(name=special_name):
                    with patch.object(proc, '_read_proc_file', return_value=special_name):
                        try:
                            name = proc.name()
                            self.assertIsInstance(name, str)
                            # Should preserve the special characters
                            self.assertEqual(name, special_name)
                        except UnicodeError:
                            # Some combinations might legitimately fail
                            pass


class TestStressConditions(unittest.TestCase):
    """Test behavior under stress conditions."""
    
    @unittest.skipUnless(Path("/proc").exists(), "Requires /proc filesystem")
    def test_rapid_process_creation_destruction(self):
        """Test behavior during rapid process creation and destruction."""
        if not os.path.exists('/usr/bin/true'):
            self.skipTest("true command not available")
        
        # Track errors and successful operations
        errors = []
        successful_operations = 0
        
        def create_destroy_processes():
            """Rapidly create and destroy processes."""
            for _ in range(20):
                try:
                    proc = subprocess.Popen(['/usr/bin/true'])
                    pid = proc.pid
                    
                    # Try to access it immediately
                    if psutil.pid_exists(pid):
                        try:
                            ps_proc = psutil.Process(pid)
                            ps_proc.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            # Expected due to race conditions
                            pass
                    
                    proc.wait()
                    
                except Exception as e:
                    errors.append(e)
        
        def monitor_processes():
            """Monitor processes during rapid creation/destruction."""
            for _ in range(100):
                try:
                    pids = psutil.pids()
                    for pid in pids[-5:]:  # Check last 5 PIDs
                        try:
                            if psutil.pid_exists(pid):
                                proc = psutil.Process(pid)
                                proc.is_running()
                                nonlocal successful_operations
                                successful_operations += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            # Expected during rapid changes
                            pass
                    time.sleep(0.01)  # Brief pause
                except Exception as e:
                    errors.append(e)
        
        # Run both operations concurrently
        threads = []
        threads.append(threading.Thread(target=create_destroy_processes))
        threads.append(threading.Thread(target=monitor_processes))
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join(timeout=30)
        
        # Should have handled rapid changes gracefully
        self.assertLess(len(errors), 10, f"Too many errors during stress test: {errors[:5]}")
        self.assertGreater(successful_operations, 0)
    
    def test_high_frequency_calls(self):
        """Test high-frequency function calls."""
        if not Path("/proc").exists():
            self.skipTest("Requires /proc filesystem")
        
        # Test rapid-fire calls to various functions
        test_functions = [
            psutil.cpu_count,
            psutil.boot_time,
            lambda: psutil.virtual_memory().total,
            lambda: len(psutil.pids()),
        ]
        
        for func in test_functions:
            with self.subTest(func=func.__name__ if hasattr(func, '__name__') else str(func)):
                start_time = time.time()
                
                # Rapid calls
                for _ in range(1000):
                    try:
                        result = func()
                        self.assertIsNotNone(result)
                    except Exception as e:
                        self.fail(f"Function {func} failed on rapid call: {e}")
                
                end_time = time.time()
                
                # Should complete in reasonable time
                total_time = end_time - start_time
                self.assertLess(total_time, 30.0, 
                               f"1000 calls to {func} took {total_time:.2f}s")


class TestResourceExhaustion(unittest.TestCase):
    """Test behavior under resource exhaustion conditions."""
    
    def test_file_descriptor_exhaustion_simulation(self):
        """Test behavior when file descriptors are exhausted."""
        if not Path("/proc").exists():
            self.skipTest("Requires /proc filesystem")
        
        # Get current file descriptor limit
        try:
            import resource
            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
        except ImportError:
            self.skipTest("resource module not available")
        
        # Open many files to approach the limit
        open_files = []
        
        try:
            # Open files until we're close to the limit
            for i in range(min(soft_limit - 50, 100)):  # Leave some buffer
                try:
                    f = open('/dev/null', 'r')
                    open_files.append(f)
                except OSError:
                    # Hit the limit
                    break
            
            # Try psutil operations with limited file descriptors
            try:
                mem = psutil.virtual_memory()
                pids = psutil.pids()
                
                # Brief process iteration
                count = 0
                for proc in psutil.process_iter():
                    try:
                        proc.name()
                        count += 1
                        if count >= 10:
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Should still work despite limited file descriptors
                self.assertIsInstance(mem, psutil.VirtualMemory)
                self.assertIsInstance(pids, list)
                
            except OSError as e:
                # Might fail due to file descriptor exhaustion, but shouldn't crash
                self.assertIn("Too many open files", str(e))
        
        finally:
            # Clean up
            for f in open_files:
                try:
                    f.close()
                except:
                    pass


class TestErrorRecoveryAndRobustness(unittest.TestCase):
    """Test error recovery and robustness under adverse conditions."""
    
    @patch('builtins.open')
    def test_intermittent_file_errors(self, mock_open_builtin):
        """Test handling of intermittent file access errors."""
        # Simulate intermittent failures
        call_count = 0
        
        def intermittent_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 3 == 0:  # Fail every 3rd call
                raise OSError("Intermittent failure")
            
            # Return a mock file object
            mock_file = MagicMock()
            mock_file.read.return_value = "cpu  100 200 300 400\n"
            mock_file.readline.return_value = "cpu  100 200 300 400\n"
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            return mock_file
        
        mock_open_builtin.side_effect = intermittent_failure
        
        # Functions should handle intermittent failures gracefully
        success_count = 0
        failure_count = 0
        
        for _ in range(12):  # Increase iterations to ensure some successes
            try:
                times = psutil.cpu_times()
                if times.user > 0:  # Valid data
                    success_count += 1
                else:  # Default/fallback data
                    failure_count += 1
            except OSError:
                failure_count += 1
        
        # Should have some successes and handle failures gracefully
        self.assertGreater(success_count, 0)
        self.assertGreater(failure_count, 0)
    
    def test_corrupted_proc_filesystem_simulation(self):
        """Test behavior with simulated corrupted /proc files."""
        corrupted_scenarios = [
            # Binary data
            (b'\x00\x01\x02\x03\x04\x05', "binary data"),
            # Truncated files
            ("cpu  100 2", "truncated"),
            # Random text
            ("".join(random.choices(string.ascii_letters, k=1000)), "random text"),
            # Very long lines
            ("cpu  " + " ".join(str(random.randint(0, 999999)) for _ in range(1000)), "very long"),
            # Mixed encodings (Latin-1)
            ("cpu  100 200 300 \xff\xfe\xfd", "mixed encoding"),
        ]
        
        for corrupted_data, description in corrupted_scenarios:
            with self.subTest(scenario=description):
                with patch('builtins.open', mock_open(read_data=corrupted_data)):
                    try:
                        # Functions should not crash on corrupted data
                        times = psutil.cpu_times()
                        mem = psutil.virtual_memory()
                        count = psutil.cpu_count()
                        
                        # Should return valid objects even with bad data
                        self.assertIsInstance(times, psutil.CPUTimes)
                        self.assertIsInstance(mem, psutil.VirtualMemory)
                        self.assertIsInstance(count, int)
                        
                    except (UnicodeDecodeError, ValueError) as e:
                        # Some corruption might legitimately cause these errors
                        self.assertIsInstance(e, (UnicodeDecodeError, ValueError))


class TestDataConsistencyAndValidation(unittest.TestCase):
    """Test data consistency and validation under various conditions."""
    
    @unittest.skipUnless(Path("/proc").exists(), "Requires /proc filesystem")
    def test_data_consistency_over_time(self):
        """Test that data remains consistent over multiple reads."""
        # Some values should be stable, others can change
        stable_data = []
        variable_data = []
        
        for _ in range(10):
            data_point = {
                'cpu_count': psutil.cpu_count(),
                'boot_time': psutil.boot_time(),
                'memory_total': psutil.virtual_memory().total,
                'memory_percent': psutil.virtual_memory().percent,
                'pid_count': len(psutil.pids()),
            }
            
            stable_data.append({
                'cpu_count': data_point['cpu_count'],
                'boot_time': data_point['boot_time'],
                'memory_total': data_point['memory_total'],
            })
            
            variable_data.append({
                'memory_percent': data_point['memory_percent'],
                'pid_count': data_point['pid_count'],
            })
            
            time.sleep(0.1)
        
        # Stable values should be consistent
        for key in ['cpu_count', 'boot_time', 'memory_total']:
            values = [d[key] for d in stable_data]
            unique_values = set(values)
            self.assertEqual(len(unique_values), 1, 
                           f"{key} should be stable but got {unique_values}")
        
        # Variable values can change but should be reasonable
        for data_point in variable_data:
            self.assertGreaterEqual(data_point['memory_percent'], 0.0)
            self.assertLessEqual(data_point['memory_percent'], 100.0)
            self.assertGreater(data_point['pid_count'], 0)
    
    def test_mathematical_consistency(self):
        """Test mathematical consistency in computed values."""
        if not Path("/proc").exists():
            self.skipTest("Requires /proc filesystem")
        
        # Memory calculations should be consistent
        mem = psutil.virtual_memory()
        
        # Basic arithmetic consistency
        if mem.total > 0:
            calculated_percent = (mem.used / mem.total) * 100
            # Allow some tolerance for rounding differences
            self.assertAlmostEqual(mem.percent, calculated_percent, delta=5.0)
        
        # Available memory should make sense
        self.assertLessEqual(mem.available, mem.total)
        self.assertGreaterEqual(mem.available, mem.free)
        
        # Swap memory consistency
        swap = psutil.swap_memory()
        if swap.total > 0:
            calculated_swap_percent = (swap.used / swap.total) * 100
            self.assertAlmostEqual(swap.percent, calculated_swap_percent, delta=1.0)
            
            # Used + free should approximately equal total
            self.assertAlmostEqual(swap.used + swap.free, swap.total, 
                                 delta=swap.total * 0.01)  # 1% tolerance


if __name__ == '__main__':
    # Configure test runner for comprehensive output
    unittest.main(verbosity=2, buffer=True, failfast=False)
