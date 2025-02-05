from __future__ import annotations

import dataclasses as dc
import enum
import typing as tp
import xml.etree.ElementTree as pyet
from warnings import deprecated, warn

import lxml.etree as lxet

from PythonTmx.functions import _make_elem, _make_xml_attrs


class POS(enum.Enum):
  BEGIN = "begin"
  END = "end"


class ASSOC(enum.Enum):
  P = "p"
  F = "f"
  B = "b"


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Bpt:
  i: int = dc.field(
    hash=True,
    compare=True,
  )
  x: tp.Optional[int] = dc.field(
    hash=True,
    compare=True,
    default=None,
  )
  type: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Bpt:
    i = kwargs.get("i", element.attrib.get("i"))
    x = kwargs.get("x", element.attrib.get("x"))
    type_ = kwargs.get("type", element.attrib.get("type"))
    try:
      i = int(i)
    except (ValueError, TypeError):
      warn(f"Expected int for i but got {type(i)!r}")
    if x is not None:
      try:
        x = int(x)
      except (ValueError, TypeError):
        warn(f"Expected int for x but got {type(x)!r}")
    return Bpt(i=i, x=x, type=type_)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    return _make_elem("bpt", _make_xml_attrs(self, **kwargs), engine)


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Ept:
  i: int = dc.field(
    hash=True,
    compare=True,
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Ept:
    i = kwargs.get("i", element.attrib.get("i"))
    try:
      i = int(i)
    except (ValueError, TypeError):
      warn(f"Expected int for i but got {type(i)!r}")
    return Ept(i=i)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    return _make_elem("ept", _make_xml_attrs(self, **kwargs), engine)


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Sub:
  datatype: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
  )
  type: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Sub:
    return Sub(**dict(element.attrib) | kwargs)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    return _make_elem("sub", _make_xml_attrs(self, **kwargs), engine)


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class It:
  pos: POS = dc.field(
    hash=True,
    compare=True,
  )
  x: tp.Optional[int] = dc.field(
    hash=True,
    compare=True,
    default=None,
  )
  type: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> It:
    pos = kwargs.get("pos", element.attrib.get("pos"))
    x = kwargs.get("x", element.attrib.get("x"))
    type_ = kwargs.get("type", element.attrib.get("type"))
    try:
      x = int(x)
    except (ValueError, TypeError):
      warn(f"Expected int for x but got {x!r}")
    try:
      pos = POS(pos)
    except (ValueError, TypeError):
      warn(f"Expected one of 'begin' or 'end' for pos but got {pos!r}")
    return It(pos=pos, x=x, type=type_)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    return _make_elem("it", _make_xml_attrs(self, **kwargs), engine)


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Ph:
  x: tp.Optional[int] = dc.field(
    hash=True,
    default=None,
    compare=True,
  )
  assoc: tp.Optional[ASSOC] = dc.field(
    hash=True,
    default=None,
    compare=True,
  )
  type: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Ph:
    x = kwargs.get("x", element.attrib.get("x"))
    assoc = kwargs.get("assoc", element.attrib.get("pos"))
    type_ = kwargs.get("type", element.attrib.get("type"))
    try:
      x = int(x)
    except (ValueError, TypeError):
      warn(f"Expected int for x but got {x!r}")
    try:
      assoc = ASSOC(assoc)
    except (ValueError, TypeError):
      warn(f"Expected one of 'p', 'f' or 'b' for pos but got {assoc!r}")
    return Ph(assoc=assoc, x=x, type=type_)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    return _make_elem("ph", _make_xml_attrs(self, **kwargs), engine)


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Hi:
  x: tp.Optional[int] = dc.field(
    hash=True,
    default=None,
    compare=True,
  )
  type: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Hi:
    x = kwargs.get("x", element.attrib.get("x"))
    type_ = kwargs.get("type", element.attrib.get("type"))
    try:
      x = int(x)
    except (ValueError, TypeError):
      warn(f"Expected int for x but got {x!r}")
    return Hi(x=x, type=type_)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    return _make_elem("hi", _make_xml_attrs(self, **kwargs), engine)


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
@deprecated("Deprecated since TMX 1.4")
class Ut:
  x: tp.Optional[int] = dc.field(
    hash=True,
    default=None,
    compare=True,
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Ut:
    x = kwargs.get("x", element.attrib.get("x"))
    try:
      x = int(x)
    except (ValueError, TypeError):
      warn(f"Expected int for x but got {x!r}")
    return Ut(x=x)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    return _make_elem("ut", _make_xml_attrs(self, **kwargs), engine)
