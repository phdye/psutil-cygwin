#!/usr/bin/env python3
"""
Find the exact method with the orphaned finally block that needs the try: fix.
"""

import sys
from pathlib import Path


def find_method_with_orphaned_finally():
    """Find which method has the orphaned finally block at line 352."""
    test_file = Path(__file__).parent.parent / "tests" / "test_pth_functionality.py"
    
    try:
        with open(test_file, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"File has {len(lines)} lines")
    print(f"Looking for the method containing line 352...")
    
    # Find the method containing line 352
    method_start = None
    current_method = None
    
    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        
        # Track method definitions
        if stripped.startswith('def '):
            method_start = line_num
            current_method = stripped
            
        # When we hit line 352, show the context
        if line_num == 352:
            print(f"\nLine 352 (the error): '{stripped}'")
            print(f"Current method: {current_method}")
            print(f"Method started at line: {method_start}")
            
            # Show the full method context
            print(f"\nMethod context (lines {method_start}-{line_num+5}):")
            start = max(0, method_start - 1)  # 0-indexed
            end = min(len(lines), line_num + 5)
            
            for j in range(start, end):
                context_line_num = j + 1
                context_line = lines[j].rstrip()
                marker = " <-- ERROR" if context_line_num == 352 else ""
                method_marker = " <-- METHOD START" if context_line_num == method_start else ""
                print(f"{context_line_num:3d}: {context_line}{marker}{method_marker}")
            
            break
    
    # Analyze what should be fixed
    print(f"\n" + "="*60)
    print("ANALYSIS: What needs to be fixed")
    print("="*60)
    
    print("The user correctly identified that this method needs:")
    print("1. A 'try:' statement added at the beginning of the method")
    print("2. All code before the 'finally:' indented to be inside the try block")
    print("3. The 'finally:' block undoes the action of the first line of the method")
    print("\nThis creates proper try/finally structure where:")
    print("- try: contains the main method logic")
    print("- finally: contains cleanup that undoes the setup from the first line")


if __name__ == "__main__":
    find_method_with_orphaned_finally()
