#!/bin/bash
set -x

cd "$(dirname "$0")/.."

echo "🧪 Running final test for issue 020 resolution..."

# Run the specific failing tests
echo "Testing individual failures..."

# Test 1: CPU times edge cases
python -m pytest tests/test_unit_comprehensive.py::TestSystemFunctionsComprehensive::test_cpu_times_edge_cases -v

# Test 2: Corrupted proc filesystem
python -m pytest tests/test_stress.py::TestErrorRecoveryAndRobustness::test_corrupted_proc_filesystem_simulation -v

# Test 3: Intermittent file errors  
python -m pytest tests/test_stress.py::TestErrorRecoveryAndRobustness::test_intermittent_file_errors -v

# Test 4: PTH creation user site fallback
python -m pytest tests/test_pth_comprehensive.py::TestPthFileCreationComprehensive::test_pth_creation_user_site_fallback -v

echo ""
echo "🏁 Running full test suite to verify overall status..."
python -m pytest tests/ --tb=short

echo ""
echo "✅ Issue 020 resolution testing complete!"
