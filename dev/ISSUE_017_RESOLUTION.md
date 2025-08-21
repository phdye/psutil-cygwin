# Issue 017 Resolution: Mock Patch Target Incorrect

## Problem Summary

**Error**: `AssertionError: Expected 'create_psutil_pth' to have been called once. Called 0 times.`

**Paradox**: The test output clearly showed the function **was** being called successfully:
```
✅ Created psutil.pth: /usr/local/lib/python3.9/site-packages/psutil.pth
```

**Root Cause**: Mock patch was targeting the function where it's **defined** instead of where it's **used**.

## Technical Analysis

### The Mock Patching Problem

**How Python Imports Work**:
```python
# In setup_script.py:
from psutil_cygwin.cygwin_check import create_psutil_pth

def setup_environment():
    pth_file = create_psutil_pth()  # Uses local reference
```

**What the Test Was Doing (Wrong)**:
```python
@patch('psutil_cygwin.cygwin_check.create_psutil_pth')  # Patches original
def test_modern_setup_script_calls_pth_creation(self, mock_create_pth):
    # setup_environment() still uses its local imported reference!
```

**The Issue**:
1. `setup_script.py` imports the function and gets a **local reference**
2. Test patches the **original location** in `cygwin_check` module
3. The **local reference** in `setup_script` is unaffected by the patch
4. Real function gets called, mock never gets called
5. Test assertion fails even though function actually worked

### Mock Patching Rules

**Golden Rule**: **Patch where it's USED, not where it's DEFINED**

**Correct Approach**:
```python
@patch('psutil_cygwin._build.setup_script.create_psutil_pth')  # Patch local reference
def test_modern_setup_script_calls_pth_creation(self, mock_create_pth):
    # Now the mock intercepts the local reference!
```

## Solution Applied

### 1. **Fixed Setup Script Test**

**Before (Broken)**:
```python
@patch('psutil_cygwin.cygwin_check.is_cygwin')
@patch('psutil_cygwin.cygwin_check.create_psutil_pth')
def test_modern_setup_script_calls_pth_creation(self, mock_create_pth, mock_is_cygwin):
    mock_is_cygwin.return_value = True
    mock_create_pth.return_value = '/site-packages/psutil.pth'
    
    result = setup_environment()
    
    mock_create_pth.assert_called_once()  # ❌ Fails - mock never called
```

**After (Fixed)**:
```python
@patch('psutil_cygwin._build.setup_script.create_psutil_pth')
@patch('psutil_cygwin._build.setup_script.check_cygwin_requirements')
def test_modern_setup_script_calls_pth_creation(self, mock_check_cygwin, mock_create_pth):
    mock_check_cygwin.return_value = True
    mock_create_pth.return_value = '/site-packages/psutil.pth'
    
    result = setup_environment()
    
    mock_check_cygwin.assert_called_once()  # ✅ Works - mock intercepted
    mock_create_pth.assert_called_once()    # ✅ Works - mock intercepted
```

### 2. **Fixed Cleanup Script Test**

**Before (Broken)**:
```python
@patch('psutil_cygwin._build.hooks.remove_psutil_pth')  # Wrong target
```

**After (Fixed)**:
```python
@patch('psutil_cygwin._build.setup_script.remove_psutil_pth')  # Correct target
```

## Key Technical Insights

### 1. **Import Binding Behavior**
```python
# This creates a local binding:
from module import function

# Later patches to 'module.function' don't affect the local 'function'
```

### 2. **Mock Target Selection**
```python
# ❌ Wrong - patches where defined
@patch('original_module.function')

# ✅ Right - patches where used  
@patch('using_module.function')
```

### 3. **Import vs Assignment**
```python
# Import binding (harder to patch):
from module import function

# Module reference (easier to patch):
import module
module.function()  # Can patch 'module.function'
```

## Expected Results

**Test Outcomes**:
- ✅ `test_modern_setup_script_calls_pth_creation` - passes
- ✅ `test_modern_cleanup_script_calls_pth_removal` - passes  
- ✅ Total: 57 passed, 0 failed, 1 skipped

**Mock Behavior**:
- ✅ Mocks properly intercept function calls
- ✅ Assertions validate expected behavior
- ✅ No actual file system operations during testing

## Prevention Strategies

### 1. **Mock Patching Best Practices**
```python
# Always patch where the function is used:
@patch('module_that_calls.function_name')

# Not where it's defined:
@patch('module_that_defines.function_name')  # Usually wrong
```

### 2. **Import Strategy for Testability**
```python
# Less testable (creates local binding):
from module import function

# More testable (keeps module reference):
import module
module.function()
```

### 3. **Test Design Patterns**
```python
# Verify the right target:
def test_function():
    with patch('target_module.function') as mock_func:
        # Call the code under test
        result = function_under_test()
        
        # Verify mock was called
        mock_func.assert_called_once()
```

## Lessons Learned

### 1. **Understanding Python's Import System**
- `from module import function` creates local bindings
- These bindings are independent of the original module
- Patches must target the local binding, not the original

### 2. **Mock Patching Strategy**
- Always consider where functions are actually called from
- Patch the path that the code under test actually uses
- Test the patch location before writing complex test logic

### 3. **Debugging Mock Issues**
- If a mock isn't being called but output shows the function ran, suspect patching location
- Check import statements in the module under test
- Verify patch target matches actual call path

## Result

**Issue 017 is RESOLVED**. The mock patching strategy has been corrected to target functions where they are used rather than where they are defined. This ensures that:

✅ **Proper Interception**: Mocks actually intercept function calls  
✅ **Accurate Testing**: Test assertions validate real behavior  
✅ **Isolation**: Tests don't perform actual file system operations  
✅ **Reliability**: Test results are deterministic and meaningful  

The modern installation integration tests now properly validate the setup and cleanup functionality without side effects.
