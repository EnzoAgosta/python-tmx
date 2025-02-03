from __future__ import annotations

import collections.abc as abc
import dataclasses as dc
import datetime as dt
import typing as tp
import xml.etree.ElementTree as pyet
from enum import Enum

import lxml.etree as lxet


class Structural:
  __slots__ = ()


class SEGTYPE(Enum):
  BLOCK = "block"
  PARAGRAPH = "paragraph"
  SENTENCE = "sentence"
  PHRASE = "phrase"


def parse_notes(elem: pyet.Element | lxet._Element) -> list[Note]:
  return [Note.from_element(note) for note in elem.iter("note")]


def parse_props(elem: pyet.Element | lxet._Element) -> list[Prop]:
  return [Prop.from_element(note) for note in elem.iter("prop")]


def _make_elem(
  tag: str, attrib: dict[str, str], method: tp.Literal["python", "lxml"]
) -> lxet._Element | pyet.Element:
  if method == "lxml":
    return lxet.Element(tag, attrib=attrib)
  elif method == "python":
    return pyet.Element(tag, attrib=attrib)
  else:
    raise ValueError(f"Unknown method: {method!r}")


@dc.dataclass(kw_only=True, slots=True, unsafe_hash=True)
class Map(Structural):
  unicode: str = dc.field(hash=True, compare=True)
  code: tp.Optional[str] = dc.field(default=None, hash=True, compare=True)
  ent: tp.Optional[str] = dc.field(default=None, hash=True, compare=True)
  subst: tp.Optional[str] = dc.field(default=None, hash=True, compare=True)

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Map:
    return Map(**dict(element.attrib) | kwargs)

  def to_element(
    self, method: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    xml_attrs = dict()
    xml_attrs.update(kwargs)
    xml_attrs.update(dc.asdict(self))
    return _make_elem("map", xml_attrs, method)


@dc.dataclass(kw_only=True, slots=True, unsafe_hash=True)
class Ude(Structural):
  name: str = dc.field(hash=True, compare=True)
  base: tp.Optional[str] = dc.field(hash=True, compare=True, default=None)
  maps: abc.Sequence[Map] = dc.field(hash=True, compare=True, default_factory=list)

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Ude:
    maps = kwargs.pop("maps", None)
    if maps is None:
      if element.find("map") is not None:
        maps = [Map.from_element(map_) for map_ in element.iter("map")]
      else:
        maps = []
    return Ude(**dict(element.attrib) | kwargs, maps=maps)

  def to_element(
    self, method: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    xml_attrs = dict()
    xml_attrs.update(kwargs)
    xml_attrs.update(dc.asdict(self))
    elem = _make_elem("ude", xml_attrs, method)
    if len(self.maps):
      for map in self.maps:
        if not self.base and map.code:
          raise ValueError("base must be set if at least one map has a code attribute")
        elem.append(map.to_element(method))  # type: ignore
    return elem


@dc.dataclass(kw_only=True, slots=True, unsafe_hash=True)
class Note(Structural):
  text: str = dc.field(hash=True, compare=True)
  lang: tp.Optional[str] = dc.field(hash=True, compare=True, default=None)
  encoding: tp.Optional[str] = dc.field(hash=True, compare=True, default=None)

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Note:
    lang = kwargs.get(
      "lang", element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    encoding = kwargs.get("encoding", element.attrib.get("o-encoding"))
    text = kwargs.get("text", element.text)
    return Note(text=text, lang=lang, encoding=encoding)

  def to_element(
    self, method: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    xml_attrs = dict()
    xml_attrs.update(kwargs)
    xml_attrs.update(dc.asdict(self))
    elem = _make_elem("note", xml_attrs, method)
    elem.text = elem.attrib.pop("text")
    return elem


@dc.dataclass(kw_only=True, slots=True, unsafe_hash=True)
class Prop(Structural):
  text: str = dc.field(hash=True, compare=True)
  type: str = dc.field(hash=True, compare=True)
  lang: tp.Optional[str] = dc.field(hash=True, compare=True, default=None)
  encoding: tp.Optional[str] = dc.field(hash=True, compare=True, default=None)

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Prop:
    lang = kwargs.get(
      "lang", element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    encoding = kwargs.get("encoding", element.attrib.get("o-encoding"))
    text = kwargs.get("text", element.text)
    type_ = kwargs.get("type", element.attrib.get("type"))
    return Prop(text=text, lang=lang, encoding=encoding, type=type_)

  def to_element(
    self, method: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    xml_attrs = dict()
    xml_attrs.update(kwargs)
    xml_attrs.update(dc.asdict(self))
    elem = _make_elem("note", xml_attrs, method)
    elem.text = elem.attrib.pop("text")
    return elem


@dc.dataclass(kw_only=True, slots=True, unsafe_hash=True)
class Header(Structural):
  creationtool: str = dc.field(hash=True, compare=True)
  creationtoolversion: str = dc.field(hash=True, compare=True)
  segtype: SEGTYPE = dc.field(hash=True, compare=True)
  tmf: str = dc.field(hash=True, compare=True)
  adminlang: str = dc.field(hash=True, compare=True)
  srclang: str = dc.field(hash=True, compare=True)
  datatype: str = dc.field(hash=True, compare=True)
  encoding: tp.Optional[str] = dc.field(default=None, hash=True, compare=True)
  creationdate: tp.Optional[dt.datetime | str] = dc.field(
    default=None, hash=True, compare=True
  )
  creationid: tp.Optional[str] = dc.field(default=None, hash=True, compare=True)
  changedate: tp.Optional[dt.datetime | str] = dc.field(
    default=None, hash=True, compare=True
  )
  changeid: tp.Optional[str] = dc.field(default=None, hash=True, compare=True)
  notes: abc.Sequence[Note] = dc.field(default_factory=list, hash=True, compare=True)
  props: abc.Sequence[Prop] = dc.field(default_factory=list, hash=True, compare=True)
  udes: abc.Sequence[Ude] = dc.field(default_factory=list, hash=True, compare=True)

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Header:
    creationtool = kwargs.get("creationtool", element.attrib.get("creationtool"))
    creationtoolversion = kwargs.get(
      "creationtoolversion", element.attrib.get("creationtoolversion")
    )
    segtype = SEGTYPE(kwargs.get("segtype", element.attrib.get("segtype")))
    tmf = kwargs.get("tmf", element.attrib.get("o-tmf"))
    adminlang = kwargs.get("adminlang", element.attrib.get("adminlang"))
    srclang = kwargs.get("srclang", element.attrib.get("srclang"))
    datatype = kwargs.get("datatype", element.attrib.get("datatype"))
    encoding = kwargs.get("encoding", element.attrib.get("encoding"))
    creationdate = kwargs.get("creationdate", element.attrib.get("creationdate"))
    creationid = kwargs.get("creationid", element.attrib.get("creationid"))
    changedate = kwargs.get("changedate", element.attrib.get("changedate"))
    changeid = kwargs.get("changeid", element.attrib.get("changeid"))
    if creationdate is not None:
      try:
        creationdate = dt.datetime.fromisoformat(creationdate)
      except (ValueError, TypeError):
        pass
    if changedate is not None:
      try:
        changedate = dt.datetime.fromisoformat(changedate)
      except (ValueError, TypeError):
        pass
    return Header(
      creationtool=creationtool,
      creationtoolversion=creationtoolversion,
      segtype=segtype,
      tmf=tmf,
      adminlang=adminlang,
      srclang=srclang,
      datatype=datatype,
      encoding=encoding,
      creationdate=creationdate,
      creationid=creationid,
      changedate=changedate,
      changeid=changeid,
      notes=notes
      if (notes := kwargs.get("notes")) is not None
      else parse_notes(element),
      props=props
      if (props := kwargs.get("props")) is not None
      else parse_props(element),
      udes=udes
      if (udes := kwargs.get("udes")) is not None
      else [Ude.from_element(ude) for ude in element.iter("ude")],
    )
