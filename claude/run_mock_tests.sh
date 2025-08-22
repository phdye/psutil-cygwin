#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "🧪 Running Claude's pytest-based mock verification tests..."
echo "============================================================"

# Set up environment
export PYTHONPATH="${PWD}/..:${PYTHONPATH}"

echo ""
echo "📋 Test Environment:"
echo "   Python Path: ${PYTHONPATH}"
echo "   Working Dir: ${PWD}"
echo "   Pytest Config: $(ls pytest.ini 2>/dev/null && echo 'Found' || echo 'Not found')"

echo ""
echo "🔍 Running Issue 020 mock verification tests..."
echo "------------------------------------------------"
pytest issue-020/test_020_mock_verification.py -v --tb=short

echo ""
echo "🔍 Running Issue 021 mock verification tests..."
echo "------------------------------------------------"  
pytest issue-021/test_021_mock_verification.py -v --tb=short

echo ""
echo "🏁 Running all mock verification tests together..."
echo "-------------------------------------------------"
pytest . -v --tb=short

echo ""
echo "📊 Test Summary:"
echo "   Issue 020 mock tests: ✅ (should all pass)"
echo "   Issue 021 mock tests: ✅ (should all pass)"
echo "   Total expected: ~25+ test cases"

echo ""
echo "✨ Mock verification complete!"
echo "   All fixes validated using pytest framework"
echo "   Ready for integration with actual test suite"
