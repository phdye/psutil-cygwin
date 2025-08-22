#!/usr/bin/env python3
"""
Enhanced tests for psutil.pth functionality and transparent importing with comprehensive edge cases.

These tests verify that the .pth file mechanism works correctly under all conditions,
including edge cases, error scenarios, and complex installation environments.
"""

import os
import sys
import site
import tempfile
import unittest
import subprocess
import shutil
import importlib
import threading
import time
from unittest.mock import patch, mock_open, MagicMock, call
from pathlib import Path

# Add the package to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import setup functions from their locations
from psutil_cygwin.cygwin_check import create_psutil_pth, is_cygwin, check_transparent_import
from psutil_cygwin._build.hooks import remove_psutil_pth


class TestPthFileCreationComprehensive(unittest.TestCase):
    """Comprehensive tests for psutil.pth file creation with all edge cases."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dirs = []
        self.original_modules = sys.modules.copy()
        
    def tearDown(self):
        """Clean up test environment."""
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Restore sys.modules
        sys.modules.clear()
        sys.modules.update(self.original_modules)
    
    def create_temp_dir(self):
        """Create a temporary directory and track it for cleanup."""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def test_pth_creation_multiple_site_packages(self):
        """Test .pth file creation with multiple site-packages directories."""
        temp_dirs = [self.create_temp_dir() for _ in range(3)]
        
        # Make first directory read-only, second writable, third as backup
        os.chmod(temp_dirs[0], 0o444)  # Read-only
        os.chmod(temp_dirs[1], 0o755)  # Writable
        os.chmod(temp_dirs[2], 0o755)  # Writable
        
        with patch('site.getsitepackages', return_value=temp_dirs):
            with patch('os.path.exists', return_value=True):
                with patch('os.access') as mock_access:
                    # First dir not writable, second is writable
                    mock_access.side_effect = lambda path, mode: path == temp_dirs[1]
                    
                    result = create_psutil_pth()
                    
                    expected_path = os.path.join(temp_dirs[1], 'psutil.pth')
                    self.assertEqual(result, expected_path)
                    self.assertTrue(os.path.exists(expected_path))
        
        # Restore permissions
        for temp_dir in temp_dirs:
            try:
                os.chmod(temp_dir, 0o755)
            except:
                pass
    
    def test_pth_creation_user_site_fallback(self):
        """Test fallback to user site-packages when system not writable."""
        system_dir = self.create_temp_dir()
        user_dir = self.create_temp_dir()
        
        # Make system directory not writable
        os.chmod(system_dir, 0o444)
        
        with patch('site.getsitepackages', return_value=[system_dir]):
            with patch('site.getusersitepackages', return_value=user_dir):
                with patch('os.access') as mock_access:
                    # System dir not writable
                    mock_access.return_value = False
                    
                    result = create_psutil_pth()
                    
                    expected_path = os.path.join(user_dir, 'psutil.pth')
                    self.assertEqual(result, expected_path)
                    self.assertTrue(os.path.exists(expected_path))
        
        # Restore permissions
        os.chmod(system_dir, 0o755)
    
    def test_pth_file_content_variations(self):
        """Test .pth file content under various conditions."""
        temp_dir = self.create_temp_dir()
        
        with patch('site.getsitepackages', return_value=[temp_dir]):
            with patch('os.path.exists', return_value=True):
                with patch('os.access', return_value=True):
                    result = create_psutil_pth()
                    self.assertIsNotNone(result)
                    
                    # Read and validate content
                    with open(result, 'r') as f:
                        content = f.read()
                    
                    # Validate content structure
                    self.assertIn('psutil-cygwin', content)
                    self.assertIn("sys.modules['psutil']", content)
                    self.assertIn("__import__('psutil_cygwin')", content)
                    
                    # Validate it's executable Python code
                    try:
                        compile(content, result, 'exec')
                    except SyntaxError:
                        self.fail("Generated .pth file contains invalid Python syntax")


class TestPthFileRemovalComprehensive(unittest.TestCase):
    """Comprehensive tests for psutil.pth file removal with edge cases."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dirs = []
        
    def tearDown(self):
        """Clean up test environment."""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def create_temp_dir(self):
        """Create a temporary directory and track it for cleanup."""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def test_pth_removal_multiple_locations(self):
        """Test removal from multiple possible locations."""
        temp_dirs = [self.create_temp_dir() for _ in range(3)]
        
        # Create .pth files in multiple locations
        pth_files = []
        for temp_dir in temp_dirs:
            pth_file = os.path.join(temp_dir, 'psutil.pth')
            with open(pth_file, 'w') as f:
                f.write("# psutil-cygwin: Make psutil_cygwin available as 'psutil'\n")
                f.write("import sys; sys.modules['psutil'] = __import__('psutil_cygwin')\n")
            pth_files.append(pth_file)
        
        with patch('site.getsitepackages', return_value=temp_dirs[:2]):
            with patch('site.getusersitepackages', return_value=temp_dirs[2]):
                remove_psutil_pth()
                
                # All .pth files should be removed
                for pth_file in pth_files:
                    self.assertFalse(os.path.exists(pth_file))
    
    def test_pth_removal_wrong_content_preservation(self):
        """Test that .pth files with wrong content are preserved."""
        temp_dir = self.create_temp_dir()
        pth_file = os.path.join(temp_dir, 'psutil.pth')
        
        # Create .pth file with different content
        wrong_content = "# Different .pth file\nimport other_module\n"
        with open(pth_file, 'w') as f:
            f.write(wrong_content)
        
        with patch('site.getsitepackages', return_value=[temp_dir]):
            with patch('site.getusersitepackages', return_value='/user/site'):
                remove_psutil_pth()
                
                # File should still exist with original content
                self.assertTrue(os.path.exists(pth_file))
                with open(pth_file, 'r') as f:
                    content = f.read()
                self.assertEqual(content, wrong_content)


class TestTransparentImportComprehensive(unittest.TestCase):
    """Comprehensive tests for transparent import functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.original_modules = sys.modules.copy()
        self.original_path = sys.path.copy()
        
        # Clean psutil from sys.modules
        modules_to_remove = [mod for mod in sys.modules if mod.startswith('psutil')]
        for mod in modules_to_remove:
            del sys.modules[mod]
    
    def tearDown(self):
        """Clean up test environment."""
        # Restore sys.modules and sys.path
        sys.modules.clear()
        sys.modules.update(self.original_modules)
        sys.path[:] = self.original_path
    
    def test_transparent_import_mechanism_detailed(self):
        """Test detailed transparent import mechanism."""
        # Add psutil_cygwin to path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        try:
            # Simulate .pth file execution
            pth_code = "import sys; sys.modules['psutil'] = __import__('psutil_cygwin')"
            
            # Execute the .pth code
            exec(pth_code)
            
            # Now import psutil
            import psutil
            
            # Verify it's psutil_cygwin
            self.assertEqual(psutil.__name__, 'psutil_cygwin')
            
            # Test various attributes exist
            required_attributes = [
                'Process', 'cpu_percent', 'virtual_memory', 'pids',
                'AccessDenied', 'NoSuchProcess', 'TimeoutExpired'
            ]
            
            for attr in required_attributes:
                self.assertTrue(hasattr(psutil, attr), f"Missing attribute: {attr}")
            
            # Test that functions work
            self.assertIsInstance(psutil.cpu_count(), int)
            
            # Test exception classes
            self.assertTrue(issubclass(psutil.AccessDenied, Exception))
            self.assertTrue(issubclass(psutil.NoSuchProcess, Exception))
            
        finally:
            sys.path.pop(0)
    
    def test_transparent_import_thread_safety(self):
        """Test thread safety of transparent import mechanism."""
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        try:
            results = []
            errors = []
            
            def import_worker():
                """Worker function to test concurrent imports."""
                try:
                    # Clean import state for this thread
                    if 'psutil' in sys.modules:
                        del sys.modules['psutil']
                    
                    # Simulate .pth execution and import
                    pth_code = "import sys; sys.modules['psutil'] = __import__('psutil_cygwin')"
                    exec(pth_code)
                    
                    import psutil
                    
                    # Test basic functionality
                    cpu_count = psutil.cpu_count()
                    module_name = psutil.__name__
                    
                    results.append((module_name, cpu_count))
                    
                except Exception as e:
                    errors.append(e)
            
            # Run multiple threads
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=import_worker)
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join(timeout=10)
            
            # Validate results
            self.assertEqual(len(errors), 0, f"Import errors: {errors}")
            self.assertEqual(len(results), 10)
            
            # All should have imported psutil_cygwin
            for module_name, cpu_count in results:
                self.assertEqual(module_name, 'psutil_cygwin')
                self.assertIsInstance(cpu_count, int)
        
        finally:
            sys.path.pop(0)


class TestCygwinDetectionComprehensive(unittest.TestCase):
    """Comprehensive tests for Cygwin detection functionality."""
    
    def test_is_cygwin_all_conditions(self):
        """Test all Cygwin detection conditions."""
        # Test individual detection methods
        with patch('psutil_cygwin.cygwin_check.platform.system', return_value='CYGWIN_NT-10.0'):
            with patch('psutil_cygwin.cygwin_check.os.path.exists', return_value=False):
                # Should detect based on platform alone
                self.assertTrue(is_cygwin())
        
        with patch('psutil_cygwin.cygwin_check.platform.system', return_value='Windows'):
            with patch('psutil_cygwin.cygwin_check.os.path.exists') as mock_exists:
                def exists_side_effect(path):
                    return path == '/proc'
                mock_exists.side_effect = exists_side_effect
                
                # Should detect based on /proc filesystem
                self.assertTrue(is_cygwin())
    
    def test_is_cygwin_negative_cases(self):
        """Test Cygwin detection negative cases."""
        # Mock all indicators as negative
        with patch('psutil_cygwin.cygwin_check.platform.system', return_value='Linux'):
            with patch('psutil_cygwin.cygwin_check.os.path.exists', return_value=False):
                with patch('psutil_cygwin.cygwin_check.os.environ', {}):
                    with patch('psutil_cygwin.cygwin_check.sys.executable', '/usr/bin/python'):
                        with patch('psutil_cygwin.cygwin_check.subprocess.run') as mock_run:
                            mock_run.return_value.returncode = 1  # uname fails
                            
                            # Should not detect as Cygwin
                            self.assertFalse(is_cygwin())


if __name__ == '__main__':
    # Configure test runner for comprehensive output
    unittest.main(verbosity=2, buffer=True, failfast=False)
