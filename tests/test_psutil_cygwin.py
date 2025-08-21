#!/usr/bin/env python3
"""
Test suite and examples for Cygwin psutil replacement
"""

import sys
import time
import traceback
from pathlib import Path

# Import our Cygwin psutil replacement
try:
    import psutil_cygwin as psutil
except ImportError:
    print("Please ensure psutil_cygwin is installed")
    sys.exit(1)


def test_system_info():
    """Test system-wide information functions"""
    print("=== System Information ===")
    
    try:
        # CPU information
        cpu_times = psutil.cpu_times()
        print(f"CPU Times: user={cpu_times.user:.2f}s, system={cpu_times.system:.2f}s, idle={cpu_times.idle:.2f}s")
        
        cpu_pct = psutil.cpu_percent(interval=1)
        print(f"CPU Usage: {cpu_pct:.1f}%")
        
        # Memory information
        mem = psutil.virtual_memory()
        print(f"Memory: {mem.percent:.1f}% used ({mem.used // 1024**2}MB / {mem.total // 1024**2}MB)")
        
        swap = psutil.swap_memory()
        print(f"Swap: {swap.percent:.1f}% used ({swap.used // 1024**2}MB / {swap.total // 1024**2}MB)")
        
        # Boot time
        boot_time = psutil.boot_time()
        print(f"Boot time: {time.ctime(boot_time)}")
        
        # Users
        users = psutil.users()
        print(f"Logged in users: {len(users)}")
        for user in users:
            print(f"  {user.name} on {user.terminal}")
            
    except Exception as e:
        print(f"Error in system info: {e}")
        traceback.print_exc()


def test_disk_info():
    """Test disk-related functions"""
    print("\n=== Disk Information ===")
    
    try:
        # Disk partitions
        partitions = psutil.disk_partitions()
        print(f"Found {len(partitions)} disk partitions:")
        
        for partition in partitions[:5]:  # Show first 5
            print(f"  {partition.device} -> {partition.mountpoint} ({partition.fstype})")
            
            # Get usage for each partition
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                pct_used = (usage.used / usage.total * 100) if usage.total > 0 else 0
                print(f"    Usage: {pct_used:.1f}% ({usage.used // 1024**3}GB / {usage.total // 1024**3}GB)")
            except Exception as e:
                print(f"    Could not get usage: {e}")
                
    except Exception as e:
        print(f"Error in disk info: {e}")
        traceback.print_exc()


def test_network_info():
    """Test network-related functions"""
    print("\n=== Network Information ===")
    
    try:
        # Network connections
        connections = psutil.net_connections()
        print(f"Found {len(connections)} network connections")
        
        # Group by type
        tcp_conns = [c for c in connections if c.type == 'tcp']
        udp_conns = [c for c in connections if c.type == 'udp']
        
        print(f"  TCP connections: {len(tcp_conns)}")
        print(f"  UDP connections: {len(udp_conns)}")
        
        # Show some examples
        for conn in connections[:3]:
            raddr_str = f" -> {conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
            print(f"  {conn.type.upper()}: {conn.laddr.ip}:{conn.laddr.port}{raddr_str}")
            
    except Exception as e:
        print(f"Error in network info: {e}")
        traceback.print_exc()


def test_process_info():
    """Test process-related functions"""
    print("\n=== Process Information ===")
    
    try:
        # Get all PIDs
        all_pids = psutil.pids()
        print(f"Total processes: {len(all_pids)}")
        
        # Test current process
        current_pid = os.getpid() if 'os' in globals() else all_pids[0]
        print(f"\nTesting with PID {current_pid}:")
        
        proc = psutil.Process(current_pid)
        print(f"  Name: {proc.name()}")
        print(f"  Executable: {proc.exe()}")
        print(f"  Command line: {' '.join(proc.cmdline())}")
        print(f"  Status: {proc.status()}")
        print(f"  Parent PID: {proc.ppid()}")
        print(f"  Creation time: {time.ctime(proc.create_time())}")
        
        # Memory info
        mem_info = proc.memory_info()
        print(f"  Memory: RSS={mem_info.rss // 1024}KB, VMS={mem_info.vms // 1024}KB")
        
        # CPU times
        cpu_times = proc.cpu_times()
        print(f"  CPU times: user={cpu_times.user:.2f}s, system={cpu_times.system:.2f}s")
        
        # Open files
        open_files = proc.open_files()
        print(f"  Open files: {len(open_files)}")
        for f in open_files[:3]:  # Show first 3
            print(f"    FD {f.fd}: {f.path}")
            
    except Exception as e:
        print(f"Error in process info: {e}")
        traceback.print_exc()


def test_process_iteration():
    """Test iterating over all processes"""
    print("\n=== Process Iteration ===")
    
    try:
        process_count = 0
        running_processes = []
        
        for proc in psutil.process_iter():
            try:
                process_count += 1
                if proc.is_running():
                    name = proc.name()
                    status = proc.status()
                    running_processes.append((proc.pid, name, status))
                    
                # Stop after collecting info on 20 processes to avoid spam
                if process_count >= 20:
                    break
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        print(f"Examined {process_count} processes")
        print("Sample running processes:")
        
        for pid, name, status in running_processes[:10]:
            print(f"  PID {pid:5d}: {name:20s} ({status})")
            
    except Exception as e:
        print(f"Error in process iteration: {e}")
        traceback.print_exc()


def test_additional_features():
    """Test additional psutil features"""
    print("\n=== Additional Features ===")
    
    try:
        # CPU count
        cpu_count = psutil.cpu_count()
        print(f"CPU count: {cpu_count}")
        
        # PID existence check
        current_pid = os.getpid() if 'os' in globals() else psutil.pids()[0]
        exists = psutil.pid_exists(current_pid)
        print(f"PID {current_pid} exists: {exists}")
        
        # Process relationships
        proc = psutil.Process(current_pid)
        parent = proc.parent()
        if parent:
            print(f"Parent process: PID {parent.pid} ({parent.name()})")
        
        children = proc.children()
        print(f"Child processes: {len(children)}")
        
    except Exception as e:
        print(f"Error in additional features: {e}")
        traceback.print_exc()


def benchmark_performance():
    """Simple performance benchmark"""
    print("\n=== Performance Benchmark ===")
    
    tests = [
        ("Get all PIDs", lambda: psutil.pids()),
        ("CPU percentage", lambda: psutil.cpu_percent(interval=0.1)),
        ("Memory info", lambda: psutil.virtual_memory()),
        ("Disk partitions", lambda: psutil.disk_partitions()),
        ("Process iteration (first 50)", lambda: list(proc for i, proc in enumerate(psutil.process_iter()) if i < 50))
    ]
    
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            print(f"  {test_name:30s}: {duration:6.2f}ms")
            
        except Exception as e:
            print(f"  {test_name:30s}: ERROR - {e}")


def demonstrate_psutil_compatibility():
    """Demonstrate compatibility with psutil interface"""
    print("\n=== psutil Compatibility Demo ===")
    
    # This should work exactly like regular psutil
    try:
        # System overview
        print("System Overview:")
        print(f"  CPU count: Available via /proc/cpuinfo")
        print(f"  Memory: {psutil.virtual_memory().total // 1024**3}GB total")
        print(f"  Disk partitions: {len(psutil.disk_partitions())}")
        print(f"  Network connections: {len(psutil.net_connections())}")
        print(f"  Running processes: {len(psutil.pids())}")
        
        # Process management example
        print("\nProcess Management Example:")
        current_proc = psutil.Process(psutil.pids()[0])  # Use first available PID
        print(f"  Process: {current_proc.name()} (PID {current_proc.pid})")
        print(f"  Memory usage: {current_proc.memory_info().rss // 1024}KB")
        print(f"  CPU times: {current_proc.cpu_times()}")
        print(f"  Is running: {current_proc.is_running()}")
        
    except Exception as e:
        print(f"Error in compatibility demo: {e}")
        traceback.print_exc()


def main():
    """Run all tests"""
    print("Cygwin psutil Replacement - Test Suite")
    print("=" * 50)
    
    # Check if we're running on Cygwin
    try:
        if not Path("/proc").exists():
            print("WARNING: /proc not found - are you running on Cygwin?")
    except:
        pass
    
    # Run all tests
    test_system_info()
    test_disk_info()
    test_network_info()
    test_process_info()
    test_process_iteration()
    test_additional_features()
    benchmark_performance()
    demonstrate_psutil_compatibility()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
    print("\nUsage examples:")
    print("  import psutil_cygwin as psutil")
    print("  print(f'CPU: {psutil.cpu_percent()}%')")
    print("  print(f'Memory: {psutil.virtual_memory().percent}%')")
    print("  for proc in psutil.process_iter():")
    print("      print(f'{proc.pid}: {proc.name()}')")
    print("\nConsole commands:")
    print("  psutil-cygwin-monitor    # Real-time monitoring")
    print("  psutil-cygwin-proc list  # List processes")


if __name__ == "__main__":
    import os  # Add this import for the test
    main()
