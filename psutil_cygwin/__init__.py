"""
psutil-cygwin: A drop-in replacement for psutil on Cygwin environments.

This package provides a psutil-compatible interface for Cygwin environments,
leveraging Cygwin's /proc pseudo-filesystem for system information.

Important: This package is specifically designed for Cygwin and will only
install on Cygwin environments. For other platforms, use the standard psutil.

Example usage:
    import psutil  # This will work transparently after installation
    
    # OR explicitly:
    import psutil_cygwin as psutil
    
    # System information
    print(f"CPU: {psutil.cpu_percent()}%")
    print(f"Memory: {psutil.virtual_memory().percent}%")
    
    # Process information
    for proc in psutil.process_iter():
        print(f"{proc.pid}: {proc.name()}")
"""

# Perform Cygwin environment check on import
import sys
import warnings

try:
    from . import cygwin_check
    from .cygwin_check import is_cygwin
    
    # Check if we're in a Cygwin environment
    if not is_cygwin():
        warnings.warn(
            "psutil-cygwin is designed for Cygwin environments. "
            "For other platforms, consider using the standard psutil package.",
            UserWarning,
            stacklevel=2
        )
except ImportError:
    # If cygwin_check import fails, continue anyway
    pass

# Import build modules for test access
try:
    from . import _build
except ImportError:
    # _build might not be available in all installations
    pass

__version__ = "1.0.0"
__author__ = "psutil-cygwin contributors"
__license__ = "MIT"

# Import main classes and functions
from .core import (
    # Exceptions
    AccessDenied,
    NoSuchProcess,
    TimeoutExpired,
    
    # Process class
    Process,
    
    # System functions
    pids,
    process_iter,
    pid_exists,
    
    # CPU functions
    cpu_times,
    cpu_percent,
    cpu_count,
    
    # Memory functions
    virtual_memory,
    swap_memory,
    
    # Disk functions
    disk_usage,
    disk_partitions,
    disk_io_counters,
    
    # Network functions
    net_connections,
    net_io_counters,
    
    # System functions
    boot_time,
    users,
    
    # Named tuples
    CPUTimes,
    VirtualMemory,
    SwapMemory,
    DiskUsage,
    DiskIO,
    NetworkConnection,
    Address,
    User,
)

# Version info
version_info = tuple(map(int, __version__.split('.')))

# All exported symbols
__all__ = [
    # Version info
    "__version__",
    "version_info",
    
    # Exceptions
    "AccessDenied",
    "NoSuchProcess", 
    "TimeoutExpired",
    
    # Process class
    "Process",
    
    # System functions
    "pids",
    "process_iter",
    "pid_exists",
    
    # CPU functions
    "cpu_times",
    "cpu_percent", 
    "cpu_count",
    
    # Memory functions
    "virtual_memory",
    "swap_memory",
    
    # Disk functions
    "disk_usage",
    "disk_partitions",
    "disk_io_counters",
    
    # Network functions
    "net_connections",
    "net_io_counters",
    
    # System functions
    "boot_time",
    "users",
    
    # Named tuples
    "CPUTimes",
    "VirtualMemory", 
    "SwapMemory",
    "DiskUsage",
    "DiskIO",
    "NetworkConnection",
    "Address",
    "User",
]
