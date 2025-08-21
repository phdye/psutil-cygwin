Quick Start Guide
=================

This guide will get you up and running with psutil-cygwin in minutes.

Basic Usage
-----------

Import and Basic System Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil

   # CPU information
   print(f"CPU Usage: {psutil.cpu_percent()}%")
   print(f"CPU Count: {psutil.cpu_count()}")
   
   # Memory information  
   mem = psutil.virtual_memory()
   print(f"Memory: {mem.percent}% used ({mem.used//1024**3}GB/{mem.total//1024**3}GB)")
   
   # System uptime
   import time
   boot_time = psutil.boot_time()
   uptime = time.time() - boot_time
   print(f"Uptime: {uptime/3600:.1f} hours")

Process Management
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil

   # List all running processes
   for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
       try:
           print(f"PID {proc.info['pid']}: {proc.info['name']} "
                 f"({proc.info['memory_percent']:.1f}%)")
       except (psutil.NoSuchProcess, psutil.AccessDenied):
           pass

   # Get information about a specific process
   proc = psutil.Process(1234)  # Replace with actual PID
   print(f"Process: {proc.name()}")
   print(f"Status: {proc.status()}")
   print(f"Memory: {proc.memory_info().rss // 1024**2} MB")

Disk and Network Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil

   # Disk usage
   disk = psutil.disk_usage('/')
   print(f"Disk: {disk.used//1024**3}GB used, {disk.free//1024**3}GB free")

   # Disk partitions
   for partition in psutil.disk_partitions():
       print(f"{partition.device} -> {partition.mountpoint} ({partition.fstype})")

   # Network connections
   connections = psutil.net_connections()
   print(f"Network connections: {len(connections)}")

Common Patterns
---------------

System Monitoring Loop
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil
   import time

   def monitor_system():
       while True:
           # Get system stats
           cpu = psutil.cpu_percent(interval=1)
           memory = psutil.virtual_memory()
           
           # Clear screen and display
           print("\\033[2J\\033[H", end="")  # ANSI clear screen
           print("System Monitor")
           print("-" * 20)
           print(f"CPU: {cpu:6.1f}%")
           print(f"Memory: {memory.percent:6.1f}%")
           print(f"Available: {memory.available//1024**2:6d} MB")
           
           time.sleep(1)

   # Run monitor (Ctrl+C to exit)
   monitor_system()

Finding Top Memory Processes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil

   def top_memory_processes(limit=10):
       processes = []
       
       for proc in psutil.process_iter():
           try:
               mem_info = proc.memory_info()
               processes.append({
                   'pid': proc.pid,
                   'name': proc.name(),
                   'memory': mem_info.rss
               })
           except (psutil.NoSuchProcess, psutil.AccessDenied):
               continue
       
       # Sort by memory usage
       processes.sort(key=lambda x: x['memory'], reverse=True)
       
       print(f"Top {limit} processes by memory usage:")
       print("PID     Name                Memory (MB)")
       print("-" * 40)
       
       for proc in processes[:limit]:
           print(f"{proc['pid']:7d} {proc['name']:15s} "
                 f"{proc['memory']//1024**2:10d}")

   top_memory_processes()

Process Tree Visualization
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil

   def print_process_tree(proc, indent=0):
       try:
           print("  " * indent + f"{proc.pid}: {proc.name()}")
           children = proc.children()
           for child in children:
               print_process_tree(child, indent + 1)
       except (psutil.NoSuchProcess, psutil.AccessDenied):
           pass

   def show_process_tree():
       # Find root processes (no parent or parent is init)
       for proc in psutil.process_iter():
           try:
               if proc.ppid() in [0, 1]:  # Root process
                   print_process_tree(proc)
           except (psutil.NoSuchProcess, psutil.AccessDenied):
               continue

   show_process_tree()

Error Handling
--------------

Robust Process Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil

   def safe_process_info(pid):
       try:
           proc = psutil.Process(pid)
           
           # Gather information with error handling
           info = {}
           
           try:
               info['name'] = proc.name()
           except psutil.AccessDenied:
               info['name'] = 'ACCESS_DENIED'
           
           try:
               info['status'] = proc.status()
           except psutil.AccessDenied:
               info['status'] = 'unknown'
           
           try:
               mem = proc.memory_info()
               info['memory_mb'] = mem.rss // 1024**2
           except psutil.AccessDenied:
               info['memory_mb'] = 0
           
           return info
           
       except psutil.NoSuchProcess:
           return None

   # Usage
   for pid in psutil.pids():
       info = safe_process_info(pid)
       if info:
           print(f"PID {pid}: {info}")

Performance Tips
----------------

Efficient Process Iteration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil

   # Instead of calling methods multiple times
   def inefficient():
       for proc in psutil.process_iter():
           try:
               name = proc.name()
               memory = proc.memory_info().rss
               cpu = proc.cpu_times()
           except (psutil.NoSuchProcess, psutil.AccessDenied):
               pass

   # Use process_iter with attrs parameter (more efficient)
   def efficient():
       for proc in psutil.process_iter(['name', 'memory_info', 'cpu_times']):
           try:
               name = proc.info['name']
               memory = proc.info['memory_info'].rss
               cpu = proc.info['cpu_times']
           except (psutil.NoSuchProcess, psutil.AccessDenied):
               pass

Caching Boot Time
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psutil_cygwin as psutil

   # Cache boot time since it doesn't change
   BOOT_TIME = psutil.boot_time()

   def get_process_uptime(proc):
       create_time = proc.create_time()
       return BOOT_TIME - create_time  # Use cached boot time

Console Applications
--------------------

Simple System Information Tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   #!/usr/bin/env python3
   import psutil_cygwin as psutil
   import sys

   def main():
       if len(sys.argv) > 1 and sys.argv[1] == '--json':
           # JSON output
           import json
           data = {
               'cpu_percent': psutil.cpu_percent(),
               'memory': psutil.virtual_memory()._asdict(),
               'disk': psutil.disk_usage('/')._asdict(),
               'boot_time': psutil.boot_time()
           }
           print(json.dumps(data, indent=2))
       else:
           # Human-readable output
           print("System Information")
           print("=" * 20)
           print(f"CPU Usage: {psutil.cpu_percent()}%")
           
           mem = psutil.virtual_memory()
           print(f"Memory: {mem.percent:.1f}% ({mem.used//1024**3}GB/{mem.total//1024**3}GB)")
           
           disk = psutil.disk_usage('/')
           print(f"Disk Usage: {disk.used//1024**3}GB/{disk.total//1024**3}GB")
           
           print(f"Processes: {len(psutil.pids())}")

   if __name__ == '__main__':
       main()

Process Killer Tool
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   #!/usr/bin/env python3
   import psutil_cygwin as psutil
   import sys

   def kill_by_name(process_name):
       killed = 0
       for proc in psutil.process_iter(['pid', 'name']):
           if proc.info['name'] == process_name:
               try:
                   proc.terminate()
                   print(f"Terminated {process_name} (PID {proc.info['pid']})")
                   killed += 1
               except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                   print(f"Could not terminate PID {proc.info['pid']}: {e}")
       
       return killed

   def main():
       if len(sys.argv) != 2:
           print("Usage: python kill_proc.py <process_name>")
           sys.exit(1)
       
       process_name = sys.argv[1]
       killed = kill_by_name(process_name)
       print(f"Killed {killed} processes named '{process_name}'")

   if __name__ == '__main__':
       main()

Next Steps
----------

Now that you're familiar with the basics:

- Explore the :doc:`api` for complete function reference
- Check out more :doc:`examples` for advanced usage patterns
- Learn about :doc:`compatibility` with standard psutil
- Consider :doc:`development` if you want to contribute
