from __future__ import annotations
from warnings import warn

from .base import XMLBackend
from .standard import StandardBackend

__all__ = ["XMLBackend", "StandardBackend"]

try:
  from .lxml import LxmlBackend  # noqa: F401

  __all__.append("LxmlBackend")
except ImportError:
  warn("lxml not installed, Only StandardBackend will be available")
