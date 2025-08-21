Development Guide
=================

This guide covers development practices, architecture decisions, and contribution guidelines for psutil-cygwin.

Development Environment
-----------------------

Setting Up Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow these steps to set up a complete development environment:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/your-username/psutil-cygwin.git
   cd psutil-cygwin

   # Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Cygwin

   # Install development dependencies
   pip install -e ".[dev]"

   # Install pre-commit hooks
   pre-commit install

   # Verify installation
   python -c "import psutil_cygwin; print('Success!')"

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

The development environment includes:

- **Testing**: pytest, pytest-cov, pytest-mock
- **Code Quality**: black, flake8, mypy, pre-commit
- **Documentation**: sphinx, sphinx-rtd-theme, sphinx-autodoc-typehints
- **Build Tools**: build, twine

Architecture Overview
--------------------

Design Principles
~~~~~~~~~~~~~~~~

psutil-cygwin follows these key design principles:

1. **API Compatibility**: Maintain exact compatibility with psutil
2. **Performance**: Optimize for Cygwin's /proc filesystem
3. **Reliability**: Robust error handling and edge case management
4. **Simplicity**: Pure Python implementation, no external dependencies
5. **Maintainability**: Clean, well-documented code structure

Module Structure
~~~~~~~~~~~~~~~

.. code-block::

   psutil_cygwin/
   ├── __init__.py          # Public API exports
   ├── core.py              # Main implementation
   └── examples/            # Example applications
       ├── __init__.py
       ├── system_monitor.py
       └── process_manager.py

Core Components
~~~~~~~~~~~~~~

**Exception Classes**:
- Custom exception hierarchy matching psutil
- Enhanced error information with PID/name context
- Proper inheritance from built-in exceptions

**Process Class**:
- Lazy loading of process information
- Efficient /proc file parsing
- Robust error handling for process state changes

**System Functions**:
- Direct /proc filesystem access
- Caching of expensive operations
- Fallback mechanisms for missing data

Implementation Details
---------------------

/proc Filesystem Access
~~~~~~~~~~~~~~~~~~~~~~

psutil-cygwin leverages Cygwin's /proc filesystem:

.. code-block:: python

   # CPU information from /proc/stat
   def cpu_times():
       with open('/proc/stat', 'r') as f:
           line = f.readline().strip()
           if line.startswith('cpu '):
               fields = line.split()[1:]
               # Convert clock ticks to seconds
               clock_ticks_per_sec = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
               times = [int(x) / clock_ticks_per_sec for x in fields[:5]]
               return CPUTimes(user=times[0], system=times[2], ...)

   # Process information from /proc/[pid]/
   def process_name(pid):
       try:
           with open(f'/proc/{pid}/comm', 'r') as f:
               return f.read().strip()
       except FileNotFoundError:
           raise NoSuchProcess(pid=pid)

Error Handling Strategy
~~~~~~~~~~~~~~~~~~~~~~

Comprehensive error handling ensures reliability:

.. code-block:: python

   def robust_process_operation(pid):
       try:
           # Attempt operation
           return perform_operation(pid)
       except FileNotFoundError:
           # Process disappeared
           raise NoSuchProcess(pid=pid)
       except PermissionError:
           # Access denied
           raise AccessDenied(pid=pid)
       except (OSError, IOError) as e:
           # Other system errors
           if "No such file" in str(e):
               raise NoSuchProcess(pid=pid)
           raise

Performance Optimizations
~~~~~~~~~~~~~~~~~~~~~~~~~

Several optimizations improve performance:

**Caching**:
.. code-block:: python

   # Cache boot time (doesn't change)
   def boot_time_cached():
       if not hasattr(boot_time_cached, '_cached_time'):
           with open('/proc/stat', 'r') as f:
               for line in f:
                   if line.startswith('btime'):
                       boot_time_cached._cached_time = float(line.split()[1])
                       break
       return boot_time_cached._cached_time

**Lazy Loading**:
.. code-block:: python

   class Process:
       def __init__(self, pid):
           self.pid = pid
           self._proc_path = f"/proc/{pid}"
           # Don't validate existence until first access
       
       def name(self):
           # Load only when requested
           return self._read_proc_file("comm")

**Efficient Parsing**:
.. code-block:: python

   def parse_proc_stat(content):
       # Optimized parsing of /proc/stat format
       fields = content.split()
       return {
           'user': int(fields[1]),
           'nice': int(fields[2]),
           'system': int(fields[3]),
           # ... parse only needed fields
       }

Testing Strategy
---------------

Test Organization
~~~~~~~~~~~~~~~~

Tests are organized into several categories:

**Unit Tests** (``tests/test_unit.py``):
- Mock external dependencies
- Test individual functions in isolation
- Fast execution, no external requirements

**Integration Tests** (``tests/test_integration.py``):
- Test with real /proc filesystem
- Verify actual system interactions
- Require Cygwin environment

**Comprehensive Tests** (``tests/test_psutil_cygwin.py``):
- End-to-end functionality testing
- Performance benchmarks
- Real-world scenario validation

Writing Tests
~~~~~~~~~~~~

Follow these patterns for writing tests:

.. code-block:: python

   import unittest
   from unittest.mock import patch, mock_open
   import psutil_cygwin as psutil

   class TestCPUFunctions(unittest.TestCase):
       
       @patch('builtins.open', new_callable=mock_open,
              read_data="cpu  100 200 300 400 500\\n")
       @patch('os.sysconf')
       def test_cpu_times_parsing(self, mock_sysconf, mock_file):
           """Test CPU times parsing with mocked data."""
           mock_sysconf.return_value = 100  # Clock ticks per second
           
           times = psutil.cpu_times()
           
           self.assertEqual(times.user, 1.0)  # 100/100
           self.assertEqual(times.system, 3.0)  # 300/100
           mock_file.assert_called_once_with('/proc/stat', 'r')

       @unittest.skipUnless(Path("/proc").exists(), "Requires /proc filesystem")
       def test_cpu_times_integration(self):
           """Test CPU times with real /proc data."""
           times = psutil.cpu_times()
           
           self.assertIsInstance(times, psutil.CPUTimes)
           self.assertGreaterEqual(times.user, 0)
           self.assertGreaterEqual(times.system, 0)

Running Tests
~~~~~~~~~~~~

Execute tests with different scopes:

.. code-block:: bash

   # Run all tests
   python -m pytest tests/

   # Run only unit tests (fast)
   python -m pytest tests/test_unit.py -v

   # Run only integration tests (requires Cygwin /proc)
   python -m pytest tests/test_integration.py -v

   # Run with coverage
   python -m pytest --cov=psutil_cygwin tests/

   # Run specific test
   python -m pytest tests/test_unit.py::TestCPUFunctions::test_cpu_times_parsing -v

Code Quality Standards
----------------------

Formatting and Style
~~~~~~~~~~~~~~~~~~~~

We use automated tools to maintain code quality:

.. code-block:: bash

   # Format code with Black
   black psutil_cygwin/

   # Check style with Flake8
   flake8 psutil_cygwin/

   # Type checking with MyPy
   mypy psutil_cygwin/

Code Style Guidelines
~~~~~~~~~~~~~~~~~~~~

Follow these conventions:

**Function Names**: Use descriptive names matching psutil
.. code-block:: python

   # Good
   def cpu_percent(interval=None):
       pass

   def virtual_memory():
       pass

   # Avoid
   def get_cpu():
       pass

**Docstrings**: Use Google-style docstrings
.. code-block:: python

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
           >>> cpu_usage = psutil.cpu_percent(interval=1.0)
           >>> print(f"CPU: {cpu_usage:.1f}%")
       """

**Error Handling**: Use specific exception types
.. code-block:: python

   # Good
   try:
       proc = Process(pid)
       return proc.name()
   except NoSuchProcess:
       return None
   except AccessDenied:
       return "ACCESS_DENIED"

   # Avoid generic exceptions
   except Exception:
       return None

Documentation Standards
-----------------------

API Documentation
~~~~~~~~~~~~~~~~

All public functions must have complete docstrings:

.. code-block:: python

   def disk_usage(path: str) -> DiskUsage:
       """Get disk usage statistics for a path.
       
       Args:
           path: Filesystem path to check (e.g., '/', '/home').
       
       Returns:
           DiskUsage named tuple with total, used, and free bytes.
       
       Raises:
           OSError: If path doesn't exist or cannot be accessed.
           
       Example:
           >>> usage = disk_usage('/')
           >>> print(f"Disk: {usage.used}/{usage.total} bytes")
       
       Note:
           Values are in bytes. Use format_bytes() helper for 
           human-readable output.
       """

Documentation Build
~~~~~~~~~~~~~~~~~~

Build documentation locally:

.. code-block:: bash

   cd docs/
   make html
   
   # View documentation
   open _build/html/index.html

Contributing Guidelines
----------------------

Contribution Workflow
~~~~~~~~~~~~~~~~~~~~~

1. **Fork and Clone**:
   .. code-block:: bash

      git clone https://github.com/your-username/psutil-cygwin.git
      cd psutil-cygwin

2. **Create Feature Branch**:
   .. code-block:: bash

      git checkout -b feature/your-feature-name

3. **Make Changes**:
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation as needed

4. **Test Changes**:
   .. code-block:: bash

      # Run tests
      python -m pytest tests/
      
      # Check style
      black --check psutil_cygwin/
      flake8 psutil_cygwin/
      mypy psutil_cygwin/

5. **Commit and Push**:
   .. code-block:: bash

      git add .
      git commit -m "feat: add new feature description"
      git push origin feature/your-feature-name

6. **Create Pull Request**:
   - Provide clear description
   - Reference any related issues
   - Ensure CI passes

Code Review Process
~~~~~~~~~~~~~~~~~~

All contributions go through code review:

**Review Criteria**:
- API compatibility with psutil
- Code quality and style compliance
- Test coverage for new features
- Documentation completeness
- Performance considerations

**Review Timeline**:
- Initial review within 3-5 days
- Follow-up reviews within 1-2 days
- Merge after approval and CI success

Release Process
--------------

Version Management
~~~~~~~~~~~~~~~~~

We follow Semantic Versioning (SemVer):

- **MAJOR** (X.0.0): Breaking API changes
- **MINOR** (1.X.0): New features, backward compatible
- **PATCH** (1.0.X): Bug fixes, backward compatible

Release Checklist
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 1. Update version numbers
   # - pyproject.toml
   # - psutil_cygwin/__init__.py
   
   # 2. Update CHANGELOG.md
   
   # 3. Run full test suite
   python -m pytest tests/
   
   # 4. Build and test package
   python -m build
   pip install dist/psutil-cygwin-*.tar.gz
   
   # 5. Tag release
   git tag v1.x.x
   git push origin v1.x.x
   
   # 6. GitHub Actions handles PyPI upload

Debugging and Troubleshooting
-----------------------------

Common Issues
~~~~~~~~~~~~

**Permission Errors**:
.. code-block:: python

   # Debug permission issues
   import os
   import stat
   
   def debug_proc_access(pid):
       proc_path = f"/proc/{pid}"
       try:
           st = os.stat(proc_path)
           print(f"Permissions: {stat.filemode(st.st_mode)}")
           print(f"Owner: {st.st_uid}, Group: {st.st_gid}")
       except OSError as e:
           print(f"Cannot access {proc_path}: {e}")

**Performance Issues**:
.. code-block:: python

   # Profile performance
   import time
   import psutil_cygwin as psutil
   
   def profile_function(func, *args, **kwargs):
       start = time.time()
       result = func(*args, **kwargs)
       end = time.time()
       print(f"{func.__name__} took {end - start:.4f} seconds")
       return result
   
   # Usage
   processes = profile_function(list, psutil.process_iter())

Debugging Tools
~~~~~~~~~~~~~~

**Enable Debug Output**:
.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   # Add debug prints to core functions
   def _read_proc_file(path):
       logging.debug(f"Reading {path}")
       # ... rest of function

**Test with Minimal Example**:
.. code-block:: python

   # Minimal test to isolate issues
   import psutil_cygwin as psutil
   
   try:
       print(f"PIDs: {len(psutil.pids())}")
       print(f"CPU: {psutil.cpu_percent()}")
       print(f"Memory: {psutil.virtual_memory().percent}")
   except Exception as e:
       print(f"Error: {e}")
       import traceback
       traceback.print_exc()

Future Development
-----------------

Roadmap
~~~~~~

**Version 1.1.0**:
- Enhanced network connection mapping
- Additional process statistics
- Performance optimizations

**Version 1.2.0**:
- Async API support
- Extended compatibility features
- Advanced monitoring capabilities

**Version 2.0.0**:
- Python 3.12+ type hints
- Structured logging
- Plugin architecture

Contributing Areas
~~~~~~~~~~~~~~~~~

Areas where contributions are especially welcome:

1. **Performance Optimization**: Faster /proc parsing
2. **Feature Enhancement**: Additional psutil compatibility
3. **Testing**: More comprehensive test coverage
4. **Documentation**: Examples and tutorials
5. **Platform Support**: Extended Cygwin compatibility

Getting Help
-----------

If you need help with development:

- **Documentation**: Read this guide and API docs
- **Issues**: Search existing GitHub issues
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Ask for feedback on draft PRs

Contact the maintainers for questions about:
- Architecture decisions
- Major feature planning
- Release coordination
- Security issues
