"""Compatibility wrapper for the modular `markdown_report` package.

Keep this thin wrapper so existing imports like
`import markdown_report_generator as mrg` continue to work.
The real implementation lives under the `markdown_report` package.
"""

from markdown_report import *  # re-export public API

__all__ = [name for name in dir() if not name.startswith('__')]
