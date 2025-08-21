API Reference
=============

This page provides detailed documentation for all functions, classes, and constants in psutil-cygwin.

.. currentmodule:: psutil_cygwin

System Functions
---------------

CPU Functions
~~~~~~~~~~~~~

.. autofunction:: cpu_times

.. autofunction:: cpu_percent

.. autofunction:: cpu_count

Memory Functions
~~~~~~~~~~~~~~~~

.. autofunction:: virtual_memory

.. autofunction:: swap_memory

Disk Functions
~~~~~~~~~~~~~~

.. autofunction:: disk_usage

.. autofunction:: disk_partitions

.. autofunction:: disk_io_counters

Network Functions
~~~~~~~~~~~~~~~~~

.. autofunction:: net_connections

.. autofunction:: net_io_counters

System Functions
~~~~~~~~~~~~~~~~

.. autofunction:: boot_time

.. autofunction:: users

Process Functions
-----------------

Process Management
~~~~~~~~~~~~~~~~~~

.. autofunction:: pids

.. autofunction:: process_iter

.. autofunction:: pid_exists

Process Class
~~~~~~~~~~~~~

.. autoclass:: Process
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

.. autoexception:: NoSuchProcess
   :members:
   :show-inheritance:

.. autoexception:: AccessDenied
   :members:
   :show-inheritance:

.. autoexception:: TimeoutExpired
   :members:
   :show-inheritance:

Named Tuples
------------

System Named Tuples
~~~~~~~~~~~~~~~~~~~

.. autodata:: CPUTimes
   :annotation: = namedtuple('CPUTimes', ['user', 'system', 'idle', 'interrupt', 'dpc'])

   CPU times information.
   
   :param float user: Time spent in user mode
   :param float system: Time spent in system mode  
   :param float idle: Time spent idle
   :param float interrupt: Time spent servicing interrupts
   :param float dpc: Time spent in deferred procedure calls (Windows-specific, always 0)

.. autodata:: VirtualMemory
   :annotation: = namedtuple('VirtualMemory', ['total', 'available', 'percent', 'used', 'free'])

   Virtual memory information.
   
   :param int total: Total physical memory in bytes
   :param int available: Available memory in bytes
   :param float percent: Percentage of memory used
   :param int used: Used memory in bytes
   :param int free: Free memory in bytes

.. autodata:: SwapMemory
   :annotation: = namedtuple('SwapMemory', ['total', 'used', 'free', 'percent', 'sin', 'sout'])

   Swap memory information.
   
   :param int total: Total swap memory in bytes
   :param int used: Used swap memory in bytes
   :param int free: Free swap memory in bytes
   :param float percent: Percentage of swap used
   :param int sin: Bytes swapped in from disk
   :param int sout: Bytes swapped out to disk

.. autodata:: DiskUsage
   :annotation: = namedtuple('DiskUsage', ['total', 'used', 'free'])

   Disk usage information.
   
   :param int total: Total disk space in bytes
   :param int used: Used disk space in bytes  
   :param int free: Free disk space in bytes

.. autodata:: DiskIO
   :annotation: = namedtuple('DiskIO', ['read_count', 'write_count', 'read_bytes', 'write_bytes', 'read_time', 'write_time'])

   Disk I/O statistics.
   
   :param int read_count: Number of reads
   :param int write_count: Number of writes
   :param int read_bytes: Bytes read
   :param int write_bytes: Bytes written
   :param int read_time: Time spent reading (ms)
   :param int write_time: Time spent writing (ms)

Network Named Tuples
~~~~~~~~~~~~~~~~~~~~~

.. autodata:: NetworkConnection
   :annotation: = namedtuple('NetworkConnection', ['fd', 'family', 'type', 'laddr', 'raddr', 'status', 'pid'])

   Network connection information.
   
   :param int fd: File descriptor (may be None)
   :param str family: Address family ('AF_INET', 'AF_INET6')
   :param str type: Socket type ('tcp', 'udp')  
   :param Address laddr: Local address
   :param Address raddr: Remote address (may be None)
   :param str status: Connection status
   :param int pid: Process ID (may be None)

.. autodata:: Address
   :annotation: = namedtuple('Address', ['ip', 'port'])

   Network address information.
   
   :param str ip: IP address
   :param int port: Port number

User Named Tuples
~~~~~~~~~~~~~~~~~~

.. autodata:: User
   :annotation: = namedtuple('User', ['name', 'terminal', 'host', 'started', 'pid'])

   Logged in user information.
   
   :param str name: Username
   :param str terminal: Terminal device
   :param str host: Hostname (may be empty)
   :param float started: Login time as timestamp
   :param int pid: Process ID (may be None)

Constants
---------

Version Information
~~~~~~~~~~~~~~~~~~~

.. autodata:: __version__
   :annotation: = "1.0.0"

   Version string for the package.

.. autodata:: version_info
   :annotation: = (1, 0, 0)

   Version information as a tuple of integers.

Usage Examples
--------------

Basic System Information
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil
   
   # CPU information
   times = psutil.cpu_times()
   print(f"User: {times.user}s, System: {times.system}s")
   
   usage = psutil.cpu_percent(interval=1)
   print(f"CPU Usage: {usage}%")
   
   # Memory information
   mem = psutil.virtual_memory()
   print(f"Memory: {mem.percent}% used")
   
   # Disk information
   disk = psutil.disk_usage('/')
   percent_used = (disk.used / disk.total) * 100
   print(f"Disk: {percent_used:.1f}% used")

Process Management
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil
   
   # List all processes
   for proc in psutil.process_iter():
       try:
           print(f"{proc.pid}: {proc.name()}")
       except (psutil.NoSuchProcess, psutil.AccessDenied):
           pass
   
   # Get specific process info
   proc = psutil.Process(1234)
   print(f"Name: {proc.name()}")
   print(f"Status: {proc.status()}")
   print(f"Memory: {proc.memory_info().rss} bytes")
   
   # Process relationships
   children = proc.children()
   parent = proc.parent()

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil
   
   try:
       proc = psutil.Process(99999)  # Non-existent process
   except psutil.NoSuchProcess as e:
       print(f"Process not found: {e}")
   
   try:
       proc = psutil.Process(1)  # May be restricted
       name = proc.name()
   except psutil.AccessDenied as e:
       print(f"Access denied: {e}")
   
   try:
       proc.wait(timeout=5.0)
   except psutil.TimeoutExpired as e:
       print(f"Timeout: {e}")

Performance Considerations
--------------------------

Efficient Process Iteration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working with many processes, consider these performance tips:

.. code-block:: python

   import psutil_cygwin as psutil
   
   # Efficient: specify needed attributes
   for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
       info = proc.info
       print(f"{info['pid']}: {info['name']} - {info['memory_info'].rss}")
   
   # Less efficient: multiple method calls
   for proc in psutil.process_iter():
       try:
           pid = proc.pid
           name = proc.name()
           memory = proc.memory_info().rss
           print(f"{pid}: {name} - {memory}")
       except (psutil.NoSuchProcess, psutil.AccessDenied):
           pass

Caching Strategy
~~~~~~~~~~~~~~~~

For frequently accessed information that doesn't change:

.. code-block:: python

   import psutil_cygwin as psutil
   
   # Cache boot time (doesn't change)
   BOOT_TIME = psutil.boot_time()
   
   # Cache CPU count (rarely changes)
   CPU_COUNT = psutil.cpu_count()
   
   def get_uptime():
       return time.time() - BOOT_TIME

Implementation Notes
--------------------

Data Sources
~~~~~~~~~~~~

psutil-cygwin reads information from various ``/proc`` filesystem files:

- **CPU information**: ``/proc/stat``, ``/proc/cpuinfo``
- **Memory information**: ``/proc/meminfo``
- **Process information**: ``/proc/[pid]/stat``, ``/proc/[pid]/status``, ``/proc/[pid]/cmdline``
- **Disk information**: ``/proc/mounts``, ``/proc/diskstats``
- **Network information**: ``/proc/net/tcp``, ``/proc/net/udp``, ``/proc/net/dev``

Limitations
~~~~~~~~~~~

Some limitations compared to full psutil:

- **Network process mapping**: Cannot associate network connections with specific processes
- **Advanced CPU stats**: Some Windows-specific CPU statistics are not available
- **Real-time updates**: Some statistics may have slight delays due to filesystem access
- **Permission restrictions**: Some process information requires elevated privileges

Thread Safety
~~~~~~~~~~~~~~

psutil-cygwin is generally thread-safe for read operations, but:

- Process objects may become invalid if the underlying process terminates
- Concurrent access to the same Process object should be handled carefully
- System-wide functions are safe to call from multiple threads

See Also
--------

- :doc:`quickstart` - Getting started guide
- :doc:`examples` - Practical usage examples  
- :doc:`compatibility` - Compatibility with standard psutil
