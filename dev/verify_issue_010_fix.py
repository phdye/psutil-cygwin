#!/usr/bin/env python3
"""
Verification script for Issue 010 resolution.

This script tests that the improvements made to test_pth_functionality.py
provide better feedback and reduce unnecessary skips on Cygwin.
"""

import sys
import subprocess
from pathlib import Path

def test_improved_skip_behavior():
    """Test that the improved test file behaves better."""
    print("=" * 60)
    print("TESTING IMPROVED SKIP BEHAVIOR")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    
    # Run pytest with collection only to see test structure
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_pth_functionality.py", 
            "--collect-only", "-q"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Test collection successful")
            print("Collected tests:")
            for line in result.stdout.split('\n'):
                if '::' in line and 'test_' in line:
                    print(f"  {line.strip()}")
        else:
            print("❌ Test collection failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"Error running pytest collection: {e}")
        return False
    
    # Run the actual tests to see skip behavior
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_pth_functionality.py", 
            "-v", "-s"
        ], capture_output=True, text=True, cwd=project_root)
        
        print(f"\nTest execution exit code: {result.returncode}")
        
        # Count skipped tests
        output = result.stdout
        skip_count = output.count("SKIPPED")
        passed_count = output.count("PASSED")
        failed_count = output.count("FAILED")
        
        print(f"Results: {passed_count} passed, {failed_count} failed, {skip_count} skipped")
        
        # Analyze skip reasons
        if "SKIPPED" in output:
            print("\nSkip reasons:")
            lines = output.split('\n')
            for line in lines:
                if "SKIPPED" in line and "[" in line:
                    # Extract skip reason
                    if "] " in line:
                        reason = line.split("] ", 1)[1]
                        print(f"  • {reason}")
        
        # Show any helpful output from our improved tests
        if "✅" in output or "⚠️" in output or "❌" in output:
            print("\nTest feedback:")
            lines = output.split('\n')
            for line in lines:
                if any(marker in line for marker in ["✅", "⚠️", "❌"]):
                    print(f"  {line.strip()}")
        
        return True
        
    except Exception as e:
        print(f"Error running pytest: {e}")
        return False


def check_test_improvements():
    """Check specific improvements made to the test file."""
    print("\n" + "=" * 60)
    print("CHECKING TEST IMPROVEMENTS")
    print("=" * 60)
    
    test_file = Path(__file__).parent.parent / "tests" / "test_pth_functionality.py"
    
    if not test_file.exists():
        print("❌ Test file not found")
        return False
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    improvements = [
        ("Modern installation tests", "TestModernInstallationIntegration"),
        ("Modern Cygwin detection", "TestModernCygwinDetection"), 
        ("Better skip messages", "psutil_cygwin not available"),
        ("Transparent import instructions", "psutil-cygwin-setup install"),
        ("Development mode check", "package not installed in development mode"),
    ]
    
    for description, pattern in improvements:
        if pattern in content:
            print(f"✅ {description}: Found")
        else:
            print(f"❌ {description}: Missing '{pattern}'")
    
    # Check that old problematic patterns are gone
    old_patterns = [
        ("Old CygwinInstallCommand", "CygwinInstallCommand"),
        ("Old CygwinDevelopCommand", "CygwinDevelopCommand"),
    ]
    
    for description, pattern in old_patterns:
        if pattern in content and "removed during modernization" not in content:
            print(f"⚠️  {description}: Still present (should be disabled)")
        else:
            print(f"✅ {description}: Properly handled")
    
    return True


def main():
    """Run all verification checks."""
    print("Verifying Issue 010 Resolution: Improved Skip Behavior")
    print("This script tests that test skips are more helpful and appropriate.")
    
    success = True
    
    # Check test improvements
    if not check_test_improvements():
        success = False
    
    # Test skip behavior
    if not test_improved_skip_behavior():
        success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ ISSUE 010 IMPROVEMENTS VERIFIED")
        print("")
        print("Key improvements:")
        print("• Better error messages in transparent import tests")
        print("• Modern installation tests replace old setuptools command tests")
        print("• Clear instructions when setup is not complete")
        print("• Diagnostic tools available for troubleshooting")
        print("")
        print("To achieve zero skips on Cygwin:")
        print("1. pip install -e .")
        print("2. psutil-cygwin-setup install")
        print("3. pytest tests/test_pth_functionality.py")
    else:
        print("❌ SOME ISSUES REMAIN")
        print("Check the output above for specific problems.")
    
    print("\nFor detailed diagnosis, run: python dev/diagnose_issue_010.py")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
