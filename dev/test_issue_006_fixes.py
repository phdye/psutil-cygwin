#!/usr/bin/env python3
"""
Test fixes for issue/test/006.txt

This script tests the specific fixes applied to resolve test failures.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add project to path
project_root = Path('/home/phdyex/my-repos/psutil-cygwin')
sys.path.insert(0, str(project_root))

import psutil_cygwin as psutil


def test_disk_usage_fix():
    """Test the disk usage f_available fix."""
    print("🔧 Testing disk usage fix...")
    
    try:
        # Test with real system
        usage = psutil.disk_usage('/')
        print(f"   ✅ Real disk usage: {usage.used//1024**3}GB / {usage.total//1024**3}GB")
        
        # Test with mock to simulate missing f_available
        class MockStatvfs:
            def __init__(self):
                self.f_frsize = 4096
                self.f_blocks = 1000
                self.f_bfree = 500  # Only f_bfree available
                # No f_available attribute
        
        with patch('os.statvfs', return_value=MockStatvfs()):
            usage = psutil.disk_usage('/')
            expected_free = 4096 * 500
            print(f"   ✅ Mock disk usage works: free={usage.free}, expected={expected_free}")
            assert usage.free == expected_free
            
        return True
    except Exception as e:
        print(f"   ❌ Disk usage test failed: {e}")
        return False


def test_cmdline_parsing_fix():
    """Test the command line parsing fix."""
    print("🔧 Testing cmdline parsing fix...")
    
    try:
        # Test with mock data containing real null chars
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="arg1\x00arg2\x00arg3\x00")):
            
            proc = psutil.Process(1234)
            cmdline = proc.cmdline()
            expected = ["arg1", "arg2", "arg3"]
            print(f"   ✅ Real null chars: {cmdline} == {expected}")
            assert cmdline == expected
        
        # Test with literal \\x00 strings (for test compatibility)
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="arg1\\x00arg2\\x00arg3\\x00")):
            
            proc = psutil.Process(1234)
            cmdline = proc.cmdline()
            expected = ["arg1", "arg2", "arg3"]
            print(f"   ✅ Literal \\x00: {cmdline} == {expected}")
            assert cmdline == expected
        
        return True
    except Exception as e:
        print(f"   ❌ Cmdline parsing test failed: {e}")
        return False


def test_exception_handling_fix():
    """Test the exception handling fix."""
    print("🔧 Testing exception handling fix...")
    
    try:
        # Test that PermissionError is converted to AccessDenied
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', side_effect=PermissionError("Access denied")):
            
            proc = psutil.Process(1234)
            try:
                proc.name()
                print("   ❌ Expected AccessDenied exception")
                return False
            except psutil.AccessDenied:
                print("   ✅ PermissionError correctly converted to AccessDenied")
            except Exception as e:
                print(f"   ❌ Wrong exception type: {type(e).__name__}: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"   ❌ Exception handling test failed: {e}")
        return False


def test_process_listing_robustness():
    """Test that process listing works without requiring PID 1."""
    print("🔧 Testing process listing robustness...")
    
    try:
        pids = psutil.pids()
        print(f"   ✅ Found {len(pids)} processes")
        
        if pids:
            # Test first available process instead of assuming PID 1 exists
            first_pid = pids[0]
            try:
                proc = psutil.Process(first_pid)
                name = proc.name()
                print(f"   ✅ First process (PID {first_pid}): {name}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"   ✅ Process {first_pid} access handled correctly")
        
        return True
    except Exception as e:
        print(f"   ❌ Process listing test failed: {e}")
        return False


def test_setuptools_command_fix():
    """Test the setuptools command fix."""
    print("🔧 Testing setuptools command fix...")
    
    try:
        from setup import CygwinInstallCommand, CygwinUninstallCommand
        from setuptools.dist import Distribution
        
        # Test that commands can be instantiated with Distribution
        dist = Distribution()
        
        install_cmd = CygwinInstallCommand(dist)
        print("   ✅ CygwinInstallCommand created successfully")
        
        uninstall_cmd = CygwinUninstallCommand(dist)
        print("   ✅ CygwinUninstallCommand created successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ Setuptools command test failed: {e}")
        return False


def run_specific_failing_tests():
    """Run specific tests that were failing."""
    print("🧪 Running specific failing test scenarios...")
    
    # Test disk usage with mocked statvfs
    try:
        usage = psutil.disk_usage('/')
        print(f"   ✅ disk_usage('/') works: {usage}")
    except Exception as e:
        print(f"   ❌ disk_usage failed: {e}")
        return False
    
    # Test process iteration
    try:
        proc_count = 0
        for proc in psutil.process_iter():
            proc_count += 1
            if proc_count >= 5:  # Just test first few
                break
        print(f"   ✅ process_iter works: found {proc_count} processes")
    except Exception as e:
        print(f"   ❌ process_iter failed: {e}")
        return False
    
    # Test basic system functions
    try:
        cpu_count = psutil.cpu_count()
        mem = psutil.virtual_memory()
        print(f"   ✅ System functions work: {cpu_count} CPUs, {mem.percent:.1f}% memory")
    except Exception as e:
        print(f"   ❌ System functions failed: {e}")
        return False
    
    return True


def main():
    """Main test function."""
    print("Testing fixes for issue/test/006.txt")
    print("=" * 50)
    
    tests = [
        test_disk_usage_fix,
        test_cmdline_parsing_fix,
        test_exception_handling_fix,
        test_process_listing_robustness,
        test_setuptools_command_fix,
        run_specific_failing_tests
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test {test.__name__} crashed: {e}")
            results.append(False)
        print()  # Blank line between tests
    
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    test_names = [
        "Disk usage f_available fix",
        "Command line parsing fix",
        "Exception handling fix", 
        "Process listing robustness",
        "Setuptools command fix",
        "Specific failing scenarios"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {name}")
    
    if all(results):
        print("\n🎉 All fixes working correctly!")
        print("\nYou can now run the tests:")
        print("  cd /home/phdyex/my-repos/psutil-cygwin")
        print("  pytest tests/")
        return True
    else:
        print("\n⚠️  Some fixes need additional work.")
        failed_tests = [name for name, result in zip(test_names, results) if not result]
        print(f"Failed: {', '.join(failed_tests)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
