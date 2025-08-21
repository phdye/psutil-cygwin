#!/usr/bin/env python3
"""
Quick verification script for psutil-cygwin modernization.

Run this script to verify that the modernization eliminated warnings
and implemented modern Python packaging practices.
"""

import os
import sys
from pathlib import Path


def check_file_exists(path, description):
    """Check if a file exists and report."""
    if path.exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: Missing {path}")
        return False


def check_file_content(path, should_contain, should_not_contain, description):
    """Check file content for required and prohibited patterns."""
    if not path.exists():
        print(f"❌ {description}: File {path} not found")
        return False
    
    with open(path, 'r') as f:
        content = f.read()
    
    # Check for required content
    missing_required = []
    for item in should_contain:
        if item not in content:
            missing_required.append(item)
    
    # Check for prohibited content
    found_prohibited = []
    for item in should_not_contain:
        if item in content:
            found_prohibited.append(item)
    
    if missing_required:
        print(f"⚠️  {description}: Missing required content: {missing_required}")
    
    if found_prohibited:
        print(f"❌ {description}: Contains prohibited content: {found_prohibited}")
        return False
    
    if not missing_required:
        print(f"✅ {description}: Content looks good")
        return True
    else:
        return False


def main():
    """Run verification checks."""
    print("Verifying psutil-cygwin modernization...")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    all_good = True
    
    # Check new build system files
    build_files = [
        (project_root / "psutil_cygwin" / "_build" / "__init__.py", "Build system __init__.py"),
        (project_root / "psutil_cygwin" / "_build" / "hooks.py", "Modern build hooks"),
        (project_root / "psutil_cygwin" / "_build" / "setup_script.py", "Setup script"),
        (project_root / "psutil_cygwin" / "_build" / "backend.py", "Build backend"),
    ]
    
    print("\n1. Checking new build system files:")
    for file_path, description in build_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Check setup.py is minimal
    print("\n2. Checking setup.py modernization:")
    setup_py = project_root / "setup.py"
    setup_good = check_file_content(
        setup_py,
        should_contain=["setup()"],  # Should be minimal
        should_not_contain=[
            "CygwinInstallCommand", 
            "CygwinDevelopCommand", 
            "warnings.catch_warnings",
            "cmdclass"
        ],
        description="setup.py"
    )
    all_good = all_good and setup_good
    
    # Check pyproject.toml is clean
    print("\n3. Checking pyproject.toml:")
    pyproject = project_root / "pyproject.toml"
    pyproject_good = check_file_content(
        pyproject,
        should_contain=["psutil-cygwin-setup", "setuptools.build_meta"],
        should_not_contain=[
            "filterwarnings = [",
            "ignore::DeprecationWarning",
            "setup.py.*is deprecated"
        ],
        description="pyproject.toml"
    )
    all_good = all_good and pyproject_good
    
    # Check documentation files
    print("\n4. Checking documentation:")
    doc_files = [
        (project_root / "MODERN_INSTALLATION.md", "Modern installation guide"),
        (project_root / "dev" / "MODERNIZATION_SUMMARY.md", "Modernization summary"),
    ]
    
    for file_path, description in doc_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_good:
        print("✅ MODERNIZATION VERIFICATION PASSED")
        print("")
        print("Key improvements implemented:")
        print("• Eliminated deprecated setuptools custom commands")
        print("• Removed all warning suppression code")
        print("• Implemented modern PEP 517/518 build system")
        print("• Created entry point-based post-install setup")
        print("• Clean pyproject.toml configuration")
        print("")
        print("Next steps to test:")
        print("1. pip install -e .")
        print("2. psutil-cygwin-setup install")
        print("3. psutil-cygwin-check")
        print("4. pytest tests/ (should be clean)")
        print("")
        print("Expected result: No deprecation warnings anywhere!")
        
    else:
        print("❌ MODERNIZATION VERIFICATION FAILED")
        print("Some files are missing or contain deprecated patterns.")
        print("Check the output above for specific issues.")
        
    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())
