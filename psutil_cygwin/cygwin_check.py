#!/usr/bin/env python3
"""
Cygwin environment checker for psutil-cygwin.

This module provides functions to detect and validate Cygwin environments
before allowing installation of psutil-cygwin, and to check transparent
import functionality.
"""

import os
import sys
import platform
import subprocess
import site
from pathlib import Path


def is_cygwin():
    """Check if we're running in a Cygwin environment.
    
    Returns:
        bool: True if running in Cygwin, False otherwise.
    """
    # Multiple checks to reliably detect Cygwin
    checks = [
        _check_platform(),
        _check_proc_filesystem(),
        _check_environment_variables(),
        _check_cygwin_paths(),
        _check_python_executable(),
        _check_uname(),
    ]
    
    # Require at least 2 positive checks to be confident
    positive_checks = sum(1 for check in checks if check)
    return positive_checks >= 2


def _check_platform():
    """Check if platform identifies as Cygwin."""
    return platform.system().startswith('CYGWIN')


def _check_proc_filesystem():
    """Check for /proc filesystem (Cygwin-specific on Windows)."""
    if not os.path.exists('/proc'):
        return False
    
    # On Linux/macOS, /proc exists naturally
    # On Windows, it only exists in Cygwin
    if platform.system() in ['Linux', 'Darwin']:
        return False
        
    return True


def _check_environment_variables():
    """Check for Cygwin-specific environment variables."""
    cygwin_vars = ['CYGWIN', 'CYGWIN_ROOT']
    return any(var in os.environ for var in cygwin_vars)


def _check_cygwin_paths():
    """Check for Cygwin-specific paths."""
    cygwin_paths = ['/cygdrive', '/usr/bin', '/bin']
    return any(os.path.exists(path) for path in cygwin_paths)


def _check_python_executable():
    """Check if Python executable is in Cygwin path."""
    python_path = sys.executable.lower()
    cygwin_indicators = ['/cygwin', '/usr/bin', '/bin']
    return any(indicator in python_path for indicator in cygwin_indicators)


def _check_uname():
    """Check uname output for Cygwin signature."""
    try:
        result = subprocess.run(['uname', '-a'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            uname_output = result.stdout.lower()
            return 'cygwin' in uname_output
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False


def check_cygwin_requirements():
    """Validate that Cygwin environment meets requirements.
    
    Returns:
        bool: True if environment is valid, False otherwise.
    """
    print("🔍 Validating Cygwin environment...")
    
    # Check if we're in Cygwin
    if not is_cygwin():
        print("❌ ERROR: psutil-cygwin can only be installed on Cygwin environments.")
        print("")
        print("This package is specifically designed for Cygwin and uses Cygwin's")
        print("/proc filesystem. For other platforms, please use the standard")
        print("psutil package instead:")
        print("")
        print("    pip install psutil")
        print("")
        print("Current environment detection results:")
        print(f"  Platform: {platform.system()}")
        print(f"  /proc exists: {os.path.exists('/proc')}")
        print(f"  Python executable: {sys.executable}")
        print("")
        return False
    
    # Check for required /proc files
    required_proc_files = [
        ('/proc/stat', 'CPU statistics'),
        ('/proc/meminfo', 'Memory information'),
        ('/proc/mounts', 'Mount information'),
        ('/proc/version', 'Kernel version'),
    ]
    
    missing_files = []
    for proc_file, description in required_proc_files:
        if not os.path.exists(proc_file):
            missing_files.append((proc_file, description))
    
    if missing_files:
        print("❌ ERROR: Required /proc files are missing:")
        for proc_file, description in missing_files:
            print(f"  {proc_file} ({description})")
        print("")
        print("Please ensure /proc is properly mounted in your Cygwin environment:")
        print("    mount -t proc proc /proc")
        print("")
        print("Or reinstall Cygwin with the 'procps-ng' package.")
        print("")
        return False
    
    # Check for recommended tools
    recommended_tools = ['ps', 'who', 'df', 'mount']
    missing_tools = []
    
    for tool in recommended_tools:
        try:
            subprocess.run([tool, '--version'], 
                          capture_output=True, timeout=2)
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            missing_tools.append(tool)
    
    if missing_tools:
        print("⚠️  Warning: Some recommended tools are missing:")
        for tool in missing_tools:
            print(f"  {tool}")
        print("")
        print("psutil-cygwin will work but some features may be limited.")
        print("Consider installing these tools through Cygwin setup.")
        print("")
    
    print("✅ Cygwin environment validation passed")
    print(f"   Platform: {platform.system()}")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   /proc filesystem: Available")
    print("")
    return True


def create_psutil_pth():
    """Create psutil.pth file to make psutil_cygwin available as 'psutil'."""
    try:
        # Get site-packages directory
        site_packages_dirs = site.getsitepackages()
        
        # Try to find the best site-packages directory
        site_packages = None
        for sp_dir in site_packages_dirs:
            if os.path.exists(sp_dir) and os.access(sp_dir, os.W_OK):
                site_packages = sp_dir
                break
        
        if not site_packages:
            # Fallback to user site-packages
            site_packages = site.getusersitepackages()
            # Ensure user site-packages directory exists
            if not os.path.exists(site_packages):
                try:
                    os.makedirs(site_packages, exist_ok=True)
                except OSError:
                    # If makedirs fails, return None for permission error tests
                    return None
        
        # Construct the path to the .pth file
        pth_file = os.path.join(site_packages, 'psutil.pth')
        
        # Create the .pth file content
        pth_content = '''# psutil-cygwin: Make psutil_cygwin available as 'psutil'
# This allows 'import psutil' to work transparently with psutil_cygwin
import sys; sys.modules['psutil'] = __import__('psutil_cygwin')
'''
        
        # Write the .pth file
        try:
            with open(pth_file, 'w') as f:
                f.write(pth_content)
            
            # Verify file was created (important for tests)
            if not os.path.exists(pth_file):
                return None
                
        except (OSError, IOError, PermissionError):
            # If writing fails, return None to indicate failure
            return None
        
        print(f"✅ Created psutil.pth: {pth_file}")
        print("📦 'import psutil' will now use psutil_cygwin transparently")
        
        return pth_file
        
    except Exception as e:
        print(f"⚠️  Warning: Could not create psutil.pth file: {e}")
        print("   You can still use: import psutil_cygwin as psutil")
        return None


def check_transparent_import():
    """Check if transparent psutil import is working correctly.
    
    Returns:
        dict: Information about transparent import status.
    """
    result = {
        'pth_file_found': False,
        'pth_file_path': None,
        'pth_file_content': None,
        'import_works': False,
        'import_module_name': None,
        'import_error': None,
    }
    
    # Check for psutil.pth file
    site_dirs = site.getsitepackages() + [site.getusersitepackages()]
    
    for site_dir in site_dirs:
        if not site_dir or not os.path.exists(site_dir):
            continue
            
        pth_file = os.path.join(site_dir, 'psutil.pth')
        if os.path.exists(pth_file):
            result['pth_file_found'] = True
            result['pth_file_path'] = pth_file
            
            try:
                with open(pth_file, 'r') as f:
                    result['pth_file_content'] = f.read().strip()
            except Exception as e:
                result['pth_file_content'] = f"Error reading file: {e}"
            break
    
    # Test transparent import
    try:
        # Save current sys.modules state
        original_modules = sys.modules.copy()
        
        # Remove psutil from sys.modules if present
        if 'psutil' in sys.modules:
            del sys.modules['psutil']
        
        # Try importing psutil
        import psutil
        result['import_works'] = True
        result['import_module_name'] = getattr(psutil, '__name__', 'unknown')
        
        # Clean up
        if 'psutil' in sys.modules:
            del sys.modules['psutil']
        
        # Restore original state
        sys.modules.update(original_modules)
        
    except Exception as e:
        result['import_error'] = str(e)
    
    return result


def get_cygwin_info():
    """Get information about the Cygwin environment.
    
    Returns:
        dict: Information about the Cygwin environment.
    """
    info = {
        'is_cygwin': is_cygwin(),
        'platform': platform.system(),
        'python_version': sys.version.split()[0],
        'python_executable': sys.executable,
        'proc_available': os.path.exists('/proc'),
        'proc_files': {},
        'environment_vars': {},
        'transparent_import': check_transparent_import(),
    }
    
    # Check /proc files
    proc_files = ['stat', 'meminfo', 'mounts', 'version', 'cpuinfo']
    for proc_file in proc_files:
        path = f'/proc/{proc_file}'
        info['proc_files'][proc_file] = os.path.exists(path)
    
    # Check environment variables
    env_vars = ['CYGWIN', 'CYGWIN_ROOT', 'PATH']
    for var in env_vars:
        info['environment_vars'][var] = os.environ.get(var, None)
    
    return info


def main():
    """Command-line interface for psutil-cygwin-check."""
    import json
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--info':
            info = get_cygwin_info()
            print(json.dumps(info, indent=2))
            return
        elif sys.argv[1] == '--transparent':
            print("🔍 Checking transparent psutil import...")
            result = check_transparent_import()
            
            if result['pth_file_found']:
                print(f"✅ psutil.pth file found: {result['pth_file_path']}")
                if result['pth_file_content']:
                    print(f"📄 Content: {result['pth_file_content'][:100]}...")
            else:
                print("❌ psutil.pth file not found")
                print("   Transparent import will not work")
                print("   Try: pip install --force-reinstall psutil-cygwin")
            
            if result['import_works']:
                if result['import_module_name'] == 'psutil_cygwin':
                    print("✅ Transparent import working correctly")
                    print(f"   'import psutil' uses: {result['import_module_name']}")
                else:
                    print(f"⚠️  'import psutil' uses: {result['import_module_name']}")
                    print("   This might be standard psutil, not psutil-cygwin")
            else:
                print("❌ Transparent import failed")
                if result['import_error']:
                    print(f"   Error: {result['import_error']}")
            
            return
        elif sys.argv[1] in ['--help', '-h']:
            print("psutil-cygwin-check - Validate Cygwin environment and installation")
            print("")
            print("Usage:")
            print("  psutil-cygwin-check              # Basic environment validation")
            print("  psutil-cygwin-check --info       # Show detailed environment info")
            print("  psutil-cygwin-check --transparent # Check transparent import")
            print("  psutil-cygwin-check --help       # Show this help")
            return
    
    # Default: validate environment
    success = check_cygwin_requirements()
    
    if not success:
        sys.exit(1)
    
    # Also check transparent import
    print("")
    print("🔍 Checking transparent import setup...")
    result = check_transparent_import()
    
    if result['pth_file_found'] and result['import_works'] and result['import_module_name'] == 'psutil_cygwin':
        print("✅ Transparent import configured correctly")
        print("   You can use 'import psutil' directly")
    elif result['pth_file_found']:
        print("⚠️  psutil.pth file found but import may not work as expected")
        print(f"   'import psutil' uses: {result.get('import_module_name', 'unknown')}")
    else:
        print("⚠️  Transparent import not configured")
        print("   Use 'import psutil_cygwin as psutil' instead")
        print("   Or run: psutil-cygwin-setup install")
    
    print("")
    print("Environment validation and import check complete.")


if __name__ == '__main__':
    main()
