from __future__ import annotations

import collections.abc as abc
import dataclasses as dc
import datetime as dt
import typing as tp
import xml.etree.ElementTree as pyet
from enum import Enum
from warnings import warn

import lxml.etree as lxet

from PythonTmx.functions import _make_elem, _make_xml_attrs


class SEGTYPE(Enum):
  BLOCK = "block"
  PARAGRAPH = "paragraph"
  SENTENCE = "sentence"
  PHRASE = "phrase"


def _parse_notes(elem: pyet.Element | lxet._Element) -> list[Note]:
  return [Note.from_element(note) for note in elem.iter("note")]


def _parse_props(elem: pyet.Element | lxet._Element) -> list[Prop]:
  return [Prop.from_element(note) for note in elem.iter("prop")]


def _parse_tuvs(elem: pyet.Element | lxet._Element) -> list[Tuv]:
  return [Tuv.from_element(note) for note in elem.iter("tuv")]


def _parse_tus(elem: pyet.Element | lxet._Element) -> list[Tu]:
  return [Tu.from_element(note) for note in elem.iter("tu")]


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Map:
  unicode: str = dc.field(
    hash=True,
    compare=True,
  )
  code: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  ent: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  subst: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Map:
    return Map(**dict(element.attrib) | kwargs)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    return _make_elem("map", _make_xml_attrs(self, **kwargs), engine)


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Ude:
  name: str = dc.field(
    hash=True,
    compare=True,
  )
  base: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
  )
  maps: abc.Sequence[Map] = dc.field(
    hash=True,
    compare=True,
    default_factory=list,
    metadata={"exclude": True},
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Ude:
    maps = kwargs.pop("maps", None)
    if maps is None:
      if len(element):
        maps = [Map.from_element(map_) for map_ in element.iter("map")]
      else:
        maps = []
    return Ude(**dict(element.attrib) | kwargs, maps=maps)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem(
      "ude",
      _make_xml_attrs(self, **kwargs),
      engine,
    )
    if len(self.maps):
      for map_ in self.maps:
        if not self.base and map_.code:
          raise ValueError("base must be set if at least one map has a code attribute")
        # Impossible to know if wich engine we'll be using, so we'll always to
        # type ignore this line in every implementation
        elem.append(map_.to_element(engine))  # type: ignore
    return elem


@dc.dataclass(
  kw_only=True,
  slots=True,
  unsafe_hash=True,
)
class Note:
  text: str = dc.field(
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
  lang: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
    metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"},
  )
  encoding: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
    metadata={"export_name": "o-encoding"},
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Note:
    lang = kwargs.get(
      "lang", element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    encoding = kwargs.get("encoding", element.attrib.get("o-encoding"))
    text = kwargs.get("text", element.text)
    return Note(text=text, lang=lang, encoding=encoding)

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("note", _make_xml_attrs(self, **kwargs), engine)
    elem.text = self.text
    return elem


@dc.dataclass(kw_only=True, slots=True, unsafe_hash=True)
class Prop:
  text: str = dc.field(
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
  type: str = dc.field(
    hash=True,
    compare=True,
  )
  lang: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
    metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"},
  )
  encoding: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
    metadata={"export_name": "o-encoding"},
  )

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
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("prop", _make_xml_attrs(self, **kwargs), engine)
    elem.text = self.text
    return elem


@dc.dataclass(kw_only=True, slots=True, unsafe_hash=True)
class Header:
  creationtool: str = dc.field(
    hash=True,
    compare=True,
  )
  creationtoolversion: str = dc.field(
    hash=True,
    compare=True,
  )
  segtype: SEGTYPE = dc.field(
    hash=True,
    compare=True,
  )
  tmf: str = dc.field(
    hash=True,
    compare=True,
    metadata={"export_name": "o-tmf"},
  )
  adminlang: str = dc.field(
    hash=True,
    compare=True,
  )
  srclang: str = dc.field(
    hash=True,
    compare=True,
  )
  datatype: str = dc.field(
    hash=True,
    compare=True,
  )
  encoding: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
    metadata={"export_name": "o-encoding"},
  )
  creationdate: tp.Optional[dt.datetime] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  creationid: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  changedate: tp.Optional[dt.datetime] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  changeid: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  notes: abc.Sequence[Note] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
  props: abc.Sequence[Prop] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
  udes: abc.Sequence[Ude] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Header:
    creationtool = kwargs.get("creationtool", element.attrib.get("creationtool"))
    creationtoolversion = kwargs.get(
      "creationtoolversion", element.attrib.get("creationtoolversion")
    )
    segtype = kwargs.get("segtype", element.attrib.get("segtype"))
    tmf = kwargs.get("tmf", element.attrib.get("o-tmf"))
    adminlang = kwargs.get("adminlang", element.attrib.get("adminlang"))
    srclang = kwargs.get("srclang", element.attrib.get("srclang"))
    datatype = kwargs.get("datatype", element.attrib.get("datatype"))
    encoding = kwargs.get("encoding", element.attrib.get("o-encoding"))
    creationdate = kwargs.get("creationdate", element.attrib.get("creationdate"))
    creationid = kwargs.get("creationid", element.attrib.get("creationid"))
    changedate = kwargs.get("changedate", element.attrib.get("changedate"))
    changeid = kwargs.get("changeid", element.attrib.get("changeid"))
    if creationdate is not None:
      try:
        creationdate = dt.datetime.fromisoformat(creationdate)
      except (ValueError, TypeError):
        warn(f"could not parse {creationdate!r} as a datetime object.")
    if changedate is not None:
      try:
        changedate = dt.datetime.fromisoformat(changedate)
      except (ValueError, TypeError):
        warn(f"could not parse {changedate!r} as a datetime object.")
    if segtype is not None:
      try:
        segtype = SEGTYPE(segtype)
      except (ValueError, TypeError):
        warn(
          f"Expected one of 'block', 'paragraph', 'sentence' or 'phrase' for segtype but got {segtype!r}."
        )
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
      else _parse_notes(element),
      props=props
      if (props := kwargs.get("props")) is not None
      else _parse_props(element),
      udes=udes
      if (udes := kwargs.get("udes")) is not None
      else [Ude.from_element(ude) for ude in element.iter("ude")],
    )

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("header", _make_xml_attrs(self, **kwargs), engine)
    elem.extend(note.to_element(engine) for note in self.notes)  # type: ignore
    elem.extend(prop.to_element(engine) for prop in self.props)  # type: ignore
    elem.extend(ude.to_element(engine) for ude in self.udes)  # type: ignore
    return elem


@dc.dataclass(kw_only=True, slots=True, unsafe_hash=True)
class Tuv:
  lang: str = dc.field(
    hash=True,
    compare=True,
    metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"},
  )
  encoding: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
    metadata={"export_name": "o-encoding"},
  )
  datatype: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  usagecount: tp.Optional[int] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  lastusagedate: tp.Optional[dt.datetime] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  creationtool: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  creationtoolversion: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  creationdate: tp.Optional[dt.datetime] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  creationid: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  changedate: tp.Optional[dt.datetime] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  tmf: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  changeid: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  notes: abc.Sequence[Note] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
  props: abc.Sequence[Prop] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Tuv:
    lang = kwargs.get(
      "lang", element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    encoding = kwargs.get("encoding", element.attrib.get("o-encoding"))
    datatype = kwargs.get("datatype", element.attrib.get("datatype"))
    usagecount = kwargs.get("usagecount", element.attrib.get("usagecount"))
    lastusagedate = kwargs.get("lastusagedate", element.attrib.get("lastusagedate"))
    creationtool = kwargs.get("creationtool", element.attrib.get("creationtool"))
    creationtoolversion = kwargs.get(
      "creationtoolversion", element.attrib.get("creationtoolversion")
    )
    creationdate = kwargs.get("creationdate", element.attrib.get("creationdate"))
    creationid = kwargs.get("creationid", element.attrib.get("creationid"))
    changedate = kwargs.get("changedate", element.attrib.get("changedate"))
    tmf = kwargs.get("tmf", element.attrib.get("o-tmf"))
    changeid = kwargs.get("changeid", element.attrib.get("changeid"))
    if creationdate is not None:
      try:
        creationdate = dt.datetime.fromisoformat(creationdate)
      except (ValueError, TypeError):
        warn(f"could not parse {creationdate!r} as a datetime object.")
    if changedate is not None:
      try:
        changedate = dt.datetime.fromisoformat(changedate)
      except (ValueError, TypeError):
        warn(f"could not parse {changedate!r} as a datetime object.")
    if lastusagedate is not None:
      try:
        lastusagedate = dt.datetime.fromisoformat(lastusagedate)
      except (ValueError, TypeError):
        warn(f"could not parse {lastusagedate!r} as a datetime object.")
    if usagecount is not None:
      try:
        usagecount = int(usagecount)
      except (ValueError, TypeError):
        warn(f"could not parse {usagecount!r} as an int.")
    return Tuv(
      lang=lang,
      encoding=encoding,
      datatype=datatype,
      usagecount=usagecount,
      lastusagedate=lastusagedate,
      creationtool=creationtool,
      creationtoolversion=creationtoolversion,
      creationdate=creationdate,
      creationid=creationid,
      changedate=changedate,
      tmf=tmf,
      changeid=changeid,
      notes=notes
      if (notes := kwargs.get("notes")) is not None
      else _parse_notes(element),
      props=props
      if (props := kwargs.get("props")) is not None
      else _parse_props(element),
    )

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("tuv", _make_xml_attrs(self, **kwargs), engine)
    elem.extend(note.to_element(engine) for note in self.notes)  # type: ignore
    elem.extend(prop.to_element(engine) for prop in self.props)  # type: ignore
    return elem


@dc.dataclass(kw_only=True, slots=True, unsafe_hash=True)
class Tu:
  tuid: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  encoding: tp.Optional[str] = dc.field(
    hash=True,
    compare=True,
    default=None,
    metadata={"export_name": "o-encoding"},
  )
  datatype: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  usagecount: tp.Optional[int] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  lastusagedate: tp.Optional[dt.datetime] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  creationtool: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  creationtoolversion: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  creationdate: tp.Optional[dt.datetime] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  creationid: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  changedate: tp.Optional[dt.datetime] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  segtype: tp.Optional[SEGTYPE] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  changeid: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  tmf: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  srclang: tp.Optional[str] = dc.field(
    default=None,
    hash=True,
    compare=True,
  )
  tuvs: abc.Sequence[Tuv] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
  notes: abc.Sequence[Note] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
  props: abc.Sequence[Prop] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Tu:
    tuid = kwargs.get("tuid", element.attrib.get("tuid"))
    encoding = kwargs.get("encoding", element.attrib.get("o-encoding"))
    datatype = kwargs.get("datatype", element.attrib.get("datatype"))
    usagecount = kwargs.get("usagecount", element.attrib.get("usagecount"))
    lastusagedate = kwargs.get("lastusagedate", element.attrib.get("lastusagedate"))
    creationtool = kwargs.get("creationtool", element.attrib.get("creationtool"))
    creationtoolversion = kwargs.get(
      "creationtoolversion", element.attrib.get("creationtoolversion")
    )
    creationdate = kwargs.get("creationdate", element.attrib.get("creationdate"))
    creationid = kwargs.get("creationid", element.attrib.get("creationid"))
    changedate = kwargs.get("changedate", element.attrib.get("changedate"))
    segtype = kwargs.get("segtype", element.attrib.get("segtype"))
    tmf = kwargs.get("tmf", element.attrib.get("o-tmf"))
    changeid = kwargs.get("changeid", element.attrib.get("changeid"))
    srclang = kwargs.get("srclang", element.attrib.get("srclang"))
    if creationdate is not None:
      try:
        creationdate = dt.datetime.fromisoformat(creationdate)
      except (ValueError, TypeError):
        warn(f"could not parse {creationdate!r} as a datetime object.")
    if changedate is not None:
      try:
        changedate = dt.datetime.fromisoformat(changedate)
      except (ValueError, TypeError):
        warn(f"could not parse {changedate!r} as a datetime object.")
    if lastusagedate is not None:
      try:
        lastusagedate = dt.datetime.fromisoformat(lastusagedate)
      except (ValueError, TypeError):
        warn(f"could not parse {lastusagedate!r} as a datetime object.")
    if usagecount is not None:
      try:
        usagecount = int(usagecount)
      except (ValueError, TypeError):
        warn(f"could not parse {usagecount!r} as an int.")
    if segtype is not None:
      try:
        segtype = SEGTYPE(segtype)
      except (ValueError, TypeError):
        warn(
          f"Expected one of 'block', 'paragraph', 'sentence' or 'phrase' for segtype but got {segtype!r}."
        )
    return Tu(
      tuid=tuid,
      encoding=encoding,
      datatype=datatype,
      usagecount=usagecount,
      lastusagedate=lastusagedate,
      creationtool=creationtool,
      creationtoolversion=creationtoolversion,
      creationdate=creationdate,
      creationid=creationid,
      changedate=changedate,
      segtype=segtype,
      tmf=tmf,
      changeid=changeid,
      srclang=srclang,
      tuvs=tuvs if (tuvs := kwargs.get("tuvs")) is not None else _parse_tuvs(element),
      notes=notes
      if (notes := kwargs.get("notes")) is not None
      else _parse_notes(element),
      props=props
      if (props := kwargs.get("props")) is not None
      else _parse_props(element),
    )

  def to_element(
    self, engine: tp.Literal["lxml", "python"] = "lxml", **kwargs
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("tuv", _make_xml_attrs(self, **kwargs), engine)
    elem.extend(note.to_element(engine) for note in self.notes)  # type: ignore
    elem.extend(prop.to_element(engine) for prop in self.props)  # type: ignore
    elem.extend(tuv.to_element(engine) for tuv in self.tuvs)  # type: ignore
    return elem


@dc.dataclass(kw_only=True, slots=True, unsafe_hash=True)
class Tmx:
  header: tp.Optional[Header] = dc.field(
    default=None,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )
  tus: abc.Sequence[Tu] = dc.field(
    default_factory=list,
    hash=True,
    compare=True,
    metadata={"exclude": True},
  )

  @classmethod
  def from_element(cls, element: pyet.Element | lxet._Element, **kwargs) -> Tmx:
    header = kwargs.get("header", None)
    if header is None:
      if (header_elem := element.find("header")) is None:
        raise ValueError("could not find header")
      header = Header.from_element(header_elem)
    tus_ = kwargs.get("tus", None)
    if tus_ is None:
      if (body := element.find("body")) is None:
        raise ValueError("could not find body")
      tus_ = _parse_tus(body)
    return Tmx(header=header, tus=tus_)

  def to_element(
    self,
    engine: tp.Literal["lxml", "python"] = "lxml",
  ) -> lxet._Element | pyet.Element:
    elem = _make_elem("tmx", {"version": "1.4"}, engine)
    elem.append(self.header.to_element(engine))  # type: ignore
    body = _make_elem("body", dict(), engine)
    elem.append(body)  # type: ignore
    body.extend(tu.to_element(engine) for tu in self.tus)  # type: ignore
    return elem
