#!/usr/bin/env python3
"""
Verification script for psutil-cygwin after fixing the import issue

Run this script to verify that the import issue has been resolved.
"""

import sys
import os

def test_imports():
    """Test all the imports that were failing"""
    
    # Add project directory to path
    project_dir = '/home/phdyex/my-repos/psutil-cygwin'
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    
    print("🧪 Testing psutil-cygwin imports...")
    print("=" * 40)
    
    try:
        # Test 1: Direct core imports
        print("1. Testing direct core imports...")
        from psutil_cygwin.core import (
            User, CPUTimes, VirtualMemory, SwapMemory, 
            DiskUsage, DiskIO, NetworkConnection, Address,
            Process, AccessDenied, NoSuchProcess, TimeoutExpired,
            cpu_percent, virtual_memory, pids
        )
        print("   ✓ All core imports successful")
        print(f"   ✓ User namedtuple fields: {User._fields}")
        
        # Test 2: Package-level imports  
        print("\n2. Testing package-level imports...")
        import psutil_cygwin as psutil
        print("   ✓ Package imported successfully")
        
        # Verify all expected attributes are available
        expected_attrs = [
            'User', 'Process', 'cpu_percent', 'virtual_memory', 
            'pids', 'disk_usage', 'net_connections', 'users'
        ]
        
        missing_attrs = []
        for attr in expected_attrs:
            if hasattr(psutil, attr):
                print(f"   ✓ {attr} available")
            else:
                missing_attrs.append(attr)
                print(f"   ✗ {attr} missing")
        
        if missing_attrs:
            print(f"\n❌ Missing attributes: {missing_attrs}")
            return False
        
        # Test 3: Functional test
        print("\n3. Testing functionality...")
        
        # Test User namedtuple
        users_list = psutil.users()
        print(f"   ✓ users() returns {len(users_list)} users")
        
        # Test basic system info
        cpu_pct = psutil.cpu_percent(interval=0.1)
        print(f"   ✓ CPU usage: {cpu_pct:.1f}%")
        
        mem = psutil.virtual_memory()
        print(f"   ✓ Memory usage: {mem.percent:.1f}%")
        
        pid_count = len(psutil.pids())
        print(f"   ✓ Process count: {pid_count}")
        
        # Test 4: The exact import that was failing
        print("\n4. Testing the exact failing import pattern...")
        
        # Clear module cache to simulate fresh import
        modules_to_clear = [k for k in sys.modules.keys() if k.startswith('psutil_cygwin')]
        for mod in modules_to_clear:
            del sys.modules[mod]
        
        # This is exactly what the test was trying to do
        import psutil_cygwin as psutil  # This line was failing
        
        # Verify User is accessible
        if hasattr(psutil, 'User'):
            print("   ✓ User namedtuple accessible from package")
            test_user = psutil.User('test', 'tty1', 'localhost', 0, 1234)
            print(f"   ✓ User namedtuple works: {test_user}")
        else:
            print("   ✗ User namedtuple NOT accessible")
            return False
            
        print("\n🎉 ALL TESTS PASSED!")
        print("\nThe import issue has been resolved. You can now run:")
        print("   pytest tests/")
        print("   python tests/test_psutil_cygwin.py")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_cache():
    """Clean up Python cache files"""
    print("🧹 Cleaning Python cache files...")
    
    project_dir = '/home/phdyex/my-repos/psutil-cygwin'
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk(project_dir):
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            try:
                import shutil
                shutil.rmtree(cache_path)
                print(f"   Removed {cache_path}")
            except Exception as e:
                print(f"   Warning: Could not remove {cache_path}: {e}")

if __name__ == "__main__":
    print("psutil-cygwin Import Issue Resolution")
    print("=" * 50)
    
    # Clean cache first
    cleanup_cache()
    
    # Run tests
    success = test_imports()
    
    if success:
        print("\n✅ Resolution successful!")
        sys.exit(0)
    else:
        print("\n❌ Resolution failed!")
        sys.exit(1)
