from __future__ import annotations

import dataclasses as dc
import enum
import typing as tp
import xml.etree.ElementTree as pyet
from collections import abc
from warnings import deprecated, warn

import lxml.etree as lxet

from PythonTmx.functions import (
  _add_content,
  _make_elem,
  _make_xml_attrs,
  _parse_content,
)


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
  content: abc.Sequence[str | Sub] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
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
    content = kwargs.get("content", _parse_content(element))
    return Bpt(content=content, i=i, x=x, type=type_)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("bpt", _make_xml_attrs(self, **kwargs), engine)
    _add_content(elem, kwargs.get("content", self.content), engine, (str, Sub))
    return elem


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Ept:
  content: abc.Sequence[str | Sub] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
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
    content = kwargs.get("content", _parse_content(element))
    return Ept(i=i, content=content)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("ept", _make_xml_attrs(self, **kwargs), engine)
    _add_content(elem, kwargs.get("content", self.content), engine, (str, Sub))
    return elem


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Sub:
  content: abc.Sequence[str | Bpt | Ept | It | Ph | Hi | Ut] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
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
    content = kwargs.get("content", _parse_content(element))
    datatype = kwargs.get("datatype", element.attrib.get("datatype"))
    type_ = kwargs.get("type", element.attrib.get("type"))
    return Sub(content=content, datatype=datatype, type=type_)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("sub", _make_xml_attrs(self, **kwargs), engine)
    _add_content(
      elem, kwargs.get("content", self.content), engine, (str, Bpt, Ept, It, Ph, Hi, Ut)
    )
    return elem


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class It:
  content: abc.Sequence[str | Sub] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
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
    content = kwargs.get("content", _parse_content(element))
    return It(pos=pos, x=x, type=type_, content=content)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("it", _make_xml_attrs(self, **kwargs), engine)
    _add_content(elem, kwargs.get("content", self.content), engine, (str, Sub))
    return elem


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Ph:
  content: abc.Sequence[str | Sub] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
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
    content = kwargs.get("content", _parse_content(element))
    return Ph(assoc=assoc, x=x, type=type_, content=content)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("ph", _make_xml_attrs(self, **kwargs), engine)
    _add_content(elem, kwargs.get("content", self.content), engine, (str, Sub))
    return elem


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Hi:
  content: abc.Sequence[str | Sub] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
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
    content = kwargs.get("content", _parse_content(element))
    return Hi(x=x, type=type_, content=content)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("hi", _make_xml_attrs(self, **kwargs), engine)
    _add_content(elem, kwargs.get("content", self.content), engine, (str, Sub))
    return elem


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
@deprecated("Deprecated since TMX 1.4")
class Ut:
  content: abc.Sequence[str | Sub] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
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
    content = kwargs.get("content", _parse_content(element))
    return Ut(x=x, content=content)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("ut", _make_xml_attrs(self, **kwargs), engine)
    _add_content(elem, kwargs.get("content", self.content), engine, (str, Sub))
    return elem
