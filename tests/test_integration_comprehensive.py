#!/usr/bin/env python3
"""
Enhanced integration tests for psutil-cygwin with comprehensive stress testing.

These tests require a real Cygwin environment and test real-world scenarios,
edge cases, and stress conditions.
"""

import os
import sys
import time
import unittest
import threading
import tempfile
import subprocess
import resource
import gc
import weakref
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal

# Add the package to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

import psutil_cygwin as psutil


class TestCygwinEnvironmentRobustness(unittest.TestCase):
    """Test robustness under various Cygwin environment conditions."""
    
    def test_proc_filesystem_availability(self):
        """Test comprehensive /proc filesystem availability."""
        required_files = [
            '/proc/stat', '/proc/meminfo', '/proc/mounts', '/proc/version',
            '/proc/cpuinfo', '/proc/loadavg', '/proc/uptime'
        ]
        
        for proc_file in required_files:
            with self.subTest(proc_file=proc_file):
                self.assertTrue(Path(proc_file).exists(), f"{proc_file} not found")
                
                # Test readability
                try:
                    with open(proc_file, 'r') as f:
                        content = f.read(1024)  # Read first 1KB
                    self.assertIsInstance(content, str)
                    self.assertGreater(len(content), 0)
                except PermissionError:
                    self.fail(f"{proc_file} not readable")


@unittest.skipUnless(Path("/proc").exists(), "Requires Cygwin /proc filesystem")
class TestSystemIntegrationStress(unittest.TestCase):
    """Stress testing for system-wide functions."""
    
    def test_cpu_monitoring_extended(self):
        """Extended CPU monitoring test with various intervals."""
        intervals = [0.01, 0.1, 0.5, 1.0, 2.0]
        
        for interval in intervals:
            with self.subTest(interval=interval):
                start_time = time.time()
                
                # Multiple measurements
                percentages = []
                for _ in range(5):
                    pct = psutil.cpu_percent(interval=interval)
                    percentages.append(pct)
                    
                    # Validate each measurement
                    self.assertIsInstance(pct, float)
                    self.assertGreaterEqual(pct, 0.0)
                    self.assertLessEqual(pct, 100.0)
                
                end_time = time.time()
                
                # Verify timing is reasonable
                expected_min_time = len(percentages) * interval
                actual_time = end_time - start_time
                self.assertGreaterEqual(actual_time, expected_min_time * 0.8)  # Allow 20% tolerance
    
    def test_memory_monitoring_stress(self):
        """Stress test memory monitoring functions."""
        # Rapid successive calls
        for _ in range(100):
            mem = psutil.virtual_memory()
            
            # Comprehensive validation
            self.assertIsInstance(mem, psutil.VirtualMemory)
            self.assertGreater(mem.total, 0)
            self.assertGreaterEqual(mem.used, 0)
            self.assertGreaterEqual(mem.free, 0)
            self.assertGreaterEqual(mem.available, 0)
            self.assertGreaterEqual(mem.percent, 0.0)
            self.assertLessEqual(mem.percent, 100.0)
            
            # Logical consistency checks
            self.assertLessEqual(mem.used, mem.total)
            self.assertLessEqual(mem.free, mem.total)
            self.assertLessEqual(mem.available, mem.total)
            
            # Swap memory
            swap = psutil.swap_memory()
            self.assertIsInstance(swap, psutil.SwapMemory)
            self.assertGreaterEqual(swap.total, 0)
            self.assertGreaterEqual(swap.used, 0)
            self.assertGreaterEqual(swap.free, 0)
            self.assertGreaterEqual(swap.percent, 0.0)
            self.assertLessEqual(swap.percent, 100.0)
            
            if swap.total > 0:
                self.assertLessEqual(swap.used, swap.total)
                self.assertLessEqual(swap.free, swap.total)


@unittest.skipUnless(Path("/proc").exists(), "Requires Cygwin /proc filesystem")
class TestProcessIntegrationStress(unittest.TestCase):
    """Stress testing for process-related functions."""
    
    def test_process_enumeration_stress(self):
        """Stress test process enumeration under various conditions."""
        # Multiple rapid enumerations
        for iteration in range(10):
            pids = psutil.pids()
            self.assertIsInstance(pids, list)
            self.assertGreater(len(pids), 0)
            
            # Verify PIDs are integers and reasonable
            for pid in pids:
                self.assertIsInstance(pid, int)
                self.assertGreater(pid, 0)
                self.assertLess(pid, 2**31)  # Reasonable upper bound
            
            # PIDs should be sorted
            self.assertEqual(pids, sorted(pids))
            
            # Test existence of some PIDs
            for pid in pids[:10]:  # Test first 10
                exists = psutil.pid_exists(pid)
                self.assertIsInstance(exists, bool)
    
    def test_process_lifecycle_tracking(self):
        """Test tracking processes through their lifecycle."""
        if not os.path.exists('/usr/bin/sleep'):
            self.skipTest("sleep command not available")
        
        # Start a test process
        test_proc = subprocess.Popen(['/usr/bin/sleep', '5'])
        test_pid = test_proc.pid
        
        try:
            # Process should exist and be accessible
            self.assertTrue(psutil.pid_exists(test_pid))
            
            proc = psutil.Process(test_pid)
            self.assertEqual(proc.pid, test_pid)
            self.assertTrue(proc.is_running())
            
            # Get initial information
            name = proc.name()
            self.assertIn('sleep', name.lower())
            
            status = proc.status()
            self.assertIn(status, ['running', 'sleeping'])
            
            cmdline = proc.cmdline()
            self.assertIn('sleep', ' '.join(cmdline).lower())
            self.assertIn('5', ' '.join(cmdline))
            
            # Memory information
            mem_info = proc.memory_info()
            self.assertGreater(mem_info.rss, 0)
            
            # CPU times
            cpu_times = proc.cpu_times()
            self.assertGreaterEqual(cpu_times.user, 0.0)
            self.assertGreaterEqual(cpu_times.system, 0.0)
            
            # Wait a bit then check if still running
            time.sleep(1)
            self.assertTrue(proc.is_running())
            
        finally:
            # Clean up
            try:
                test_proc.terminate()
                test_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                test_proc.kill()
                test_proc.wait()
        
        # Process should no longer exist
        time.sleep(0.1)  # Brief delay for cleanup
        self.assertFalse(psutil.pid_exists(test_pid))
        self.assertFalse(proc.is_running())


@unittest.skipUnless(Path("/proc").exists(), "Requires Cygwin /proc filesystem")
class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarking and regression testing."""
    
    def test_function_call_latency(self):
        """Measure and validate function call latencies."""
        test_functions = [
            ('cpu_times', lambda: psutil.cpu_times()),
            ('virtual_memory', lambda: psutil.virtual_memory()),
            ('cpu_count', lambda: psutil.cpu_count()),
            ('boot_time', lambda: psutil.boot_time()),
            ('pids', lambda: psutil.pids()),
        ]
        
        performance_results = {}
        
        for func_name, func in test_functions:
            times = []
            
            # Warm up
            for _ in range(5):
                func()
            
            # Measure
            for _ in range(20):
                start = time.perf_counter()
                result = func()
                end = time.perf_counter()
                times.append(end - start)
                
                # Validate result is reasonable
                self.assertIsNotNone(result)
            
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)
            
            performance_results[func_name] = {
                'avg': avg_time,
                'max': max_time,
                'min': min_time
            }
            
            # Performance thresholds (generous to avoid flaky tests)
            if func_name in ['cpu_times', 'virtual_memory', 'cpu_count', 'boot_time']:
                self.assertLess(avg_time, 0.1, f"{func_name} too slow: {avg_time:.4f}s average")
                self.assertLess(max_time, 0.5, f"{func_name} too slow: {max_time:.4f}s maximum")
            elif func_name == 'pids':
                self.assertLess(avg_time, 0.2, f"{func_name} too slow: {avg_time:.4f}s average")
        
        # Print performance summary
        print("\nPerformance Summary:")
        for func_name, results in performance_results.items():
            print(f"  {func_name:15s}: avg={results['avg']:.4f}s, max={results['max']:.4f}s, min={results['min']:.4f}s")


@unittest.skipUnless(Path("/proc").exists(), "Requires Cygwin /proc filesystem")
class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios and edge cases."""
    
    def test_system_monitoring_scenario(self):
        """Test a comprehensive system monitoring scenario."""
        monitoring_data = []
        
        # Collect system data over time
        for i in range(10):
            timestamp = time.time()
            
            try:
                # System-wide metrics
                cpu_pct = psutil.cpu_percent(interval=0.1)
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                
                # Disk usage for root
                disk = psutil.disk_usage('/')
                
                # Process count
                process_count = len(psutil.pids())
                
                # Top memory consumers
                top_processes = []
                process_iter_count = 0
                for proc in psutil.process_iter():
                    try:
                        mem_info = proc.memory_info()
                        top_processes.append({
                            'pid': proc.pid,
                            'name': proc.name(),
                            'memory': mem_info.rss
                        })
                        process_iter_count += 1
                        if process_iter_count >= 20:  # Limit for performance
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Sort by memory usage
                top_processes.sort(key=lambda x: x['memory'], reverse=True)
                
                monitoring_data.append({
                    'timestamp': timestamp,
                    'cpu_percent': cpu_pct,
                    'memory_percent': mem.percent,
                    'memory_used': mem.used,
                    'memory_total': mem.total,
                    'swap_percent': swap.percent,
                    'disk_percent': (disk.used / disk.total * 100) if disk.total > 0 else 0,
                    'process_count': process_count,
                    'top_process_memory': top_processes[0]['memory'] if top_processes else 0,
                    'top_process_name': top_processes[0]['name'] if top_processes else 'unknown'
                })
                
            except Exception as e:
                self.fail(f"Monitoring iteration {i} failed: {e}")
        
        # Validate collected data
        self.assertEqual(len(monitoring_data), 10)
        
        for data in monitoring_data:
            # All metrics should be reasonable
            self.assertGreaterEqual(data['cpu_percent'], 0.0)
            self.assertLessEqual(data['cpu_percent'], 100.0)
            self.assertGreaterEqual(data['memory_percent'], 0.0)
            self.assertLessEqual(data['memory_percent'], 100.0)
            self.assertGreater(data['memory_total'], 0)
            self.assertGreaterEqual(data['memory_used'], 0)
            self.assertGreater(data['process_count'], 0)


if __name__ == '__main__':
    # Configure test runner for comprehensive output
    unittest.main(verbosity=2, buffer=True, failfast=False)
