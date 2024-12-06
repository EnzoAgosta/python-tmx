from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
from warnings import deprecated


@dataclass(slots=True)
class Structural:
  pass


@dataclass(slots=True)
class Inline:
  pass


@dataclass(slots=True)
class Note(Structural):
  text: str
  lang: str | None = None
  encoding: str | None = None


@dataclass(slots=True)
class Prop(Structural):
  text: str
  type: str
  lang: str | None = None
  encoding: str | None = None


@dataclass(slots=True)
class Map(Structural):
  unicode: str
  code: str | None = None
  ent: str | None = None
  subst: str | None = None


@dataclass(slots=True)
class Ude(Structural):
  name: str
  base: str | None = None
  maps: list[Map] = field(default_factory=list)


@dataclass(slots=True)
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
  props: list[Prop] = field(default_factory=list)
  notes: list[Note] = field(default_factory=list)
  ude: list[Ude] = field(default_factory=list)

  def __post_init__(self):
    if isinstance(self.creationdate, str):
      self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
    if isinstance(self.changedate, str):
      self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")


@dataclass(slots=True)
class Tuv(Structural):
  segment: list[Bpt | Ept | It | Hi | Ph | str] = field(default_factory=list)
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
  notes: list[Note] = field(default_factory=list)
  props: list[Prop] = field(default_factory=list)

  def __post_init__(self):
    if isinstance(self.lastusagedate, str):
      self.lastusagedate = datetime.strptime(self.lastusagedate, r"%Y%m%dT%H%M%SZ")
    if isinstance(self.creationdate, str):
      self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
    if isinstance(self.changedate, str):
      self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
    if isinstance(self.usagecount, str):
      self.usagecount = int(self.usagecount)


@dataclass(slots=True)
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
  tuvs: list[Tuv] = field(default_factory=list)
  notes: list[Note] = field(default_factory=list)
  props: list[Prop] = field(default_factory=list)

  def __post_init__(self):
    if isinstance(self.lastusagedate, str):
      self.lastusagedate = datetime.strptime(self.lastusagedate, r"%Y%m%dT%H%M%SZ")
    if isinstance(self.creationdate, str):
      self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
    if isinstance(self.changedate, str):
      self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
    if isinstance(self.usagecount, str):
      self.usagecount = int(self.usagecount)


@dataclass(slots=True)
class Tmx(Structural):
  header: Header | None = None
  tu: list[Tu] = field(default_factory=list)


@dataclass(slots=True)
class Bpt(Inline):
  i: int | str
  x: int | str | None = None
  type: str | None = None
  text: list[str | Sub] = field(default_factory=list)

  def __post_init__(self):
    if isinstance(self.i, str):
      self.i = int(self.i)
    if isinstance(self.x, str):
      self.x = int(self.x)


@dataclass(slots=True)
class Ept(Inline):
  i: int | str
  text: list[str | Sub] = field(default_factory=list)

  def __post_init__(self):
    if isinstance(self.i, str):
      self.i = int(self.i)


@dataclass(slots=True)
class Hi(Inline):
  x: int | str | None = None
  type: str | None = None
  text: list[str | Bpt | Ept | It | Ph | Hi] = field(default_factory=list)

  def __post_init__(self):
    if isinstance(self.x, str):
      self.x = int(self.x)


@dataclass(slots=True)
class It(Inline):
  pos: Literal["begin", "end"]
  x: int | str | None = None
  type: str | None = None
  text: list[str | Sub] = field(default_factory=list)

  def __post_init__(self):
    if isinstance(self.x, str):
      self.x = int(self.x)


@dataclass(slots=True)
class Ph(Inline):
  i: int | str | None = None
  x: int | str | None = None
  assoc: Literal["p", "f", "b"] | None = None
  text: list[str | Sub] = field(default_factory=list)

  def __post_init__(self):
    if isinstance(self.i, str):
      self.i = int(self.i)
    if isinstance(self.x, str):
      self.x = int(self.x)


@dataclass(slots=True)
class Sub(Inline):
  type: str | None = None
  datatype: str | None = None
  text: list[str | Bpt | Ept | It | Ph | Hi] = field(default_factory=list)


@deprecated(
  "The Ut element is deprecated, "
  "please check https://www.gala-global.org/tmx-14b#ContentMarkup_Rules to "
  "know with which element to replace it with."
)
@dataclass(slots=True)
class Ut(Inline):
  x: int | str | None = None
  text: list[str | Sub] = field(default_factory=list)
