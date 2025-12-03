from __future__ import annotations
from typing import Any


def normalize_tag(tag: Any) -> str:
  if isinstance(tag, str):
    return tag.split("}", 1)[1] if "}" in tag else tag
  elif isinstance(tag, (bytes, bytearray)):
    return normalize_tag(tag.decode("utf-8"))
  elif hasattr(tag, "localname"):
    return tag.localname
  elif hasattr(tag, "text"):
    return normalize_tag(tag.text)
  else:
    raise TypeError(f"Unexpected tag type: {type(tag)}")
