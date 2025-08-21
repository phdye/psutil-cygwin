#!/usr/bin/env python3
"""
Simple test to debug the User import issue
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, '/home/phdyex/my-repos/psutil-cygwin')

print("=" * 50)
print("Debugging psutil-cygwin User import issue")
print("=" * 50)

# Test 1: Direct core import
print("\n1. Testing direct core import...")
try:
    from psutil_cygwin.core import User, cpu_percent, Process
    print("   ✓ Direct core imports successful")
    print(f"   User fields: {User._fields}")
    print(f"   Process type: {type(Process)}")
    print(f"   cpu_percent type: {type(cpu_percent)}")
except ImportError as e:
    print(f"   ✗ Direct core import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Core module attributes
print("\n2. Checking core module attributes...")
try:
    from psutil_cygwin import core
    print(f"   Core module loaded: {core}")
    print(f"   Has User: {hasattr(core, 'User')}")
    if hasattr(core, 'User'):
        print(f"   User: {core.User}")
        print(f"   User type: {type(core.User)}")
    
    # List all namedtuples
    namedtuples = []
    for attr in dir(core):
        obj = getattr(core, attr, None)
        if obj and hasattr(obj, '_fields'):
            namedtuples.append(attr)
    print(f"   Namedtuples found: {namedtuples}")
    
except Exception as e:
    print(f"   ✗ Core module inspection failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Package level import
print("\n3. Testing package level import...")
try:
    # Clear any cached imports
    modules_to_clear = [k for k in sys.modules.keys() if k.startswith('psutil_cygwin')]
    for mod in modules_to_clear:
        del sys.modules[mod]
    
    import psutil_cygwin
    print(f"   ✓ Package imported: {psutil_cygwin}")
    print(f"   Has User: {hasattr(psutil_cygwin, 'User')}")
    
    if hasattr(psutil_cygwin, 'User'):
        print(f"   User from package: {psutil_cygwin.User}")
    else:
        print("   Available attributes:")
        attrs = [attr for attr in dir(psutil_cygwin) if not attr.startswith('_')]
        for attr in sorted(attrs):
            print(f"     {attr}")
            
except Exception as e:
    print(f"   ✗ Package import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: __init__.py import list
print("\n4. Checking __init__.py import statement...")
try:
    init_file = '/home/phdyex/my-repos/psutil-cygwin/psutil_cygwin/__init__.py'
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Find the import statement
    import_start = content.find('from .core import (')
    if import_start != -1:
        import_end = content.find(')', import_start)
        if import_end != -1:
            import_section = content[import_start:import_end + 1]
            print("   Import statement found:")
            print(f"   {import_section}")
            
            # Check if User is in the import list
            if 'User,' in import_section or 'User\n' in import_section:
                print("   ✓ User is in the import list")
            else:
                print("   ✗ User is NOT in the import list")
        else:
            print("   ✗ Could not find end of import statement")
    else:
        print("   ✗ Could not find import statement")
        
except Exception as e:
    print(f"   ✗ __init__.py inspection failed: {e}")

print("\n" + "=" * 50)
print("End of diagnostic")
print("=" * 50)
