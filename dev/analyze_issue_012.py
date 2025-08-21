#!/usr/bin/env python3
"""
Analyze the syntax error in issue 012.

This script will carefully examine the test file to find the exact source 
of the syntax error at line 352.
"""

import ast
import sys
from pathlib import Path


def analyze_syntax_error():
    """Analyze the syntax error in detail."""
    print("=" * 60)
    print("ANALYZING ISSUE 012: SYNTAX ERROR AT LINE 352")
    print("=" * 60)
    
    test_file = Path(__file__).parent.parent / "tests" / "test_pth_functionality.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    # Read the file
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Split into lines
    lines = content.split('\n')
    print(f"File has {len(lines)} lines")
    
    # Look around line 352
    print(f"\nLines around 352:")
    for i in range(345, 360):
        if i < len(lines):
            line_num = i + 1
            line = lines[i]
            marker = "👈 ERROR LINE" if line_num == 352 else ""
            print(f"{line_num:3d}: '{line}' {marker}")
    
    # Find all finally statements
    finally_lines = []
    for i, line in enumerate(lines):
        if line.strip() == 'finally:':
            finally_lines.append(i + 1)
    
    if finally_lines:
        print(f"\nFound 'finally:' statements at lines: {finally_lines}")
    
    # Try to parse the file and get specific error details
    try:
        ast.parse(content)
        print("✅ File parses correctly - no syntax errors found!")
        return True
    except SyntaxError as e:
        print(f"\n❌ SYNTAX ERROR DETAILS:")
        print(f"   Line: {e.lineno}")
        print(f"   Column: {e.offset}")
        print(f"   Message: {e.msg}")
        if e.text:
            print(f"   Text: '{e.text.rstrip()}'")
            
        # Show context around the error
        if e.lineno and e.lineno <= len(lines):
            print(f"\nContext around line {e.lineno}:")
            start = max(0, e.lineno - 5)
            end = min(len(lines), e.lineno + 5)
            
            for i in range(start, end):
                line_num = i + 1
                line = lines[i]
                marker = " --> " if line_num == e.lineno else "     "
                print(f"{marker}{line_num:3d}: {line}")
        
        return False


def check_encoding_issues():
    """Check for encoding or hidden character issues."""
    print("\n" + "=" * 60)
    print("CHECKING FOR ENCODING ISSUES")
    print("=" * 60)
    
    test_file = Path(__file__).parent.parent / "tests" / "test_pth_functionality.py"
    
    try:
        # Try reading with different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(test_file, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✅ Successfully read with {encoding}")
                
                # Check for unusual characters
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    # Check for non-printable characters
                    for j, char in enumerate(line):
                        if ord(char) > 127 or (ord(char) < 32 and char not in ['\t']):
                            print(f"⚠️  Non-ASCII character at line {i+1}, column {j+1}: {repr(char)}")
                
                break
                
            except UnicodeDecodeError:
                print(f"❌ Failed to read with {encoding}")
                
    except Exception as e:
        print(f"❌ Error checking encodings: {e}")


def try_manual_fix():
    """Try to identify and fix the specific issue."""
    print("\n" + "=" * 60)
    print("ATTEMPTING MANUAL FIX")
    print("=" * 60)
    
    test_file = Path(__file__).parent.parent / "tests" / "test_pth_functionality.py"
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Look for structural issues around line 352
        if len(lines) >= 352:
            problem_line = lines[351]  # 0-indexed
            print(f"Line 352 content: '{problem_line}'")
            print(f"Line 352 repr: {repr(problem_line)}")
            
            # Check previous lines for context
            for i in range(max(0, 345), min(len(lines), 360)):
                line = lines[i]
                line_num = i + 1
                
                # Look for unmatched blocks
                if 'try:' in line:
                    print(f"Found 'try:' at line {line_num}")
                elif 'except' in line:
                    print(f"Found 'except' at line {line_num}")
                elif 'finally:' in line:
                    print(f"Found 'finally:' at line {line_num}")
                    
                    # Check if this finally has a proper try before it
                    # Look backwards for the matching try
                    found_try = False
                    for j in range(i-1, max(0, i-20), -1):
                        prev_line = lines[j].strip()
                        if prev_line.endswith('try:'):
                            found_try = True
                            print(f"  Matching try: found at line {j+1}")
                            break
                        elif prev_line.endswith(':') and 'def ' in prev_line:
                            break  # Hit a method definition
                    
                    if not found_try:
                        print(f"  ❌ No matching 'try:' found for 'finally:' at line {line_num}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during manual analysis: {e}")
        return False


def main():
    """Main analysis function."""
    print("Analyzing syntax error for issue 012...")
    
    # Step 1: Basic syntax analysis
    syntax_ok = analyze_syntax_error()
    
    # Step 2: Check for encoding issues
    check_encoding_issues()
    
    # Step 3: Manual fix attempt
    try_manual_fix()
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    
    if syntax_ok:
        print("✅ No syntax errors found - issue may be resolved")
    else:
        print("❌ Syntax errors still present - manual fix needed")
    
    return 0 if syntax_ok else 1


if __name__ == "__main__":
    sys.exit(main())
