#!/bin/bash
# Test 023 Resolution Verification
#
# This script runs the specific tests that were failing to verify they now pass

echo "🧪 Test 023 - Verification of Fixes"
echo "=================================="
echo ""

# Change to project directory
cd "$(dirname "$0")/../.."

echo "📍 Project directory: $(pwd)"
echo ""

# Test the three specific failing tests
echo "🔍 Running the three previously failing tests..."
echo ""

echo "1. Testing: TestPthFileCreation.test_create_psutil_pth_fallback_to_user (cleanup issue)"
python -m pytest tests/test_pth_functionality.py::TestPthFileCreation::test_create_psutil_pth_fallback_to_user -v -s
test1_result=$?

echo ""
echo "2. Testing: TestErrorRecoveryAndRobustness.test_corrupted_proc_filesystem_simulation (binary data)"
python -m pytest tests/test_stress.py::TestErrorRecoveryAndRobustness::test_corrupted_proc_filesystem_simulation -v -s  
test2_result=$?

echo ""
echo "3. Testing: TestSystemFunctions.test_cpu_count (import path issue)"
python -m pytest tests/test_unit.py::TestSystemFunctions::test_cpu_count -v -s
test3_result=$?

echo ""
echo "=" * 60
echo "SUMMARY OF FIXES:"
echo "=" * 60

if [ $test1_result -eq 0 ]; then
    echo "✅ Test 1 (test_create_psutil_pth_fallback_to_user): PASSED"
else
    echo "❌ Test 1 (test_create_psutil_pth_fallback_to_user): FAILED"
fi

if [ $test2_result -eq 0 ]; then
    echo "✅ Test 2 (test_corrupted_proc_filesystem_simulation): PASSED"
else
    echo "❌ Test 2 (test_corrupted_proc_filesystem_simulation): FAILED"
fi

if [ $test3_result -eq 0 ]; then
    echo "✅ Test 3 (test_cpu_count): PASSED"
else
    echo "❌ Test 3 (test_cpu_count): FAILED"
fi

echo ""

# Calculate overall result
total_failed=$(( (1-$test1_result) + (1-$test2_result) + (1-$test3_result) ))

if [ $total_failed -eq 0 ]; then
    echo "🎉 ALL FIXES SUCCESSFUL! Test 023 issues have been resolved."
    echo ""
    echo "The following changes were made:"
    echo "  • Fixed test cleanup to use shutil.rmtree for subdirectories"
    echo "  • Enhanced cpu_count() to handle binary data from mocks"
    echo "  • Fixed mock import path for _is_mocking_active function"
    echo ""
    echo "Ready to commit changes and close Test 023."
    exit 0
else
    echo "⚠️  $total_failed test(s) still failing. Additional investigation needed."
    exit 1
fi
