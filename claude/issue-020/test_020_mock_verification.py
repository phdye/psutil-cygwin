#!/usr/bin/env python3
"""
pytest-compatible mock tests for Issue 020 fixes.

Run with: pytest claude/issue-020/test_020_mock_verification.py -v
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import tempfile

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psutil_cygwin as psutil
from psutil_cygwin.cygwin_check import create_psutil_pth


class TestIssue020MockVerification:
    """Mock verification tests for Issue 020 fixes."""
    
    def test_cpu_times_calculation_fix(self):
        """Test that CPU times calculation works correctly with mocked data."""
        with patch('builtins.open', new_callable=mock_open) as mock_file:
            with patch('os.sysconf', return_value=100):
                # This is the exact test case that was failing
                mock_file.return_value.read.return_value = "cpu  100 200 300 400 500 600 700 800\n"
                times = psutil.cpu_times()
                
                # Verify correct parsing
                assert times.user == 1.0, f"Expected user=1.0, got {times.user}"
                assert times.system == 2.0, f"Expected system=2.0, got {times.system}"
                assert times.idle == 4.0, f"Expected idle=4.0, got {times.idle}"
                assert isinstance(times, psutil.CPUTimes)

    def test_binary_data_handling_fix(self):
        """Test that binary data is handled correctly without TypeError."""
        with patch('builtins.open', mock_open(read_data=b'\x00\x01\x02\x03\x04\x05')):
            # Should not raise TypeError
            times = psutil.cpu_times()
            assert isinstance(times, psutil.CPUTimes)
            # Should return default values for binary data
            assert times.user >= 0
            assert times.system >= 0
            assert times.idle >= 0

    def test_intermittent_file_errors_handling(self):
        """Test that intermittent file errors are handled gracefully."""
        call_count = 0
        success_count = 0
        
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
        
        with patch('builtins.open', side_effect=intermittent_failure):
            for _ in range(12):
                try:
                    times = psutil.cpu_times()
                    if times.user > 0:
                        success_count += 1
                except OSError:
                    pass  # Expected intermittent failure
        
        # Should have some successful operations
        assert success_count > 0, f"Expected some successes, got {success_count}"

    def test_pth_file_creation_fix(self):
        """Test that PTH file creation works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('site.getsitepackages', return_value=[]):
                with patch('site.getusersitepackages', return_value=temp_dir):
                    result = create_psutil_pth()
                    
                    # Should return a valid path
                    assert result is not None
                    assert os.path.exists(result)
                    assert result.endswith('psutil.pth')
                    
                    # Verify file content
                    with open(result, 'r') as f:
                        content = f.read()
                    assert 'psutil-cygwin' in content
                    assert "sys.modules['psutil']" in content
                    assert "__import__('psutil_cygwin')" in content

    def test_corrupted_proc_data_scenarios(self):
        """Test various corrupted /proc data scenarios."""
        corrupted_scenarios = [
            ("", "empty file"),
            ("invalid data", "random text"),
            ("cpu", "incomplete line"),
            ("cpu  abc def ghi", "non-numeric data"),
            ("notcpu  100 200 300", "wrong format"),
        ]
        
        for corrupted_data, description in corrupted_scenarios:
            with patch('builtins.open', mock_open(read_data=corrupted_data)):
                # Should not crash, should return default values
                times = psutil.cpu_times()
                assert isinstance(times, psutil.CPUTimes)
                assert times.user >= 0
                assert times.system >= 0
                assert times.idle >= 0

    def test_edge_case_numeric_values(self):
        """Test edge case numeric values in CPU data."""
        edge_cases = [
            ("cpu  0 0 0 0 0", "all zeros"),
            ("cpu  -1 -2 -3 -4", "negative values"),
            ("cpu  999999999999 888888888888 777777777777", "very large numbers"),
            ("cpu  1", "minimal fields"),
        ]
        
        with patch('os.sysconf', return_value=100):
            for cpu_data, description in edge_cases:
                with patch('builtins.open', mock_open(read_data=cpu_data + "\n")):
                    times = psutil.cpu_times()
                    assert isinstance(times, psutil.CPUTimes)
                    # All values should be non-negative after processing
                    assert times.user >= 0, f"Negative user time in {description}"
                    assert times.system >= 0, f"Negative system time in {description}"
                    assert times.idle >= 0, f"Negative idle time in {description}"


class TestIssue020PerformanceVerification:
    """Performance-related verification tests for Issue 020."""
    
    def test_cpu_times_performance_stability(self):
        """Test that cpu_times function performs consistently."""
        import time
        
        # Mock consistent data
        with patch('builtins.open', mock_open(read_data="cpu  100 200 300 400\n")):
            with patch('os.sysconf', return_value=100):
                
                # Multiple calls should be consistent
                times1 = psutil.cpu_times()
                times2 = psutil.cpu_times()
                times3 = psutil.cpu_times()
                
                assert times1.user == times2.user == times3.user
                assert times1.system == times2.system == times3.system
                assert times1.idle == times2.idle == times3.idle

    def test_error_recovery_robustness(self):
        """Test that error recovery doesn't break subsequent calls."""
        call_count = 0
        
        def alternating_success_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:  # Fail every other call
                raise OSError("Simulated failure")
            
            mock_file = MagicMock()
            mock_file.read.return_value = "cpu  100 200 300 400\n"
            mock_file.__enter__ = MagicMock(return_value=mock_file)
            mock_file.__exit__ = MagicMock(return_value=None)
            return mock_file
        
        with patch('builtins.open', side_effect=alternating_success_failure):
            results = []
            
            for _ in range(10):
                try:
                    times = psutil.cpu_times()
                    results.append('success')
                except OSError:
                    results.append('failure')
            
            # Should have alternating success/failure pattern
            assert 'success' in results
            assert 'failure' in results


if __name__ == '__main__':
    # Run the tests if executed directly
    pytest.main([__file__, '-v'])
