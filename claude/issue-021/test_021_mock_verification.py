#!/usr/bin/env python3
"""
pytest-compatible mock tests for Issue 021 fixes.

Run with: pytest claude/issue-021/test_021_mock_verification.py -v
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import time

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psutil_cygwin as psutil
from psutil_cygwin.cygwin_check import create_psutil_pth


class TestIssue021MockVerification:
    """Mock verification tests for Issue 021 fixes."""
    
    def test_cpu_times_system_index_fix(self):
        """Test that CPU times system index is correct (index 2, not 1)."""
        with patch('builtins.open', new_callable=mock_open) as mock_file:
            with patch('os.sysconf', return_value=100):
                # Test data: "cpu  100 200 300 400 500 600 700 800"
                # Expected: user=1.0, system=3.0 (index 2), idle=4.0
                mock_file.return_value.read.return_value = "cpu  100 200 300 400 500 600 700 800\n"
                times = psutil.cpu_times()
                
                assert times.user == 1.0, f"Expected user=1.0, got {times.user}"
                assert times.system == 3.0, f"Expected system=3.0, got {times.system}"  # This was the fix!
                assert times.idle == 4.0, f"Expected idle=4.0, got {times.idle}"
                assert isinstance(times, psutil.CPUTimes)

    def test_negative_cpu_values_handling(self):
        """Test that negative CPU values are properly sanitized."""
        with patch('builtins.open', new_callable=mock_open) as mock_file:
            with patch('os.sysconf', return_value=100):
                # Test with negative values
                mock_file.return_value.read.return_value = "cpu  -1 -2 -3 -4\n"
                times = psutil.cpu_times()
                
                # All values should be non-negative after processing
                assert times.user >= 0, f"User time should be >= 0, got {times.user}"
                assert times.system >= 0, f"System time should be >= 0, got {times.system}"
                assert times.idle >= 0, f"Idle time should be >= 0, got {times.idle}"
                assert times.interrupt >= 0, f"Interrupt time should be >= 0, got {times.interrupt}"

    def test_virtual_memory_binary_data_handling(self):
        """Test that virtual_memory handles binary data correctly."""
        binary_data_scenarios = [
            b'\x00\x01\x02\x03\x04\x05',  # Pure binary
            b'MemTotal: 8192000 kB\nMemFree: 4096000 kB\n',  # Valid meminfo as bytes
            "cpu  100 200 300 \xff\xfe\xfd".encode('latin-1'),  # Mixed encoding
        ]
        
        for binary_data in binary_data_scenarios:
            with patch('builtins.open', mock_open(read_data=binary_data)):
                # Should not raise TypeError
                mem = psutil.virtual_memory()
                assert isinstance(mem, psutil.VirtualMemory)
                assert mem.total >= 0
                assert mem.available >= 0
                assert mem.percent >= 0

    def test_cpu_count_caching_performance(self):
        """Test that cpu_count function uses caching for performance."""
        original_cpu_count = psutil.cpu_count
        
        # Reset cache if it exists
        if hasattr(psutil.cpu_count, '_cached_count'):
            delattr(psutil.cpu_count, '_cached_count')
        
        call_count = 0
        
        def mock_proc_cpuinfo(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_file = MagicMock()
            mock_file.read.return_value = "processor\t: 0\nprocessor\t: 1\nprocessor\t: 2\nprocessor\t: 3\n"
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            return mock_file
        
        with patch('builtins.open', side_effect=mock_proc_cpuinfo):
            # First call should read the file
            count1 = psutil.cpu_count()
            first_call_count = call_count
            
            # Second call should use cache
            count2 = psutil.cpu_count()
            second_call_count = call_count
            
            # Third call should use cache
            count3 = psutil.cpu_count()
            third_call_count = call_count
            
            # Results should be the same
            assert count1 == count2 == count3 == 4
            
            # Should only read file once (first call)
            assert first_call_count == 1, "First call should read file"
            assert second_call_count == 1, "Second call should use cache"
            assert third_call_count == 1, "Third call should use cache"

    def test_pth_permission_error_handling(self):
        """Test that PTH creation properly handles permission errors."""
        
        # Test successful creation
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('site.getsitepackages', return_value=[temp_dir]):
                with patch('os.path.exists', return_value=True):
                    with patch('os.access', return_value=True):
                        result = create_psutil_pth()
                        assert result is not None
                        assert os.path.exists(result)
        
        # Test permission error handling
        with patch('site.getsitepackages', return_value=['/tmp/test']):
            with patch('os.path.exists', return_value=True):
                with patch('os.access', return_value=True):
                    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                        result = create_psutil_pth()
                        assert result is None, "Should return None on permission error"

    def test_extreme_cpu_values_handling(self):
        """Test handling of extreme CPU values."""
        extreme_cases = [
            # Very large numbers
            ("cpu  999999999999999999 888888888888888888 777777777777777777 666666666666666666", "very large"),
            # Maximum possible values
            (f"cpu  {2**63-1} {2**63-1} {2**63-1} {2**63-1}", "maximum values"),
            # Zero values
            ("cpu  0 0 0 0 0 0 0 0", "all zeros"),
            # Single huge value
            ("cpu  999999999999999999", "single large value"),
            # Mixed positive/negative
            ("cpu  1000 -500 2000 -100", "mixed signs"),
        ]
        
        with patch('os.sysconf', return_value=100):
            for cpu_data, description in extreme_cases:
                with patch('builtins.open', mock_open(read_data=cpu_data + "\n")):
                    times = psutil.cpu_times()
                    assert isinstance(times, psutil.CPUTimes)
                    # Values should be reasonable after processing
                    assert times.user >= 0, f"User time negative in {description}"
                    assert times.system >= 0, f"System time negative in {description}"
                    assert times.idle >= 0, f"Idle time negative in {description}"

    def test_corrupted_meminfo_data(self):
        """Test virtual_memory with corrupted /proc/meminfo data."""
        corrupted_scenarios = [
            ("", "empty file"),
            ("invalid data without colons", "no colons"),
            ("MemTotal\nMemFree", "malformed lines"),
            ("MemTotal: abc kB\nMemFree: def kB", "non-numeric values"),
            ("MemTotal: 8192000 kB\nCorrupted: \xff\xfe\xfd", "mixed corruption"),
        ]
        
        for corrupted_data, description in corrupted_scenarios:
            with patch('builtins.open', mock_open(read_data=corrupted_data)):
                # Should not crash, should return valid object
                mem = psutil.virtual_memory()
                assert isinstance(mem, psutil.VirtualMemory)
                assert mem.total >= 0
                assert mem.available >= 0
                assert mem.percent >= 0


class TestIssue021PerformanceVerification:
    """Performance verification tests for Issue 021."""
    
    def test_high_frequency_cpu_count_calls(self):
        """Test that high frequency cpu_count calls perform well."""
        # Clear cache
        if hasattr(psutil.cpu_count, '_cached_count'):
            delattr(psutil.cpu_count, '_cached_count')
        
        with patch('builtins.open', mock_open(read_data="processor\t: 0\nprocessor\t: 1\n")):
            start_time = time.time()
            
            # Rapid calls - should be fast due to caching
            results = []
            for _ in range(100):  # Reduced from 1000 for faster testing
                result = psutil.cpu_count()
                results.append(result)
            
            end_time = time.time()
            
            # All results should be the same
            assert all(r == results[0] for r in results)
            
            # Should complete quickly (with caching)
            total_time = end_time - start_time
            assert total_time < 1.0, f"100 calls took {total_time:.3f}s, should be < 1s with caching"

    def test_memory_function_performance(self):
        """Test that memory functions handle large data efficiently."""
        # Create large but valid meminfo data
        large_meminfo = "\n".join([
            "MemTotal:       8192000 kB",
            "MemFree:        4096000 kB",
            "MemAvailable:   6144000 kB", 
            "Buffers:         512000 kB",
            "Cached:         1024000 kB",
        ] + [f"ExtraField{i}:  {i*1000} kB" for i in range(100)])  # Add many fields
        
        with patch('builtins.open', mock_open(read_data=large_meminfo)):
            start_time = time.time()
            
            # Multiple calls to test consistency
            for _ in range(10):
                mem = psutil.virtual_memory()
                assert isinstance(mem, psutil.VirtualMemory)
                assert mem.total > 0
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Should process large data efficiently
            assert total_time < 1.0, f"Processing large meminfo took {total_time:.3f}s"


class TestIssue021RegressionPrevention:
    """Tests to prevent regression of the original issues."""
    
    def test_original_issue_020_scenarios_still_work(self):
        """Ensure Issue 020 fixes still work after Issue 021 changes."""
        # Binary data handling
        with patch('builtins.open', mock_open(read_data=b'\x00\x01\x02\x03')):
            times = psutil.cpu_times()
            assert isinstance(times, psutil.CPUTimes)
        
        # Intermittent errors
        call_count = 0
        def intermittent_error(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise OSError("Intermittent error")
            mock_file = MagicMock()
            mock_file.read.return_value = "cpu  100 200 300 400\n"
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            return mock_file
        
        with patch('builtins.open', side_effect=intermittent_error):
            # Should handle the intermittent error gracefully
            times1 = psutil.cpu_times()  # Success
            try:
                times2 = psutil.cpu_times()  # Error
            except OSError:
                pass
            times3 = psutil.cpu_times()  # Success again
            
            assert isinstance(times1, psutil.CPUTimes)
            assert isinstance(times3, psutil.CPUTimes)

    def test_all_fixes_integrated_correctly(self):
        """Test that all fixes work together without conflicts."""
        # Test comprehensive scenario with multiple edge cases
        with patch('os.sysconf', return_value=100):
            with patch('builtins.open', mock_open(read_data="cpu  -10 50 300 400 500\n")):
                times = psutil.cpu_times()
                
                # Should handle negative values (Issue 021 fix)
                assert times.user >= 0
                
                # Should have correct system index (Issue 021 fix)  
                assert times.system == 3.0  # 300/100
                
                # Should handle the mock data correctly (Issue 020 fix)
                assert isinstance(times, psutil.CPUTimes)
                assert times.idle == 4.0


if __name__ == '__main__':
    # Run the tests if executed directly
    pytest.main([__file__, '-v'])
