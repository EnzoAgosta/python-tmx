from collections.abc import Iterable

from PythonTmx.elements import __TAG_MAP__
from PythonTmx.errors import WrongTagError


def create_tag_mask(
  mask: str | Iterable[str] | None, exclude: bool, include_tmx: bool
) -> tuple[str, ...]:
  tag_mask: tuple[str, ...]
  match mask:
    case None:
      tag_mask = tuple(__TAG_MAP__.keys())
    case str():
      if mask not in __TAG_MAP__:
        raise WrongTagError(mask, ", ".join(__TAG_MAP__.keys()))
      if exclude:
        tag_mask = tuple(tag for tag in __TAG_MAP__.keys() if tag != mask)
      else:
        tag_mask = (mask,)
    case Iterable():
      _mask = tuple(mask)
      for tag in _mask:
        if tag not in __TAG_MAP__:
          raise WrongTagError(tag, ", ".join(__TAG_MAP__.keys()))
      if exclude:
        tag_mask = tuple(tag for tag in __TAG_MAP__.keys() if tag not in _mask)
      else:
        tag_mask = _mask
  return tuple(tag for tag in tag_mask if tag != "tmx") if not include_tmx else tag_mask
