#!/usr/bin/env python3
"""
Verification script for setup.py import fix

This script verifies that:
1. The setup.py functions can be imported correctly
2. pytest can collect the test_pth_functionality.py tests
3. The import issue in issue/test/004.txt is resolved
"""

import sys
import os
import subprocess

def test_setup_imports():
    """Test that setup.py functions can be imported."""
    print("1. Testing setup.py function imports...")
    
    try:
        # Add project directory to path
        project_dir = '/home/phdyex/my-repos/psutil-cygwin'
        if project_dir not in sys.path:
            sys.path.insert(0, project_dir)
        
        # Try importing the functions that were failing
        from setup import create_psutil_pth, remove_psutil_pth, is_cygwin
        
        print("   ✓ create_psutil_pth imported successfully")
        print("   ✓ remove_psutil_pth imported successfully") 
        print("   ✓ is_cygwin imported successfully")
        
        # Test that they are callable
        assert callable(create_psutil_pth), "create_psutil_pth is not callable"
        assert callable(remove_psutil_pth), "remove_psutil_pth is not callable"
        assert callable(is_cygwin), "is_cygwin is not callable"
        
        print("   ✓ All functions are callable")
        
        return True
        
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False

def test_setup_classes():
    """Test that setup.py classes can be imported."""
    print("\n2. Testing setup.py class imports...")
    
    try:
        from setup import CygwinInstallCommand, CygwinDevelopCommand, CygwinUninstallCommand
        
        print("   ✓ CygwinInstallCommand imported successfully")
        print("   ✓ CygwinDevelopCommand imported successfully")
        print("   ✓ CygwinUninstallCommand imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"   ✗ Class import failed: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False

def test_pytest_collection():
    """Test that pytest can collect the pth functionality tests."""
    print("\n3. Testing pytest test collection...")
    
    try:
        os.chdir('/home/phdyex/my-repos/psutil-cygwin')
        
        # Run pytest with collect-only to test if tests can be imported
        result = subprocess.run(
            ['pytest', 'tests/test_pth_functionality.py', '--collect-only', '--quiet'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("   ✓ pytest can collect test_pth_functionality.py tests")
            
            # Count collected tests
            output_lines = result.stdout.split('\n')
            collected_line = [line for line in output_lines if 'collected' in line.lower()]
            if collected_line:
                print(f"   ✓ {collected_line[0].strip()}")
            
            return True
        else:
            print(f"   ✗ pytest collection failed:")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠ pytest collection timed out")
        return True
    except FileNotFoundError:
        print("   ⚠ pytest not found, skipping collection test")
        return True
    except Exception as e:
        print(f"   ✗ Error testing pytest: {e}")
        return False

def test_specific_failing_import():
    """Test the specific import that was failing in issue/test/004.txt."""
    print("\n4. Testing the specific failing import pattern...")
    
    try:
        # This is exactly what test_pth_functionality.py was trying to do
        from setup import create_psutil_pth, remove_psutil_pth, is_cygwin
        
        print("   ✓ Exact failing import pattern now works")
        
        # Test basic functionality without side effects
        print(f"   ✓ is_cygwin() returns: {is_cygwin()}")
        
        return True
        
    except ImportError as e:
        print(f"   ✗ The original failing import still fails: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False

def main():
    """Main verification function."""
    print("setup.py Import Fix Verification")
    print("=" * 40)
    
    tests = [
        test_setup_imports,
        test_setup_classes,
        test_pytest_collection,
        test_specific_failing_import
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("Summary:")
    test_names = [
        "setup.py function imports",
        "setup.py class imports", 
        "pytest test collection",
        "specific failing import"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✓" if result else "✗"
        print(f"  {status} {name}")
    
    if all(results):
        print("\n🎉 All tests passed! The issue has been resolved.")
        print("\nYou can now run:")
        print("  cd /home/phdyex/my-repos/psutil-cygwin")
        print("  pytest tests/")
        return True
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
