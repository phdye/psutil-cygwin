#!/usr/bin/env python3
"""
Syntax checker for issue 011 resolution.

This script verifies that the syntax error in test_pth_functionality.py has been fixed.
"""

import ast
import sys
from pathlib import Path


def check_syntax(file_path):
    """Check the syntax of a Python file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse the file to check for syntax errors
        ast.parse(content)
        
        # Count lines
        lines = content.split('\n')
        
        print(f"✅ File syntax is CORRECT")
        print(f"   File: {file_path}")
        print(f"   Lines: {len(lines)}")
        
        # Check for finally statements (the issue was around line 352)
        finally_lines = []
        for i, line in enumerate(lines):
            if line.strip() == 'finally:':
                finally_lines.append(i + 1)
        
        if finally_lines:
            print(f"   'finally:' statements at lines: {finally_lines}")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ SYNTAX ERROR found:")
        print(f"   File: {file_path}")
        print(f"   Line {e.lineno}: {e.text.strip() if e.text else 'Unknown'}")
        print(f"   Error: {e.msg}")
        return False
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


def test_import_statements():
    """Test that the imports in the file work correctly."""
    print("\nTesting import statements...")
    
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        # Test the imports that were causing issues
        from psutil_cygwin.cygwin_check import create_psutil_pth, is_cygwin
        print("✅ Import from psutil_cygwin.cygwin_check successful")
        
        from psutil_cygwin._build.hooks import remove_psutil_pth
        print("✅ Import from psutil_cygwin._build.hooks successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        sys.path.pop(0)


def main():
    """Check syntax and imports for the fixed test file."""
    print("=" * 60)
    print("ISSUE 011 SYNTAX CHECK")
    print("=" * 60)
    
    test_file = Path(__file__).parent.parent / "tests" / "test_pth_functionality.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return 1
    
    # Check syntax
    syntax_ok = check_syntax(test_file)
    
    # Check imports
    imports_ok = test_import_statements()
    
    # Summary
    print("\n" + "=" * 60)
    if syntax_ok and imports_ok:
        print("✅ ISSUE 011 RESOLVED")
        print("")
        print("The syntax error has been fixed:")
        print("• File parses correctly with no syntax errors")
        print("• All import statements work properly")
        print("• Test file should now run with pytest")
        print("")
        print("You can verify with:")
        print("  pytest tests/test_pth_functionality.py --collect-only")
        print("  pytest tests/test_pth_functionality.py -v")
    else:
        print("❌ ISSUE 011 NOT FULLY RESOLVED")
        if not syntax_ok:
            print("• Syntax errors still present")
        if not imports_ok:
            print("• Import errors still present")
    
    return 0 if (syntax_ok and imports_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
