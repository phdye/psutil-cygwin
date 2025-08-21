#!/usr/bin/env python3
"""
Process Manager Example using Cygwin psutil replacement
"""

import sys
import psutil_cygwin as psutil

def list_processes():
    """List all running processes"""
    print("Running Processes:")
    print("PID     Name                Status      Memory (MB)")
    print("-" * 55)
    
    for proc in psutil.process_iter():
        try:
            pid = proc.pid
            name = proc.name()[:15]  # Truncate long names
            status = proc.status()
            memory = proc.memory_info().rss // 1024**2
            
            print(f"{pid:7d} {name:15s} {status:10s} {memory:10d}")
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def process_info(pid):
    """Show detailed info about a process"""
    try:
        proc = psutil.Process(int(pid))
        
        print(f"Process Information for PID {pid}:")
        print("-" * 40)
        print(f"Name:        {proc.name()}")
        print(f"Executable:  {proc.exe()}")
        print(f"Status:      {proc.status()}")
        print(f"Parent PID:  {proc.ppid()}")
        print(f"Command:     {' '.join(proc.cmdline())}")
        
        mem_info = proc.memory_info()
        print(f"Memory RSS:  {mem_info.rss // 1024**2} MB")
        print(f"Memory VMS:  {mem_info.vms // 1024**2} MB")
        
        cpu_times = proc.cpu_times()
        print(f"CPU User:    {cpu_times.user:.2f}s")
        print(f"CPU System:  {cpu_times.system:.2f}s")
        
        open_files = proc.open_files()
        print(f"Open Files:  {len(open_files)}")
        
    except psutil.NoSuchProcess:
        print(f"Process {pid} not found")
    except psutil.AccessDenied:
        print(f"Access denied to process {pid}")
    except ValueError:
        print(f"Invalid PID: {pid}")



def main():
    """Entry point for console script."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  psutil-cygwin-proc list          - List all processes")
        print("  psutil-cygwin-proc info <PID>    - Show process info")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_processes()
    elif command == "info" and len(sys.argv) > 2:
        process_info(sys.argv[2])
    else:
        print("Invalid command")


if __name__ == "__main__":
    main()
