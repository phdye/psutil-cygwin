#!/usr/bin/env python3
"""
Post-installation script for psutil-cygwin.

This script is called after package installation to set up the environment.
It replaces the deprecated setuptools custom install commands.
"""

import sys
import argparse
from psutil_cygwin.cygwin_check import (
    check_cygwin_requirements,
    create_psutil_pth,
)
from psutil_cygwin._build.hooks import remove_psutil_pth


def setup_environment():
    """Set up the psutil-cygwin environment after installation."""
    print("Setting up psutil-cygwin environment...")
    
    # Check Cygwin environment
    if not check_cygwin_requirements():
        print("❌ Environment validation failed")
        return False
    
    # Create psutil.pth file
    pth_file = create_psutil_pth()
    
    if pth_file:
        print("")
        print("🎉 psutil-cygwin setup complete!")
        print("")
        print("You can now use either:")
        print("  import psutil                    # Transparent replacement")
        print("  import psutil_cygwin as psutil   # Explicit import")
        print("")
        print("Console commands available:")
        print("  psutil-cygwin-monitor            # System monitoring")
        print("  psutil-cygwin-proc               # Process management")
        print("  psutil-cygwin-check              # Environment validation")
        print("")
        return True
    else:
        print("⚠️  Setup completed with warnings")
        return False


def cleanup_environment():
    """Clean up the psutil-cygwin environment."""
    print("Cleaning up psutil-cygwin environment...")
    remove_psutil_pth()
    print("✅ Cleanup complete")


def main():
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(
        description="psutil-cygwin post-installation setup",
        prog="psutil-cygwin-setup"
    )
    parser.add_argument(
        'action',
        choices=['install', 'uninstall', 'check'],
        help='Action to perform'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress output'
    )
    
    args = parser.parse_args()
    
    if args.action == 'install':
        success = setup_environment()
        sys.exit(0 if success else 1)
    elif args.action == 'uninstall':
        cleanup_environment()
        sys.exit(0)
    elif args.action == 'check':
        success = check_cygwin_requirements()
        if success:
            print("✅ Environment is properly configured")
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
