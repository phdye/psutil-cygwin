psutil-cygwin Documentation
==========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   examples
   compatibility
   development
   changelog

Overview
--------

psutil-cygwin is a drop-in replacement for the popular psutil library that works seamlessly on Cygwin environments. It leverages Cygwin's unique ``/proc`` pseudo-filesystem to provide comprehensive system and process information without requiring external dependencies or compilation.

Key Features
------------

- **Drop-in compatibility**: Same API as standard psutil
- **Zero dependencies**: Pure Python implementation using only the standard library
- **Cygwin optimized**: Designed specifically for Cygwin environments
- **Complete coverage**: System info, process management, disk/network monitoring
- **High performance**: Direct ``/proc`` filesystem access
- **Well tested**: Comprehensive unit and integration test suites

Quick Example
-------------

.. code-block:: python

   import psutil_cygwin as psutil

   # System information
   print(f"CPU Usage: {psutil.cpu_percent()}%")
   print(f"Memory: {psutil.virtual_memory().percent}%")
   print(f"Boot time: {psutil.boot_time()}")

   # Process management
   for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
       print(f"{proc.info['pid']}: {proc.info['name']} ({proc.info['memory_percent']:.1f}%)")

Why psutil-cygwin?
------------------

While the standard psutil library is excellent for most environments, it can be challenging to install and configure on Cygwin due to compilation requirements and dependency management. psutil-cygwin solves this by:

1. **Eliminating compilation**: Pure Python implementation means no C extensions to build
2. **Leveraging Cygwin's strengths**: Uses the ``/proc`` filesystem that Cygwin provides
3. **Maintaining compatibility**: Exact same API means existing code works unchanged
4. **Optimizing for Cygwin**: Designed specifically for the Cygwin environment

Installation
------------

.. code-block:: bash

   # From PyPI (recommended)
   pip install psutil-cygwin

   # From source
   git clone https://github.com/your-username/psutil-cygwin.git
   cd psutil-cygwin
   pip install -e .

Requirements
------------

- Cygwin environment with ``/proc`` filesystem mounted
- Python 3.6 or higher
- Standard Cygwin tools: ``ps``, ``who``, ``df``, ``mount``

Compatibility
-------------

psutil-cygwin implements the core psutil API and maintains compatibility with:

- **System functions**: CPU, memory, disk, network statistics
- **Process management**: Process listing, information, control
- **Named tuples**: All return types match psutil exactly
- **Exception classes**: ``NoSuchProcess``, ``AccessDenied``, ``TimeoutExpired``

For detailed compatibility information, see the :doc:`compatibility` page.

Support
-------

- **Documentation**: https://psutil-cygwin.readthedocs.io/
- **Issues**: https://github.com/your-username/psutil-cygwin/issues
- **Discussions**: https://github.com/your-username/psutil-cygwin/discussions

License
-------

psutil-cygwin is released under the MIT License. See the LICENSE file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
