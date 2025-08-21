#!/usr/bin/env python3
"""
Quick syntax verification for issue 012.
"""

import ast
import sys
from pathlib import Path

def verify_syntax():
    """Verify the test file syntax is correct."""
    test_file = Path(__file__).parent.parent / "tests" / "test_pth_functionality.py"
    
    print(f"Checking syntax of: {test_file}")
    
    try:
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Parse the file
        ast.parse(content)
        
        lines = content.split('\n')
        print(f"✅ File syntax is CORRECT")
        print(f"   Lines: {len(lines)}")
        print(f"   File parses successfully with Python AST")
        
        # Check for finally statements
        finally_count = sum(1 for line in lines if line.strip() == 'finally:')
        print(f"   'finally:' statements found: {finally_count}")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ SYNTAX ERROR:")
        print(f"   Line {e.lineno}: {e.msg}")
        print(f"   Text: {e.text.strip() if e.text else 'N/A'}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = verify_syntax()
    print(f"\nResult: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)
