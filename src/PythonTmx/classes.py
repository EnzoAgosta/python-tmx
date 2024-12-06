from __future__ import annotations

from datetime import datetime
from typing import Literal, Self
from warnings import deprecated

from attrs import define, field

from . import XmlElement


@define
class TmxElement: ...


@define
class Structural(TmxElement): ...


@define
class Inline(TmxElement): ...


@define(kw_only=True)
class Note(Structural):
  text: str
  lang: str | None = None
  encoding: str | None = None

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      text=elem.text, lang=elem.get("xml:lang"), encoding=elem.get("o-encoding")
    )


@define(kw_only=True)
class Prop(Structural):
  text: str
  type: str
  lang: str | None = None
  encoding: str | None = None

  def __init__(
    self,
    **kwargs,
  ):
    if "lang" not in kwargs:
      if "{http://www.w3.org/XML/1998/namespace}lang" in kwargs:
        kwargs["lang"] = kwargs.pop("{http://www.w3.org/XML/1998/namespace}lang")
    self.__attrs_init__(**kwargs)


@define(kw_only=True)
class Map(Structural):
  unicode: str
  code: str | None = None
  ent: str | None = None
  subst: str | None = None


@define(kw_only=True)
class Ude(Structural):
  name: str
  base: str | None = None
  maps: list[Map] = field(factory=list)


@define(kw_only=True)
class Header(Structural):
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
  props: list[Prop] = field(factory=list)
  notes: list[Note] = field(factory=list)
  ude: list[Ude] = field(factory=list)

  def __init__(
    self,
    **kwargs,
  ):
    if "encoding" not in kwargs:
      if "o-encoding" in kwargs:
        kwargs["encoding"] = kwargs.pop("o-encoding")
    if "tmf" not in kwargs:
      if "o-tmf" in kwargs:
        kwargs["tmf"] = kwargs.pop("o-tmf")
    self.__attrs_init__(**kwargs)

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


@define(kw_only=True)
class Tuv(Structural):
  segment: list[Bpt | Ept | It | Hi | Ph | str] = field(factory=list)
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
  notes: list[Note] = field(factory=list)
  props: list[Prop] = field(factory=list)

  def __init__(
    self,
    **kwargs,
  ):
    if "encoding" not in kwargs:
      if "o-encoding" in kwargs:
        kwargs["encoding"] = kwargs.pop("o-encoding")
    if "tmf" not in kwargs:
      if "o-tmf" in kwargs:
        kwargs["tmf"] = kwargs.pop("o-tmf")
    self.__attrs_init__(**kwargs)

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
class Tu(Structural):
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
  tuvs: list[Tuv] = field(factory=list)
  notes: list[Note] = field(factory=list)
  props: list[Prop] = field(factory=list)

  def __init__(
    self,
    **kwargs,
  ):
    if "encoding" not in kwargs:
      if "o-encoding" in kwargs:
        kwargs["encoding"] = kwargs.pop("o-encoding")
    if "tmf" not in kwargs:
      if "o-tmf" in kwargs:
        kwargs["tmf"] = kwargs.pop("o-tmf")
    self.__attrs_init__(**kwargs)

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
class Tmx(Structural):
  header: Header | None = None
  tu: list[Tu] = field(factory=list)


@define(kw_only=True)
class Bpt(Inline):
  i: int | str
  x: int | str | None = None
  type: str | None = None
  content: list[str | Sub] = field(factory=list)

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
class Ept(Inline):
  i: int | str
  content: list[str | Sub] = field(factory=list)

  def __attrs_post_init__(self):
    if self.i is not None and not isinstance(self.i, int):
      try:
        self.i = int(self.i)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Hi(Inline):
  x: int | str | None = None
  type: str | None = None
  content: list[str | Bpt | Ept | It | Ph | Hi] = field(factory=list)

  def __attrs_post_init__(self):
    if self.i is not None and not isinstance(self.i, int):
      try:
        self.i = int(self.i)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class It(Inline):
  pos: Literal["begin", "end"]
  x: int | str | None = None
  type: str | None = None
  content: list[str | Sub] = field(factory=list)

  def __attrs_post_init__(self):
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Ph(Inline):
  i: int | str | None = None
  x: int | str | None = None
  assoc: Literal["p", "f", "b"] | None = None
  content: list[str | Sub] = field(factory=list)

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
class Sub(Inline):
  type: str | None = None
  datatype: str | None = None
  text: list[str | Bpt | Ept | It | Ph | Hi] = field(factory=list)


@deprecated(
  "The Ut element is deprecated, "
  "please check https://www.gala-global.org/tmx-14b#ContentMarkup_Rules to "
  "know with which element to replace it with."
)
@define(kw_only=True)
class Ut(Inline):
  x: int | str | None = None
  text: list[str | Sub] = field(factory=list)

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
