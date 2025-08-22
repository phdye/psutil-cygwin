#!/usr/bin/env python3
"""
Quick test to verify our fixes work for issue 020
"""

import sys
import os
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import psutil_cygwin as psutil
from unittest.mock import patch, mock_open

def test_cpu_times_fix():
    """Test the CPU times fix."""
    print("🧪 Testing CPU times calculation fix...")
    
    with patch('builtins.open', new_callable=mock_open) as mock_file:
        with patch('os.sysconf', return_value=100):
            # This is the exact test case that was failing
            mock_file.return_value.read.return_value = "cpu  100 200 300 400 500 600 700 800\n"
            times = psutil.cpu_times()
            
            print(f"   User time: {times.user} (expected: 1.0)")
            print(f"   System time: {times.system} (expected: 2.0)")
            
            if times.user == 1.0:
                print("   ✅ CPU times test PASSED")
                return True
            else:
                print("   ❌ CPU times test FAILED")
                return False

def test_binary_data_fix():
    """Test the binary data handling fix."""
    print("🧪 Testing binary data handling fix...")
    
    try:
        with patch('builtins.open', mock_open(read_data=b'\x00\x01\x02\x03\x04\x05')):
            times = psutil.cpu_times()
            print(f"   Result: {type(times).__name__} (no TypeError)")
            print("   ✅ Binary data test PASSED")
            return True
    except TypeError as e:
        print(f"   ❌ Binary data test FAILED: {e}")
        return False

def test_intermittent_errors_fix():
    """Test the intermittent errors handling."""
    print("🧪 Testing intermittent errors fix...")
    
    call_count = 0
    success_count = 0
    
    def intermittent_failure(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count % 3 == 0:  # Fail every 3rd call
            raise OSError("Intermittent failure")
        
        # Return a mock file object
        from unittest.mock import MagicMock
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
    
    print(f"   Successful operations: {success_count}/12")
    if success_count > 0:
        print("   ✅ Intermittent errors test PASSED")
        return True
    else:
        print("   ❌ Intermittent errors test FAILED")
        return False

def test_pth_creation_fix():
    """Test the PTH file creation fix."""
    print("🧪 Testing PTH file creation fix...")
    
    import tempfile
    from psutil_cygwin.cygwin_check import create_psutil_pth
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch('site.getsitepackages', return_value=[]):
            with patch('site.getusersitepackages', return_value=temp_dir):
                result = create_psutil_pth()
                
                if result and os.path.exists(result):
                    print(f"   Created: {result}")
                    print("   ✅ PTH creation test PASSED")
                    return True
                else:
                    print("   ❌ PTH creation test FAILED")
                    return False

def main():
    """Run all test fixes."""
    print("🔍 Testing fixes for issue/test/020.txt failures...")
    print()
    
    tests = [
        test_cpu_times_fix,
        test_binary_data_fix, 
        test_intermittent_errors_fix,
        test_pth_creation_fix
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        print()
    
    print("📋 Summary:")
    print(f"   Tests passed: {passed}/{total}")
    
    if passed == total:
        print("   🎉 All fixes working correctly!")
        return True
    else:
        print("   ⚠️  Some fixes need more work")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
