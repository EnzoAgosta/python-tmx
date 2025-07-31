from collections.abc import Iterable

from PythonTmx.elements import __TAG_MAP__


def create_tag_mask(mask: str | Iterable[str] | None, exclude: bool) -> tuple[str, ...]:
  tag_mask: tuple[str, ...]
  match mask:
    case None:
      tag_mask = tuple(__TAG_MAP__.keys())
    case str():
      if mask not in __TAG_MAP__:
        raise ValueError(f"Unknown tag {mask!r}")
      if exclude:
        tag_mask = tuple(tag for tag in __TAG_MAP__.keys() if tag != mask)
      else:
        tag_mask = (mask,)
    case Iterable():
      _mask = tuple(mask)
      for tag in _mask:
        if tag not in __TAG_MAP__:
          raise ValueError(f"Unknown tag {tag!r}")
      if exclude:
        tag_mask = tuple(tag for tag in __TAG_MAP__.keys() if tag not in _mask)
      else:
        tag_mask = _mask
  return tag_mask
