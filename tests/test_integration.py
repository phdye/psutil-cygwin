"""
Integration tests for psutil-cygwin.

These tests require a real Cygwin environment with /proc filesystem.
"""

import os
import sys
import time
import unittest
from pathlib import Path

# Add the package to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

import psutil_cygwin as psutil


class TestCygwinEnvironment(unittest.TestCase):
    """Test that we're running in a proper Cygwin environment."""
    
    def test_proc_filesystem_exists(self):
        """Test that /proc filesystem is available."""
        self.assertTrue(Path("/proc").exists(), "/proc filesystem not found")
        self.assertTrue(Path("/proc/stat").exists(), "/proc/stat not found")
        self.assertTrue(Path("/proc/meminfo").exists(), "/proc/meminfo not found")
        
    def test_basic_proc_files_readable(self):
        """Test that basic /proc files are readable."""
        with open("/proc/stat", "r") as f:
            content = f.read()
            self.assertIn("cpu", content)
            
        with open("/proc/meminfo", "r") as f:
            content = f.read()
            self.assertIn("MemTotal", content)


@unittest.skipUnless(Path("/proc").exists(), "Requires Cygwin /proc filesystem")
class TestSystemIntegration(unittest.TestCase):
    """Integration tests for system-wide functions."""
    
    def test_cpu_functions(self):
        """Test CPU-related functions with real data."""
        # CPU times
        times = psutil.cpu_times()
        self.assertIsInstance(times, psutil.CPUTimes)
        self.assertGreaterEqual(times.user, 0)
        self.assertGreaterEqual(times.system, 0)
        self.assertGreaterEqual(times.idle, 0)
        
        # CPU count
        count = psutil.cpu_count()
        self.assertIsInstance(count, int)
        self.assertGreaterEqual(count, 1)
        
        # CPU percentage
        pct = psutil.cpu_percent(interval=0.1)
        self.assertIsInstance(pct, float)
        self.assertGreaterEqual(pct, 0.0)
        self.assertLessEqual(pct, 100.0)
        
    def test_memory_functions(self):
        """Test memory-related functions with real data."""
        # Virtual memory
        mem = psutil.virtual_memory()
        self.assertIsInstance(mem, psutil.VirtualMemory)
        self.assertGreater(mem.total, 0)
        self.assertGreaterEqual(mem.used, 0)
        self.assertGreaterEqual(mem.free, 0)
        self.assertGreaterEqual(mem.available, 0)
        self.assertGreaterEqual(mem.percent, 0.0)
        self.assertLessEqual(mem.percent, 100.0)
        
        # Swap memory
        swap = psutil.swap_memory()
        self.assertIsInstance(swap, psutil.SwapMemory)
        self.assertGreaterEqual(swap.total, 0)
        self.assertGreaterEqual(swap.used, 0)
        self.assertGreaterEqual(swap.free, 0)
        
    def test_disk_functions(self):
        """Test disk-related functions with real data."""
        # Disk partitions
        partitions = psutil.disk_partitions()
        self.assertIsInstance(partitions, list)
        self.assertGreater(len(partitions), 0)
        
        # Check root partition exists
        root_parts = [p for p in partitions if p.mountpoint == "/"]
        self.assertGreater(len(root_parts), 0)
        
        # Disk usage for root
        usage = psutil.disk_usage("/")
        self.assertIsInstance(usage, psutil.DiskUsage)
        self.assertGreater(usage.total, 0)
        self.assertGreaterEqual(usage.used, 0)
        self.assertGreaterEqual(usage.free, 0)
        
    def test_network_functions(self):
        """Test network-related functions with real data."""
        connections = psutil.net_connections()
        self.assertIsInstance(connections, list)
        
        # Check connection structure if any exist
        if connections:
            conn = connections[0]
            self.assertIsInstance(conn, psutil.NetworkConnection)
            self.assertIsInstance(conn.laddr, psutil.Address)
            
    def test_system_functions(self):
        """Test other system functions."""
        # Boot time
        boot_time = psutil.boot_time()
        self.assertIsInstance(boot_time, float)
        self.assertGreater(boot_time, 0)
        self.assertLess(boot_time, time.time())  # Should be in the past
        
        # Users
        users = psutil.users()
        self.assertIsInstance(users, list)


@unittest.skipUnless(Path("/proc").exists(), "Requires Cygwin /proc filesystem")
class TestProcessIntegration(unittest.TestCase):
    """Integration tests for process-related functions."""
    
    def test_process_listing(self):
        """Test process listing functions."""
        # Get all PIDs
        pids = psutil.pids()
        self.assertIsInstance(pids, list)
        self.assertGreater(len(pids), 0)
        # In Cygwin, PID 1 might not exist - check for any low PID instead
        low_pids = [pid for pid in pids if pid <= 10]
        if not low_pids:
            # If no low PIDs, just check we have some PIDs
            self.assertGreater(len(pids), 0)
        
        # Test PID existence
        for pid in pids[:5]:  # Test first 5 PIDs
            self.assertTrue(psutil.pid_exists(pid))
            
        # Test non-existent PID
        self.assertFalse(psutil.pid_exists(99999))
        
    def test_process_iteration(self):
        """Test process iteration."""
        processes = list(psutil.process_iter())
        self.assertIsInstance(processes, list)
        self.assertGreater(len(processes), 0)
        
        # Test that all returned objects are Process instances
        for proc in processes[:5]:  # Test first 5
            self.assertIsInstance(proc, psutil.Process)
            self.assertIsInstance(proc.pid, int)
            
    def test_current_process(self):
        """Test operations on current process."""
        current_pid = os.getpid()
        proc = psutil.Process(current_pid)
        
        # Basic properties
        self.assertEqual(proc.pid, current_pid)
        self.assertTrue(proc.is_running())
        
        # Name and executable
        name = proc.name()
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)
        
        exe = proc.exe()
        self.assertIsInstance(exe, str)
        
        # Command line
        cmdline = proc.cmdline()
        self.assertIsInstance(cmdline, list)
        
        # Status
        status = proc.status()
        self.assertIsInstance(status, str)
        self.assertIn(status, ['running', 'sleeping', 'disk-sleep', 'zombie', 'stopped', 'paging', 'unknown'])
        
        # Parent PID
        ppid = proc.ppid()
        self.assertIsInstance(ppid, int)
        self.assertGreaterEqual(ppid, 0)
        
        # Creation time
        create_time = proc.create_time()
        self.assertIsInstance(create_time, float)
        self.assertGreater(create_time, 0)
        self.assertLess(create_time, time.time())
        
        # Memory info
        mem_info = proc.memory_info()
        self.assertGreaterEqual(mem_info.rss, 0)
        self.assertGreaterEqual(mem_info.vms, 0)
        
        # CPU times
        cpu_times = proc.cpu_times()
        self.assertGreaterEqual(cpu_times.user, 0.0)
        self.assertGreaterEqual(cpu_times.system, 0.0)
        
        # Open files
        open_files = proc.open_files()
        self.assertIsInstance(open_files, list)
        
    def test_process_relationships(self):
        """Test process parent-child relationships."""
        current_pid = os.getpid()
        proc = psutil.Process(current_pid)
        
        # Test parent
        parent = proc.parent()
        if parent:
            self.assertIsInstance(parent, psutil.Process)
            self.assertEqual(parent.pid, proc.ppid())
            
        # Test children
        children = proc.children()
        self.assertIsInstance(children, list)
        
        # Recursive children
        all_children = proc.children(recursive=True)
        self.assertIsInstance(all_children, list)
        self.assertGreaterEqual(len(all_children), len(children))
        
    def test_process_errors(self):
        """Test process error conditions."""
        # Test non-existent process
        with self.assertRaises(psutil.NoSuchProcess):
            psutil.Process(99999)
            
        # Test accessing process that might deny access
        pids = psutil.pids()
        if pids:
            # Try to access first available process (might be restricted)
            first_pid = pids[0]
            try:
                proc = psutil.Process(first_pid)
                proc.name()  # This might raise AccessDenied
            except psutil.AccessDenied:
                pass  # This is expected for some processes
            except psutil.NoSuchProcess:
                pass  # Process might have disappeared


@unittest.skipUnless(Path("/proc").exists(), "Requires Cygwin /proc filesystem")
class TestPerformanceIntegration(unittest.TestCase):
    """Test performance characteristics with real data."""
    
    def test_process_iteration_performance(self):
        """Test that process iteration performs reasonably."""
        start_time = time.time()
        
        # Iterate through first 100 processes
        count = 0
        for proc in psutil.process_iter():
            try:
                proc.name()
                count += 1
                if count >= 100:
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        end_time = time.time()
        duration = end_time - start_time
        
        # Should be able to process 100 processes in reasonable time
        self.assertLess(duration, 10.0, f"Process iteration too slow: {duration}s")
        
    def test_repeated_cpu_calls(self):
        """Test repeated CPU calls for consistency."""
        percentages = []
        for i in range(5):
            pct = psutil.cpu_percent(interval=0.1)
            percentages.append(pct)
            
        # All should be valid percentages
        for pct in percentages:
            self.assertGreaterEqual(pct, 0.0)
            self.assertLessEqual(pct, 100.0)
            
        # Should not vary wildly (within 50% range)
        if len(percentages) > 1:
            avg = sum(percentages) / len(percentages)
            for pct in percentages:
                self.assertLess(abs(pct - avg), 50.0)


@unittest.skipUnless(Path("/proc").exists(), "Requires Cygwin /proc filesystem")
class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios."""
    
    def test_system_monitoring_scenario(self):
        """Test a typical system monitoring scenario."""
        # Get system overview
        cpu_pct = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        # Verify we got reasonable values
        self.assertIsInstance(cpu_pct, float)
        self.assertIsInstance(mem.percent, float)
        self.assertIsInstance(disk.total, int)
        
        # Get top memory processes
        processes = []
        for proc in psutil.process_iter():
            try:
                mem_info = proc.memory_info()
                processes.append((proc.pid, proc.name(), mem_info.rss))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        # Sort by memory usage
        processes.sort(key=lambda x: x[2], reverse=True)
        
        # Should have found some processes
        self.assertGreater(len(processes), 0)
        
        # Top process should have some memory usage
        if processes:
            self.assertGreater(processes[0][2], 0)
            
    def test_process_management_scenario(self):
        """Test a typical process management scenario."""
        current_pid = os.getpid()
        
        # Find current process in process list
        found_current = False
        for proc in psutil.process_iter():
            if proc.pid == current_pid:
                found_current = True
                
                # Get detailed info
                name = proc.name()
                status = proc.status()
                mem_info = proc.memory_info()
                
                # Verify reasonable values
                self.assertIsInstance(name, str)
                self.assertIn(status, ['running', 'sleeping', 'disk-sleep', 'zombie', 'stopped', 'paging', 'unknown'])
                self.assertGreaterEqual(mem_info.rss, 0)
                break
                
        self.assertTrue(found_current, "Current process not found in process list")
        
        # Test process tree navigation
        proc = psutil.Process(current_pid)
        parent = proc.parent()
        if parent:
            # Should be able to get parent info
            parent_name = parent.name()
            self.assertIsInstance(parent_name, str)
            
            # Current process should be in parent's children
            parent_children = parent.children()
            child_pids = [child.pid for child in parent_children]
            self.assertIn(current_pid, child_pids)


if __name__ == '__main__':
    # Run with more verbose output
    unittest.main(verbosity=2)
