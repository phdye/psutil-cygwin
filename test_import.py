#!/usr/bin/env python3
"""
Quick test to verify import is working
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing psutil_cygwin import...")

try:
    import psutil_cygwin as psutil
    print("✅ SUCCESS: Import worked!")
    
    # Test basic functionality
    print(f"📊 Available functions: {len([x for x in dir(psutil) if not x.startswith('_')])}")
    
    # Test some basic calls
    try:
        cpu_count = psutil.cpu_count()
        print(f"🖥️  CPU count: {cpu_count}")
    except Exception as e:
        print(f"⚠️  CPU count error: {e}")
    
    try:
        pids = psutil.pids()
        print(f"⚙️  Process count: {len(pids)}")
    except Exception as e:
        print(f"⚠️  Process count error: {e}")
    
    try:
        mem = psutil.virtual_memory()
        print(f"💾 Memory: {mem.percent:.1f}% used")
    except Exception as e:
        print(f"⚠️  Memory error: {e}")
    
    print("✅ Basic functionality test passed!")
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ RUNTIME ERROR: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")
