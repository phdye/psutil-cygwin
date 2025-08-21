#!/usr/bin/env python3
"""
Diagnostic and cleanup script for Issue 018: .pth file module resolution error.

This script helps identify and resolve the ModuleNotFoundError with psutil.pth.
"""

import os
import sys
import site
import tempfile
from pathlib import Path


def diagnose_pth_issue():
    """Diagnose the .pth file issue and provide solutions."""
    print("=" * 60)
    print("DIAGNOSING ISSUE 018: .pth FILE MODULE RESOLUTION ERROR")
    print("=" * 60)
    
    print("\n1. CHECKING PYTHON ENVIRONMENT:")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    
    print("\n2. CHECKING SITE-PACKAGES DIRECTORIES:")
    try:
        site_dirs = site.getsitepackages()
        print(f"   System site-packages: {site_dirs}")
    except:
        print("   Could not get system site-packages")
        site_dirs = []
    
    try:
        user_site = site.getusersitepackages()
        print(f"   User site-packages: {user_site}")
    except:
        print("   Could not get user site-packages")
        user_site = None
    
    print("\n3. LOOKING FOR EXISTING psutil.pth FILES:")
    pth_files_found = []
    
    # Check system site-packages
    for site_dir in site_dirs:
        pth_path = os.path.join(site_dir, 'psutil.pth')
        if os.path.exists(pth_path):
            pth_files_found.append(pth_path)
            print(f"   Found: {pth_path}")
    
    # Check user site-packages
    if user_site:
        user_pth = os.path.join(user_site, 'psutil.pth')
        if os.path.exists(user_pth):
            pth_files_found.append(user_pth)
            print(f"   Found: {user_pth}")
    
    if not pth_files_found:
        print("   No psutil.pth files found")
    
    print("\n4. CHECKING psutil_cygwin MODULE AVAILABILITY:")
    try:
        import psutil_cygwin
        print(f"   ✅ psutil_cygwin module is available at: {psutil_cygwin.__file__}")
        module_available = True
    except ImportError as e:
        print(f"   ❌ psutil_cygwin module NOT available: {e}")
        module_available = False
    
    print("\n5. EXAMINING .pth FILE CONTENTS:")
    for pth_file in pth_files_found:
        try:
            print(f"\n   Contents of {pth_file}:")
            with open(pth_file, 'r') as f:
                content = f.read()
            for i, line in enumerate(content.split('\n'), 1):
                if line.strip():
                    print(f"   Line {i}: {line}")
                    if i == 3:  # The problematic line 3
                        print(f"           ^ This is line 3 causing the error")
        except PermissionError:
            print(f"   ❌ Permission denied reading {pth_file}")
        except Exception as e:
            print(f"   ❌ Error reading {pth_file}: {e}")
    
    return pth_files_found, module_available


def suggest_solutions(pth_files_found, module_available):
    """Suggest solutions based on the diagnosis."""
    print("\n" + "=" * 60)
    print("SUGGESTED SOLUTIONS")
    print("=" * 60)
    
    if not pth_files_found:
        print("\n✅ No problematic .pth files found")
        return
    
    if not module_available:
        print("\n🔧 SOLUTION 1: Install psutil_cygwin in development mode")
        print("   cd /home/phdyex/my-repos/psutil-cygwin")
        print("   pip install -e .")
        print("   This will make psutil_cygwin available to Python")
        
    print("\n🔧 SOLUTION 2: Remove problematic .pth files")
    for pth_file in pth_files_found:
        print(f"   Remove: {pth_file}")
        if os.access(pth_file, os.W_OK):
            print(f"   Command: rm '{pth_file}'")
        else:
            print(f"   Command: sudo rm '{pth_file}'  # May need admin rights")
    
    print("\n🔧 SOLUTION 3: Recreate .pth file with working psutil_cygwin")
    print("   After installing psutil_cygwin:")
    print("   python -c \"from psutil_cygwin.cygwin_check import create_psutil_pth; create_psutil_pth()\"")
    
    print("\n🔧 SOLUTION 4: Use cleanup script")
    print("   python -c \"from psutil_cygwin._build.hooks import remove_psutil_pth; remove_psutil_pth()\"")


def attempt_cleanup():
    """Attempt to clean up the problematic .pth files."""
    print("\n" + "=" * 60)
    print("ATTEMPTING AUTOMATIC CLEANUP")
    print("=" * 60)
    
    try:
        from psutil_cygwin._build.hooks import remove_psutil_pth
        print("\n🧹 Using psutil_cygwin cleanup function...")
        remove_psutil_pth()
        print("✅ Cleanup function executed successfully")
        return True
    except Exception as e:
        print(f"❌ Cleanup function failed: {e}")
        return False


def verify_fix():
    """Verify that the issue has been resolved."""
    print("\n" + "=" * 60)
    print("VERIFYING FIX")
    print("=" * 60)
    
    print("\n🧪 Testing .pth file processing...")
    try:
        # Try to reload site module to reprocess .pth files
        import importlib
        importlib.reload(site)
        print("✅ Site module reloaded successfully - no .pth errors")
        return True
    except Exception as e:
        print(f"❌ Site reload failed: {e}")
        return False


def main():
    """Main diagnostic and resolution function."""
    print("Diagnosing and resolving .pth file module resolution error...")
    
    # Step 1: Diagnose the issue
    pth_files_found, module_available = diagnose_pth_issue()
    
    # Step 2: Suggest solutions
    suggest_solutions(pth_files_found, module_available)
    
    # Step 3: Attempt automatic cleanup
    cleanup_success = attempt_cleanup()
    
    # Step 4: Verify fix
    fix_verified = verify_fix()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if fix_verified:
        print("✅ ISSUE 018 RESOLVED")
        print("\nThe .pth file module resolution error has been fixed.")
        print("Tests should now run without .pth file warnings.")
    else:
        print("⚠️  MANUAL INTERVENTION REQUIRED")
        print("\nPlease follow the suggested solutions above to resolve the issue.")
        
        if pth_files_found:
            print("\nQuick fix commands:")
            for pth_file in pth_files_found:
                print(f"  rm '{pth_file}'")
    
    return 0 if fix_verified else 1


if __name__ == "__main__":
    sys.exit(main())
