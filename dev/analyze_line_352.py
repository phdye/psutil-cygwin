#!/usr/bin/env python3
"""
Line-by-line analysis of the test file to find line 352.
"""

import sys
from pathlib import Path


def analyze_line_352():
    """Analyze the exact content at line 352."""
    test_file = Path(__file__).parent.parent / "tests" / "test_pth_functionality.py"
    
    try:
        with open(test_file, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"File has {len(lines)} lines")
    print(f"Examining line 352 and surrounding context...")
    
    # Show a wider context around line 352
    start = max(0, 352 - 15)
    end = min(len(lines), 352 + 15)
    
    for i in range(start, end):
        line_num = i + 1
        line = lines[i].rstrip()
        
        # Mark special lines
        markers = []
        if line_num == 352:
            markers.append("<<< ERROR LINE")
        if line.strip() == 'finally:':
            markers.append("FINALLY")
        if line.strip().endswith('try:'):
            markers.append("TRY")
        if line.strip().startswith('except'):
            markers.append("EXCEPT")
        if line.strip().startswith('def '):
            markers.append("METHOD")
        if line.strip().startswith('class '):
            markers.append("CLASS")
            
        marker_str = " ".join(markers)
        if marker_str:
            marker_str = " --> " + marker_str
            
        print(f"{line_num:3d}: {line}{marker_str}")


if __name__ == "__main__":
    analyze_line_352()
