"""
Modern build hooks for psutil-cygwin installation.

Replaces deprecated setuptools custom commands with modern build system hooks.
"""
import sys
from psutil_cygwin.cygwin_check import (
    check_cygwin_requirements,
    create_psutil_pth,
)


def post_install_hook():
    """
    Post-installation hook called after package installation.
    
    This replaces the deprecated custom install command approach.
    """
    # Only proceed if we're not building wheels
    if len(sys.argv) > 1 and sys.argv[1] in ['bdist_wheel', 'sdist', 'egg_info']:
        return
    
    # Check Cygwin environment
    if not check_cygwin_requirements():
        sys.exit(1)
    
    # Create psutil.pth file
    create_psutil_pth()
    
    print("")
    print("🎉 psutil-cygwin installation complete!")
    print("")
    print("You can now use either:")
    print("  import psutil                    # Transparent replacement")
    print("  import psutil_cygwin as psutil   # Explicit import")
    print("")
    print("Console commands available:")
    print("  psutil-cygwin-monitor            # System monitoring")
    print("  psutil-cygwin-proc               # Process management")
    print("  psutil-cygwin-check              # Environment validation")
    print("  psutil-cygwin-setup              # Setup/cleanup utility")
    print("")


def remove_psutil_pth():
    """Remove psutil.pth file during uninstall."""
    import os
    import site
    
    try:
        site_packages_dirs = site.getsitepackages() + [site.getusersitepackages()]
        
        for site_packages in site_packages_dirs:
            if not os.path.exists(site_packages):
                continue
                
            pth_file = os.path.join(site_packages, 'psutil.pth')
            if os.path.exists(pth_file):
                # Check if it's our file
                try:
                    with open(pth_file, 'r') as f:
                        content = f.read()
                    if 'psutil_cygwin' in content:
                        os.remove(pth_file)
                        print(f"🗑️  Removed psutil.pth: {pth_file}")
                except Exception as e:
                    print(f"Warning: Could not remove {pth_file}: {e}")
                    
    except Exception as e:
        print(f"Warning: Error during psutil.pth cleanup: {e}")
