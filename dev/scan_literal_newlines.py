#!/usr/bin/env python3
"""
Comprehensive scan for literal \\n characters in psutil-cygwin project

This script scans all text files in the project to identify files that
contain literal \\n characters where actual newlines should be used.
"""

import os
import re
from pathlib import Path

def scan_file_for_literal_newlines(file_path):
    """Scan a file for problematic literal \\n characters."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Split into lines for analysis
        lines = content.split('\n')
        
        # Look for literal \n that are NOT inside string literals
        problematic_lines = []
        
        for line_num, line in enumerate(lines, 1):
            # Skip empty lines
            if not line.strip():
                continue
                
            # Find all literal \n occurrences
            literal_newlines = []
            pos = 0
            while True:
                pos = line.find('\\n', pos)
                if pos == -1:
                    break
                literal_newlines.append(pos)
                pos += 2
            
            if not literal_newlines:
                continue
                
            # Analyze each occurrence
            for nl_pos in literal_newlines:
                # Check if it's inside a string literal
                before = line[:nl_pos]
                
                # Count quotes before the \n
                single_quotes = before.count("'") - before.count("\\'")
                double_quotes = before.count('"') - before.count('\\"')
                
                # Check for triple quotes
                triple_single = before.count("'''")
                triple_double = before.count('"""')
                
                # If we're inside a string literal, it's probably legitimate
                in_single_string = (single_quotes % 2) == 1
                in_double_string = (double_quotes % 2) == 1
                in_triple_string = (triple_single % 2) == 1 or (triple_double % 2) == 1
                
                # Additional heuristics for problematic \n
                is_problematic = False
                
                # Very long lines with many \n suggest formatting issues
                if line.count('\\n') > 5 and len(line) > 200:
                    is_problematic = True
                
                # Lines that look like they should be multiple lines
                if not (in_single_string or in_double_string or in_triple_string):
                    # Check for code-like patterns with \n
                    if any(pattern in line for pattern in [
                        'def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ',
                        'try:', 'except:', 'finally:', 'with ', 'return ', 'yield '
                    ]):
                        is_problematic = True
                
                if is_problematic:
                    problematic_lines.append({
                        'line_num': line_num,
                        'position': nl_pos,
                        'content': line.strip()[:100] + ('...' if len(line.strip()) > 100 else ''),
                        'severity': 'high' if len(line) > 300 else 'medium'
                    })
        
        return {
            'file_path': str(file_path),
            'total_lines': len(lines),
            'problematic_lines': problematic_lines,
            'has_issues': len(problematic_lines) > 0
        }
        
    except Exception as e:
        return {
            'file_path': str(file_path),
            'error': str(e),
            'has_issues': False
        }

def scan_project():
    """Scan the entire project for literal newline issues."""
    project_root = Path('/home/phdyex/my-repos/psutil-cygwin')
    
    # File patterns to scan
    patterns = [
        '**/*.py',
        '**/*.md', 
        '**/*.rst',
        '**/*.txt',
        '**/*.toml',
        '**/*.yml',
        '**/*.yaml',
        '**/*.cfg',
        '**/*.ini'
    ]
    
    # Directories to skip
    skip_dirs = {
        '.git', '__pycache__', '.pytest_cache', '_build', 'dist', 'build',
        '.tox', '.coverage', 'node_modules', '.venv', 'venv'
    }
    
    files_to_scan = set()
    
    # Collect all files matching patterns
    for pattern in patterns:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                # Check if file is in a skipped directory
                if not any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    files_to_scan.add(file_path)
    
    print(f"🔍 Scanning {len(files_to_scan)} files for literal \\n issues...")
    print("=" * 70)
    
    # Scan each file
    results = []
    for file_path in sorted(files_to_scan):
        result = scan_file_for_literal_newlines(file_path)
        results.append(result)
        
        # Print progress
        rel_path = file_path.relative_to(project_root)
        if result.get('error'):
            print(f"❌ {rel_path}: Error - {result['error']}")
        elif result['has_issues']:
            severity_counts = {}
            for line in result['problematic_lines']:
                severity = line['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            severity_str = ', '.join(f"{count} {sev}" for sev, count in severity_counts.items())
            print(f"🚨 {rel_path}: {len(result['problematic_lines'])} issues ({severity_str})")
            
            # Show first few problematic lines
            for i, line in enumerate(result['problematic_lines'][:2]):
                severity_icon = "🔥" if line['severity'] == 'high' else "⚠️"
                print(f"   {severity_icon} Line {line['line_num']}: {line['content']}")
            
            if len(result['problematic_lines']) > 2:
                print(f"   ... and {len(result['problematic_lines']) - 2} more")
        else:
            print(f"✅ {rel_path}: Clean")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SCAN SUMMARY")
    print("=" * 70)
    
    total_files = len(results)
    clean_files = len([r for r in results if not r['has_issues'] and not r.get('error')])
    problem_files = len([r for r in results if r['has_issues']])
    error_files = len([r for r in results if r.get('error')])
    
    print(f"Total files scanned: {total_files}")
    print(f"Clean files: {clean_files}")
    print(f"Files with issues: {problem_files}")
    print(f"Files with errors: {error_files}")
    
    if problem_files > 0:
        print(f"\n🚨 FILES NEEDING ATTENTION:")
        for result in results:
            if result['has_issues']:
                rel_path = Path(result['file_path']).relative_to(project_root)
                high_issues = len([l for l in result['problematic_lines'] if l['severity'] == 'high'])
                med_issues = len([l for l in result['problematic_lines'] if l['severity'] == 'medium'])
                
                if high_issues > 0:
                    print(f"  🔥 {rel_path}: {high_issues} high priority issues")
                elif med_issues > 0:
                    print(f"  ⚠️  {rel_path}: {med_issues} medium priority issues")
        
        print(f"\n💡 RECOMMENDATION:")
        print(f"   Review and fix files with 'high' priority issues first.")
        print(f"   These likely have formatting problems that affect functionality.")
        
    else:
        print(f"\n🎉 ALL FILES ARE CLEAN!")
        print(f"   No problematic literal \\n characters found.")
    
    return results

if __name__ == "__main__":
    results = scan_project()
