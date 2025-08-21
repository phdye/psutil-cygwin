#!/usr/bin/env python3
"""
Quick one-liner test to verify pyproject.toml is fixed
"""

import sys
import os

def quick_test():
    os.chdir('/home/phdyex/my-repos/psutil-cygwin')
    
    # Test TOML
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            import toml
            with open('pyproject.toml', 'r') as f:
                config = toml.load(f)
            print("✓ TOML valid")
            return
    
    with open('pyproject.toml', 'rb') as f:
        config = tomllib.load(f)
    print("✓ TOML valid")

if __name__ == "__main__":
    try:
        quick_test()
        print("🎉 pyproject.toml fix successful!")
    except Exception as e:
        print(f"❌ pyproject.toml still has issues: {e}")
        sys.exit(1)
