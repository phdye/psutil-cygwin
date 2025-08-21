#!/usr/bin/env python3
"""
Cygwin psutil drop-in replacement

This module provides a psutil-compatible interface for Cygwin environments,
leveraging Cygwin's /proc pseudo-filesystem for system information.
"""

import os
import time
import glob
import subprocess
from pathlib import Path
from collections import namedtuple
from typing import List, Dict, Optional, Union, Iterator


# Named tuples matching psutil interface
NetworkConnection = namedtuple('NetworkConnection', ['fd', 'family', 'type', 'laddr', 'raddr', 'status', 'pid'])
Address = namedtuple('Address', ['ip', 'port'])
DiskUsage = namedtuple('DiskUsage', ['total', 'used', 'free'])
DiskIO = namedtuple('DiskIO', ['read_count', 'write_count', 'read_bytes', 'write_bytes', 'read_time', 'write_time'])
CPUTimes = namedtuple('CPUTimes', ['user', 'system', 'idle', 'interrupt', 'dpc'])
VirtualMemory = namedtuple('VirtualMemory', ['total', 'available', 'percent', 'used', 'free'])
SwapMemory = namedtuple('SwapMemory', ['total', 'used', 'free', 'percent', 'sin', 'sout'])
User = namedtuple('User', ['name', 'terminal', 'host', 'started', 'pid'])


class AccessDenied(Exception):
    """Raised when access to a process is denied"""
    
    def __init__(self, pid: Optional[int] = None, name: Optional[str] = None, msg: Optional[str] = None):
        self.pid = pid
        self.name = name
        self.msg = msg
        if msg is None:
            if pid is not None:
                self.msg = f"Access denied to process {pid}"
            else:
                self.msg = "Access denied"
        super().__init__(self.msg)


class NoSuchProcess(Exception):
    """Raised when a process doesn't exist"""
    
    def __init__(self, pid: Optional[int] = None, name: Optional[str] = None, msg: Optional[str] = None):
        self.pid = pid
        self.name = name
        self.msg = msg
        if msg is None:
            if pid is not None:
                self.msg = f"Process {pid} not found"
            else:
                self.msg = "Process not found"
        super().__init__(self.msg)


class TimeoutExpired(Exception):
    """Raised when a timeout expires"""
    
    def __init__(self, seconds: float, pid: Optional[int] = None, name: Optional[str] = None):
        self.seconds = seconds
        self.pid = pid
        self.name = name
        if pid is not None:
            msg = f"Process {pid} did not terminate within {seconds} seconds"
        else:
            msg = f"Timeout expired after {seconds} seconds"
        super().__init__(msg)


class Process:
    """Process information class compatible with psutil.Process"""
    
    def __init__(self, pid: int):
        self.pid = pid
        self._proc_path = f"/proc/{pid}"
        if not os.path.exists(self._proc_path):
            raise NoSuchProcess(pid=pid)
    
    def _read_proc_file(self, filename: str) -> str:
        """Read a file from /proc/pid/"""
        try:
            with open(f"{self._proc_path}/{filename}", 'r') as f:
                return f.read().strip()
        except PermissionError:
            raise AccessDenied(pid=self.pid)
        except (IOError, OSError) as e:
            if "Permission denied" in str(e):
                raise AccessDenied(pid=self.pid)
            raise
    
    def _read_proc_lines(self, filename: str) -> List[str]:
        """Read lines from a /proc file"""
        content = self._read_proc_file(filename)
        return [line.strip() for line in content.split('\n') if line.strip()]
    
    def name(self) -> str:
        """Get process name"""
        try:
            return self._read_proc_file("comm")
        except AccessDenied:
            raise  # Re-raise AccessDenied
        except:
            # Fallback to cmdline first argument
            try:
                cmdline = self.cmdline()
                if cmdline:
                    return os.path.basename(cmdline[0])
                return ""
            except AccessDenied:
                raise  # Re-raise AccessDenied
            except:
                return ""
    
    def exe(self) -> str:
        """Get process executable path"""
        try:
            return os.readlink(f"{self._proc_path}/exe")
        except OSError:
            # Try to get from cmdline
            cmdline = self.cmdline()
            return cmdline[0] if cmdline else ""
    
    def cmdline(self) -> List[str]:
        """Get process command line arguments"""
        try:
            cmdline = self._read_proc_file("cmdline")
            # Arguments are null-separated - handle both real and literal null chars
            if '\x00' in cmdline:
                # Real null characters
                return [arg for arg in cmdline.split('\x00') if arg]
            elif '\\x00' in cmdline:
                # Literal \x00 string
                return [arg for arg in cmdline.split('\\x00') if arg]
            else:
                # Fallback: split on \0 (literal backslash-zero)
                return [arg for arg in cmdline.split('\0') if arg]
        except:
            return []
    
    def status(self) -> str:
        """Get process status"""
        try:
            stat_content = self._read_proc_file("stat")
            # Third field is status
            fields = stat_content.split()
            status_char = fields[2] if len(fields) > 2 else 'U'
            status_map = {
                'R': 'running',
                'S': 'sleeping',
                'D': 'disk-sleep',
                'Z': 'zombie',
                'T': 'stopped',
                'W': 'paging'
            }
            return status_map.get(status_char, 'unknown')
        except:
            return 'unknown'
    
    def ppid(self) -> int:
        """Get parent process ID"""
        try:
            stat_content = self._read_proc_file("stat")
            fields = stat_content.split()
            return int(fields[3]) if len(fields) > 3 else 0
        except:
            return 0
    
    def create_time(self) -> float:
        """Get process creation time"""
        try:
            stat_content = self._read_proc_file("stat")
            fields = stat_content.split()
            if len(fields) > 21:
                # starttime is in clock ticks since boot
                starttime_ticks = int(fields[21])
                boot_time = boot_time_cached()
                clock_ticks_per_sec = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
                return boot_time + (starttime_ticks / clock_ticks_per_sec)
        except:
            pass
        return time.time()  # Fallback
    
    def memory_info(self) -> namedtuple:
        """Get memory information"""
        MemInfo = namedtuple('MemInfo', ['rss', 'vms'])
        try:
            status_lines = self._read_proc_lines("status")
            rss = vms = 0
            for line in status_lines:
                if line.startswith('VmRSS:'):
                    rss = int(line.split()[1]) * 1024  # Convert KB to bytes
                elif line.startswith('VmSize:'):
                    vms = int(line.split()[1]) * 1024  # Convert KB to bytes
            return MemInfo(rss=rss, vms=vms)
        except:
            return MemInfo(rss=0, vms=0)
    
    def cpu_times(self) -> namedtuple:
        """Get CPU times for this process"""
        ProcessCPUTimes = namedtuple('ProcessCPUTimes', ['user', 'system'])
        try:
            stat_content = self._read_proc_file("stat")
            fields = stat_content.split()
            if len(fields) > 15:
                clock_ticks_per_sec = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
                user_time = int(fields[13]) / clock_ticks_per_sec
                system_time = int(fields[14]) / clock_ticks_per_sec
                return ProcessCPUTimes(user=user_time, system=system_time)
        except:
            pass
        return ProcessCPUTimes(user=0.0, system=0.0)
    
    def open_files(self) -> List[namedtuple]:
        """Get list of open files"""
        OpenFile = namedtuple('OpenFile', ['path', 'fd'])
        files = []
        try:
            fd_dir = f"{self._proc_path}/fd"
            if os.path.exists(fd_dir):
                for fd_name in os.listdir(fd_dir):
                    try:
                        fd_path = os.path.join(fd_dir, fd_name)
                        target = os.readlink(fd_path)
                        if target.startswith('/') and not target.startswith('/dev'):
                            files.append(OpenFile(path=target, fd=int(fd_name)))
                    except (OSError, ValueError):
                        continue
        except OSError:
            pass
        return files
    
    def connections(self, kind: str = 'inet') -> List[NetworkConnection]:
        """Get network connections for this process"""
        # This would need to parse /proc/net/tcp, /proc/net/udp etc.
        # and match by inode to process fd inodes - simplified implementation
        return []
    
    def children(self, recursive: bool = False) -> List['Process']:
        """Get child processes"""
        children = []
        for proc in process_iter():
            try:
                if proc.ppid() == self.pid:
                    children.append(proc)
                    if recursive:
                        children.extend(proc.children(recursive=True))
            except (NoSuchProcess, AccessDenied):
                continue
        return children
    
    def parent(self) -> Optional['Process']:
        """Get parent process"""
        try:
            ppid = self.ppid()
            if ppid > 0:
                return Process(ppid)
        except (NoSuchProcess, AccessDenied):
            pass
        return None
    
    def is_running(self) -> bool:
        """Check if process is still running"""
        return os.path.exists(self._proc_path)
    
    def kill(self):
        """Kill the process"""
        os.kill(self.pid, 9)
    
    def terminate(self):
        """Terminate the process"""
        os.kill(self.pid, 15)
    
    def wait(self, timeout: Optional[float] = None) -> int:
        """Wait for process to terminate"""
        start_time = time.time()
        while self.is_running():
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutExpired(timeout, pid=self.pid, name=self.name())
            time.sleep(0.1)
        
        # Return exit code (simplified - would need more complex logic)
        return 0


def pids() -> List[int]:
    """Get list of all process IDs"""
    proc_pids = []
    try:
        for item in os.listdir('/proc'):
            if item.isdigit():
                proc_pids.append(int(item))
    except OSError:
        pass
    return sorted(proc_pids)


def process_iter() -> Iterator[Process]:
    """Iterate over all processes"""
    for pid in pids():
        try:
            yield Process(pid)
        except (NoSuchProcess, AccessDenied):
            continue


def cpu_times() -> CPUTimes:
    """Get system CPU times"""
    try:
        with open('/proc/stat', 'r') as f:
            line = f.readline().strip()
            if line.startswith('cpu '):
                fields = line.split()[1:]  # Skip 'cpu' label
                # Convert from clock ticks to seconds
                clock_ticks_per_sec = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
                times = [int(x) / clock_ticks_per_sec for x in fields[:5]]
                
                user = times[0] if len(times) > 0 else 0
                system = times[2] if len(times) > 2 else 0
                idle = times[3] if len(times) > 3 else 0
                interrupt = times[4] if len(times) > 4 else 0
                dpc = 0  # Not available on Linux/Cygwin
                
                return CPUTimes(user=user, system=system, idle=idle, 
                              interrupt=interrupt, dpc=dpc)
    except (OSError, IOError):
        pass
    
    return CPUTimes(user=0, system=0, idle=0, interrupt=0, dpc=0)


def cpu_percent(interval: Optional[float] = None) -> float:
    """Get CPU usage percentage"""
    if interval is None:
        interval = 0.1
    
    times1 = cpu_times()
    time.sleep(interval)
    times2 = cpu_times()
    
    total_delta = sum([
        times2.user - times1.user,
        times2.system - times1.system,
        times2.idle - times1.idle
    ])
    
    if total_delta == 0:
        return 0.0
    
    idle_delta = times2.idle - times1.idle
    return max(0.0, 100.0 * (1.0 - idle_delta / total_delta))


def cpu_count(logical: bool = True) -> int:
    """Get number of CPUs"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_count = 0
            for line in f:
                if line.startswith('processor'):
                    cpu_count += 1
            return max(1, cpu_count)
    except (OSError, IOError):
        return 1


def virtual_memory() -> VirtualMemory:
    """Get virtual memory statistics"""
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = {}
            for line in f:
                if ':' in line:
                    key, value = line.split(':', 1)
                    # Extract numeric value (in KB)
                    value_kb = int(value.strip().split()[0])
                    meminfo[key.strip()] = value_kb * 1024  # Convert to bytes
        
        total = meminfo.get('MemTotal', 0)
        free = meminfo.get('MemFree', 0)
        available = meminfo.get('MemAvailable', free)
        buffers = meminfo.get('Buffers', 0)
        cached = meminfo.get('Cached', 0)
        
        used = total - free - buffers - cached
        percent = (used / total * 100) if total > 0 else 0
        
        return VirtualMemory(
            total=total,
            available=available,
            percent=percent,
            used=used,
            free=free
        )
    except (OSError, IOError):
        pass
    
    return VirtualMemory(total=0, available=0, percent=0, used=0, free=0)


def swap_memory() -> SwapMemory:
    """Get swap memory statistics"""
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = {}
            for line in f:
                if ':' in line:
                    key, value = line.split(':', 1)
                    value_kb = int(value.strip().split()[0])
                    meminfo[key.strip()] = value_kb * 1024
        
        total = meminfo.get('SwapTotal', 0)
        free = meminfo.get('SwapFree', 0)
        used = total - free
        percent = (used / total * 100) if total > 0 else 0
        
        return SwapMemory(
            total=total,
            used=used,
            free=free,
            percent=percent,
            sin=0,  # Swap in - would need /proc/vmstat
            sout=0  # Swap out - would need /proc/vmstat
        )
    except (OSError, IOError):
        pass
    
    return SwapMemory(total=0, used=0, free=0, percent=0, sin=0, sout=0)


def disk_usage(path: str) -> DiskUsage:
    """Get disk usage statistics for a path"""
    try:
        statvfs = os.statvfs(path)
        total = statvfs.f_frsize * statvfs.f_blocks
        # Handle Cygwin compatibility - f_available might not be available
        if hasattr(statvfs, 'f_available'):
            free = statvfs.f_frsize * statvfs.f_available
        elif hasattr(statvfs, 'f_bavail'):
            free = statvfs.f_frsize * statvfs.f_bavail
        else:
            # Fallback to f_bfree if neither is available
            free = statvfs.f_frsize * statvfs.f_bfree
        used = total - free
        return DiskUsage(total=total, used=used, free=free)
    except OSError:
        return DiskUsage(total=0, used=0, free=0)


def disk_partitions(all: bool = False) -> List[namedtuple]:
    """Get disk partitions"""
    Partition = namedtuple('Partition', ['device', 'mountpoint', 'fstype', 'opts'])
    partitions = []
    
    try:
        with open('/proc/mounts', 'r') as f:
            for line in f:
                fields = line.strip().split()
                if len(fields) >= 4:
                    device, mountpoint, fstype, opts = fields[:4]
                    
                    # Skip virtual filesystems unless all=True
                    if not all and fstype in ['proc', 'sysfs', 'tmpfs', 'devpts', 'devtmpfs']:
                        continue
                    
                    partitions.append(Partition(
                        device=device,
                        mountpoint=mountpoint,
                        fstype=fstype,
                        opts=opts
                    ))
    except (OSError, IOError):
        pass
    
    return partitions


def net_connections(kind: str = 'inet') -> List[NetworkConnection]:
    """Get network connections"""
    connections = []
    
    # Parse /proc/net/tcp and /proc/net/udp
    tcp_files = ['/proc/net/tcp', '/proc/net/tcp6'] if kind in ['inet', 'tcp'] else []
    udp_files = ['/proc/net/udp', '/proc/net/udp6'] if kind in ['inet', 'udp'] else []
    
    for filename in tcp_files + udp_files:
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()[1:]  # Skip header
                for line in lines:
                    fields = line.strip().split()
                    if len(fields) >= 10:
                        local_addr = fields[1]
                        remote_addr = fields[2]
                        status = fields[3]
                        
                        # Parse addresses (hex format: IP:PORT)
                        def parse_addr(addr_hex):
                            if ':' in addr_hex:
                                ip_hex, port_hex = addr_hex.split(':')
                                # Convert hex IP to dotted decimal (IPv4)
                                if len(ip_hex) == 8:  # IPv4
                                    ip_int = int(ip_hex, 16)
                                    ip = '.'.join(str((ip_int >> (i*8)) & 0xFF) for i in range(4))
                                else:  # IPv6 - simplified
                                    ip = ip_hex
                                port = int(port_hex, 16)
                                return Address(ip=ip, port=port)
                            return Address(ip='0.0.0.0', port=0)
                        
                        laddr = parse_addr(local_addr)
                        raddr = parse_addr(remote_addr) if remote_addr != '00000000:0000' else None
                        
                        conn_type = 'tcp' if 'tcp' in filename else 'udp'
                        family = 'AF_INET6' if '6' in filename else 'AF_INET'
                        
                        connections.append(NetworkConnection(
                            fd=None,
                            family=family,
                            type=conn_type,
                            laddr=laddr,
                            raddr=raddr,
                            status=status,
                            pid=None  # Would need to match with process fd inodes
                        ))
        except (OSError, IOError):
            continue
    
    return connections


def boot_time() -> float:
    """Get system boot time"""
    return boot_time_cached()


def boot_time_cached() -> float:
    """Get system boot time (cached version)"""
    if not hasattr(boot_time_cached, '_cached_time'):
        try:
            with open('/proc/stat', 'r') as f:
                for line in f:
                    if line.startswith('btime'):
                        boot_time_cached._cached_time = float(line.split()[1])
                        break
                else:
                    boot_time_cached._cached_time = time.time() - 3600  # Fallback
        except (OSError, IOError):
            boot_time_cached._cached_time = time.time() - 3600  # Fallback
    
    return boot_time_cached._cached_time


def users() -> List[User]:
    """Get logged in users"""
    users = []
    
    try:
        # Use 'who' command as fallback since /proc/loginuid might not be available
        result = subprocess.run(['who'], capture_output=True, text=True, timeout=5)
        for line in result.stdout.splitlines():
            fields = line.split()
            if len(fields) >= 3:
                name = fields[0]
                terminal = fields[1]
                # Parse date/time - simplified
                started = time.time()  # Placeholder
                users.append(User(
                    name=name,
                    terminal=terminal,
                    host='',
                    started=started,
                    pid=None
                ))
    except (OSError, subprocess.SubprocessError, subprocess.TimeoutExpired):
        pass
    
    return users


def disk_io_counters(perdisk: bool = False) -> Union[DiskIO, Dict[str, DiskIO]]:
    """Get disk I/O statistics"""
    # Parse /proc/diskstats for disk I/O information
    if perdisk:
        disk_stats = {}
        try:
            with open('/proc/diskstats', 'r') as f:
                for line in f:
                    fields = line.strip().split()
                    if len(fields) >= 14:
                        device = fields[2]
                        # Skip loop devices and partitions for main stats
                        if device.startswith('loop') or device[-1].isdigit():
                            continue
                        
                        read_count = int(fields[3])
                        read_merged = int(fields[4]) 
                        read_sectors = int(fields[5])
                        read_time = int(fields[6])
                        write_count = int(fields[7])
                        write_merged = int(fields[8])
                        write_sectors = int(fields[9])
                        write_time = int(fields[10])
                        
                        # Convert sectors to bytes (assuming 512 bytes per sector)
                        read_bytes = read_sectors * 512
                        write_bytes = write_sectors * 512
                        
                        disk_stats[device] = DiskIO(
                            read_count=read_count,
                            write_count=write_count,
                            read_bytes=read_bytes,
                            write_bytes=write_bytes,
                            read_time=read_time,
                            write_time=write_time
                        )
        except (OSError, IOError, ValueError):
            pass
        return disk_stats
    else:
        # Return aggregated stats
        all_stats = disk_io_counters(perdisk=True)
        if not all_stats:
            return DiskIO(read_count=0, write_count=0, read_bytes=0, write_bytes=0, read_time=0, write_time=0)
        
        total_read_count = sum(stats.read_count for stats in all_stats.values())
        total_write_count = sum(stats.write_count for stats in all_stats.values())
        total_read_bytes = sum(stats.read_bytes for stats in all_stats.values())
        total_write_bytes = sum(stats.write_bytes for stats in all_stats.values())
        total_read_time = sum(stats.read_time for stats in all_stats.values())
        total_write_time = sum(stats.write_time for stats in all_stats.values())
        
        return DiskIO(
            read_count=total_read_count,
            write_count=total_write_count,
            read_bytes=total_read_bytes,
            write_bytes=total_write_bytes,
            read_time=total_read_time,
            write_time=total_write_time
        )


def net_io_counters(pernic: bool = False) -> Union[namedtuple, Dict[str, namedtuple]]:
    """Get network I/O statistics"""
    NetIO = namedtuple('NetIO', ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'errin', 'errout', 'dropin', 'dropout'])
    
    # Parse /proc/net/dev for network interface statistics
    if pernic:
        net_stats = {}
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]  # Skip header lines
                for line in lines:
                    if ':' in line:
                        iface, data = line.split(':', 1)
                        iface = iface.strip()
                        fields = data.strip().split()
                        
                        if len(fields) >= 16:
                            bytes_recv = int(fields[0])
                            packets_recv = int(fields[1])
                            errin = int(fields[2])
                            dropin = int(fields[3])
                            bytes_sent = int(fields[8])
                            packets_sent = int(fields[9])
                            errout = int(fields[10])
                            dropout = int(fields[11])
                            
                            net_stats[iface] = NetIO(
                                bytes_sent=bytes_sent,
                                bytes_recv=bytes_recv,
                                packets_sent=packets_sent,
                                packets_recv=packets_recv,
                                errin=errin,
                                errout=errout,
                                dropin=dropin,
                                dropout=dropout
                            )
        except (OSError, IOError, ValueError):
            pass
        return net_stats
    else:
        # Return aggregated stats
        all_stats = net_io_counters(pernic=True)
        if not all_stats:
            return NetIO(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0, errin=0, errout=0, dropin=0, dropout=0)
        
        total_bytes_sent = sum(stats.bytes_sent for stats in all_stats.values())
        total_bytes_recv = sum(stats.bytes_recv for stats in all_stats.values())
        total_packets_sent = sum(stats.packets_sent for stats in all_stats.values())
        total_packets_recv = sum(stats.packets_recv for stats in all_stats.values())
        total_errin = sum(stats.errin for stats in all_stats.values())
        total_errout = sum(stats.errout for stats in all_stats.values())
        total_dropin = sum(stats.dropin for stats in all_stats.values())
        total_dropout = sum(stats.dropout for stats in all_stats.values())
        
        return NetIO(
            bytes_sent=total_bytes_sent,
            bytes_recv=total_bytes_recv,
            packets_sent=total_packets_sent,
            packets_recv=total_packets_recv,
            errin=total_errin,
            errout=total_errout,
            dropin=total_dropin,
            dropout=total_dropout
        )


def pid_exists(pid: int) -> bool:
    """Check if a process with given PID exists"""
    return os.path.exists(f"/proc/{pid}")


if __name__ == "__main__":
    # Simple test
    print("Cygwin psutil replacement - Test")
    print(f"PIDs: {len(pids())}")
    print(f"CPU: {cpu_percent():.1f}%")
    print(f"Memory: {virtual_memory().percent:.1f}%")
    print(f"Boot time: {time.ctime(boot_time())}")
    
    print("\nRunning processes:")
    for proc in list(process_iter())[:5]:  # Show first 5
        try:
            print(f"  PID {proc.pid}: {proc.name()} ({proc.status()})")
        except (NoSuchProcess, AccessDenied):
            continue
