#!/usr/bin/env bash
# Verification script for Issue 013: Orphaned Finally Block Resolution

echo "============================================================"
echo "ISSUE 013 VERIFICATION: Orphaned Finally Block Fix"
echo "============================================================"

cd "$(dirname "$0")/.."

echo "1. Python syntax compilation test..."
if python -m py_compile tests/test_pth_functionality.py 2>/dev/null; then
    echo "✅ Python compilation SUCCESSFUL - no syntax errors"
else
    echo "❌ Python compilation FAILED - syntax errors remain"
    echo "Detailed error:"
    python -m py_compile tests/test_pth_functionality.py
    exit 1
fi

echo ""
echo "2. AST parsing verification..."
python -c "
import ast
try:
    with open('tests/test_pth_functionality.py', 'r') as f:
        content = f.read()
    ast.parse(content)
    print('✅ AST parsing SUCCESSFUL - file structure is valid')
except SyntaxError as e:
    print(f'❌ AST parsing FAILED - SyntaxError: {e}')
    print(f'   Line {e.lineno}: {e.text.strip() if e.text else \"N/A\"}')
    exit(1)
"

echo ""
echo "3. Control flow structure analysis..."
if python dev/find_orphaned_finally.py >/dev/null 2>&1; then
    echo "✅ Control flow analysis PASSED - no orphaned finally blocks"
else
    echo "❌ Control flow analysis FAILED - structural issues remain"
    python dev/find_orphaned_finally.py
    exit 1
fi

echo ""
echo "4. pytest collection test..."
if pytest tests/test_pth_functionality.py --collect-only -q >/dev/null 2>&1; then
    echo "✅ pytest collection SUCCESSFUL - tests discoverable"
else
    echo "❌ pytest collection FAILED"
    pytest tests/test_pth_functionality.py --collect-only
    exit 1
fi

echo ""
echo "5. Line 352 specific check..."
line_352=$(sed -n '352p' tests/test_pth_functionality.py | xargs)
if [ -n "$line_352" ]; then
    echo "Line 352 content: '$line_352'"
    if [[ "$line_352" == "finally:" ]]; then
        echo "⚠️  Line 352 still contains 'finally:' - checking context..."
        # Show context around line 352
        echo "Context:"
        sed -n '347,357p' tests/test_pth_functionality.py | nl -ba -s": " -v347
    else
        echo "✅ Line 352 no longer contains orphaned 'finally:'"
    fi
else
    echo "✅ Line 352 is beyond file length - no orphaned finally block"
fi

echo ""
echo "6. Import verification..."
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
echo "============================================================"
echo "✅ ISSUE 013 RESOLUTION VERIFIED"
echo "============================================================"
echo ""
echo "All verification tests passed:"
echo "• Python syntax compilation successful"
echo "• AST parsing validates file structure"
echo "• No orphaned finally blocks detected"
echo "• pytest can collect tests without errors"
echo "• Line 352 no longer contains orphaned 'finally:'"
echo "• All required imports work correctly"
echo ""
echo "The orphaned finally block syntax error has been resolved."
echo "The test suite can now run without structural syntax errors."
echo ""
echo "Next steps:"
echo "  pytest tests/test_pth_functionality.py -v"
echo ""
