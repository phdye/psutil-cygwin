# Comprehensive Testing Documentation for psutil-cygwin

## Overview

This document describes the comprehensive testing strategy and implementation for the psutil-cygwin project. The testing suite ensures that every aspect of the implemented functionality is thoroughly tested, including all conceivable edge cases and stress scenarios.

## Test Architecture

### Test Categories

1. **Unit Tests** (`test_unit*.py`)
   - `test_unit.py` - Basic unit tests with mocking
   - `test_unit_comprehensive.py` - Comprehensive unit testing with extensive edge cases, error handling, thread safety, and memory leak detection

2. **Integration Tests** (`test_integration*.py`)
   - `test_integration.py` - Basic integration tests requiring Cygwin
   - `test_integration_comprehensive.py` - Real environment testing with performance benchmarks, stress scenarios, and real-world usage patterns

3. **PTH/Installation Tests** (`test_pth*.py`)
   - `test_pth_functionality.py` - Basic .pth file functionality
   - `test_pth_comprehensive.py` - Comprehensive installation/uninstallation scenarios, multi-environment compatibility, and error recovery

4. **Stress Tests** (`test_stress.py`)
   - Extreme boundary conditions and resource exhaustion scenarios
   - Data corruption handling and concurrent access testing
   - Mathematical consistency validation

5. **Manual Test Suite** (`test_psutil_cygwin.py`)
   - Interactive examples and manual testing scenarios

## Running the Tests

### Quick Start

```bash
# Run all comprehensive tests
python comprehensive_test_runner.py

# Run specific test categories
python comprehensive_test_runner.py --tests unit integration

# Run without coverage analysis (faster)
python comprehensive_test_runner.py --no-coverage

# Run in quiet mode
python comprehensive_test_runner.py --quiet
```

### Individual Test Files

```bash
# Run all unit tests (basic + comprehensive)
pytest tests/test_unit*.py

# Run all integration tests (basic + comprehensive)  
pytest tests/test_integration*.py

# Run all PTH tests (basic + comprehensive)
pytest tests/test_pth*.py

# Run stress tests
python tests/test_stress.py

# Run specific comprehensive test files
python tests/test_unit_comprehensive.py
python tests/test_integration_comprehensive.py
python tests/test_pth_comprehensive.py
```

### Using pytest (if available)

```bash
# Install pytest (optional)
pip install pytest pytest-cov

# Run all tests with pytest
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=psutil_cygwin --cov-report=html
```

## Test Coverage Areas

### 1. Core System Functions

**CPU Functions**
- `cpu_times()`, `cpu_percent()`, `cpu_count()`
- Edge cases: empty/malformed `/proc/stat`, extreme values, different clock tick rates
- Stress tests: rapid successive calls, concurrent access, long intervals

**Memory Functions**
- `virtual_memory()`, `swap_memory()`
- Edge cases: zero memory, missing fields, very large values, no swap
- Validation: mathematical consistency, logical constraints

**Process Management**
- `Process` class, `pids()`, `process_iter()`, `pid_exists()`
- Edge cases: zombie processes, kernel threads, special characters, race conditions
- Stress tests: rapid process creation/destruction, large process counts

**Disk Operations**
- `disk_usage()`, `disk_partitions()`, `disk_io_counters()`
- Edge cases: full filesystems, read-only mounts, virtual filesystems
- Validation: usage calculations, partition consistency

**Network Operations**
- `net_connections()`, `net_io_counters()`
- Edge cases: IPv6, Unix sockets, large connection counts, various states
- Validation: address parsing, connection types

### 2. Error Handling and Robustness

**Permission Errors**
- Access denied scenarios
- File not found conditions
- Read-only filesystem handling

**Data Corruption**
- Malformed `/proc` files
- Binary data in text files
- Unicode/encoding issues
- Truncated files

**Race Conditions**
- Processes disappearing during access
- System state changes
- Concurrent access patterns

**Resource Exhaustion**
- File descriptor limits
- Memory pressure
- Process table stress

### 3. Performance and Scalability

**Load Testing**
- High CPU usage scenarios
- Memory pressure simulation
- Large process counts
- Many network connections

**Concurrency Testing**
- Thread safety validation
- Concurrent function calls
- Shared resource access
- Deadlock prevention

**Performance Benchmarking**
- Function call latencies
- Memory usage tracking
- Throughput measurements
- Performance regression detection

### 4. Installation and Integration

**Transparent Import Testing**
- `.pth` file creation/removal
- Module substitution correctness
- Installation workflow validation
- Multi-environment compatibility

**Cygwin Environment Validation**
- Environment detection
- Requirements checking
- Configuration validation
- Compatibility verification

## Test Environment Requirements

### Minimum Requirements

1. **Cygwin Environment**
   - Windows with Cygwin installed
   - `/proc` filesystem mounted and accessible
   - Basic POSIX tools available (`ps`, `who`, `mount`)

2. **Python Environment**
   - Python 3.6+ (tested with 3.6-3.12)
   - Standard library modules
   - Access to `/proc` filesystem

3. **Permissions**
   - Read access to `/proc` files
   - Ability to create temporary files
   - Process enumeration permissions

### Optional Dependencies

1. **Testing Framework Enhancements**
   ```bash
   pip install pytest pytest-cov pytest-mock
   ```

2. **Coverage Analysis**
   ```bash
   pip install coverage
   ```

3. **Performance Profiling**
   ```bash
   pip install memory-profiler psutil
   ```

### Environment Setup

```bash
# Ensure /proc is mounted
mount | grep proc

# Check required tools
which ps who mount df

# Verify Python access to /proc
python -c "import os; print('✅' if os.path.exists('/proc/stat') else '❌')"

# Install optional testing dependencies
pip install pytest coverage pytest-cov memory-profiler
```

## Performance Benchmarks and Thresholds

### Performance Expectations

**Function Call Latencies**
- `cpu_times()`: < 10ms average
- `virtual_memory()`: < 5ms average
- `cpu_count()`: < 1ms average
- `pids()`: < 50ms average
- `process_iter()` (100 processes): < 2s

**Memory Usage**
- Base import: < 10MB
- Process enumeration: < 50MB additional
- Long-running monitoring: < 100MB total
- No significant memory leaks over time

**Throughput**
- Process enumeration: > 20 processes/second
- System function calls: > 100 calls/second
- Concurrent access: No significant degradation

## Running Instructions

### Complete Test Suite

```bash
# Run all comprehensive tests
python comprehensive_test_runner.py

# Run specific categories only
python comprehensive_test_runner.py --tests enhanced_unit stress

# Quick validation (essential tests only)
python comprehensive_test_runner.py --tests enhanced_unit enhanced_integration
```

### Individual Test Categories

```bash
# All unit tests (basic + comprehensive)
pytest tests/test_unit*.py

# All integration tests (basic + comprehensive)
pytest tests/test_integration*.py

# All PTH/installation tests (basic + comprehensive)
pytest tests/test_pth*.py

# Stress and boundary testing
python tests/test_stress.py
```

### Troubleshooting

**"No /proc filesystem found"**
- Ensure running in Cygwin environment
- Check `/proc` mount: `mount | grep proc`
- Install `procps-ng` package in Cygwin

**"Permission denied" errors**
- Run tests with appropriate user permissions
- Some processes may be inaccessible (normal)
- Check file permissions on test directories

**Tests running slowly**
- Skip stress tests: `--tests enhanced_unit enhanced_integration`
- Disable coverage: `--no-coverage`
- Run individual test files

## Expected Results

### Success Criteria
- All test categories pass without failures
- No memory leaks detected
- Performance within expected thresholds
- All edge cases handled gracefully
- Installation/uninstallation works correctly

### Performance Targets
- Unit tests: Complete in < 60 seconds
- Integration tests: Complete in < 300 seconds
- Stress tests: Complete in < 600 seconds
- Memory usage: < 200MB peak during testing
- No significant performance regressions

## Conclusion

This comprehensive testing strategy ensures that psutil-cygwin is thoroughly validated across all functionality, edge cases, and stress conditions. The multi-layered approach provides confidence in the reliability, performance, and robustness of the implementation.

Regular execution of these tests, especially before releases, helps maintain high quality and prevents regressions. The detailed reporting and analysis capabilities support continuous improvement of both the code and the testing strategy itself.
