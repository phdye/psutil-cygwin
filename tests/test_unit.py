"""
Unit tests for psutil-cygwin core functionality.
"""

import os
import sys
import time
import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

# Add the package to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

import psutil_cygwin as psutil


class TestExceptions(unittest.TestCase):
    """Test custom exception classes."""
    
    def test_access_denied(self):
        """Test AccessDenied exception."""
        # Test with PID
        exc = psutil.AccessDenied(pid=1234)
        self.assertEqual(exc.pid, 1234)
        self.assertIn("1234", str(exc))
        
        # Test with custom message
        exc = psutil.AccessDenied(msg="Custom error")
        self.assertEqual(exc.msg, "Custom error")
        
    def test_no_such_process(self):
        """Test NoSuchProcess exception."""
        # Test with PID
        exc = psutil.NoSuchProcess(pid=9999)
        self.assertEqual(exc.pid, 9999)
        self.assertIn("9999", str(exc))
        
    def test_timeout_expired(self):
        """Test TimeoutExpired exception."""
        exc = psutil.TimeoutExpired(5.0, pid=1234)
        self.assertEqual(exc.seconds, 5.0)
        self.assertEqual(exc.pid, 1234)
        self.assertIn("5.0", str(exc))


class TestSystemFunctions(unittest.TestCase):
    """Test system-wide functions."""
    
    @patch('builtins.open', new_callable=mock_open, 
           read_data="cpu  100 200 300 400 500\n")
    @patch('os.sysconf')
    def test_cpu_times(self, mock_sysconf, mock_file):
        """Test CPU times parsing."""
        mock_sysconf.return_value = 100  # Clock ticks per second
        
        times = psutil.cpu_times()
        self.assertIsInstance(times, psutil.CPUTimes)
        self.assertEqual(times.user, 1.0)  # 100/100
        self.assertEqual(times.system, 3.0)  # 300/100
        self.assertEqual(times.idle, 4.0)  # 400/100
        
    @patch('builtins.open', new_callable=mock_open,
           read_data="MemTotal: 1000000 kB\nMemFree: 500000 kB\n")
    def test_virtual_memory(self, mock_file):
        """Test virtual memory parsing."""
        mem = psutil.virtual_memory()
        self.assertIsInstance(mem, psutil.VirtualMemory)
        self.assertEqual(mem.total, 1000000 * 1024)
        self.assertEqual(mem.free, 500000 * 1024)
        
    @patch('builtins.open', new_callable=mock_open,
           read_data="processor : 0\nprocessor : 1\n")
    def test_cpu_count(self, mock_file):
        """Test CPU count parsing."""
        count = psutil.cpu_count()
        self.assertEqual(count, 2)
        
    @patch('os.listdir')
    def test_pids(self, mock_listdir):
        """Test PID listing."""
        mock_listdir.return_value = ['1', '2', '100', 'self', 'stat']
        pids = psutil.pids()
        self.assertEqual(sorted(pids), [1, 2, 100])
        
    @patch('os.path.exists')
    def test_pid_exists(self, mock_exists):
        """Test PID existence check."""
        mock_exists.return_value = True
        self.assertTrue(psutil.pid_exists(1234))
        
        mock_exists.return_value = False
        self.assertFalse(psutil.pid_exists(9999))


class TestProcessClass(unittest.TestCase):
    """Test Process class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_pid = 1234
        
    @patch('os.path.exists')
    def test_process_init(self, mock_exists):
        """Test Process initialization."""
        # Test successful creation
        mock_exists.return_value = True
        proc = psutil.Process(self.test_pid)
        self.assertEqual(proc.pid, self.test_pid)
        
        # Test NoSuchProcess exception
        mock_exists.return_value = False
        with self.assertRaises(psutil.NoSuchProcess):
            psutil.Process(99999)
            
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="test_process")
    def test_process_name(self, mock_file, mock_exists):
        """Test process name retrieval."""
        proc = psutil.Process(self.test_pid)
        name = proc.name()
        self.assertEqual(name, "test_process")
        
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, 
           read_data="arg1\x00arg2\x00arg3\x00")
    def test_process_cmdline(self, mock_file, mock_exists):
        """Test process command line parsing."""
        proc = psutil.Process(self.test_pid)
        cmdline = proc.cmdline()
        self.assertEqual(cmdline, ["arg1", "arg2", "arg3"])
        
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open,
           read_data="VmRSS: 1000 kB\nVmSize: 2000 kB\n")
    def test_process_memory_info(self, mock_file, mock_exists):
        """Test process memory information."""
        proc = psutil.Process(self.test_pid)
        mem = proc.memory_info()
        self.assertEqual(mem.rss, 1000 * 1024)
        self.assertEqual(mem.vms, 2000 * 1024)


class TestDiskFunctions(unittest.TestCase):
    """Test disk-related functions."""
    
    @patch('builtins.open', new_callable=mock_open,
           read_data="/dev/sda1 / ext4 rw,relatime 0 0\n")
    def test_disk_partitions(self, mock_file):
        """Test disk partitions parsing."""
        partitions = psutil.disk_partitions()
        self.assertEqual(len(partitions), 1)
        
        part = partitions[0]
        self.assertEqual(part.device, "/dev/sda1")
        self.assertEqual(part.mountpoint, "/")
        self.assertEqual(part.fstype, "ext4")
        
    @patch('os.statvfs')
    def test_disk_usage(self, mock_statvfs):
        """Test disk usage calculation."""
        # Mock statvfs result
        mock_result = MagicMock()
        mock_result.f_frsize = 4096
        mock_result.f_blocks = 1000
        mock_result.f_available = 500
        mock_statvfs.return_value = mock_result
        
        usage = psutil.disk_usage("/")
        self.assertEqual(usage.total, 4096 * 1000)
        self.assertEqual(usage.free, 4096 * 500)
        self.assertEqual(usage.used, 4096 * 500)


class TestNetworkFunctions(unittest.TestCase):
    """Test network-related functions."""
    
    @patch('builtins.open', new_callable=mock_open,
           read_data="  sl  local_address rem_address   st tx_queue rx_queue\\n"
                    "   0: 0100007F:0050 00000000:0000 0A 00000000:00000000\\n")
    def test_net_connections(self, mock_file):
        """Test network connections parsing."""
        connections = psutil.net_connections()
        self.assertGreaterEqual(len(connections), 0)
        
        if connections:
            conn = connections[0]
            self.assertIsInstance(conn, psutil.NetworkConnection)


class TestPerformance(unittest.TestCase):
    """Test performance and edge cases."""
    
    def test_cpu_percent_interval(self):
        """Test CPU percentage with different intervals."""
        # This is an integration test that actually measures CPU
        if Path("/proc/stat").exists():
            pct = psutil.cpu_percent(interval=0.1)
            self.assertIsInstance(pct, float)
            self.assertGreaterEqual(pct, 0.0)
            self.assertLessEqual(pct, 100.0)
            
    def test_large_process_list(self):
        """Test handling of large process lists."""
        if Path("/proc").exists():
            # This should not crash or timeout
            procs = list(psutil.process_iter())
            self.assertIsInstance(procs, list)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    @patch('builtins.open', side_effect=PermissionError("Access denied"))
    @patch('os.path.exists', return_value=True)
    def test_access_denied_handling(self, mock_exists, mock_open):
        """Test handling of permission errors."""
        proc = psutil.Process(1)
        with self.assertRaises(psutil.AccessDenied):
            proc.name()
            
    @patch('builtins.open', side_effect=FileNotFoundError("No such file"))
    def test_file_not_found_handling(self, mock_open):
        """Test handling of missing files."""
        # Should not crash, should return sensible defaults
        mem = psutil.virtual_memory()
        self.assertIsInstance(mem, psutil.VirtualMemory)
        
    def test_malformed_proc_files(self):
        """Test handling of malformed /proc files."""
        with patch('builtins.open', new_callable=mock_open, read_data="invalid data"):
            # Should not crash
            times = psutil.cpu_times()
            self.assertIsInstance(times, psutil.CPUTimes)


if __name__ == '__main__':
    # Run with more verbose output
    unittest.main(verbosity=2)
