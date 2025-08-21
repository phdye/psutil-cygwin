#!/usr/bin/env python3
"""
Complete fix for the psutil-cygwin import issue

This script will:
1. Remove all Python cache files
2. Verify the core module is correct
3. Test imports systematically 
4. Provide a working solution
"""

import os
import sys
import shutil
import subprocess

def main():
    """Main fix function"""
    print("🔧 Fixing psutil-cygwin import issue...")
    print("=" * 50)
    
    # Change to project directory
    project_dir = "/home/phdyex/my-repos/psutil-cygwin"
    os.chdir(project_dir)
    print(f"Working in: {project_dir}")
    
    # Step 1: Remove all cache files
    print("\n1. Removing Python cache files...")
    cache_patterns = [
        "**/__pycache__",
        "**/*.pyc", 
        "**/*.pyo",
        ".pytest_cache"
    ]
    
    for pattern in cache_patterns:
        try:
            if pattern.endswith("__pycache__"):
                # Remove __pycache__ directories
                for root, dirs, files in os.walk("."):
                    if "__pycache__" in dirs:
                        cache_path = os.path.join(root, "__pycache__")
                        print(f"   Removing {cache_path}")
                        shutil.rmtree(cache_path)
                        dirs.remove("__pycache__")
            else:
                # Use find command for files
                cmd = f"find . -name '{pattern.replace('**/', '')}' -delete"
                subprocess.run(cmd, shell=True, capture_output=True)
        except Exception as e:
            print(f"   Warning: Could not clean {pattern}: {e}")
    
    # Step 2: Test core module  
    print("\n2. Testing core module...")
    try:
        # Add current directory to path
        if "." not in sys.path:
            sys.path.insert(0, ".")
            
        # Import core and check User
        from psutil_cygwin.core import User, cpu_percent, Process
        print(f"   ✓ Core imports successful")
        print(f"   ✓ User namedtuple: {User._fields}")
        
    except Exception as e:
        print(f"   ✗ Core import failed: {e}")
        return False
    
    # Step 3: Test package import
    print("\n3. Testing package import...")
    try:
        # Clear any cached modules
        modules_to_clear = [k for k in sys.modules.keys() if k.startswith('psutil_cygwin')]
        for mod in modules_to_clear:
            del sys.modules[mod]
        
        # Import package
        import psutil_cygwin as psutil
        print(f"   ✓ Package import successful")
        
        # Test key functions
        funcs_to_test = ['cpu_percent', 'virtual_memory', 'pids', 'User']
        for func in funcs_to_test:
            if hasattr(psutil, func):
                print(f"   ✓ {func} available")
            else:
                print(f"   ✗ {func} missing")
                
    except Exception as e:
        print(f"   ✗ Package import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Test the actual failing test
    print("\n4. Testing pytest import...")
    try:
        # This simulates what the test does
        import psutil_cygwin as psutil
        
        # Test basic functionality
        print(f"   ✓ Package imported as psutil")
        print(f"   ✓ CPU count: {psutil.cpu_count()}")
        
        # Test User namedtuple specifically
        users = psutil.users()
        print(f"   ✓ Users function works: {len(users)} users")
        
        print("   ✓ All tests passed!")
        
    except Exception as e:
        print(f"   ✗ Pytest-style test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Fix completed successfully!")
    print("\nYou can now run:")
    print("  cd /home/phdyex/my-repos/psutil-cygwin")
    print("  pytest tests/")
    print("  # or")
    print("  python tests/test_psutil_cygwin.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
