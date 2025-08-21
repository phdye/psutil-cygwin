#!/usr/bin/env python3
"""
Test script to verify that issue 009 is resolved.

This script tests that the imports in test_pth_functionality.py work correctly
after the modernization changes.
"""

import sys
from pathlib import Path

# Add the package to the path for testing
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all imports in the updated test file work correctly."""
    print("Testing imports after modernization...")
    
    try:
        # Test the new import locations
        from psutil_cygwin.cygwin_check import create_psutil_pth, is_cygwin
        print("✅ Successfully imported from psutil_cygwin.cygwin_check")
        
        from psutil_cygwin._build.hooks import remove_psutil_pth
        print("✅ Successfully imported from psutil_cygwin._build.hooks")
        
        # Test that the functions are callable
        assert callable(create_psutil_pth), "create_psutil_pth is not callable"
        assert callable(is_cygwin), "is_cygwin is not callable"
        assert callable(remove_psutil_pth), "remove_psutil_pth is not callable"
        print("✅ All imported functions are callable")
        
        # Test that we can call is_cygwin without errors
        cygwin_detected = is_cygwin()
        print(f"✅ is_cygwin() returned: {cygwin_detected}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_pytest_collection():
    """Test that pytest can collect the test file without errors."""
    print("\nTesting pytest collection...")
    
    import subprocess
    
    try:
        # Run pytest --collect-only on the specific test file
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_pth_functionality.py", 
            "--collect-only", "-q"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ pytest can collect tests without import errors")
            return True
        else:
            print("❌ pytest collection failed:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Issue 009 Fix: Import Errors After Modernization")
    print("=" * 60)
    
    success = True
    
    # Test 1: Import resolution
    if not test_imports():
        success = False
    
    # Test 2: Pytest collection
    if not test_pytest_collection():
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ ISSUE 009 RESOLVED")
        print("")
        print("All imports work correctly after modernization:")
        print("• create_psutil_pth from psutil_cygwin.cygwin_check")
        print("• is_cygwin from psutil_cygwin.cygwin_check") 
        print("• remove_psutil_pth from psutil_cygwin._build.hooks")
        print("")
        print("The test file should now run without import errors.")
        print("You can verify with: pytest tests/test_pth_functionality.py")
    else:
        print("❌ ISSUE 009 NOT FULLY RESOLVED")
        print("Some imports or tests are still failing.")
        print("Check the output above for specific errors.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
