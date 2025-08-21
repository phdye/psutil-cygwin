#!/bin/bash
# Fix script for psutil-cygwin import issue

echo "Fixing psutil-cygwin import issue..."

# Navigate to project directory
cd /home/phdyex/my-repos/psutil-cygwin

# Clear Python bytecode cache
echo "Clearing Python bytecode cache..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Clear any existing installations
echo "Clearing any existing installations..."
pip uninstall -y psutil-cygwin 2>/dev/null || true

# Install in development mode
echo "Installing in development mode..."
pip install -e .

# Test the import
echo "Testing import..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import psutil_cygwin as psutil
    print('✓ Import successful')
    print(f'Available functions: {len([x for x in dir(psutil) if not x.startswith(\"_\")])}')
    print(f'User namedtuple available: {hasattr(psutil, \"User\")}')
    if hasattr(psutil, 'User'):
        print(f'User fields: {psutil.User._fields}')
except Exception as e:
    print(f'✗ Import failed: {e}')
    import traceback
    traceback.print_exc()
"

echo "Done. Try running the tests now with: pytest tests/"
