#!/usr/bin/env python3
"""
Script to fix the import issue with psutil-cygwin

This script will:
1. Clear the Python bytecode cache
2. Test imports systematically
3. Identify any import conflicts
"""

import os
import sys
import shutil
import importlib


def clear_cache():
    """Clear Python bytecode cache"""
    print("Clearing Python bytecode cache...")
    
    cache_dirs = [
        'psutil_cygwin/__pycache__',
        'tests/__pycache__',
        '__pycache__'
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            print(f"  Removing {cache_dir}")
            shutil.rmtree(cache_dir)
        else:
            print(f"  {cache_dir} not found")


def test_core_import():
    """Test importing core module directly"""
    print("\nTesting core module import...")
    
    try:
        # Add current directory to path
        if '.' not in sys.path:
            sys.path.insert(0, '.')
        
        # Try importing core module directly
        from psutil_cygwin import core
        print("✓ Core module imported successfully")
        
        # Test that User is defined
        if hasattr(core, 'User'):
            print("✓ User namedtuple found in core module")
            print(f"  User fields: {core.User._fields}")
        else:
            print("✗ User namedtuple NOT found in core module")
            print(f"  Available attributes: {[attr for attr in dir(core) if not attr.startswith('_')]}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Core import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_init_import():
    """Test importing via __init__.py"""
    print("\nTesting __init__.py import...")
    
    try:
        # Clear any existing imports
        if 'psutil_cygwin' in sys.modules:
            del sys.modules['psutil_cygwin']
        if 'psutil_cygwin.core' in sys.modules:
            del sys.modules['psutil_cygwin.core']
        
        # Try importing the package
        import psutil_cygwin
        print("✓ psutil_cygwin package imported successfully")
        
        # Test that User is accessible
        if hasattr(psutil_cygwin, 'User'):
            print("✓ User namedtuple accessible from package")
        else:
            print("✗ User namedtuple NOT accessible from package")
            print(f"  Available attributes: {[attr for attr in dir(psutil_cygwin) if not attr.startswith('_')]}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Package import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specific_imports():
    """Test importing specific items"""
    print("\nTesting specific imports...")
    
    success = True
    
    try:
        from psutil_cygwin.core import User
        print("✓ User imported directly from core")
    except ImportError as e:
        print(f"✗ Direct User import failed: {e}")
        success = False
    
    try:
        from psutil_cygwin.core import cpu_percent
        print("✓ cpu_percent imported from core")
    except ImportError as e:
        print(f"✗ cpu_percent import failed: {e}")
        success = False
    
    try:
        from psutil_cygwin.core import Process
        print("✓ Process imported from core")
    except ImportError as e:
        print(f"✗ Process import failed: {e}")
        success = False
    
    return success


def inspect_core_module():
    """Inspect the core module to see what's actually defined"""
    print("\nInspecting core module contents...")
    
    try:
        from psutil_cygwin import core
        
        # Get all public attributes
        public_attrs = [attr for attr in dir(core) if not attr.startswith('_')]
        print(f"Public attributes in core: {len(public_attrs)}")
        
        # Group by type
        classes = []
        functions = []
        namedtuples = []
        other = []
        
        for attr in public_attrs:
            obj = getattr(core, attr)
            if hasattr(obj, '__bases__') and Exception in obj.__mro__:
                classes.append(attr)
            elif callable(obj):
                functions.append(attr)
            elif hasattr(obj, '_fields'):  # namedtuple check
                namedtuples.append(attr)
            else:
                other.append(attr)
        
        print(f"  Classes (exceptions): {classes}")
        print(f"  Functions: {functions}")
        print(f"  NamedTuples: {namedtuples}")
        print(f"  Other: {other}")
        
        # Specifically check for User
        if 'User' in namedtuples:
            User = getattr(core, 'User')
            print(f"  User namedtuple fields: {User._fields}")
        
        return True
        
    except Exception as e:
        print(f"✗ Inspection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main diagnostic function"""
    print("psutil-cygwin Import Issue Diagnostic")
    print("=" * 40)
    
    # Change to the project directory
    os.chdir('/home/phdyex/my-repos/psutil-cygwin')
    print(f"Working directory: {os.getcwd()}")
    
    # Step 1: Clear cache
    clear_cache()
    
    # Step 2: Test core import
    core_ok = test_core_import()
    
    # Step 3: Inspect core module
    inspect_ok = inspect_core_module()
    
    # Step 4: Test specific imports
    specific_ok = test_specific_imports()
    
    # Step 5: Test package import
    package_ok = test_init_import()
    
    print("\n" + "=" * 40)
    print("Summary:")
    print(f"  Core import: {'✓' if core_ok else '✗'}")
    print(f"  Core inspection: {'✓' if inspect_ok else '✗'}")
    print(f"  Specific imports: {'✓' if specific_ok else '✗'}")
    print(f"  Package import: {'✓' if package_ok else '✗'}")
    
    if all([core_ok, inspect_ok, specific_ok, package_ok]):
        print("\n✓ All tests passed! Import issue should be resolved.")
        print("You can now run the tests with: pytest tests/")
    else:
        print("\n✗ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()
