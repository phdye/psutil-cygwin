Examples
========

This page provides practical examples of using psutil-cygwin for common system monitoring and process management tasks.

System Monitoring
-----------------

Basic System Information
~~~~~~~~~~~~~~~~~~~~~~~~

Get an overview of system resources:

.. code-block:: python

   import psutil_cygwin as psutil
   import time

   def system_overview():
       """Display comprehensive system information."""
       print("System Overview")
       print("=" * 50)
       
       # CPU information
       cpu_count = psutil.cpu_count()
       cpu_times = psutil.cpu_times()
       cpu_percent = psutil.cpu_percent(interval=1)
       
       print(f"CPU Cores: {cpu_count}")
       print(f"CPU Usage: {cpu_percent:.1f}%")
       print(f"CPU Times: User={cpu_times.user:.1f}s, System={cpu_times.system:.1f}s")
       
       # Memory information
       memory = psutil.virtual_memory()
       swap = psutil.swap_memory()
       
       print(f"Memory: {memory.percent:.1f}% used ({memory.used//1024**3}GB/{memory.total//1024**3}GB)")
       print(f"Swap: {swap.percent:.1f}% used ({swap.used//1024**2}MB/{swap.total//1024**2}MB)")
       
       # Disk information
       disk = psutil.disk_usage('/')
       disk_percent = (disk.used / disk.total) * 100
       print(f"Disk: {disk_percent:.1f}% used ({disk.used//1024**3}GB/{disk.total//1024**3}GB)")
       
       # Network information
       connections = psutil.net_connections()
       print(f"Network Connections: {len(connections)}")
       
       # System uptime
       boot_time = psutil.boot_time()
       uptime = time.time() - boot_time
       print(f"Uptime: {uptime/3600:.1f} hours")

   if __name__ == "__main__":
       system_overview()

Real-time System Monitor
~~~~~~~~~~~~~~~~~~~~~~~~

Create a live updating system monitor:

.. code-block:: python

   import psutil_cygwin as psutil
   import time
   import os

   class SystemMonitor:
       def __init__(self, update_interval=1.0):
           self.update_interval = update_interval
           self.running = False
       
       def clear_screen(self):
           """Clear the terminal screen."""
           print("\\033[2J\\033[H", end="")
       
       def format_bytes(self, bytes_value):
           """Format bytes to human readable format."""
           for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
               if bytes_value < 1024.0:
                   return f"{bytes_value:.1f} {unit}"
               bytes_value /= 1024.0
           return f"{bytes_value:.1f} PB"
       
       def get_top_processes(self, limit=10):
           """Get top processes by memory usage."""
           processes = []
           
           for proc in psutil.process_iter():
               try:
                   mem_info = proc.memory_info()
                   processes.append({
                       'pid': proc.pid,
                       'name': proc.name(),
                       'memory_mb': mem_info.rss // 1024**2
                   })
               except (psutil.NoSuchProcess, psutil.AccessDenied):
                   continue
           
           # Sort by memory usage
           processes.sort(key=lambda x: x['memory_mb'], reverse=True)
           return processes[:limit]
       
       def display_stats(self):
           """Display current system statistics."""
           self.clear_screen()
           
           print("🖥️  Real-time System Monitor")
           print("=" * 60)
           print(f"⏰ Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
           print()
           
           # CPU stats
           cpu_percent = psutil.cpu_percent(interval=None)
           cpu_count = psutil.cpu_count()
           print(f"🔧 CPU: {cpu_percent:6.1f}% ({cpu_count} cores)")
           
           # Memory stats
           memory = psutil.virtual_memory()
           print(f"💾 Memory: {memory.percent:6.1f}% "
                 f"({self.format_bytes(memory.used)} / {self.format_bytes(memory.total)})")
           
           # Disk stats
           disk = psutil.disk_usage('/')
           disk_percent = (disk.used / disk.total) * 100
           print(f"💿 Disk: {disk_percent:6.1f}% "
                 f"({self.format_bytes(disk.used)} / {self.format_bytes(disk.total)})")
           
           print()
           print("🔝 Top Processes by Memory:")
           print(f"{'PID':>7} {'Name':<20} {'Memory':>10}")
           print("-" * 40)
           
           for proc in self.get_top_processes(8):
               print(f"{proc['pid']:7d} {proc['name'][:20]:<20} {proc['memory_mb']:7d} MB")
           
           print()
           print("Press Ctrl+C to exit")
       
       def run(self):
           """Run the monitor loop."""
           self.running = True
           try:
               while self.running:
                   self.display_stats()
                   time.sleep(self.update_interval)
           except KeyboardInterrupt:
               print("\\n\\n👋 Monitor stopped.")
               self.running = False

   if __name__ == "__main__":
       monitor = SystemMonitor(update_interval=2.0)
       monitor.run()

Process Management Examples
---------------------------

For more detailed examples, see the complete :doc:`development` guide and check out the example applications in the ``psutil_cygwin/examples/`` directory.

Console Applications
--------------------

The package includes two ready-to-use console applications:

- **System Monitor**: ``psutil-cygwin-monitor`` - Real-time system monitoring
- **Process Manager**: ``psutil-cygwin-proc list`` - Process listing and management

These can be run directly after installation and serve as practical examples of the library's capabilities.
