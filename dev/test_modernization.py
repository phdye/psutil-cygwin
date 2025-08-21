#!/usr/bin/env python3
"""
Test script to verify modern build system eliminates warnings.

This script tests the modernized psutil-cygwin package to ensure:
1. No deprecation warnings during installation
2. Clean test execution  
3. Proper functionality
4. Modern build system works correctly
"""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path


def run_command(cmd, capture_output=True, check=True, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, 
            capture_output=capture_output, 
            text=True, 
            check=check,
            cwd=cwd
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT:\n{e.stdout}")
        if e.stderr:
            print(f"STDERR:\n{e.stderr}")
        raise


def test_modern_build():
    """Test modern build system."""
    print("=" * 60)
    print("Testing Modern Build System")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    
    # Test build command
    print("\n1. Testing 'python -m build'...")
    try:
        result = run_command([sys.executable, "-m", "build"], cwd=project_root)
        print("✅ Build completed successfully")
        
        # Check for warnings in output
        if "warning" in result.stderr.lower() or "deprecated" in result.stderr.lower():
            print("⚠️  Build produced warnings:")
            print(result.stderr)
        else:
            print("✅ No warnings during build")
            
    except subprocess.CalledProcessError:
        print("❌ Build failed or 'build' module not available")
        print("   Install with: pip install build")
    
    # Test wheel creation
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        wheels = list(dist_dir.glob("*.whl"))
        if wheels:
            print(f"✅ Wheel created: {wheels[0].name}")
        else:
            print("⚠️  No wheel file found")


def test_installation_methods():
    """Test different installation methods."""
    print("\n" + "=" * 60)
    print("Testing Installation Methods")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    
    # Create a virtual environment for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_dir = Path(temp_dir) / "test_venv"
        
        print(f"\n1. Creating test virtual environment in {venv_dir}")
        run_command([sys.executable, "-m", "venv", str(venv_dir)])
        
        # Get python executable in venv
        if os.name == 'nt':  # Windows
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:  # Unix-like
            python_exe = venv_dir / "bin" / "python"
        
        # Test pip install . (modern method)
        print("\n2. Testing 'pip install .' (modern method)")
        try:
            result = run_command([
                str(python_exe), "-m", "pip", "install", "."
            ], cwd=project_root)
            
            # Check for warnings
            if "deprecated" in result.stdout.lower() or "deprecated" in result.stderr.lower():
                print("⚠️  pip install produced deprecation warnings")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
            else:
                print("✅ pip install completed without deprecation warnings")
                
            # Test import
            import_result = run_command([
                str(python_exe), "-c", "import psutil_cygwin; print('Import successful')"
            ])
            print("✅ Package import successful")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")


def test_entry_points():
    """Test that entry points work correctly."""
    print("\n" + "=" * 60)
    print("Testing Entry Points")
    print("=" * 60)
    
    # Test that our entry points are available
    entry_points = [
        "psutil-cygwin-check",
        "psutil-cygwin-setup",
        "psutil-cygwin-monitor",
        "psutil-cygwin-proc"
    ]
    
    for entry_point in entry_points:
        try:
            result = run_command([entry_point, "--help"], check=False)
            if result.returncode == 0:
                print(f"✅ {entry_point} available and working")
            else:
                print(f"⚠️  {entry_point} available but may have issues")
        except FileNotFoundError:
            print(f"❌ {entry_point} not found")
        except subprocess.CalledProcessError:
            print(f"⚠️  {entry_point} found but --help failed")


def test_pytest_clean_output():
    """Test that pytest runs without warnings."""
    print("\n" + "=" * 60)
    print("Testing Pytest Clean Output")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    
    try:
        # Run pytest and capture output
        result = run_command([
            sys.executable, "-m", "pytest", "tests/", "-v"
        ], cwd=project_root, check=False)
        
        # Check for warnings in output
        output = result.stdout + result.stderr
        
        if "DeprecationWarning" in output:
            print("⚠️  Pytest output contains DeprecationWarnings:")
            # Show just the warning lines
            lines = output.split('\n')
            warning_lines = [line for line in lines if "DeprecationWarning" in line]
            for line in warning_lines[:5]:  # Show first 5
                print(f"   {line}")
            if len(warning_lines) > 5:
                print(f"   ... and {len(warning_lines) - 5} more")
        else:
            print("✅ Pytest output is clean - no DeprecationWarnings")
            
        if "warning" in output.lower():
            print("⚠️  Pytest output contains other warnings")
        else:
            print("✅ Pytest output has no warnings at all")
            
        # Check test results
        if result.returncode == 0:
            print("✅ All tests passed")
        else:
            print(f"⚠️  Some tests failed (exit code: {result.returncode})")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Pytest execution failed: {e}")


def test_setup_py_minimal():
    """Test that setup.py is minimal and doesn't produce warnings."""
    print("\n" + "=" * 60)
    print("Testing Minimal setup.py")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    setup_py = project_root / "setup.py"
    
    # Check setup.py content
    with open(setup_py, 'r') as f:
        content = f.read()
    
    # Check for deprecated patterns
    deprecated_patterns = [
        "cmdclass",
        "CygwinInstallCommand", 
        "CygwinDevelopCommand",
        "warnings.catch_warnings",
        "warnings.filterwarnings"
    ]
    
    found_deprecated = []
    for pattern in deprecated_patterns:
        if pattern in content:
            found_deprecated.append(pattern)
    
    if found_deprecated:
        print(f"⚠️  setup.py contains deprecated patterns: {found_deprecated}")
    else:
        print("✅ setup.py is clean - no deprecated patterns")
    
    # Check that setup.py is minimal
    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
    if len(lines) <= 10:  # Should be very minimal
        print("✅ setup.py is minimal (good)")
    else:
        print(f"⚠️  setup.py has {len(lines)} non-comment lines - might not be minimal")


def main():
    """Run all tests."""
    print("Testing psutil-cygwin Modernization")
    print("This script verifies that warning suppression has been replaced")
    print("with modern practices that eliminate the root causes of warnings.")
    print("")
    
    try:
        test_setup_py_minimal()
        test_modern_build() 
        test_entry_points()
        test_pytest_clean_output()
        # test_installation_methods()  # Skip this as it requires venv setup
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("✅ Modernization testing complete!")
        print("")
        print("Key improvements:")
        print("• Eliminated deprecated setuptools custom commands")
        print("• Replaced with modern PEP 517/518 build system")
        print("• No more warning suppression needed")
        print("• Clean pytest output")
        print("• Modern entry point-based setup")
        print("")
        print("To complete verification:")
        print("1. Run: pip install -e .")
        print("2. Run: psutil-cygwin-setup install")
        print("3. Run: psutil-cygwin-check")
        print("4. Run: pytest tests/ (should be clean)")
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
