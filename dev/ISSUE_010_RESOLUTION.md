# Issue 010 Resolution: Tests Skipped on Cygwin

## Problem Summary

**Question**: "Running on Cygwin, why would any tests be skipped?"

**Context**: The test suite was showing 3 skipped tests on Cygwin:
1. `SKIPPED [1] tests/test_pth_functionality.py:298: psutil not available (may not be installed)`
2. `SKIPPED [1] tests/test_pth_functionality.py:338: Custom setuptools commands removed during modernization`
3. `SKIPPED [1] tests/test_pth_functionality.py:352: Custom setuptools commands removed during modernization`

**Issue**: On Cygwin (the target platform), tests should NOT be skipped since psutil-cygwin is specifically designed for Cygwin environments.

## Root Cause Analysis

### 1. Transparent Import Test Skip (Line 298)
**Problem**: Test tries to import `psutil` but gets `ImportError`
```python
try:
    import psutil
except ImportError:
    self.skipTest("psutil not available (may not be installed)")
```

**Root Causes**:
- No `psutil.pth` file configured (transparent import not set up)
- Package not installed in development mode
- Standard psutil installed instead of psutil-cygwin
- Unhelpful error message that doesn't guide user to solution

### 2. Modernization Tests Skip (Lines 338 & 352)
**Problem**: Tests disabled during modernization without replacement
```python
@unittest.skip("Custom setuptools commands removed during modernization")
class TestInstallationIntegration(unittest.TestCase): ...
```

**Root Cause**: 
- Old tests referenced removed setuptools custom commands
- No modern equivalent tests created
- Lost test coverage for installation functionality

## Solution Implemented

### 1. **Improved Transparent Import Test Logic**

**Before (Problematic)**:
```python
try:
    import psutil
except ImportError:
    self.skipTest("psutil not available (may not be installed)")
```

**After (Helpful)**:
```python
# First ensure psutil_cygwin is available in development mode
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import psutil_cygwin
except ImportError:
    self.skipTest("psutil_cygwin not available (package not installed in development mode)")

# Try importing psutil - check if transparent import is working
try:
    import psutil
except ImportError:
    self.skipTest("Transparent import not configured - run 'psutil-cygwin-setup install' first")

# Check if it's our psutil_cygwin or standard psutil
if hasattr(psutil, '__name__') and psutil.__name__ == 'psutil_cygwin':
    # SUCCESS: Test the functionality
    ...
else:
    self.skipTest(f"Standard psutil detected ({psutil.__name__}), not psutil-cygwin")
```

### 2. **Added Modern Installation Tests**

**Replaced Old Tests**:
```python
class TestModernInstallationIntegration(unittest.TestCase):
    """Test integration with modern installation process."""
    
    @patch('psutil_cygwin.cygwin_check.create_psutil_pth')
    def test_modern_setup_script_calls_pth_creation(self, mock_create_pth):
        from psutil_cygwin._build.setup_script import setup_environment
        result = setup_environment()
        mock_create_pth.assert_called_once()

class TestModernCygwinDetection(unittest.TestCase):
    """Test Cygwin detection in modern architecture."""
    
    def test_cygwin_requirements_validation(self):
        from psutil_cygwin.cygwin_check import check_cygwin_requirements
        # Test actual validation logic
        ...
```

### 3. **Created Diagnostic Tools**

**diagnostic script**: `dev/diagnose_issue_010.py`
- Checks environment setup
- Validates .pth file configuration  
- Tests import behavior
- Provides step-by-step solutions

**verification script**: `dev/verify_issue_010_fix.py`
- Tests that improvements are working
- Verifies test collection and execution
- Checks for better error messages

## Expected Behavior After Fix

### On Cygwin (Target Platform)

**Properly Configured** (Zero Skips):
```bash
pip install -e .
psutil-cygwin-setup install
pytest tests/test_pth_functionality.py -v
# Result: 0 skipped, all tests pass
```

**Not Configured** (Helpful Skips):
```bash
pytest tests/test_pth_functionality.py -v
# Result: Clear error messages explaining how to fix setup
# "Transparent import not configured - run 'psutil-cygwin-setup install' first"
```

### On Non-Cygwin Platforms
- `TestRealTransparentImport` skipped (correct - requires `/proc` filesystem)
- Other tests run with mocked functionality
- No unexpected skips

## Installation Instructions for Zero Skips

For developers/testers who want all tests to pass on Cygwin:

```bash
# 1. Install package in development mode
pip install -e .

# 2. Configure transparent import
psutil-cygwin-setup install

# 3. Verify configuration
psutil-cygwin-check --transparent

# 4. Run tests (should have 0 skips)
pytest tests/test_pth_functionality.py -v
```

## Files Modified

1. **`tests/test_pth_functionality.py`**
   - Improved transparent import test logic
   - Added modern installation tests
   - Better error messages and setup instructions

2. **`dev/diagnose_issue_010.py`**
   - Comprehensive diagnostic tool
   - Checks environment, .pth files, imports
   - Provides solutions

3. **`dev/verify_issue_010_fix.py`**  
   - Verification script for the fix
   - Tests improved behavior

4. **`issue/test/010.txt`**
   - Documented the issue and resolution

## Benefits Achieved

✅ **Better User Experience**: Clear error messages explain what to do  
✅ **Actionable Feedback**: Tests guide users to proper setup  
✅ **Modern Test Coverage**: New tests for modernized installation  
✅ **Diagnostic Tools**: Help troubleshoot setup issues  
✅ **Zero Skips Possible**: When properly configured on Cygwin  

## Prevention

To prevent similar issues:
1. **Test on target platform** during development
2. **Provide setup instructions** when tests require configuration
3. **Replace removed functionality** with modern equivalents
4. **Create diagnostic tools** for complex setup requirements

## Result

The question "why would any tests be skipped on Cygwin?" is now answered:

**Before**: Tests skipped due to unclear setup requirements and missing modern tests  
**After**: Tests provide clear guidance for proper setup and comprehensive coverage

When properly configured, **zero tests should be skipped on Cygwin**.
