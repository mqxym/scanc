"""
scanc
=====

A small, fast, portable project code-scanner that emits AI-ready Markdown.

Exports
-------
* __version__           - semantic version string
* scan_directory()      - thin alias of scanc.core.scan_directory
"""
from importlib.metadata import PackageNotFoundError, version

try:  # Keep editable installs happy.
    __version__: str = version("scanc")
except PackageNotFoundError:
    __version__ = "1.1.0"

from .core import scan_directory 

__all__ = ["__version__", "scan_directory"]