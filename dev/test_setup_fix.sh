#!/bin/bash
# Quick test for setup.py import fix

echo "Testing setup.py import fix..."

cd /home/phdyex/my-repos/psutil-cygwin

# Test 1: Import the failing functions
echo "1. Testing function imports..."
python3 -c "
from setup import create_psutil_pth, remove_psutil_pth, is_cygwin
print('✓ All setup.py functions imported successfully')
print(f'✓ is_cygwin() = {is_cygwin()}')
"

if [ $? -eq 0 ]; then
    echo "   ✓ Function imports work"
else
    echo "   ✗ Function imports failed"
    exit 1
fi

# Test 2: Test pytest collection
echo "2. Testing pytest collection..."
pytest tests/test_pth_functionality.py --collect-only --quiet >/dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   ✓ pytest can collect pth functionality tests"
else
    echo "   ✗ pytest collection failed"
    exit 1
fi

echo ""
echo "🎉 setup.py import fix successful!"
echo ""
echo "Issue/test/004.txt has been resolved."
echo "You can now run the full test suite:"
echo "   pytest tests/"
