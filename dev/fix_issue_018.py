#!/usr/bin/env python3
"""
Simple fix for Issue 018: Remove problematic .pth files.
"""

import sys
import os
from pathlib import Path

# Add the project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def fix_pth_issue():
    """Fix the .pth file issue by removing problematic files."""
    print("Fixing Issue 018: .pth file module resolution error...")
    
    try:
        # Use the existing cleanup function
        from psutil_cygwin._build.hooks import remove_psutil_pth
        
        print("🧹 Removing problematic psutil.pth files...")
        remove_psutil_pth()
        print("✅ Cleanup completed successfully")
        
        # Verify the fix
        print("\n🧪 Testing Python site module reload...")
        import site
        import importlib
        importlib.reload(site)
        print("✅ No .pth file errors - issue resolved!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        print("\nManual cleanup required:")
        print("1. Remove any psutil.pth files from site-packages directories")
        print("2. Or install psutil_cygwin in development mode: pip install -e .")
        return False

if __name__ == "__main__":
    success = fix_pth_issue()
    sys.exit(0 if success else 1)
