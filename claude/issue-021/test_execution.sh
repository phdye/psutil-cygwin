#!/bin/bash
set -x

cd "$(dirname "$0")/.."

echo "🧪 Running test verification for issue 021 resolution..."

# Test our fixes first
echo "Testing fix verification script..."
python claude/issue-021/test_fixes.py

echo ""
echo "🔍 Testing individual failures from issue/test/021.txt..."

# Test 1: CPU times system index
pytest tests/test_unit.py::TestSystemFunctions::test_cpu_times -v

# Test 2: CPU times edge cases  
pytest tests/test_unit_comprehensive.py::TestSystemFunctionsComprehensive::test_cpu_times_edge_cases -v

# Test 3: Extreme CPU values
pytest tests/test_stress.py::TestExtremeEdgeCases::test_extreme_cpu_values -v

# Test 4: High frequency calls (performance)
pytest tests/test_stress.py::TestStressConditions::test_high_frequency_calls -v

# Test 5: Corrupted proc filesystem simulation
pytest tests/test_stress.py::TestErrorRecoveryAndRobustness::test_corrupted_proc_filesystem_simulation -v

# Test 6: PTH creation user site fallback
pytest tests/test_pth_comprehensive.py::TestPthFileCreationComprehensive::test_pth_creation_user_site_fallback -v

# Test 7: PTH permission error handling
pytest tests/test_pth_functionality.py::TestPthFileCreation::test_create_psutil_pth_permission_error -v

echo ""
echo "🏁 Running full test suite to verify overall status..."
time pytest tests/ --tb=short

echo ""
echo "✅ Issue 021 resolution testing complete!"
echo "Expected: 88 passed, 0 failed"
