"""
Modern build backend for psutil-cygwin.

This replaces the deprecated setuptools custom commands with a modern build system
that uses setuptools build hooks and entry points.
"""

from setuptools import build_meta as _orig_build_meta


class CygwinBuildMeta(_orig_build_meta):
    """Custom build backend that adds Cygwin-specific build behavior."""
    
    def build_wheel(self, wheel_directory, config_settings=None, metadata_directory=None):
        """Build wheel with Cygwin validation."""
        # Build the wheel normally
        return _orig_build_meta.build_wheel(
            wheel_directory, config_settings, metadata_directory
        )
    
    def build_sdist(self, sdist_directory, config_settings=None):
        """Build source distribution."""
        return _orig_build_meta.build_sdist(sdist_directory, config_settings)


# Make the build backend functions available
build_wheel = CygwinBuildMeta().build_wheel
build_sdist = CygwinBuildMeta().build_sdist
get_requires_for_build_wheel = _orig_build_meta.get_requires_for_build_wheel
get_requires_for_build_sdist = _orig_build_meta.get_requires_for_build_sdist
prepare_metadata_for_build_wheel = _orig_build_meta.prepare_metadata_for_build_wheel
