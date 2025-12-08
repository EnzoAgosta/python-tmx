from __future__ import annotations

from .base import XMLBackend
from .standard import StandardBackend

try:
  from .lxml_backend import LxmlBackend  # type: ignore

  __all__ = ["XMLBackend", "StandardBackend", "LxmlBackend"]
except Exception:

  class _LxmlMissing:
    def __init__(self, *args, **kwargs) -> None:
      raise ImportError(
        "LxmlBackend requires the 'lxml' package. "
        "Make sure it is installed in your environment before using the lxml backend."
      )

  class LxmlBackend:  # type: ignore
    def __new__(cls, *args, **kwargs):
      return _LxmlMissing(*args, **kwargs)

  __all__ = ["XMLBackend", "StandardBackend", "LxmlBackend"]
