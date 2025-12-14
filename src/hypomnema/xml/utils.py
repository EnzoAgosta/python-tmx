from __future__ import annotations
from codecs import lookup
from collections.abc import Collection
from encodings import normalize_encoding as _normalize_encoding
from typing import Any


__all__ = ["normalize_tag", "normalize_encoding", "prep_tag_set"]


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


def normalize_encoding(encoding: str | None) -> str:
  if encoding is None or encoding.lower() == "unicode":
    return "utf-8"
  normalized_encoding = _normalize_encoding(encoding)
  try:
    codec = lookup(normalized_encoding)
    return codec.name
  except LookupError as e:
    raise ValueError(f"Unknown encoding: {normalized_encoding}") from e


def prep_tag_set(tags: str | Collection[str] | None) -> set[str] | None:
  if tags is None:
    return None
  if isinstance(tags, str):
    tag_set = {normalize_tag(tags)}
  elif isinstance(tags, Collection):
    tag_set = set(normalize_tag(tag) for tag in tags)
  else:
    raise TypeError(f"Unexpected tag type: {type(tags)}")
  return tag_set or None
