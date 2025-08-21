#!/usr/bin/env python3
"""
Diagnostic script for issue 010: Understanding why tests are being skipped on Cygwin.

This script investigates:
1. Why the transparent import test is skipped
2. Whether the .pth file is properly configured
3. What version of psutil is being imported
"""

import os
import sys
import site
from pathlib import Path

# Add the package to the path for testing
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check the Cygwin environment."""
    print("=" * 60)
    print("CYGWIN ENVIRONMENT CHECK")
    print("=" * 60)
    
    print(f"Operating System: {os.name}")
    print(f"Platform: {sys.platform}")
    
    import platform
    print(f"Platform system: {platform.system()}")
    print(f"Platform release: {platform.release()}")
    
    print(f"/proc exists: {os.path.exists('/proc')}")
    print(f"Python executable: {sys.executable}")
    
    # Check for Cygwin indicators
    cygwin_vars = ['CYGWIN', 'CYGWIN_ROOT']
    print("Cygwin environment variables:")
    for var in cygwin_vars:
        value = os.environ.get(var, 'Not set')
        print(f"  {var}: {value}")
    
    # Test our is_cygwin function
    try:
        from psutil_cygwin.cygwin_check import is_cygwin
        cygwin_detected = is_cygwin()
        print(f"is_cygwin() result: {cygwin_detected}")
    except Exception as e:
        print(f"Error checking is_cygwin(): {e}")


def check_pth_file_status():
    """Check if psutil.pth file exists and is configured correctly."""
    print("\n" + "=" * 60)
    print("PTH FILE STATUS CHECK")
    print("=" * 60)
    
    # Get site-packages directories
    try:
        site_packages_dirs = site.getsitepackages()
        user_site = site.getusersitepackages()
        all_site_dirs = site_packages_dirs + [user_site]
    except Exception as e:
        print(f"Error getting site-packages directories: {e}")
        return False
    
    print("Site-packages directories:")
    for sp_dir in all_site_dirs:
        print(f"  {sp_dir}")
        if sp_dir and os.path.exists(sp_dir):
            print(f"    Exists: Yes, Writable: {os.access(sp_dir, os.W_OK)}")
        else:
            print(f"    Exists: No")
    
    # Check for psutil.pth file
    pth_found = False
    for sp_dir in all_site_dirs:
        if not sp_dir or not os.path.exists(sp_dir):
            continue
            
        pth_file = os.path.join(sp_dir, 'psutil.pth')
        if os.path.exists(pth_file):
            pth_found = True
            print(f"\n✅ Found psutil.pth: {pth_file}")
            
            try:
                with open(pth_file, 'r') as f:
                    content = f.read()
                print(f"Content:\n{content}")
                
                # Check if it's our file
                if 'psutil_cygwin' in content:
                    print("✅ This is our psutil-cygwin .pth file")
                else:
                    print("⚠️  This is not our psutil-cygwin .pth file")
                    
            except Exception as e:
                print(f"Error reading .pth file: {e}")
    
    if not pth_found:
        print("❌ No psutil.pth file found")
        print("   Transparent import will not work")
        print("   Run: psutil-cygwin-setup install")
    
    return pth_found


def check_psutil_import():
    """Check what happens when we import psutil."""
    print("\n" + "=" * 60)
    print("PSUTIL IMPORT CHECK")
    print("=" * 60)
    
    # Clean slate
    if 'psutil' in sys.modules:
        del sys.modules['psutil']
    
    # First, check if psutil_cygwin is available
    try:
        import psutil_cygwin
        print("✅ psutil_cygwin is available")
        print(f"   Module: {psutil_cygwin}")
        print(f"   File: {getattr(psutil_cygwin, '__file__', 'Unknown')}")
    except ImportError as e:
        print(f"❌ psutil_cygwin not available: {e}")
        print("   Package may not be installed in development mode")
        return False
    
    # Now try importing psutil
    try:
        import psutil
        print("✅ psutil import successful")
        print(f"   Module name: {getattr(psutil, '__name__', 'Unknown')}")
        print(f"   Module: {psutil}")
        print(f"   File: {getattr(psutil, '__file__', 'Unknown')}")
        
        # Check if it's our psutil_cygwin
        if hasattr(psutil, '__name__') and psutil.__name__ == 'psutil_cygwin':
            print("✅ SUCCESS: Transparent import is working!")
            print("   'import psutil' is using psutil_cygwin")
            
            # Test basic functionality
            try:
                cpu_count = psutil.cpu_count()
                print(f"   Basic test - CPU count: {cpu_count}")
                return True
            except Exception as e:
                print(f"   ⚠️  Basic functionality test failed: {e}")
                return False
                
        else:
            print("⚠️  Standard psutil detected, not psutil-cygwin")
            print("   Transparent import is not active")
            return False
            
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")
        print("   No psutil available (standard or psutil-cygwin)")
        return False


def suggest_solutions():
    """Suggest solutions for the identified issues."""
    print("\n" + "=" * 60)
    print("SUGGESTED SOLUTIONS")
    print("=" * 60)
    
    # Check current state
    pth_exists = check_pth_file_status()
    import_works = check_psutil_import()
    
    if not pth_exists:
        print("\n🔧 To fix transparent import:")
        print("1. pip install -e .  # Install in development mode")
        print("2. psutil-cygwin-setup install  # Create .pth file")
        print("3. pytest tests/test_pth_functionality.py -v  # Test")
    
    if pth_exists and not import_works:
        print("\n🔧 .pth file exists but import not working:")
        print("1. Check .pth file content is correct")
        print("2. Restart Python session")
        print("3. Check for conflicting standard psutil installation")
        print("4. pip uninstall psutil  # Remove standard psutil if present")
    
    if import_works:
        print("\n✅ Everything looks good!")
        print("The test skip might be due to test logic issues.")
        print("Updated test should now work correctly.")


def main():
    """Run all diagnostic checks."""
    print("Diagnosing Issue 010: Why tests are skipped on Cygwin")
    print("This script will help understand the transparent import setup.")
    
    try:
        check_environment()
        check_pth_file_status()
        check_psutil_import()
        suggest_solutions()
        
        print("\n" + "=" * 60)
        print("DIAGNOSIS COMPLETE")
        print("=" * 60)
        print("If transparent import is not working:")
        print("1. Run: pip install -e .")
        print("2. Run: psutil-cygwin-setup install") 
        print("3. Run: pytest tests/test_pth_functionality.py -v")
        print("")
        print("The updated test file should now handle these cases better.")
        
    except Exception as e:
        print(f"\nError during diagnosis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
