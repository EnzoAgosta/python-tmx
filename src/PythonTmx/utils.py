from __future__ import annotations

import xml.etree.ElementTree as et
from typing import Callable, Type, TypeVar

from PythonTmx.classes import (
  Bpt,
  Ept,
  Header,
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

R = TypeVar("R")
__elem_mapping: dict[str, Type[TmxElement]] = {
  "tmx": Tmx,
  "header": Header,
  "note": Note,
  "prop": Prop,
  "ude": Ude,
  "map": Map,
  "tu": Tu,
  "tuv": Tuv,
  "bpt": Bpt,
  "ept": Ept,
  "hi": Hi,
  "it": It,
  "ph": Ph,
  "ut": Ut,
  "sub": Sub,
}


def from_element(elem: XmlElementLike) -> TmxElement:
  if str(elem.tag) not in __elem_mapping:
    raise ValueError(f"{str(elem.tag)} is not a valid tmx element")
  return __elem_mapping[str(elem.tag)]._from_element(elem)


def to_element(
  obj: TmxElement,
  constructor: Callable[..., XmlElementLike] = et.Element,
) -> XmlElementLike:
  if not isinstance(obj, TmxElement):
    raise TypeError(f"{type(obj)} is not a Tmx Element")
  return __elem_mapping[obj.__class__.__name__.lower()]._to_element(obj, constructor)  # type: ignore
