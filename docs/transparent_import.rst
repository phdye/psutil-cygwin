Transparent Import Quick Start
==============================

This guide shows you how to use psutil-cygwin's transparent import feature
to make your existing psutil code work seamlessly in Cygwin environments.

Installation
------------

Install psutil-cygwin and it automatically sets up transparent importing:

.. code-block:: bash

   # Install from PyPI
   pip install psutil-cygwin

   # Verify transparent import is working
   psutil-cygwin-check --transparent

**What happens during installation:**

1. Validates you're in a Cygwin environment
2. Installs the psutil_cygwin package
3. Creates a ``psutil.pth`` file in site-packages
4. Makes ``import psutil`` transparently use psutil_cygwin

Transparent Usage
-----------------

After installation, your existing psutil code works unchanged:

.. code-block:: python

   # This is your existing code - no changes needed!
   import psutil

   # All your existing psutil code works transparently
   print(f"CPU Usage: {psutil.cpu_percent()}%")
   print(f"Memory: {psutil.virtual_memory().percent}%")
   print(f"CPU Cores: {psutil.cpu_count()}")

   # Process management works exactly the same
   for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
       print(f"{proc.info['pid']}: {proc.info['name']} ({proc.info['memory_percent']:.1f}%)")

   # All psutil functionality is available
   disk = psutil.disk_usage('/')
   connections = psutil.net_connections()
   boot_time = psutil.boot_time()

Verification
------------

Verify that transparent import is working correctly:

**Quick Check:**

.. code-block:: python

   import psutil
   print(f"Using module: {psutil.__name__}")  # Should show: psutil_cygwin
   print(f"Module location: {psutil.__file__}")

**Command-line verification:**

.. code-block:: bash

   # Comprehensive check
   psutil-cygwin-check

   # Should output:
   # ✅ Cygwin environment validation passed
   # ✅ Transparent import configured correctly
   #    You can use 'import psutil' directly

   # Detailed transparent import check
   psutil-cygwin-check --transparent

Migration from Standard psutil
------------------------------

If you have existing code using standard psutil, migration is automatic:

**Before (standard psutil):**

.. code-block:: python

   import psutil
   
   def get_system_info():
       return {
           'cpu_percent': psutil.cpu_percent(),
           'memory': psutil.virtual_memory()._asdict(),
           'processes': len(psutil.pids())
       }

**After (psutil-cygwin with transparent import):**

.. code-block:: python

   import psutil  # Now automatically uses psutil_cygwin!
   
   def get_system_info():
       return {
           'cpu_percent': psutil.cpu_percent(),
           'memory': psutil.virtual_memory()._asdict(),
           'processes': len(psutil.pids())
       }
   
   # Exactly the same code - no changes needed!

Example: System Monitor
-----------------------

Here's a complete example that works transparently:

.. code-block:: python

   #!/usr/bin/env python3
   """
   Simple system monitor using transparent psutil import.
   This exact code works with both standard psutil and psutil-cygwin.
   """
   
   import psutil
   import time
   
   def main():
       print(f"System Monitor (using {psutil.__name__})")
       print("-" * 40)
       
       while True:
           # CPU information
           cpu_percent = psutil.cpu_percent(interval=1)
           cpu_count = psutil.cpu_count()
           
           # Memory information  
           memory = psutil.virtual_memory()
           
           # Disk information
           disk = psutil.disk_usage('/')
           
           # Process count
           process_count = len(psutil.pids())
           
           # Clear screen and display info
           print(f"\033[2J\033[H")  # Clear screen
           print(f"System Monitor (using {psutil.__name__})")
           print("-" * 40)
           print(f"CPU Usage:    {cpu_percent:6.1f}% ({cpu_count} cores)")
           print(f"Memory Usage: {memory.percent:6.1f}% ({memory.used//1024**2:,} MB used)")
           print(f"Disk Usage:   {disk.used/disk.total*100:6.1f}% ({disk.used//1024**3:,} GB used)")
           print(f"Processes:    {process_count:6d}")
           
           # Top processes by memory
           print("\nTop Memory Users:")
           processes = []
           for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
               try:
                   processes.append((
                       proc.info['pid'],
                       proc.info['name'],
                       proc.info['memory_info'].rss
                   ))
               except (psutil.NoSuchProcess, psutil.AccessDenied):
                   continue
           
           # Sort and display top 5
           processes.sort(key=lambda x: x[2], reverse=True)
           for pid, name, memory in processes[:5]:
               print(f"  {pid:>6d} {name:<15s} {memory//1024**2:>6d} MB")
           
           time.sleep(5)
   
   if __name__ == '__main__':
       try:
           main()
       except KeyboardInterrupt:
           print("\nMonitoring stopped.")

Alternative: Explicit Import
----------------------------

If you prefer to be explicit about using psutil-cygwin:

.. code-block:: python

   # Explicit import (alternative to transparent import)
   import psutil_cygwin as psutil
   
   # Rest of your code is identical
   print(f"CPU: {psutil.cpu_percent()}%")

Both approaches work identically - choose based on your preference.

Troubleshooting
---------------

**Issue: "import psutil" not using psutil-cygwin**

Check if transparent import is set up:

.. code-block:: bash

   psutil-cygwin-check --transparent

If it's not working, reinstall:

.. code-block:: bash

   pip uninstall psutil-cygwin
   pip install psutil-cygwin

**Issue: Standard psutil is being used instead**

Remove standard psutil if you don't need it:

.. code-block:: bash

   pip uninstall psutil
   pip install --force-reinstall psutil-cygwin

**Issue: Virtual environment problems**

Install in each virtual environment:

.. code-block:: bash

   source myenv/bin/activate
   pip install psutil-cygwin
   psutil-cygwin-check --transparent

Advanced Usage
--------------

**Multiple Python versions:**

Each Python installation needs its own psutil-cygwin:

.. code-block:: bash

   python3.9 -m pip install psutil-cygwin
   python3.10 -m pip install psutil-cygwin

**Checking which module is loaded:**

.. code-block:: python

   import psutil
   import inspect
   
   print(f"Module: {psutil.__name__}")
   print(f"File: {psutil.__file__}")
   print(f"Functions: {[name for name, obj in inspect.getmembers(psutil) if inspect.isfunction(obj)][:5]}...")

**Working with .pth files manually:**

.. code-block:: python

   import site
   import os
   
   # Find .pth file
   for sp in site.getsitepackages() + [site.getusersitepackages()]:
       pth_file = os.path.join(sp, 'psutil.pth')
       if os.path.exists(pth_file):
           print(f"Found: {pth_file}")
           with open(pth_file) as f:
               print(f"Content: {f.read()}")

Next Steps
----------

- Explore :doc:`examples` for more usage patterns
- Read :doc:`api` for complete function reference  
- Check :doc:`compatibility` for psutil feature comparison
- See :doc:`installation` for advanced installation options
