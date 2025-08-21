# Contributing to psutil-cygwin

Thank you for your interest in contributing to psutil-cygwin! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows a Code of Conduct to ensure a welcoming environment for all contributors. By participating, you agree to abide by these guidelines:

- Be respectful and inclusive in all interactions
- Focus on constructive feedback and collaboration
- Respect differing viewpoints and experiences
- Show empathy towards other community members
- Report unacceptable behavior to the maintainers

## Getting Started

### Development Environment Setup

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/your-username/psutil-cygwin.git
   cd psutil-cygwin
   ```

2. **Set up Development Environment**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install development dependencies
   pip install -e ".[dev]"
   ```

3. **Verify Installation**:
   ```bash
   # Run tests
   python -m pytest tests/
   
   # Run style checks
   black --check psutil_cygwin/
   flake8 psutil_cygwin/
   mypy psutil_cygwin/
   ```

### Repository Structure

```
psutil-cygwin/
├── psutil_cygwin/          # Main package
│   ├── __init__.py         # Package initialization
│   ├── core.py             # Core implementation
│   └── examples/           # Example applications
├── tests/                  # Test suite
│   ├── test_unit.py        # Unit tests
│   ├── test_integration.py # Integration tests
│   └── test_psutil_cygwin.py # Comprehensive tests
├── docs/                   # Documentation
├── pyproject.toml          # Build configuration
├── README.md               # Project overview
├── CHANGELOG.md            # Version history
└── CONTRIBUTING.md         # This file
```

## Types of Contributions

### Bug Reports

When reporting bugs:

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** if available
3. **Include system information**:
   - Cygwin version
   - Python version
   - psutil-cygwin version
   - Operating system details

4. **Provide reproduction steps**:
   ```python
   # Minimal example that reproduces the bug
   import psutil_cygwin as psutil
   
   # Steps that cause the issue
   result = psutil.problematic_function()
   # Expected: X, Actual: Y
   ```

5. **Include relevant logs or error messages**

### Feature Requests

For new features:

1. **Check existing feature requests** and discussions
2. **Describe the use case** and motivation
3. **Provide examples** of desired API usage
4. **Consider compatibility** with standard psutil
5. **Discuss implementation approach** if you have ideas

### Code Contributions

#### Before You Start

1. **Create an issue** to discuss your proposed changes
2. **Check the roadmap** to see if the feature is planned
3. **Consider backward compatibility** implications
4. **Plan your implementation** approach

#### Development Guidelines

**Code Style**:
- Follow [PEP 8](https://pep8.org/) for Python code style
- Use [Black](https://github.com/psf/black) for code formatting
- Maximum line length: 88 characters
- Use meaningful variable and function names
- Add type hints where appropriate

**Documentation**:
- Write docstrings for all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings when helpful
- Update relevant documentation pages

**Testing**:
- Write tests for all new functionality
- Maintain or improve test coverage
- Include both unit tests and integration tests
- Test error conditions and edge cases

#### Implementation Standards

**Performance**:
- Minimize file I/O operations
- Cache expensive computations when appropriate
- Consider memory usage with large process lists
- Profile performance-critical code paths

**Error Handling**:
- Use appropriate psutil exception classes
- Provide informative error messages
- Handle edge cases gracefully
- Test error conditions thoroughly

**Compatibility**:
- Maintain API compatibility with psutil
- Use the same return types and structures
- Handle platform-specific differences appropriately
- Test on multiple Cygwin configurations

#### Code Review Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Write tests** for your changes:
   ```bash
   # Run tests
   python -m pytest tests/test_your_feature.py -v
   
   # Check coverage
   python -m pytest --cov=psutil_cygwin tests/
   ```

4. **Format and lint** your code:
   ```bash
   black psutil_cygwin/
   flake8 psutil_cygwin/
   mypy psutil_cygwin/
   ```

5. **Update documentation** if needed:
   ```bash
   cd docs/
   make html
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: descriptive commit message"
   ```

7. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Documentation Contributions

Documentation improvements are always welcome:

- **Fix typos and improve clarity**
- **Add missing examples**
- **Improve API documentation**
- **Create tutorials for specific use cases**
- **Translate documentation** (if internationalization is planned)

## Testing Guidelines

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_unit.py          # Unit tests only
python -m pytest tests/test_integration.py   # Integration tests only

# Run with coverage
python -m pytest --cov=psutil_cygwin tests/

# Run specific tests
python -m pytest tests/test_unit.py::TestProcessClass::test_process_name -v
```

### Writing Tests

**Unit Tests**:
- Mock external dependencies (file system, subprocess calls)
- Test individual functions in isolation
- Use parametrized tests for multiple input scenarios
- Test error conditions and edge cases

**Integration Tests**:
- Require real Cygwin environment with /proc filesystem
- Test actual system interactions
- Verify end-to-end functionality
- May be slower and environment-dependent

**Test Organization**:
```python
class TestSystemFunctions(unittest.TestCase):
    """Test system-wide functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = {...}
    
    def test_cpu_times_parsing(self):
        """Test CPU times parsing with mocked data."""
        with patch('builtins.open', mock_open(read_data="cpu 100 200 300")):
            times = psutil.cpu_times()
            self.assertEqual(times.user, 1.0)
    
    @unittest.skipUnless(Path("/proc").exists(), "Requires /proc filesystem")
    def test_cpu_times_integration(self):
        """Test CPU times with real /proc data."""
        times = psutil.cpu_times()
        self.assertGreater(times.user, 0)
```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes

### Release Checklist

1. **Pre-release**:
   - [ ] Update version in `pyproject.toml`
   - [ ] Update version in `psutil_cygwin/__init__.py`
   - [ ] Update `CHANGELOG.md` with release notes
   - [ ] Run full test suite on multiple environments
   - [ ] Update documentation if needed
   - [ ] Review and merge all intended changes

2. **Release**:
   - [ ] Create release branch: `git checkout -b release/v1.x.x`
   - [ ] Final testing and validation
   - [ ] Tag release: `git tag v1.x.x`
   - [ ] Build distribution: `python -m build`
   - [ ] Test installation: `pip install dist/psutil-cygwin-1.x.x.tar.gz`
   - [ ] Push tag: `git push origin v1.x.x`
   - [ ] Upload to PyPI: `twine upload dist/*`
   - [ ] Create GitHub release with changelog

3. **Post-release**:
   - [ ] Update documentation website
   - [ ] Announce release in discussions
   - [ ] Close related issues and milestones
   - [ ] Merge release branch to main

## Development Workflow

### Git Workflow

1. **Create feature branch**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/feature-name
   ```

2. **Make changes and commit**:
   ```bash
   # Make your changes
   git add .
   git commit -m "type: description"
   ```

3. **Keep branch updated**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/feature-name
   # Create pull request on GitHub
   ```

### Commit Message Format

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes

**Examples**:
```
feat(process): add memory_full_info() method
fix(cpu): handle missing /proc/stat gracefully
docs(api): improve Process class documentation
test(integration): add network connection tests
```

## Code Quality

### Static Analysis Tools

**Black** (Code Formatting):
```bash
# Format code
black psutil_cygwin/

# Check formatting
black --check psutil_cygwin/
```

**Flake8** (Linting):
```bash
# Run linting
flake8 psutil_cygwin/

# Configuration in pyproject.toml
```

**MyPy** (Type Checking):
```bash
# Type checking
mypy psutil_cygwin/

# Configuration in pyproject.toml
```

### Pre-commit Hooks

Set up pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Performance Guidelines

### Optimization Principles

1. **Minimize I/O Operations**:
   - Cache frequently accessed data
   - Batch file reads when possible
   - Use efficient parsing algorithms

2. **Memory Efficiency**:
   - Use generators for large datasets
   - Implement lazy loading
   - Clean up resources promptly

3. **Error Handling**:
   - Fail fast for invalid inputs
   - Use appropriate exception types
   - Provide informative error messages

### Benchmarking

```python
import time
import psutil_cygwin as psutil

def benchmark_function():
    start = time.time()
    # Function to benchmark
    result = psutil.some_function()
    end = time.time()
    print(f"Function took {end - start:.4f} seconds")
    return result
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def cpu_percent(interval: Optional[float] = None) -> float:
    """Get CPU usage percentage.
    
    Args:
        interval: Time to wait between measurements. If None,
                 returns instant percentage based on last call.
    
    Returns:
        CPU usage percentage as a float between 0.0 and 100.0.
    
    Raises:
        OSError: If /proc/stat cannot be read.
    
    Example:
        >>> import psutil_cygwin as psutil
        >>> cpu_usage = psutil.cpu_percent(interval=1.0)
        >>> print(f"CPU: {cpu_usage:.1f}%")
        CPU: 15.3%
    """
```

### Building Documentation

```bash
cd docs/
make html
# Open _build/html/index.html
```

## Getting Help

### Communication Channels

- **Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions
- **Email**: For security-related issues

### Resources

- [psutil documentation](https://psutil.readthedocs.io/) - Reference implementation
- [Cygwin documentation](https://cygwin.com/cygwin-ug-net/) - Platform information
- [Python /proc parsing](https://github.com/giampaolo/psutil) - Implementation examples

## Recognition

Contributors are recognized in:
- `CHANGELOG.md` for significant contributions
- GitHub contributors page
- Release notes for major contributions
- Special thanks in documentation

Thank you for contributing to psutil-cygwin!m pytest tests/test_unit.py::TestSystemFunctions::test_cpu_times -v

# Run tests with specific markers
python -m pytest -m "not slow" tests/
```

### Writing Tests

**Unit Tests**:
- Mock external dependencies (file system, system calls)
- Test individual functions in isolation
- Use `unittest.mock` for mocking
- Test both success and error conditions

**Integration Tests**:
- Test with real Cygwin environment
- Require actual `/proc` filesystem
- Test end-to-end functionality
- May be slower and require specific setup

**Test Structure**:
```python
import unittest
from unittest.mock import patch, mock_open
import psutil_cygwin as psutil

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_normal_case(self):
        """Test normal operation."""
        # Arrange
        # Act  
        # Assert
        pass
    
    def test_error_case(self):
        """Test error conditions."""
        with self.assertRaises(psutil.NoSuchProcess):
            # Test code that should raise exception
            pass
    
    @patch('builtins.open', new_callable=mock_open, read_data="test data")
    def test_with_mock(self, mock_file):
        """Test with mocked file system."""
        # Test using mocked data
        pass
```

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

1. **Update version numbers**:
   - `pyproject.toml`
   - `psutil_cygwin/__init__.py`
   - `docs/conf.py`

2. **Update documentation**:
   - `CHANGELOG.md`
   - API documentation if needed
   - README.md if needed

3. **Run full test suite**:
   ```bash
   python -m pytest tests/ -v
   python -m pytest tests/test_integration.py  # On Cygwin
   ```

4. **Check code quality**:
   ```bash
   black --check psutil_cygwin/
   flake8 psutil_cygwin/
   mypy psutil_cygwin/
   ```

5. **Build and test package**:
   ```bash
   python -m build
   python -m twine check dist/*
   ```

6. **Create release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

## Community Guidelines

### Communication

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code contributions
- **Email**: Security issues only

### Getting Help

- Check the documentation first
- Search existing issues and discussions
- Provide complete information when asking questions
- Be patient and respectful

### Recognition

Contributors are recognized in:
- `CHANGELOG.md` for significant contributions
- GitHub contributors page
- Release notes for major features

## Development Tips

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test specific functions
if __name__ == '__main__':
    import psutil_cygwin as psutil
    print(f"CPU: {psutil.cpu_percent()}%")
```

### Performance Testing

```python
import time
import psutil_cygwin as psutil

# Benchmark function
start = time.time()
for _ in range(1000):
    psutil.cpu_percent()
end = time.time()
print(f"Average time: {(end-start)/1000*1000:.2f}ms")
```

### Testing on Different Configurations

- Test on different Cygwin versions
- Test with different Python versions (3.6+)
- Test with different system loads
- Test with limited permissions

## Frequently Asked Questions

**Q: How do I add a new system function?**
A: Add it to `core.py`, write tests, update documentation, and ensure psutil compatibility.

**Q: How do I handle new /proc file formats?**
A: Add robust parsing with fallbacks, test edge cases, and handle version differences.

**Q: How do I maintain psutil compatibility?**
A: Use the same function signatures, return types, and exception handling as standard psutil.

**Q: How do I test without Cygwin?**
A: Use unit tests with mocked file system calls. Integration tests require real Cygwin.

**Q: How do I report security issues?**
A: Send email to the maintainers rather than creating public issues.

## Thank You

Thank you for contributing to psutil-cygwin! Your contributions help make system monitoring on Cygwin better for everyone.

For questions about contributing, please:
1. Check this document first
2. Search existing issues and discussions
3. Create a new discussion or issue if needed

We appreciate your time and effort in improving this project!
