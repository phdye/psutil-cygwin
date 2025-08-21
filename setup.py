#!/usr/bin/env python3
"""
Modern setup.py for psutil-cygwin.

This file is kept minimal and only exists for backward compatibility.
All configuration is now in pyproject.toml following PEP 517/518.

For installation, use:
    pip install .              # Normal installation
    pip install -e .           # Development installation
    python -m build            # Build wheel/sdist

Avoid deprecated commands:
    python setup.py install    # DEPRECATED
    python setup.py develop    # DEPRECATED
"""

from setuptools import setup

# All configuration is in pyproject.toml
# This setup.py exists only for backward compatibility
if __name__ == '__main__':
    setup()
