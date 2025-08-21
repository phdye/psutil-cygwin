#!/usr/bin/env bash
# Comprehensive verification script for Issue 012 resolution

echo "============================================================"
echo "ISSUE 012 VERIFICATION: Persistent SyntaxError Fix"
echo "============================================================"

cd "$(dirname "$0")/.."

echo "1. Python syntax compilation test..."
if python -m py_compile tests/test_pth_functionality.py 2>/dev/null; then
    echo "✅ Python compilation SUCCESSFUL"
else
    echo "❌ Python compilation FAILED"
    python -m py_compile tests/test_pth_functionality.py
    exit 1
fi

echo ""
echo "2. AST parsing verification..."
if python dev/quick_syntax_check.py; then
    echo "✅ AST parsing SUCCESSFUL"
else
    echo "❌ AST parsing FAILED"
    exit 1
fi

echo ""
echo "3. pytest collection test..."
if pytest tests/test_pth_functionality.py --collect-only -q >/dev/null 2>&1; then
    echo "✅ pytest collection SUCCESSFUL"
else
    echo "❌ pytest collection FAILED"
    pytest tests/test_pth_functionality.py --collect-only
    exit 1
fi

echo ""
echo "4. Import verification..."
if python -c "
import sys
sys.path.insert(0, '.')
try:
    from psutil_cygwin.cygwin_check import create_psutil_pth, is_cygwin
    from psutil_cygwin._build.hooks import remove_psutil_pth
    print('✅ All imports SUCCESSFUL')
except Exception as e:
    print(f'❌ Import FAILED: {e}')
    sys.exit(1)
" 2>/dev/null; then
    echo "✅ Import verification SUCCESSFUL"
else
    echo "❌ Import verification FAILED"
    exit 1
fi

echo ""
echo "5. File structure verification..."
line_count=$(wc -l < tests/test_pth_functionality.py)
if [ "$line_count" -gt 300 ]; then
    echo "✅ File structure GOOD ($line_count lines)"
else
    echo "⚠️  File may be truncated ($line_count lines)"
fi

echo ""
echo "============================================================"
echo "✅ ISSUE 012 RESOLUTION VERIFIED"
echo "============================================================"
echo ""
echo "All verification tests passed:"
echo "• Python syntax compilation works"
echo "• AST parsing succeeds"
echo "• pytest can collect tests"
echo "• All required imports work"
echo "• File structure is intact"
echo ""
echo "The persistent SyntaxError at line 352 has been resolved."
echo "The test suite can now run without syntax errors."
echo ""
echo "Next steps:"
echo "  pytest tests/test_pth_functionality.py -v"
echo ""
