"""
Tests for psutil.pth functionality and transparent importing.

These tests verify that the .pth file mechanism works correctly and that
'import psutil' transparently uses psutil_cygwin after installation.
"""

import os
import sys
import site
import tempfile
import unittest
import subprocess
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# Add the package to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import setup functions from their new locations in the modernized structure
from psutil_cygwin.cygwin_check import create_psutil_pth, is_cygwin
from psutil_cygwin._build.hooks import remove_psutil_pth


class TestPthFileCreation(unittest.TestCase):
    """Test psutil.pth file creation and management."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.pth_file = os.path.join(self.temp_dir, 'psutil.pth')
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.pth_file):
            os.remove(self.pth_file)
        os.rmdir(self.temp_dir)
        
    @patch('site.getsitepackages')
    @patch('os.path.exists')
    @patch('os.access')
    def test_create_psutil_pth_success(self, mock_access, mock_exists, mock_getsitepackages):
        """Test successful .pth file creation."""
        # Mock site-packages directory
        mock_getsitepackages.return_value = [self.temp_dir]
        mock_exists.return_value = True
        mock_access.return_value = True
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = create_psutil_pth()
            
            # Verify file was opened for writing
            mock_file.assert_called_once_with(self.pth_file, 'w')
            
            # Verify correct content was written
            handle = mock_file()
            written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
            self.assertIn('psutil_cygwin', written_content)
            self.assertIn("sys.modules['psutil']", written_content)
            
            # Should return the path to created file
            self.assertEqual(result, self.pth_file)
            
    @patch('site.getsitepackages')
    @patch('site.getusersitepackages')
    @patch('os.path.exists')
    @patch('os.access')
    @patch('os.makedirs')
    def test_create_psutil_pth_fallback_to_user(self, mock_makedirs, mock_access, 
                                               mock_exists, mock_getusersitepackages, 
                                               mock_getsitepackages):
        """Test fallback to user site-packages when system site-packages not writable."""
        user_site = os.path.join(self.temp_dir, 'user-site')
        user_pth = os.path.join(user_site, 'psutil.pth')
        
        # Mock system site-packages not writable
        mock_getsitepackages.return_value = ['/system/site-packages']
        mock_getusersitepackages.return_value = user_site
        
        def exists_side_effect(path):
            if path == '/system/site-packages':
                return True
            elif path == user_site:
                return False  # Will be created
            return False
            
        def access_side_effect(path, mode):
            if path == '/system/site-packages':
                return False  # Not writable
            return True
            
        mock_exists.side_effect = exists_side_effect
        mock_access.side_effect = access_side_effect
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = create_psutil_pth()
            
            # Should have created user site-packages directory
            mock_makedirs.assert_called_once_with(user_site, exist_ok=True)
            
            # Should have created .pth file in user site-packages
            mock_file.assert_called_once_with(user_pth, 'w')
            self.assertEqual(result, user_pth)
            
    @patch('site.getsitepackages')
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_create_psutil_pth_permission_error(self, mock_open, mock_getsitepackages):
        """Test handling of permission errors during .pth file creation."""
        mock_getsitepackages.return_value = [self.temp_dir]
        
        with patch('os.path.exists', return_value=True), \
             patch('os.access', return_value=True):
            
            result = create_psutil_pth()
            
            # Should return None on permission error
            self.assertIsNone(result)
            
    def test_pth_file_content_format(self):
        """Test that .pth file content has correct format."""
        with patch('site.getsitepackages', return_value=[self.temp_dir]), \
             patch('os.path.exists', return_value=True), \
             patch('os.access', return_value=True):
            
            # Create the .pth file for real
            result = create_psutil_pth()
            
            # Verify file was created
            self.assertEqual(result, self.pth_file)
            self.assertTrue(os.path.exists(self.pth_file))
            
            # Read and verify content
            with open(self.pth_file, 'r') as f:
                content = f.read()
                
            # Should contain comment
            self.assertIn('psutil-cygwin', content)
            self.assertIn('Make psutil_cygwin available as', content)
            
            # Should contain the import statement
            self.assertIn("import sys", content)
            self.assertIn("sys.modules['psutil']", content)
            self.assertIn("__import__('psutil_cygwin')", content)
            
            # Should be executable Python code
            try:
                compile(content, self.pth_file, 'exec')
            except SyntaxError:
                self.fail("Generated .pth file contains invalid Python syntax")


class TestPthFileRemoval(unittest.TestCase):
    """Test psutil.pth file removal during uninstall."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.pth_file = os.path.join(self.temp_dir, 'psutil.pth')
        
        # Create a test .pth file
        with open(self.pth_file, 'w') as f:
            f.write("# psutil-cygwin: Make psutil_cygwin available as 'psutil'\n")
            f.write("import sys; sys.modules['psutil'] = __import__('psutil_cygwin')\n")
            
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.pth_file):
            os.remove(self.pth_file)
        os.rmdir(self.temp_dir)
        
    @patch('site.getsitepackages')
    @patch('site.getusersitepackages')
    def test_remove_psutil_pth_success(self, mock_getusersitepackages, mock_getsitepackages):
        """Test successful .pth file removal."""
        mock_getsitepackages.return_value = [self.temp_dir]
        mock_getusersitepackages.return_value = '/user/site'
        
        # Verify file exists before removal
        self.assertTrue(os.path.exists(self.pth_file))
        
        # Remove the file
        remove_psutil_pth()
        
        # Verify file was removed
        self.assertFalse(os.path.exists(self.pth_file))
        
    def test_remove_psutil_pth_wrong_content(self):
        """Test that .pth files with wrong content are not removed."""
        # Overwrite with different content
        with open(self.pth_file, 'w') as f:
            f.write("# Some other .pth file\nimport other_module\n")
            
        with patch('site.getsitepackages', return_value=[self.temp_dir]), \
             patch('site.getusersitepackages', return_value='/user/site'):
            
            # Try to remove
            remove_psutil_pth()
            
            # File should still exist (wrong content)
            self.assertTrue(os.path.exists(self.pth_file))
            
    @patch('site.getsitepackages')
    @patch('site.getusersitepackages') 
    def test_remove_psutil_pth_no_file(self, mock_getusersitepackages, mock_getsitepackages):
        """Test removal when .pth file doesn't exist."""
        mock_getsitepackages.return_value = ['/nonexistent']
        mock_getusersitepackages.return_value = '/user/site'
        
        # Should not raise exception
        try:
            remove_psutil_pth()
        except Exception as e:
            self.fail(f"remove_psutil_pth() raised an exception: {e}")
            
    def test_remove_psutil_pth_permission_error(self):
        """Test handling permission errors during removal."""
        with patch('site.getsitepackages', return_value=[self.temp_dir]), \
             patch('site.getusersitepackages', return_value='/user/site'), \
             patch('os.remove', side_effect=PermissionError("Permission denied")):
            
            # Should not raise exception
            try:
                remove_psutil_pth()
            except Exception as e:
                self.fail(f"remove_psutil_pth() raised an exception: {e}")


class TestTransparentImport(unittest.TestCase):
    """Test transparent import functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Remove psutil from sys.modules if it exists
        if 'psutil' in sys.modules:
            del sys.modules['psutil']
            
    def tearDown(self):
        """Clean up test environment."""
        # Clean up sys.modules
        if 'psutil' in sys.modules:
            del sys.modules['psutil']
        if 'psutil_cygwin' in sys.modules:
            del sys.modules['psutil_cygwin']
            
    def test_pth_file_import_mechanism(self):
        """Test that .pth file import mechanism works correctly."""
        # Simulate the .pth file content
        pth_code = "import sys; sys.modules['psutil'] = __import__('psutil_cygwin')"
        
        # Add psutil_cygwin to path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        try:
            # Execute the .pth file content
            exec(pth_code)
            
            # Now import psutil - it should be psutil_cygwin
            import psutil
            
            # Verify it's actually psutil_cygwin
            self.assertEqual(psutil.__name__, 'psutil_cygwin')
            
            # Verify it has expected psutil functions
            self.assertTrue(hasattr(psutil, 'cpu_percent'))
            self.assertTrue(hasattr(psutil, 'virtual_memory'))
            self.assertTrue(hasattr(psutil, 'Process'))
            self.assertTrue(hasattr(psutil, 'pids'))
            
        finally:
            sys.path.pop(0)
            
    def test_explicit_vs_transparent_import(self):
        """Test that explicit and transparent imports give same result."""
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        try:
            # Explicit import
            import psutil_cygwin
            
            # Simulate transparent import
            sys.modules['psutil'] = psutil_cygwin
            import psutil
            
            # Should be the same module
            self.assertIs(psutil, psutil_cygwin)
            
            # Should have same attributes
            self.assertEqual(dir(psutil), dir(psutil_cygwin))
            
        finally:
            sys.path.pop(0)


@unittest.skipUnless(os.path.exists('/proc'), "Requires Cygwin /proc filesystem")
class TestRealTransparentImport(unittest.TestCase):
    """Test transparent import in real Cygwin environment."""
    
    def test_transparent_import_basic_functionality(self):
        """Test that transparent import works with basic psutil functions."""

        try:
            # First ensure psutil_cygwin is available in development mode
            sys.path.insert(0, str(Path(__file__).parent.parent))
        
            try:
                # Try to import psutil_cygwin first to make sure it's available
                import psutil_cygwin
            except ImportError:
                self.skipTest("psutil_cygwin not available (package not installed in development mode)")
            
            # Clean slate for psutil import
            if 'psutil' in sys.modules:
                del sys.modules['psutil']
            
            # Set up transparent import for testing by simulating .pth file behavior
            sys.modules['psutil'] = psutil_cygwin
            
            # Now import psutil - it should be psutil_cygwin
            import psutil
                
            # Check if it's our psutil_cygwin
            if hasattr(psutil, '__name__') and psutil.__name__ == 'psutil_cygwin':
                # SUCCESS: Transparent import is working, test basic functionality
                try:
                    cpu_count = psutil.cpu_count()
                    self.assertIsInstance(cpu_count, int)
                    self.assertGreater(cpu_count, 0)
                    
                    mem = psutil.virtual_memory()
                    self.assertIsInstance(mem.total, int)
                    self.assertGreater(mem.total, 0)
                    
                    pids = psutil.pids()
                    self.assertIsInstance(pids, list)
                    self.assertGreater(len(pids), 0)
                    
                    print(f"✅ Transparent import working: 'import psutil' uses {psutil.__name__}")
                    
                except Exception as e:
                    self.fail(f"Basic psutil functionality failed: {e}")
                    
            else:
                # This should not happen since we set it up above
                self.fail(f"Transparent import setup failed - got {getattr(psutil, '__name__', 'unknown')} instead of psutil_cygwin")
            
        finally:
            # Clean up sys.modules
            if 'psutil' in sys.modules:
                del sys.modules['psutil']
            sys.path.pop(0)


class TestModernInstallationIntegration(unittest.TestCase):
    """Test integration with modern installation process."""
    
    @patch('psutil_cygwin._build.setup_script.create_psutil_pth')
    @patch('psutil_cygwin._build.setup_script.check_cygwin_requirements')
    def test_modern_setup_script_calls_pth_creation(self, mock_check_cygwin, mock_create_pth):
        """Test that modern setup script calls create_psutil_pth."""
        mock_check_cygwin.return_value = True
        mock_create_pth.return_value = '/site-packages/psutil.pth'
        
        # Import and test the modern setup script
        from psutil_cygwin._build.setup_script import setup_environment
        
        result = setup_environment()
        
        # Verify environment check was called
        mock_check_cygwin.assert_called_once()
        # Verify .pth creation was called
        mock_create_pth.assert_called_once()
        self.assertTrue(result)
        
    @patch('psutil_cygwin._build.setup_script.remove_psutil_pth')
    def test_modern_cleanup_script_calls_pth_removal(self, mock_remove_pth):
        """Test that modern cleanup script calls remove_psutil_pth."""
        from psutil_cygwin._build.setup_script import cleanup_environment
        
        cleanup_environment()
        
        # Verify .pth removal was called
        mock_remove_pth.assert_called_once()


class TestModernCygwinDetection(unittest.TestCase):
    """Test Cygwin detection for installation restrictions in modern architecture."""
    
    @patch('psutil_cygwin.cygwin_check.platform.system')
    @patch('psutil_cygwin.cygwin_check.os.path.exists')
    @patch('psutil_cygwin.cygwin_check.os.environ', {})
    @patch('psutil_cygwin.cygwin_check.sys.executable', '/standard/python/path')
    def test_is_cygwin_detection_scenarios(self, mock_exists, mock_system):
        """Test various Cygwin detection scenarios in modern architecture."""
        
        # Test positive detection
        mock_system.return_value = 'CYGWIN_NT-10.0'
        self.assertTrue(is_cygwin())
        
        # Test negative detection - mock all indicators to be False
        mock_system.return_value = 'Windows'
        mock_exists.return_value = False  # All os.path.exists calls return False
        # os.environ is mocked to be empty (no CYGWIN env var)
        # sys.executable is mocked to standard path (no cygwin/usr/bin)
        self.assertFalse(is_cygwin())
        
        # Test /proc filesystem detection (should return True)
        mock_system.return_value = 'Windows'  # Not Linux/Darwin
        mock_exists.side_effect = lambda path: path == '/proc'
        self.assertTrue(is_cygwin())
    
    def test_cygwin_requirements_validation(self):
        """Test that Cygwin requirements validation works correctly."""
        from psutil_cygwin.cygwin_check import check_cygwin_requirements
        
        # On a real Cygwin system with /proc, this should return True
        if os.path.exists('/proc'):
            # We're on Cygwin, requirements should pass
            result = check_cygwin_requirements()
            self.assertTrue(result, "Cygwin requirements should pass on Cygwin system")
        else:
            # We're not on Cygwin, requirements should fail
            result = check_cygwin_requirements()
            self.assertFalse(result, "Cygwin requirements should fail on non-Cygwin system")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
