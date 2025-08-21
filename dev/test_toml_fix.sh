#!/bin/bash
# Quick test script for the pyproject.toml fix

echo "Testing pyproject.toml fix..."

# Navigate to project directory
cd /home/phdyex/my-repos/psutil-cygwin

# Test 1: Validate TOML syntax
echo "1. Testing TOML syntax..."
python3 -c "
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        import toml
        with open('pyproject.toml', 'r') as f:
            config = toml.load(f)
        print('✓ TOML is valid (using toml library)')
        exit()

with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)
print('✓ TOML is valid')
print(f'Project: {config[\"project\"][\"name\"]} v{config[\"project\"][\"version\"]}')
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✓ pyproject.toml syntax is valid"
else
    echo "   ✗ pyproject.toml syntax is invalid"
    exit 1
fi

# Test 2: Test pytest configuration
echo "2. Testing pytest configuration..."
pytest --collect-only --quiet 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✓ pytest configuration is valid"
else
    echo "   ✗ pytest configuration failed"
    echo "   Trying to get more details..."
    pytest --collect-only
    exit 1
fi

# Test 3: Run a quick test
echo "3. Running quick functionality test..."
python3 -c "
import sys
sys.path.insert(0, '.')
import psutil_cygwin as psutil
print(f'✓ psutil-cygwin imported with {len([x for x in dir(psutil) if not x.startswith(\"_\")])} functions')
"

if [ $? -eq 0 ]; then
    echo "   ✓ Basic functionality works"
else
    echo "   ✗ Basic functionality failed"
    exit 1
fi

echo ""
echo "🎉 All tests passed! Issue resolved."
echo ""
echo "You can now run the full test suite:"
echo "   pytest tests/"
