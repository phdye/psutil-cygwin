#!/usr/bin/env python3
"""
Find the orphaned finally block in issue 013.

This script will locate the specific finally block that's not part of a proper try/except structure.
"""

import sys
from pathlib import Path


def find_orphaned_finally():
    """Find the orphaned finally block causing the syntax error."""
    print("=" * 60)
    print("FINDING ORPHANED FINALLY BLOCK - ISSUE 013")
    print("=" * 60)
    
    test_file = Path(__file__).parent.parent / "tests" / "test_pth_functionality.py"
    
    try:
        with open(test_file, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    print(f"File has {len(lines)} lines")
    print(f"Error is at line 352")
    
    # Show lines around 352
    print(f"\nContext around line 352:")
    start_line = max(0, 352 - 10)
    end_line = min(len(lines), 352 + 10)
    
    for i in range(start_line, end_line):
        line_num = i + 1
        line = lines[i].rstrip()
        indicator = " --> ERROR" if line_num == 352 else ""
        print(f"{line_num:3d}: {line}{indicator}")
    
    # Find all try/except/finally blocks
    print(f"\n" + "=" * 60)
    print("ANALYZING TRY/EXCEPT/FINALLY STRUCTURE")
    print("=" * 60)
    
    block_stack = []
    issues = []
    
    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        
        # Track try blocks
        if stripped.endswith('try:'):
            block_stack.append({
                'type': 'try',
                'line': line_num,
                'indent': indent,
                'has_except': False,
                'has_finally': False
            })
            print(f"Line {line_num}: Found try: block (indent {indent})")
        
        # Track except blocks
        elif stripped.startswith('except') and stripped.endswith(':'):
            if block_stack and block_stack[-1]['type'] == 'try':
                block_stack[-1]['has_except'] = True
                print(f"Line {line_num}: Found except: block for try at line {block_stack[-1]['line']}")
            else:
                issues.append(f"Line {line_num}: except: without matching try:")
        
        # Track finally blocks - THIS IS THE KEY CHECK
        elif stripped == 'finally:':
            print(f"Line {line_num}: Found finally: block (indent {indent})")
            
            # Check if there's a matching try/except structure
            matching_try = None
            for block in reversed(block_stack):
                if block['type'] == 'try' and block['indent'] == indent:
                    matching_try = block
                    break
            
            if matching_try:
                matching_try['has_finally'] = True
                print(f"  ✅ Matches try: at line {matching_try['line']}")
            else:
                issues.append(f"Line {line_num}: ORPHANED finally: block (no matching try: at same indent level)")
                print(f"  ❌ ORPHANED finally: block!")
                
                # Show what try blocks are available
                if block_stack:
                    print("    Available try blocks:")
                    for block in block_stack:
                        print(f"      Line {block['line']}: indent {block['indent']}")
                else:
                    print("    No try blocks available")
        
        # Close blocks when we hit method/class definitions
        elif stripped.startswith('def ') or stripped.startswith('class '):
            # Close any open blocks at this level or deeper
            block_stack = [b for b in block_stack if b['indent'] < indent]
    
    # Report issues
    print(f"\n" + "=" * 60)
    print("ISSUES FOUND")
    print("=" * 60)
    
    if issues:
        for issue in issues:
            print(f"❌ {issue}")
    else:
        print("✅ No structural issues found")
    
    return len(issues) == 0


def suggest_fix():
    """Suggest how to fix the orphaned finally block."""
    print(f"\n" + "=" * 60)
    print("SUGGESTED FIX")
    print("=" * 60)
    
    print("The issue is an orphaned 'finally:' block that's not part of a try/except structure.")
    print("")
    print("Python syntax requires:")
    print("1. finally: must be paired with a try: at the same indentation level")
    print("2. A try: block can have:")
    print("   - try: + except: + finally:")
    print("   - try: + finally: (without except)")
    print("   - try: + except: (without finally)")
    print("")
    print("To fix:")
    print("1. Find the orphaned 'finally:' at line 352")
    print("2. Either:")
    print("   a) Add a matching 'try:' block before it")
    print("   b) Remove the orphaned 'finally:' if it's not needed")
    print("   c) Move the 'finally:' to be part of an existing try block")


def main():
    """Main analysis function."""
    success = find_orphaned_finally()
    suggest_fix()
    
    print(f"\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    if success:
        print("✅ No structural issues found in try/except/finally blocks")
    else:
        print("❌ Found orphaned finally: block(s) that need to be fixed")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
