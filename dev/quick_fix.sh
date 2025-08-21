#!/bin/bash
# Simple fix script for the psutil-cygwin import issue

set -e

echo "Fixing psutil-cygwin User import issue..."

# Navigate to project directory  
cd /home/phdyex/my-repos/psutil-cygwin

# Remove Python cache files
echo "Cleaning Python cache..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Test the import
echo "Testing import..."
python3 -c "
import sys
sys.path.insert(0, '.')

# Test direct core import
print('Testing core import...')
from psutil_cygwin.core import User, cpu_percent, Process
print(f'✓ User namedtuple: {User._fields}')

# Test package import  
print('Testing package import...')
import psutil_cygwin as psutil
print(f'✓ Package imported with {len([x for x in dir(psutil) if not x.startswith(\"_\")])} public attributes')

# Test the specific failing import
print('Testing specific imports...')
from psutil_cygwin import User, cpu_percent, Process
print('✓ All imports successful')

print('🎉 Import issue resolved!')
"

echo "✅ Fix completed. You can now run the tests:"
echo "   pytest tests/"
