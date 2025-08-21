# Modern Installation Guide for psutil-cygwin

## Overview

The psutil-cygwin project has been modernized to use **PEP 517/518** standards and eliminate deprecation warnings. This guide explains the new installation methods and the changes made.

## ✅ Modern Installation Methods (Recommended)

### Standard Installation
```bash
# Install from PyPI (when published)
pip install psutil-cygwin

# Install from source
pip install .

# Install in development mode
pip install -e .

# Build wheel and install
python -m build
pip install dist/psutil_cygwin-*.whl
```

### Post-Installation Setup
After installation, run the setup command to configure transparent import:
```bash
# Set up transparent import (creates psutil.pth)
psutil-cygwin-setup install

# Check environment and configuration
psutil-cygwin-check

# Check transparent import specifically
psutil-cygwin-check --transparent
```

## ❌ Deprecated Methods (Avoid)

These methods will show deprecation warnings and should be avoided:
```bash
# DEPRECATED - shows warnings
python setup.py install
python setup.py develop
python setup.py build
```

## What Changed

### 1. Eliminated setuptools Custom Commands

**Before (Deprecated)**:
- Custom `CygwinInstallCommand` class
- Custom `CygwinDevelopCommand` class  
- Warning suppression in setuptools commands
- Complex `cmdclass` configuration

**After (Modern)**:
- Pure PEP 517/518 build system
- Entry point-based post-installation setup
- No custom setuptools commands
- No warning suppression needed

### 2. Modern Build Configuration

**pyproject.toml Changes**:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

# Modern entry point for setup
[project.scripts]
psutil-cygwin-setup = "psutil_cygwin._build.setup_script:main"

# No warning filters needed!
[tool.pytest.ini_options]
# filterwarnings section removed - no warnings to suppress
```

**setup.py Simplification**:
```python
# Minimal setup.py for backward compatibility only
from setuptools import setup
setup()  # All configuration in pyproject.toml
```

### 3. New Architecture

```
psutil_cygwin/
├── _build/                    # New build system
│   ├── __init__.py
│   ├── hooks.py              # Modern build hooks
│   ├── setup_script.py       # Post-install setup
│   └── backend.py            # Custom build backend
├── cygwin_check.py           # Updated environment checker
└── ...
```

## Installation Workflow

### For End Users

1. **Install the package**:
   ```bash
   pip install psutil-cygwin
   ```

2. **Set up transparent import**:
   ```bash
   psutil-cygwin-setup install
   ```

3. **Verify installation**:
   ```bash
   psutil-cygwin-check
   python -c "import psutil; print(psutil.__name__)"
   ```

### For Developers

1. **Clone and install in development mode**:
   ```bash
   git clone <repository-url>
   cd psutil-cygwin
   pip install -e ".[dev]"
   ```

2. **Set up development environment**:
   ```bash
   psutil-cygwin-setup install
   ```

3. **Run tests** (clean output, no warnings):
   ```bash
   pytest tests/
   ```

4. **Build for distribution**:
   ```bash
   python -m build
   ```

## Benefits Achieved

✅ **No deprecation warnings** - Root causes eliminated, not suppressed  
✅ **Modern build system** - PEP 517/518 compliant  
✅ **Clean test output** - No warning noise in CI/CD  
✅ **Future-proof** - Uses current Python packaging standards  
✅ **Maintainable** - Less complex build logic  
✅ **Professional** - Clean installation experience  

## Available Commands

After installation, these commands are available:

- `psutil-cygwin-monitor` - System monitoring utility
- `psutil-cygwin-proc` - Process management utility  
- `psutil-cygwin-check` - Environment validation
- `psutil-cygwin-setup` - Setup and cleanup utility

## Troubleshooting

### Transparent Import Not Working

```bash
# Check configuration
psutil-cygwin-check --transparent

# Reinstall if needed
pip uninstall psutil-cygwin
pip install psutil-cygwin
psutil-cygwin-setup install
```

### Environment Issues

```bash
# Validate Cygwin environment
psutil-cygwin-check

# Get detailed environment info
psutil-cygwin-check --info
```

### Clean Reinstall

```bash
# Remove old installation
pip uninstall psutil-cygwin
psutil-cygwin-setup uninstall  # Clean up .pth files

# Fresh install
pip install psutil-cygwin
psutil-cygwin-setup install
```

## Migration from Old Version

If you have an existing installation with the old setup.py commands:

1. **Uninstall cleanly**:
   ```bash
   pip uninstall psutil-cygwin
   # Remove any leftover .pth files manually if needed
   ```

2. **Install modern version**:
   ```bash
   pip install psutil-cygwin
   psutil-cygwin-setup install
   ```

3. **Verify**:
   ```bash
   psutil-cygwin-check
   ```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Install psutil-cygwin
  run: |
    pip install psutil-cygwin
    psutil-cygwin-setup install

- name: Run tests
  run: pytest tests/  # Clean output, no warnings

- name: Verify installation  
  run: psutil-cygwin-check
```

This modern approach provides a much cleaner, more maintainable, and future-proof installation experience while eliminating all deprecation warnings through proper modern practices rather than suppression.
