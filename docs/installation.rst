Installation
============

psutil-cygwin is designed to work seamlessly in Cygwin environments. Choose the installation method that best fits your needs.

Requirements
------------

Before installing psutil-cygwin, ensure your environment meets these requirements:

**System Requirements:**

- Cygwin environment (latest version recommended)
- ``/proc`` filesystem mounted and accessible
- Python 3.6 or higher

**Cygwin Packages:**

Install these packages through the Cygwin installer:

.. code-block:: bash

   # Essential packages
   python3
   python3-pip
   procps-ng  # For /proc filesystem support

   # Optional but recommended
   python3-setuptools
   python3-wheel
   git

**Verify Prerequisites:**

Check that your environment is properly configured:

.. code-block:: bash

   # Check Python version
   python3 --version

   # Verify /proc filesystem
   ls -la /proc/stat /proc/meminfo /proc/mounts

   # Test basic tools
   ps --version
   who --version

Installation Methods
--------------------

Method 1: PyPI Installation (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install psutil-cygwin:

.. code-block:: bash

   # Install from PyPI
   pip install psutil-cygwin

   # Or with Python 3 explicitly
   python3 -m pip install psutil-cygwin

   # Verify installation
   python3 -c "import psutil_cygwin; print('Installation successful!')"

**Transparent psutil Replacement**

psutil-cygwin automatically creates a ``psutil.pth`` file during installation,
making it completely transparent to use:

.. code-block:: python

   # After installation, this works automatically!
   import psutil  # Uses psutil_cygwin transparently
   
   # Your existing psutil code works unchanged
   print(f"CPU: {psutil.cpu_percent()}%")
   for proc in psutil.process_iter():
       print(f"{proc.pid}: {proc.name()}")

**How Transparent Import Works:**

1. During installation, a ``psutil.pth`` file is created in your Python site-packages
2. This file contains: ``import sys; sys.modules['psutil'] = __import__('psutil_cygwin')``
3. When Python starts, it automatically executes .pth files
4. This makes ``import psutil`` transparently use psutil_cygwin
5. No code changes needed - existing psutil scripts work immediately!

**Verify Transparent Import:**

.. code-block:: bash

   # Check that transparent import is working
   python3 -c "
   import psutil
   print(f'Using: {psutil.__name__}')
   print(f'CPU: {psutil.cpu_percent()}%')
   "
   
   # Should output:
   # Using: psutil_cygwin
   # CPU: X.X%

Method 2: Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For development or to get the latest features:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/your-username/psutil-cygwin.git
   cd psutil-cygwin

   # Install in development mode
   pip install -e .

   # Or install with development dependencies
   pip install -e ".[dev]"

Method 3: From Source Archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer to install from a source archive:

.. code-block:: bash

   # Download and extract the source
   wget https://github.com/your-username/psutil-cygwin/archive/v1.0.0.tar.gz
   tar -xzf v1.0.0.tar.gz
   cd psutil-cygwin-1.0.0

   # Install
   pip install .

Verifying Installation
----------------------

After installation, verify that psutil-cygwin works correctly:

**Quick Test (Transparent Import):**

.. code-block:: bash

   # Test transparent import - this should "just work"
   python3 -c "
   import psutil  # Should use psutil_cygwin automatically
   print(f'Module: {psutil.__name__}')
   print(f'CPU: {psutil.cpu_percent()}%')
   print(f'Memory: {psutil.virtual_memory().percent}%')
   print(f'Processes: {len(psutil.pids())}')
   print('Transparent import verified!')
   "

**Alternative Test (Explicit Import):**

.. code-block:: bash

   # Run the built-in test with explicit import
   python3 -c "
   import psutil_cygwin as psutil
   print(f'CPU: {psutil.cpu_percent()}%')
   print(f'Memory: {psutil.virtual_memory().percent}%')
   print(f'Processes: {len(psutil.pids())}')
   print('Installation verified!')
   "

**Comprehensive Test:**

.. code-block:: bash

   # Run the test suite
   python3 -m pytest tests/

   # Or run the integration tests
   python3 tests/test_psutil_cygwin.py

**Console Scripts:**

Test the command-line utilities:

.. code-block:: bash

   # System monitor
   psutil-cygwin-monitor

   # Process manager
   psutil-cygwin-proc list
   
   # Environment and transparency check
   psutil-cygwin-check

**Verify Transparent Import Setup:**

.. code-block:: bash

   # Check if .pth file was created properly
   python3 -c "
   import site
   import os
   for sp in site.getsitepackages() + [site.getusersitepackages()]:
       pth_file = os.path.join(sp, 'psutil.pth')
       if os.path.exists(pth_file):
           print(f'Found psutil.pth: {pth_file}')
           with open(pth_file) as f:
               print('Content:', f.read().strip())
           break
   else:
       print('No psutil.pth file found')
   "

Configuration
-------------

Environment Setup
~~~~~~~~~~~~~~~~~

For optimal performance, ensure these environment variables are set:

.. code-block:: bash

   # Add to ~/.bashrc or ~/.profile
   export PATH="/usr/bin:$PATH"
   export PYTHONPATH="/usr/lib/python3.x/site-packages:$PYTHONPATH"

**Optional Configuration:**

Create a configuration file ``~/.psutil-cygwin.conf``:

.. code-block:: ini

   [settings]
   # Enable debug mode
   debug = false
   
   # Set polling intervals (seconds)
   cpu_interval = 1.0
   memory_interval = 5.0
   
   # Process iteration limits
   max_processes = 1000

Troubleshooting
---------------

Common Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Issue: ``/proc filesystem not found``**

.. code-block:: bash

   # Check if /proc is mounted
   mount | grep proc
   
   # If not mounted, mount it
   mount -t proc proc /proc

**Issue: ``Permission denied accessing /proc files``**

.. code-block:: bash

   # Check permissions
   ls -la /proc/stat /proc/meminfo
   
   # Ensure you're in the right groups
   groups

**Issue: ``Module not found after installation``**

.. code-block:: bash

   # Check installation location
   python3 -c "import sys; print(sys.path)"
   
   # Reinstall with user flag
   pip install --user psutil-cygwin

**Issue: ``Transparent import not working``**

If ``import psutil`` doesn't use psutil_cygwin:

.. code-block:: bash

   # Check if .pth file exists
   python3 -c "
   import site, os
   for sp in site.getsitepackages() + [site.getusersitepackages()]:
       pth = os.path.join(sp, 'psutil.pth')
       if os.path.exists(pth):
           print(f'Found: {pth}')
           break
   else:
       print('psutil.pth not found - reinstall may be needed')
   "
   
   # If .pth file is missing, reinstall:
   pip uninstall psutil-cygwin
   pip install psutil-cygwin

**Issue: ``Standard psutil detected instead of psutil-cygwin``**

If you have both psutil and psutil-cygwin installed:

.. code-block:: bash

   # Check what's imported
   python3 -c "import psutil; print(psutil.__file__)"
   
   # Remove standard psutil if not needed
   pip uninstall psutil
   
   # Or force psutil-cygwin precedence
   pip install --force-reinstall psutil-cygwin

**Issue: ``Tests fail with 'No such process' errors``**

This usually indicates permission or timing issues:

.. code-block:: bash

   # Run tests with elevated privileges
   # Or skip integration tests
   python3 -m pytest tests/test_unit.py -v

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

For better performance in resource-constrained environments:

.. code-block:: python

   import psutil_cygwin as psutil
   
   # Use cached boot time instead of reading /proc/stat repeatedly
   boot_time = psutil.boot_time()
   
   # Batch process information gathering
   processes = list(psutil.process_iter(['pid', 'name', 'memory_info']))

Virtual Environment Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install in a Python virtual environment:

.. code-block:: bash

   # Create virtual environment
   python3 -m venv psutil-cygwin-env
   
   # Activate it
   source psutil-cygwin-env/bin/activate
   
   # Install psutil-cygwin
   pip install psutil-cygwin
   
   # Deactivate when done
   deactivate

Upgrading
---------

To upgrade to a newer version:

.. code-block:: bash

   # Upgrade from PyPI
   pip install --upgrade psutil-cygwin
   
   # Or force reinstall
   pip install --force-reinstall psutil-cygwin

Uninstallation
--------------

To remove psutil-cygwin:

.. code-block:: bash

   # Uninstall the package (automatically removes .pth file)
   pip uninstall psutil-cygwin
   
   # Clean up any configuration files
   rm -f ~/.psutil-cygwin.conf

**Manual .pth File Cleanup (if needed):**

In rare cases, you may need to manually remove the .pth file:

.. code-block:: bash

   # Find and remove .pth file manually
   python3 -c "
   import site, os
   for sp in site.getsitepackages() + [site.getusersitepackages()]:
       pth = os.path.join(sp, 'psutil.pth')
       if os.path.exists(pth):
           print(f'Removing: {pth}')
           os.remove(pth)
   "

**Verify Clean Uninstall:**

.. code-block:: bash

   # Check that psutil import fails or uses standard psutil
   python3 -c "
   try:
       import psutil
       print(f'psutil available: {psutil.__name__}')
       if psutil.__name__ == 'psutil_cygwin':
           print('WARNING: psutil-cygwin still active!')
       else:
           print('Standard psutil or no psutil available')
   except ImportError:
       print('No psutil available (clean uninstall)')
   "

Advanced Installation Topics
-----------------------------

Transparent Import Technical Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The transparent import mechanism uses Python's ``.pth`` file system:

**How .pth Files Work:**

1. Python automatically processes ``.pth`` files in site-packages at startup
2. Lines in ``.pth`` files that start with ``import`` are executed as Python code
3. Our ``psutil.pth`` contains: ``import sys; sys.modules['psutil'] = __import__('psutil_cygwin')``
4. This pre-loads psutil_cygwin into sys.modules under the name 'psutil'
5. When code does ``import psutil``, Python finds it already loaded and returns psutil_cygwin

**Multiple Python Installations:**

If you have multiple Python installations in Cygwin:

.. code-block:: bash

   # Install for specific Python version
   python3.9 -m pip install psutil-cygwin
   python3.10 -m pip install psutil-cygwin
   
   # Each creates its own .pth file

**Virtual Environments:**

Transparent import works in virtual environments:

.. code-block:: bash

   python3 -m venv myenv
   source myenv/bin/activate
   pip install psutil-cygwin  # Creates .pth in venv site-packages
   python -c "import psutil; print(psutil.__name__)"  # Should show psutil_cygwin

**Compatibility with Standard psutil:**

psutil-cygwin is API-compatible but functionally different:

.. code-block:: python

   # All these work the same:
   import psutil  # (transparently uses psutil_cygwin)
   
   # But implementation differs:
   # - psutil_cygwin uses /proc filesystem
   # - Standard psutil uses Windows APIs
   # - Some features may have different limitations

Next Steps
----------

Once installed, proceed to:

- :doc:`quickstart` - Learn basic usage with transparent import
- :doc:`examples` - See practical examples
- :doc:`api` - Explore the full API reference
- :doc:`compatibility` - Understand psutil compatibility details
