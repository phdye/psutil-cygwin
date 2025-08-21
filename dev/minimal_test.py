#!/usr/bin/env python3
"""
Minimal test to isolate the User import issue
"""

import sys
import os

# Add the project to the path
project_path = '/home/phdyex/my-repos/psutil-cygwin'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

print("Testing core module imports step by step...")

try:
    print("1. Importing core module...")
    from psutil_cygwin import core
    print("   ✓ Core module imported successfully")
    
    print("2. Checking if User exists in core...")
    if hasattr(core, 'User'):
        User = getattr(core, 'User')
        print(f"   ✓ User found: {User}")
        print(f"   ✓ User fields: {User._fields}")
    else:
        print("   ✗ User NOT found in core module")
        print("   Available namedtuples in core:")
        for attr_name in dir(core):
            attr = getattr(core, attr_name)
            if hasattr(attr, '_fields'):
                print(f"     {attr_name}: {attr._fields}")
    
    print("3. Testing direct User import...")
    try:
        from psutil_cygwin.core import User
        print(f"   ✓ Direct User import successful: {User}")
    except ImportError as e:
        print(f"   ✗ Direct User import failed: {e}")
    
    print("4. Testing multiple imports...")
    try:
        from psutil_cygwin.core import User, CPUTimes, Process
        print("   ✓ Multiple imports successful")
    except ImportError as e:
        print(f"   ✗ Multiple imports failed: {e}")
        
        # Try importing them one by one
        for item in ['User', 'CPUTimes', 'Process']:
            try:
                exec(f"from psutil_cygwin.core import {item}")
                print(f"     ✓ {item} imported successfully")
            except ImportError as ie:
                print(f"     ✗ {item} import failed: {ie}")

except ImportError as e:
    print(f"✗ Core module import failed: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone.")
