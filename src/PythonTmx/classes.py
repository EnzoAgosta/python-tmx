from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import MutableSequence
from datetime import datetime
from typing import Iterable, Literal, Self, TypeAlias
from warnings import deprecated

import lxml.etree as et
from attrs import define, field

XmlElement: TypeAlias = et._Element | ET.Element
TmxElement: TypeAlias = (
  "Note | Prop | Ude | Map | Bpt | Ept | It | Ph | Hi | Ut | Sub | Ude | Tuv | Tu"
)


@define(kw_only=True)
class Note:
  text: str
  lang: str | None = None
  encoding: str | None = None

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      text=elem.text,  # type: ignore
      lang=elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
      encoding=elem.get("o-encoding"),
    )


@define(kw_only=True)
class Prop:
  text: str
  type: str
  lang: str | None = None
  encoding: str | None = None

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      text=elem.text,  # type: ignore
      type=elem.get("type"),  # type: ignore
      lang=elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
      encoding=elem.get("o-encoding"),
    )


@define(kw_only=True)
class Map:
  unicode: str
  code: str | None = None
  ent: str | None = None
  subst: str | None = None

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(**elem.attrib)


@define(kw_only=True)
class Ude:
  name: str
  base: str | None = None
  maps: MutableSequence[Map] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib, maps=[Map.from_element(e) for e in elem if e.tag == "map"]
    )


@define(kw_only=True)
class Header:
  creationtool: str
  creationtoolversion: str
  segtype: str
  tmf: str
  adminlang: str
  srclang: str
  datatype: str
  encoding: str | None = None
  creationdate: str | datetime | None = None
  creationid: str | None = None
  changedate: str | datetime | None = None
  changeid: str | None = None
  props: MutableSequence[Prop] = field(factory=list)
  notes: MutableSequence[Note] = field(factory=list)
  udes: MutableSequence[Ude] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    attribs = elem.attrib
    props, notes, udes = [], [], []
    for e in elem:
      if e.tag == "prop":
        props.append(Prop.from_element(e))
      elif e.tag == "note":
        notes.append(Note.from_element(e))
      elif e.tag == "ude":
        udes.append(Ude.from_element(e))
    return cls(
      encoding=attribs.pop("o-encoding"),
      tmf=attribs.pop("o-tmf"),
      **attribs,
      props=props,
      notes=notes,
      udes=udes,
    )

  def __attrs_post__init__(self):
    if self.creationdate is not None and not isinstance(self.creationdate, datetime):
      try:
        self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.changedate is not None and not isinstance(self.changedate, datetime):
      try:
        self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass


def _parse_inline(seg: XmlElement, mask: Iterable[str]) -> list:
  segment: list = []
  for e in seg:
    if seg.text is not None:
      segment.append(seg.text)
    for e in seg:
      if str(e.tag) not in mask:
        continue
      if e.tag == "bpt":
        segment.append(Bpt.from_element(e))
      elif e.tag == "ept":
        segment.append(Ept.from_element(e))
      elif e.tag == "it":
        segment.append(It.from_element(e))
      elif e.tag == "ph":
        segment.append(Ph.from_element(e))
      elif e.tag == "hi":
        segment.append(Hi.from_element(e))
      elif e.tag == "ut":
        segment.append(Ut.from_element(e))
      elif e.tag == "sub":
        segment.append(Sub.from_element(e))
      if e.tail is not None:
        segment.append(e.tail)
  return segment


@define(kw_only=True)
class Tuv:
  segment: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(factory=list)
  encoding: str | None = None
  datatype: str | None = None
  usagecount: str | int | None = None
  lastusagedate: str | datetime | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: str | datetime | None = None
  creationid: str | None = None
  changedate: str | datetime | None = None
  changeid: str | None = None
  tmf: str | None = None
  notes: MutableSequence[Note] = field(factory=list)
  props: MutableSequence[Prop] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    attribs = elem.attrib
    encoding = attribs.pop("o-encoding")
    tmf = attribs.pop("o-tmf")
    props, notes = [], []
    if (seg := elem.find("seg")) is not None:
      segment = _parse_inline(seg, mask=("bpt", "ept", "it", "ph", "hi", "ut"))
    else:
      segment = []
    for e in elem:
      if e.tag == "prop":
        props.append(Prop.from_element(e))
      elif e.tag == "note":
        notes.append(Note.from_element(e))
    return cls(
      segment=segment,
      encoding=encoding,
      tmf=tmf,
      props=props,
      notes=notes,
      **attribs,
    )

  def __attrs_post_init__(self):
    if self.lastusagedate is not None and not isinstance(self.lastusagedate, datetime):
      try:
        self.lastusagedate = datetime.strptime(self.lastusagedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.creationdate is not None and not isinstance(self.creationdate, datetime):
      try:
        self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.changedate is not None and not isinstance(self.changedate, datetime):
      try:
        self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.usagecount is not None and not isinstance(self.usagecount, int):
      try:
        self.usagecount = int(self.usagecount)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Tu:
  tuid: str | None = None
  encoding: str | None = None
  datatype: str | None = None
  usagecount: str | int | None = None
  lastusagedate: str | datetime | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: str | datetime | None = None
  creationid: str | None = None
  changedate: str | datetime | None = None
  segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None
  changeid: str | None = None
  tmf: str | None = None
  srclang: str | None = None
  tuvs: MutableSequence[Tuv] = field(factory=list)
  notes: MutableSequence[Note] = field(factory=list)
  props: MutableSequence[Prop] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    props, notes, tuvs = [], [], []
    attribs = elem.attrib
    for e in elem:
      if e.tag == "prop":
        props.append(Prop.from_element(e))
      elif e.tag == "note":
        notes.append(Note.from_element(e))
      elif e.tag == "tuv":
        tuvs.append(Tuv.from_element(e))
    return cls(
      encoding=attribs.pop("o-encoding"),
      tmf=attribs.pop("o-tmf"),
      **attribs,
      props=props,
      notes=notes,
      tuvs=tuvs,
    )

  def __attrs_post_init__(self):
    if self.lastusagedate is not None and not isinstance(self.lastusagedate, datetime):
      try:
        self.lastusagedate = datetime.strptime(self.lastusagedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.creationdate is not None and not isinstance(self.creationdate, datetime):
      try:
        self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.changedate is not None and not isinstance(self.changedate, datetime):
      try:
        self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.usagecount is not None and not isinstance(self.usagecount, int):
      try:
        self.usagecount = int(self.usagecount)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Tmx:
  header: Header | None = None
  tus: MutableSequence[Tu] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    if (header_elem := elem.find("header")) is not None:
      header = Header.from_element(header_elem)
    else:
      header = None
    tus: MutableSequence[Tu] = []
    if (body := elem.find("body")) is not None:
      for e in body:
        if e.tag == "tu":
          tus.append(Tu.from_element(e))
    return cls(header=header, tus=tus)


@define(kw_only=True)
class Bpt:
  i: int | str
  x: int | str | None = None
  type: str | None = None
  content: MutableSequence[str | Sub] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("sub",)),
    )

  def __attrs_post_init__(self):
    if self.i is not None and not isinstance(self.i, int):
      try:
        self.i = int(self.i)
      except (TypeError, ValueError):
        pass
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Ept:
  i: int | str
  content: MutableSequence[str | Sub] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("sub",)),
    )

  def __attrs_post_init__(self):
    if self.i is not None and not isinstance(self.i, int):
      try:
        self.i = int(self.i)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Hi:
  x: int | str | None = None
  type: str | None = None
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("bpt", "ept", "it", "ph", "hi", "ut")),
    )

  def __attrs_post_init__(self):
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class It:
  pos: Literal["begin", "end"]
  x: int | str | None = None
  type: str | None = None
  content: MutableSequence[str | Sub] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("sub",)),
    )

  def __attrs_post_init__(self):
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Ph:
  i: int | str | None = None
  x: int | str | None = None
  assoc: Literal["p", "f", "b"] | None = None
  content: MutableSequence[str | Sub] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("sub",)),
    )

  def __attrs_post_init__(self):
    if self.i is not None and not isinstance(self.i, int):
      try:
        self.i = int(self.i)
      except (TypeError, ValueError):
        pass
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Sub:
  type: str | None = None
  datatype: str | None = None
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("bpt", "ept", "it", "ph", "hi", "ut")),
    )


@deprecated(
  "The Ut element is deprecated, "
  "please check https://www.gala-global.org/tmx-14b#ContentMarkup_Rules to "
  "know with which element to replace it with."
)
@define(kw_only=True)
class Ut:
  x: int | str | None = None
  content: MutableSequence[str | Sub] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("sub",)),
    )

  def __attrs_post_init__(self):
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass
