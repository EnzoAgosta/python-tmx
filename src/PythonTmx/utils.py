from __future__ import annotations

from collections.abc import Callable
from os import PathLike
from pathlib import Path

import lxml.etree as et

from PythonTmx.classes import (
  Bpt,
  Ept,
  Hi,
  It,
  Map,
  Note,
  Ph,
  Prop,
  Sub,
  Tmx,
  TmxElement,
  Tu,
  Tuv,
  Ude,
  Ut,
  XmlElementLike,
)

__all__ = ["from_element", "to_element"]

__from_elem_func_dict__: dict[str, Callable[..., TmxElement]] = {
  "tu": Tu._from_element,
  "tuv": Tuv._from_element,
  "note": Note._from_element,
  "prop": Prop._from_element,
  "tmx": Tmx._from_element,
  "ude": Ude._from_element,
  "map": Map._from_element,
  "bpt": Bpt._from_element,
  "ept": Ept._from_element,
  "it": It._from_element,
  "hi": Hi._from_element,
  "ph": Ph._from_element,
  "ut": Ut._from_element,
  "sub": Sub._from_element,
}
__to_elem_func_dict__: dict[str, Callable[..., et._Element]] = {
  "tu": Tu._to_element,
  "tuv": Tuv._to_element,
  "note": Note._to_element,
  "prop": Prop._to_element,
  "tmx": Tmx._to_element,
  "ude": Ude._to_element,
  "map": Map._to_element,
  "bpt": Bpt._to_element,
  "ept": Ept._to_element,
  "it": It._to_element,
  "hi": Hi._to_element,
  "ph": Ph._to_element,
  "ut": Ut._to_element,
  "sub": Sub._to_element,
}


def from_element(
  element: XmlElementLike, ignore_unknown: bool = False
) -> TmxElement | None:
  """
  This the main and recommended way to create TmxElement objects from xml
  elements, for example when reading from a file.

  It will create any possible TmxElement from the given element based on its tag.
  If the tag is not recognized, it will raise a ValueError (or silently move to
  the next if ignore_unknown is True).

  Parameters
  ----------
  element : XmlElement
      The element to create the TmxElement from.
  ignore_unknown : bool, optional
      Whether to silently ignore unknown tags. If False, any unknown tag will
      raise a ValueError. Default is False.

  Returns
  -------
  TmxElement
      Any TmxElement that can be created from the provided xml element.
  """
  global __from_elem_func_dict__
  e: Callable[..., TmxElement] | None = __from_elem_func_dict__.get(str(element.tag))
  if e is None:
    if ignore_unknown:
      return None
    else:
      raise ValueError(f"Unknown element {str(element.tag)}")
  else:
    return e(element)


def to_element(obj: TmxElement) -> et._Element:
  """
  Convert a TmxElement object to an :external:class:`lxml _Element <lxml.etree._Element>`

  Parameters
  ----------
  obj : TmxElement
      _description_

  Returns
  -------
  et._Element
      _description_

  Raises
  ------
  ValueError
      _description_
  """
  if not isinstance(obj, TmxElement):
    raise ValueError(f"Unknown element {str(obj.__class__.__name__)}")
  global __to_elem_func_dict__
  e: Callable[..., et._Element] = __to_elem_func_dict__[obj.__class__.__name__.lower()]
  return e(obj)


def from_file(
  path: str | bytes | PathLike, ignore_unknown: bool = False
) -> TmxElement | None:
  if isinstance(path, bytes):
    path = str(path)
  p = Path(path)
  if not p.exists():
    raise FileNotFoundError(f"File {p} does not exist")
  if p.is_dir():
    raise IsADirectoryError(f"File {p} is a directory")
  return from_element(et.parse(p).getroot(), ignore_unknown)


def to_file(obj: TmxElement, path: str | bytes | PathLike) -> None:
  if isinstance(path, bytes):
    path = str(path)
  p = Path(path)
  if not p.exists():
    raise FileNotFoundError(f"File {p} does not exist")
  if p.is_dir():
    raise IsADirectoryError(f"File {p} is a directory")
  et.ElementTree(to_element(obj)).write(p)
