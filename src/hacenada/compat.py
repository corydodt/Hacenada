"""
Definitions required for compatibility with other Python versions
"""

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


__all__ = ["TypedDict"]
