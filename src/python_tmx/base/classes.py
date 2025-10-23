from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Self

type BaseStructuralElement = Prop | Note | Header | Tu | Tuv
type BaseInlineElement = Bpt | Ept | It | Hi | Ph | Sub
type BaseElement = BaseInlineElement | BaseStructuralElement


class Pos(StrEnum):
  BEGIN = "begin"
  END = "end"


class Assoc(StrEnum):
  P = "p"
  F = "f"
  B = "b"


class SegType(StrEnum):
  BLOCK = "block"
  PARAGRAPH = "paragraph"
  SENTENCE = "sentence"
  PHRASE = "phrase"


@dataclass(slots=True)
class Prop:
  content: str
  type: str
  lang: str | None = None
  o_encoding: str | None = None


@dataclass(slots=True)
class Note:
  content: str
  lang: str | None = None
  o_encoding: str | None = None


@dataclass(slots=True)
class Header:
  creationtool: str
  creationtoolversion: str
  segtype: SegType
  o_tmf: str
  adminlang: str
  srclang: str
  datatype: str
  o_encoding: str | None = None
  creationdate: datetime | None = None
  creationid: str | None = None
  changedate: datetime | None = None
  changeid: str | None = None
  props: list[Prop] = field(default_factory=list)
  notes: list[Note] = field(default_factory=list)


@dataclass(slots=True)
class Bpt:
  content: list[Sub | str]
  i: int
  x: int | None = None
  type: str | None = None


@dataclass(slots=True)
class Ept:
  content: list[Sub | str]
  i: int


@dataclass(slots=True)
class Hi:
  content: list[str | Bpt | Ept | It | Ph | Self]
  x: int | None
  type: str | None


@dataclass(slots=True)
class It:
  content: list[str | Sub]
  pos: Pos
  x: int | None
  type: str | None


@dataclass(slots=True)
class Ph:
  content: list[Sub | str]
  x: int | None
  type: str | None
  assoc: Assoc | None


@dataclass(slots=True)
class Sub:
  content: list[Bpt | Ept | It | Ph | Hi | str]
  datatype: str | None
  type: str | None


@dataclass(slots=True)
class Tuv:
  lang: str
  o_encoding: str | None = None
  datatype: str | None = None
  usagecount: int | None = None
  lastusagedate: datetime | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: datetime | None = None
  creationid: str | None = None
  changedate: datetime | None = None
  changeid: str | None = None
  o_tmf: str | None = None
  props: list[Prop] = field(default_factory=list)
  notes: list[Note] = field(default_factory=list)
  segment: list[str | Bpt | Ept | Hi | It | Ph] = field(default_factory=list)


@dataclass(slots=True)
class Tu:
  tuid: str | None = None
  o_encoding: str | None = None
  datatype: str | None = None
  usagecount: int | None = None
  lastusagedate: datetime | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: datetime | None = None
  creationid: str | None = None
  changedate: datetime | None = None
  segtype: SegType | None = None
  changeid: str | None = None
  o_tmf: str | None = None
  srclang: str | None = None
  props: list[Prop] = field(default_factory=list)
  notes: list[Note] = field(default_factory=list)
  variants: list[Tuv] = field(default_factory=list)


@dataclass(slots=True)
class Tmx:
  version: str
  header: Header
  body: list[Tu] = field(default_factory=list)
