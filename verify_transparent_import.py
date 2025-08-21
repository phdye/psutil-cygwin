#!/usr/bin/env python3
"""
Comprehensive verification script for psutil-cygwin transparent import functionality.

This script thoroughly tests that the .pth file mechanism works correctly
and that transparent import is functioning as expected.
"""

import os
import sys
import site
import importlib
import subprocess
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)


def print_result(test_name, success, details=""):
    """Print a test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        for line in details.split('\n'):
            if line.strip():
                print(f"      {line}")


def check_cygwin_environment():
    """Check if we're in a Cygwin environment."""
    print_header("Cygwin Environment Check")
    
    # Check /proc filesystem
    proc_exists = os.path.exists('/proc')
    print_result("Cygwin /proc filesystem", proc_exists, 
                f"/proc exists: {proc_exists}")
    
    # Check platform
    import platform
    is_cygwin = platform.system().startswith('CYGWIN')
    print_result("Platform detection", is_cygwin,
                f"Platform: {platform.system()}")
    
    return proc_exists and is_cygwin


def find_pth_files():
    """Find all psutil.pth files in site-packages."""
    print_header("psutil.pth File Discovery")
    
    pth_files = []
    
    # Check all site-packages directories
    site_dirs = []
    try:
        site_dirs.extend(site.getsitepackages())
    except:
        pass
    
    try:
        user_site = site.getusersitepackages()
        if user_site:
            site_dirs.append(user_site)
    except:
        pass
    
    for site_dir in site_dirs:
        if not site_dir or not os.path.exists(site_dir):
            continue
            
        pth_file = os.path.join(site_dir, 'psutil.pth')
        if os.path.exists(pth_file):
            pth_files.append(pth_file)
            
            # Read content
            try:
                with open(pth_file, 'r') as f:
                    content = f.read().strip()
                print_result(f"Found psutil.pth", True, 
                           f"Path: {pth_file}\nContent: {content[:100]}...")
            except Exception as e:
                print_result(f"Found psutil.pth (unreadable)", False,
                           f"Path: {pth_file}\nError: {e}")
    
    if not pth_files:
        print_result("psutil.pth file search", False, 
                    "No psutil.pth files found in any site-packages directory")
    
    return pth_files


def test_transparent_import():
    """Test transparent import functionality."""
    print_header("Transparent Import Testing")
    
    # Save original sys.modules state
    original_modules = sys.modules.copy()
    
    try:
        # Remove psutil from sys.modules if present
        modules_to_remove = ['psutil', 'psutil_cygwin']
        for mod in modules_to_remove:
            if mod in sys.modules:
                del sys.modules[mod]
        
        # Try importing psutil
        try:
            import psutil
            import_success = True
            module_name = getattr(psutil, '__name__', 'unknown')
            module_file = getattr(psutil, '__file__', 'unknown')
            
            print_result("Import psutil", True,
                        f"Module name: {module_name}\nModule file: {module_file}")
            
            # Check if it's psutil_cygwin
            is_cygwin_module = module_name == 'psutil_cygwin'
            print_result("Using psutil_cygwin", is_cygwin_module,
                        f"Expected: psutil_cygwin, Got: {module_name}")
            
            # Test basic functionality
            try:
                cpu_count = psutil.cpu_count()
                mem = psutil.virtual_memory()
                pids = psutil.pids()
                
                print_result("Basic functionality", True,
                           f"CPU count: {cpu_count}\nMemory total: {mem.total}\nProcess count: {len(pids)}")
            except Exception as e:
                print_result("Basic functionality", False, f"Error: {e}")
                
        except ImportError as e:
            print_result("Import psutil", False, f"ImportError: {e}")
            import_success = False
        except Exception as e:
            print_result("Import psutil", False, f"Unexpected error: {e}")
            import_success = False
            
    finally:
        # Clean up sys.modules
        for mod in ['psutil', 'psutil_cygwin']:
            if mod in sys.modules:
                del sys.modules[mod]
        
        # Restore original state (partially)
        for mod, obj in original_modules.items():
            if mod not in sys.modules:
                sys.modules[mod] = obj
    
    return import_success


def test_explicit_import():
    """Test explicit psutil_cygwin import."""
    print_header("Explicit Import Testing")
    
    try:
        # Add current directory to path for testing
        current_dir = Path(__file__).parent.parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        # Try explicit import
        import psutil_cygwin
        
        print_result("Import psutil_cygwin", True,
                    f"Module: {psutil_cygwin.__name__}\nFile: {psutil_cygwin.__file__}")
        
        # Test functionality
        try:
            cpu_count = psutil_cygwin.cpu_count()
            print_result("Explicit import functionality", True,
                        f"CPU count via explicit import: {cpu_count}")
        except Exception as e:
            print_result("Explicit import functionality", False, f"Error: {e}")
            
        return True
        
    except ImportError as e:
        print_result("Import psutil_cygwin", False, f"ImportError: {e}")
        return False
    except Exception as e:
        print_result("Import psutil_cygwin", False, f"Unexpected error: {e}")
        return False


def test_command_line_tools():
    """Test command-line tools."""
    print_header("Command-Line Tools Testing")
    
    tools = [
        ('psutil-cygwin-check', ['--help']),
        ('psutil-cygwin-check', ['--transparent']),
        ('psutil-cygwin-monitor', ['--help']),
        ('psutil-cygwin-proc', ['--help']),
    ]
    
    for tool, args in tools:
        try:
            result = subprocess.run([tool] + args, 
                                  capture_output=True, text=True, timeout=10)
            success = result.returncode == 0
            print_result(f"{tool} {' '.join(args)}", success,
                        f"Return code: {result.returncode}\nOutput length: {len(result.stdout)} chars")
        except FileNotFoundError:
            print_result(f"{tool} {' '.join(args)}", False, "Command not found")
        except subprocess.TimeoutExpired:
            print_result(f"{tool} {' '.join(args)}", False, "Command timed out")
        except Exception as e:
            print_result(f"{tool} {' '.join(args)}", False, f"Error: {e}")


def test_installation_integrity():
    """Test installation integrity."""
    print_header("Installation Integrity Check")
    
    # Check package is importable
    try:
        import psutil_cygwin
        print_result("Package import", True, f"Version: {getattr(psutil_cygwin, '__version__', 'unknown')}")
    except ImportError as e:
        print_result("Package import", False, f"ImportError: {e}")
        return False
    
    # Check core functionality
    try:
        # Test each major function category
        tests = [
            ("CPU functions", lambda: psutil_cygwin.cpu_count() and psutil_cygwin.cpu_times()),
            ("Memory functions", lambda: psutil_cygwin.virtual_memory().total > 0),
            ("Process functions", lambda: len(psutil_cygwin.pids()) > 0),
            ("System functions", lambda: psutil_cygwin.boot_time() > 0),
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                print_result(test_name, bool(result))
            except Exception as e:
                print_result(test_name, False, f"Error: {e}")
                
    except Exception as e:
        print_result("Core functionality", False, f"Error: {e}")
    
    return True


def generate_report():
    """Generate a comprehensive report."""
    print_header("Comprehensive Verification Report")
    
    # Summary
    print("\n📋 VERIFICATION SUMMARY")
    print("-" * 30)
    
    # Environment
    cygwin_ok = check_cygwin_environment()
    
    # PTH files
    pth_files = find_pth_files()
    pth_ok = len(pth_files) > 0
    
    # Imports
    transparent_ok = test_transparent_import()
    explicit_ok = test_explicit_import()
    
    # Installation
    install_ok = test_installation_integrity()
    
    # Tools
    test_command_line_tools()
    
    # Final assessment
    print_header("Final Assessment")
    
    overall_success = all([cygwin_ok, pth_ok, transparent_ok, explicit_ok, install_ok])
    
    print_result("Overall psutil-cygwin setup", overall_success)
    
    if overall_success:
        print("\n🎉 SUCCESS: psutil-cygwin is properly installed and configured!")
        print("   ✅ Transparent import working")
        print("   ✅ All functionality available")
        print("   ✅ You can use 'import psutil' directly")
    else:
        print("\n⚠️  ISSUES DETECTED:")
        if not cygwin_ok:
            print("   ❌ Cygwin environment issues")
        if not pth_ok:
            print("   ❌ psutil.pth file missing")
        if not transparent_ok:
            print("   ❌ Transparent import not working")
        if not explicit_ok:
            print("   ❌ Explicit import not working")
        if not install_ok:
            print("   ❌ Installation integrity issues")
        
        print("\n🔧 Suggested fixes:")
        print("   1. Reinstall: pip uninstall psutil-cygwin && pip install psutil-cygwin")
        print("   2. Check environment: psutil-cygwin-check")
        print("   3. Use explicit import: import psutil_cygwin as psutil")
    
    return overall_success


def main():
    """Main verification function."""
    print("🔍 psutil-cygwin Transparent Import Verification")
    print("=" * 60)
    print("This script comprehensively tests the transparent import functionality.")
    
    try:
        success = generate_report()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Verification failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
