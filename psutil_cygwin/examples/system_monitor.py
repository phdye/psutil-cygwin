#!/usr/bin/env python3
"""
System Monitor Example using Cygwin psutil replacement
"""

import time
import psutil_cygwin as psutil

def system_monitor():
    """Simple system monitoring loop"""
    print("System Monitor (Ctrl+C to exit)")
    print("=" * 40)
    
    try:
        while True:
            # Get system stats
            cpu_pct = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            
            # Clear screen (works in most terminals)
            print("\033[2J\033[H", end="")
            
            print("System Status:")
            print(f"CPU Usage: {cpu_pct:6.1f}%")
            print(f"Memory:    {mem.percent:6.1f}% ({mem.used//1024**2}MB/{mem.total//1024**2}MB)")
            
            # Show top processes by memory
            processes = []
            for proc in psutil.process_iter():
                try:
                    mem_info = proc.memory_info()
                    processes.append((proc.pid, proc.name(), mem_info.rss))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage
            processes.sort(key=lambda x: x[2], reverse=True)
            
            print("\nTop Memory Users:")
            print("PID     Name                Memory (MB)")
            print("-" * 40)
            for pid, name, rss in processes[:10]:
                print(f"{pid:7d} {name:15s} {rss//1024**2:10d}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

def main():
    """Entry point for console script."""
    system_monitor()


if __name__ == "__main__":
    main()
