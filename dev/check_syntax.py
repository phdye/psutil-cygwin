#!/usr/bin/env python3
"""
Check for syntax errors in core.py
"""

import ast
import sys

def check_syntax():
    """Check syntax of core.py"""
    core_file = '/home/phdyex/my-repos/psutil-cygwin/psutil_cygwin/core.py'
    
    try:
        with open(core_file, 'r') as f:
            source = f.read()
        
        # Try to parse the AST
        tree = ast.parse(source, filename=core_file)
        print("✓ core.py syntax is valid")
        
        # Check for User namedtuple definition
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'User':
                        print("✓ User namedtuple assignment found in AST")
                        return True
        
        print("✗ User namedtuple assignment NOT found in AST")
        return False
        
    except SyntaxError as e:
        print(f"✗ Syntax error in core.py: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"✗ Error checking syntax: {e}")
        return False

def try_exec():
    """Try to execute core.py and capture any runtime errors"""
    core_file = '/home/phdyex/my-repos/psutil-cygwin/psutil_cygwin/core.py'
    
    try:
        with open(core_file, 'r') as f:
            source = f.read()
        
        # Create a namespace to execute in
        namespace = {}
        
        # Execute the code
        exec(source, namespace)
        
        if 'User' in namespace:
            print(f"✓ User defined successfully: {namespace['User']}")
            return True
        else:
            print("✗ User not found in execution namespace")
            print(f"   Available namedtuples: {[k for k, v in namespace.items() if hasattr(v, '_fields')]}")
            return False
            
    except Exception as e:
        print(f"✗ Runtime error executing core.py: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Checking core.py...")
    syntax_ok = check_syntax()
    exec_ok = try_exec()
    
    if syntax_ok and exec_ok:
        print("\n✓ core.py appears to be working correctly")
        print("The import issue might be elsewhere")
    else:
        print("\n✗ Found issues in core.py")
