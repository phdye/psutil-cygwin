# Development Tools and Diagnostic Scripts

This directory contains temporary development tools and diagnostic scripts used during the development and debugging of psutil-cygwin.

## Import Issue Resolution (issue/test/001.txt)
- `debug_user_import.py` - Debug script for User namedtuple import issues
- `minimal_test.py` - Minimal test to isolate import problems  
- `check_syntax.py` - Syntax checking for core.py
- `fix_import_issue.py` - Comprehensive import issue diagnostic
- `complete_fix.py` - Complete fix script with step-by-step verification
- `quick_fix.sh` - Simple bash script to clear cache and test imports
- `fix_import.sh` - Installation-based fix script
- `verify_fix.py` - Verification script for import fixes

## TOML Configuration Issue (issue/test/003.txt)  
- `quick_toml_test.py` - Quick TOML syntax validation
- `test_toml_fix.sh` - Bash script for TOML fix verification
- `verify_toml_fix.py` - Comprehensive TOML and pytest configuration testing

## Usage

These scripts are one-off diagnostic and verification tools. They can be safely deleted once the corresponding issues are resolved.

To use any script:
```bash
cd /home/phdyex/my-repos/psutil-cygwin/dev
python3 script_name.py
# or
bash script_name.sh
```

## Note

These scripts are not part of the main psutil-cygwin package and should not be included in distributions or releases.
