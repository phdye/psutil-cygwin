Compatibility with psutil
=======================

psutil-cygwin aims to provide maximum compatibility with the standard psutil library while optimizing for Cygwin environments. This page details the compatibility status of all features.

API Compatibility
------------------

Function Compatibility Matrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Function Compatibility
   :header-rows: 1
   :widths: 30 15 15 40

   * - Function
     - psutil-cygwin
     - Standard psutil
     - Notes
   * - ``cpu_times()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``cpu_percent()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``cpu_count()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``virtual_memory()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``swap_memory()``
     - ⚠️ Partial
     - ✅ Full
     - ``sin``/``sout`` always 0
   * - ``disk_usage()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``disk_partitions()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``disk_io_counters()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``net_connections()``
     - ⚠️ Partial
     - ✅ Full
     - Cannot map to processes
   * - ``net_io_counters()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``boot_time()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``users()``
     - ⚠️ Basic
     - ✅ Full
     - Limited information
   * - ``pids()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``process_iter()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``pid_exists()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility

Process Class Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Process Methods
   :header-rows: 1
   :widths: 30 15 15 40

   * - Method
     - psutil-cygwin
     - Standard psutil
     - Notes
   * - ``name()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``exe()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``cmdline()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``status()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``ppid()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``create_time()``
     - ⚠️ Approximate
     - ✅ Precise
     - Limited by clock tick resolution
   * - ``memory_info()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``cpu_times()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``open_files()``
     - ⚠️ Limited
     - ✅ Full
     - Excludes device files
   * - ``connections()``
     - ❌ Not implemented
     - ✅ Full
     - Complex inode matching required
   * - ``children()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``parent()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``is_running()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``kill()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``terminate()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility
   * - ``wait()``
     - ✅ Full
     - ✅ Full
     - Complete compatibility

Exception Compatibility
~~~~~~~~~~~~~~~~~~~~~~~

All psutil exception classes are fully compatible:

- ``NoSuchProcess`` - Process not found
- ``AccessDenied`` - Permission denied
- ``TimeoutExpired`` - Operation timeout

Return Type Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~

All named tuples and return types match psutil exactly:

- ``CPUTimes`` - CPU time information
- ``VirtualMemory`` - Memory statistics
- ``SwapMemory`` - Swap memory information
- ``DiskUsage`` - Disk usage information
- ``DiskIO`` - Disk I/O statistics
- ``NetworkConnection`` - Network connection information
- ``Address`` - Network address information
- ``User`` - User session information

Missing Features
----------------

Features Not Available
~~~~~~~~~~~~~~~~~~~~~~

Some psutil features are not available in Cygwin environments:

**Hardware Sensors**:
- ``sensors_temperatures()`` - Not available via /proc
- ``sensors_fans()`` - Not available via /proc
- ``sensors_battery()`` - Not available via /proc

**Windows-Specific**:
- ``win_service_iter()`` - Windows services (use Cygwin services instead)
- ``win_service_get()`` - Windows service information

**Advanced Networking**:
- Process-specific network connections - Complex inode matching required
- Network interface addresses - Limited /proc information

**System-Specific**:
- CPU frequency information - Not consistently available
- Detailed hardware information - Limited /proc data

Behavioral Differences
----------------------

Performance Characteristics
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Faster Operations**:
- Process listing - Direct /proc access vs. API calls
- System information - Efficient file parsing
- Memory statistics - Single /proc/meminfo read

**Slower Operations**:
- Individual process details - Multiple file reads per process
- Network connections - Text parsing vs. binary data

**Memory Usage**:
- Lower baseline memory usage - No C extensions
- Comparable memory scaling - Similar data structures

Data Accuracy
~~~~~~~~~~~~~

**Timing Resolution**:
- Process creation time accuracy depends on system clock tick resolution
- CPU times have standard /proc resolution limitations

**Missing Data**:
- Some network connection states may be simplified
- Swap I/O statistics require additional parsing not yet implemented

Platform Differences
~~~~~~~~~~~~~~~~~~~~

**File System Access**:
- Relies on /proc filesystem availability
- Permission restrictions may differ from native Windows

**Process Information**:
- Command line parsing handles null separators correctly
- Executable paths resolved through /proc/pid/exe symlinks

Migration Guide
---------------

From Standard psutil
~~~~~~~~~~~~~~~~~~~~

Migrating from standard psutil to psutil-cygwin is straightforward:

**Step 1: Replace Import**

.. code-block:: python

   # Before
   import psutil
   
   # After
   import psutil_cygwin as psutil

**Step 2: Handle Missing Features**

.. code-block:: python

   # Check for unavailable features
   try:
       temp_sensors = psutil.sensors_temperatures()
   except AttributeError:
       print("Sensors not available on this platform")
   
   # Alternative approaches for missing features
   if hasattr(psutil, 'sensors_battery'):
       battery = psutil.sensors_battery()
   else:
       print("Battery information not available")

**Step 3: Adjust Expectations**

.. code-block:: python

   # Network connections may not include process mapping
   connections = psutil.net_connections()
   for conn in connections:
       if conn.pid is None:
           print(f"Connection {conn.laddr} -> {conn.raddr} (unknown process)")
       else:
           print(f"Connection {conn.laddr} -> {conn.raddr} (PID {conn.pid})")

Testing Compatibility
---------------------

Compatibility Test Suite
~~~~~~~~~~~~~~~~~~~~~~~~

Run the compatibility test suite to verify psutil-cygwin works with your code:

.. code-block:: bash

   # Test basic compatibility
   python -c "
   import psutil_cygwin as psutil
   
   # Test core functions
   assert hasattr(psutil, 'cpu_percent')
   assert hasattr(psutil, 'virtual_memory')
   assert hasattr(psutil, 'Process')
   
   print('Basic compatibility: OK')
   "
   
   # Test return types
   python -c "
   import psutil_cygwin as psutil
   
   # Check return types match expectations
   cpu = psutil.cpu_times()
   assert hasattr(cpu, 'user')
   assert hasattr(cpu, 'system')
   
   mem = psutil.virtual_memory()
   assert hasattr(mem, 'total')
   assert hasattr(mem, 'percent')
   
   print('Return types: OK')
   "

Version Compatibility
~~~~~~~~~~~~~~~~~~~~~

psutil-cygwin maintains API compatibility with psutil versions:

- **psutil 5.9.x**: Full core API compatibility
- **psutil 5.8.x**: Full core API compatibility  
- **psutil 5.7.x**: Core API compatibility (some newer features unavailable)

Example Migration
~~~~~~~~~~~~~~~~

Here's a complete example showing migration:

.. code-block:: python

   # Original psutil code
   import psutil
   
   def system_info_original():
       cpu_pct = psutil.cpu_percent(interval=1)
       memory = psutil.virtual_memory()
       
       processes = []
       for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
           processes.append(proc.info)
       
       return {
           'cpu': cpu_pct,
           'memory': memory.percent,
           'processes': processes
       }
   
   # Migrated psutil-cygwin code (identical!)
   import psutil_cygwin as psutil
   
   def system_info_migrated():
       cpu_pct = psutil.cpu_percent(interval=1)
       memory = psutil.virtual_memory()
       
       processes = []
       for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
           processes.append(proc.info)
       
       return {
           'cpu': cpu_pct,
           'memory': memory.percent,
           'processes': processes
       }
   
   # Both functions work identically!

Best Practices
--------------

Writing Compatible Code
~~~~~~~~~~~~~~~~~~~~~~~

To write code that works with both standard psutil and psutil-cygwin:

.. code-block:: python

   import sys
   
   try:
       import psutil
   except ImportError:
       import psutil_cygwin as psutil
   
   def get_system_info():
       # Use only features available in both
       return {
           'cpu_percent': psutil.cpu_percent(),
           'memory_percent': psutil.virtual_memory().percent,
           'process_count': len(psutil.pids()),
           'boot_time': psutil.boot_time()
       }
   
   def get_network_info():
       connections = psutil.net_connections()
       
       # Handle potential missing process mapping
       mapped_connections = []
       unmapped_connections = []
       
       for conn in connections:
           if conn.pid is not None:
               mapped_connections.append(conn)
           else:
               unmapped_connections.append(conn)
       
       return {
           'mapped': len(mapped_connections),
           'unmapped': len(unmapped_connections),
           'total': len(connections)
       }

Feature Detection
~~~~~~~~~~~~~~~~

Detect available features at runtime:

.. code-block:: python

   import psutil_cygwin as psutil
   
   def get_available_features():
       features = {
           'basic_system': True,  # Always available
           'process_management': True,  # Always available
           'sensors': hasattr(psutil, 'sensors_temperatures'),
           'windows_services': hasattr(psutil, 'win_service_iter'),
           'network_process_mapping': False  # Check at runtime
       }
       
       # Test network process mapping
       try:
           connections = psutil.net_connections()
           if connections and any(conn.pid is not None for conn in connections):
               features['network_process_mapping'] = True
       except:
           pass
       
       return features

Future Compatibility
-------------------

Planned Enhancements
~~~~~~~~~~~~~~~~~~~

Future versions of psutil-cygwin will improve compatibility:

**Version 1.1.0 (Planned)**:
- Enhanced network connection to process mapping
- Additional process statistics from /proc files
- Improved sensor information where available

**Version 1.2.0 (Planned)**:
- Windows service integration where applicable
- Extended system information
- Performance optimizations

**Version 2.0.0 (Future)**:
- Full psutil 6.x compatibility
- Async API support
- Extended Cygwin-specific features

Compatibility Promise
~~~~~~~~~~~~~~~~~~~~

psutil-cygwin maintains backward compatibility within major versions:

- **API stability**: Function signatures remain unchanged
- **Return types**: Named tuples and data structures stable
- **Behavior**: Core functionality behavior preserved
- **Migration**: Smooth upgrade path for new versions

For any compatibility questions or issues, please refer to the `issue tracker <https://github.com/your-username/psutil-cygwin/issues>`_.
