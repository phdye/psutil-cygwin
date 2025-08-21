#!/usr/bin/env python3
"""
Precise line 352 analysis for issue 014.

This script will examine exactly what's at line 352 and identify the orphaned finally block.
"""

import sys
from pathlib import Path


def analyze_exact_line_352():
    """Analyze the exact content at line 352 and surrounding context."""
    test_file = Path(__file__).parent.parent / "tests" / "test_pth_functionality.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        with open(test_file, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    print(f"File has {len(lines)} lines")
    print(f"Analyzing line 352 and context...")
    
    if len(lines) < 352:
        print(f"❌ File only has {len(lines)} lines, but error is at line 352")
        return False
    
    # Show context around line 352
    start = max(0, 352 - 20)
    end = min(len(lines), 352 + 10)
    
    print(f"\nLines {start+1} to {end}:")
    print("=" * 80)
    
    try_blocks = []
    finally_blocks = []
    
    for i in range(start, end):
        line_num = i + 1
        line = lines[i].rstrip()
        indent = len(lines[i]) - len(lines[i].lstrip())
        
        # Mark the error line
        marker = ""
        if line_num == 352:
            marker = " <<<< ERROR LINE"
        
        # Track control flow statements
        stripped = line.strip()
        if stripped.endswith('try:'):
            try_blocks.append((line_num, indent))
            marker += " [TRY]"
        elif stripped.startswith('except'):
            marker += " [EXCEPT]"
        elif stripped == 'finally:':
            finally_blocks.append((line_num, indent))
            marker += " [FINALLY]"
        elif stripped.startswith('def '):
            marker += " [METHOD]"
        elif stripped.startswith('class '):
            marker += " [CLASS]"
        
        print(f"{line_num:3d}: {line}{marker}")
    
    print("=" * 80)
    
    # Analyze the try/finally pairing
    print(f"\nControl flow analysis:")
    print(f"Try blocks found: {try_blocks}")
    print(f"Finally blocks found: {finally_blocks}")
    
    # Check if line 352 is a finally block
    if len(lines) >= 352:
        line_352_content = lines[351].strip()  # 0-indexed
        print(f"\nLine 352 content: '{line_352_content}'")
        
        if line_352_content == 'finally:':
            print("❌ Line 352 is indeed an orphaned 'finally:' block")
            
            # Find the indentation of this finally
            line_352_full = lines[351]
            finally_indent = len(line_352_full) - len(line_352_full.lstrip())
            print(f"Finally block indentation: {finally_indent} spaces")
            
            # Look for matching try blocks
            matching_tries = []
            for try_line, try_indent in try_blocks:
                if try_indent == finally_indent:
                    matching_tries.append((try_line, try_indent))
            
            if matching_tries:
                print(f"Possible matching try blocks at same indent level: {matching_tries}")
            else:
                print("❌ No try blocks found at the same indentation level")
                print("This confirms the finally block is orphaned")
        else:
            print(f"Line 352 contains: '{line_352_content}' - not a finally block")
    
    return True


def suggest_specific_fix():
    """Suggest a specific fix for the orphaned finally block."""
    print(f"\n" + "=" * 80)
    print("SPECIFIC FIX REQUIRED")
    print("=" * 80)
    
    print("The issue is that line 352 contains 'finally:' without a matching 'try:' block.")
    print("")
    print("To fix this, you need to either:")
    print("1. Add a 'try:' block before the 'finally:' at the same indentation")
    print("2. Remove the orphaned 'finally:' block if it's not needed")
    print("3. Move the 'finally:' content to an existing try/finally structure")
    print("")
    print("Example fix:")
    print("```python")
    print("# BEFORE (broken):")
    print("def some_method(self):")
    print("    # some code")
    print("    finally:  # <- orphaned")
    print("        cleanup()")
    print("")
    print("# AFTER (fixed):")
    print("def some_method(self):")
    print("    try:")
    print("        # some code")
    print("    finally:")
    print("        cleanup()")
    print("```")


def main():
    """Main analysis function."""
    print("Analyzing Issue 014: Persistent Orphaned Finally Block")
    
    success = analyze_exact_line_352()
    
    if success:
        suggest_specific_fix()
    
    print(f"\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    if success:
        print("✅ Analysis completed - identified orphaned finally block location")
        print("💡 Use the suggested fix to resolve the syntax error")
    else:
        print("❌ Analysis failed - could not examine file structure")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
