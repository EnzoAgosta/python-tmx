from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Self, TypedDict

import orjson


class NoteArrowDict(TypedDict):
  content: str
  lang: str | None
  o_encoding: str | None


class PropArrowDict(TypedDict):
  content: str
  type: str
  lang: str | None
  o_encoding: str | None


class HeaderArrowDict(TypedDict):
  creationtool: str
  creationtoolversion: str
  segtype: str
  o_tmf: str
  adminlang: str
  srclang: str
  datatype: str
  o_encoding: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  changeid: str | None
  props: list[PropArrowDict]
  notes: list[NoteArrowDict]


class SegmentPartFromArrowDict(TypedDict):
  content: str | list[SegmentPartFromArrowDict]
  type: SegmentPartType
  attributes: dict[str, str]

class SegmentPartToArrowDict(TypedDict):
  content: bytes
  type: str
  attributes: dict[str, str]


class TuvFromArrowDict(TypedDict):
  lang: str
  o_encoding: str | None
  datatype: str | None
  usagecount: int | None
  lastusagedate: datetime | None
  creationtool: str | None
  creationtoolversion: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  changeid: str | None
  o_tmf: str | None
  props: list[PropArrowDict]
  notes: list[NoteArrowDict]
  segment: list[SegmentPartFromArrowDict]

class TuvToArrowDict(TypedDict):
  lang: str
  o_encoding: str | None
  datatype: str | None
  usagecount: int | None
  lastusagedate: datetime | None
  creationtool: str | None
  creationtoolversion: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  changeid: str | None
  o_tmf: str | None
  props: list[PropArrowDict]
  notes: list[NoteArrowDict]
  segment: list[SegmentPartToArrowDict]


class TuToArrowDict(TypedDict):
  tuid: str | None
  o_encoding: str | None
  datatype: str | None
  usagecount: int | None
  lastusagedate: datetime | None
  creationtool: str | None
  creationtoolversion: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  segtype: str | None
  changeid: str | None
  o_tmf: str | None
  srclang: str | None
  props: list[PropArrowDict]
  notes: list[NoteArrowDict]
  variants: list[TuvToArrowDict]

class TuFromArrowDict(TypedDict):
  tuid: str | None
  o_encoding: str | None
  datatype: str | None
  usagecount: int | None
  lastusagedate: datetime | None
  creationtool: str | None
  creationtoolversion: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  segtype: str | None
  changeid: str | None
  o_tmf: str | None
  srclang: str | None
  props: list[PropArrowDict]
  notes: list[NoteArrowDict]
  variants: list[TuFromArrowDict]

class TmxFromArrowDict(TypedDict):
  version: str
  header: HeaderArrowDict
  body: list[TuFromArrowDict]

class TmxToArrowDict(TypedDict):
  version: str
  header: HeaderArrowDict
  body: list[TuToArrowDict]

class SegmentPartType(Enum):
  STRING = "string"
  BPT = "bpt"
  EPT = "ept"
  PH = "ph"
  IT = "it"
  HI = "hi"
  SUB = "sub"
  UT = "ut"


class SegType(Enum):
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

  def _to_arrow_dict(self) -> PropArrowDict:
    return {
      "content": self.content,
      "type": self.type,
      "lang": self.lang,
      "o_encoding": self.o_encoding,
    }


@dataclass(slots=True)
class Note:
  content: str
  lang: str | None = None
  o_encoding: str | None = None

  def _to_arrow_dict(self) -> NoteArrowDict:
    return {
      "content": self.content,
      "lang": self.lang,
      "o_encoding": self.o_encoding,
    }


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

  def _to_arrow_dict(self) -> HeaderArrowDict:
    return {
      "creationtool": self.creationtool,
      "creationtoolversion": self.creationtoolversion,
      "segtype": self.segtype.value,
      "o_tmf": self.o_tmf,
      "adminlang": self.adminlang,
      "srclang": self.srclang,
      "datatype": self.datatype,
      "o_encoding": self.o_encoding,
      "creationdate": self.creationdate,
      "creationid": self.creationid,
      "changedate": self.changedate,
      "changeid": self.changeid,
      "props": [prop._to_arrow_dict() for prop in self.props],
      "notes": [note._to_arrow_dict() for note in self.notes],
    }


@dataclass(slots=True)
class SegmentPart:
  content: str | list[Self]
  type: SegmentPartType
  attributes: dict[str, str] = field(default_factory=dict)

  def _to_arrow_dict(self) -> SegmentPartToArrowDict:
    return {
      "content": orjson.dumps(self.content),
      "type": self.type.value,
      "attributes": self.attributes,
    }


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
  segment: list[SegmentPart] = field(default_factory=list)

  def _to_arrow_dict(self) -> TuvToArrowDict:
    return {
      "lang": self.lang,
      "o_encoding": self.o_encoding,
      "datatype": self.datatype,
      "usagecount": self.usagecount,
      "lastusagedate": self.lastusagedate,
      "creationtool": self.creationtool,
      "creationtoolversion": self.creationtoolversion,
      "creationdate": self.creationdate,
      "creationid": self.creationid,
      "changedate": self.changedate,
      "changeid": self.changeid,
      "o_tmf": self.o_tmf,
      "props": [prop._to_arrow_dict() for prop in self.props],
      "notes": [note._to_arrow_dict() for note in self.notes],
      "segment": [part._to_arrow_dict() for part in self.segment],
    }


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

  def _to_arrow_dict(self) -> TuToArrowDict:
    return {
      "tuid": self.tuid,
      "o_encoding": self.o_encoding,
      "datatype": self.datatype,
      "usagecount": self.usagecount,
      "lastusagedate": self.lastusagedate,
      "creationtool": self.creationtool,
      "creationtoolversion": self.creationtoolversion,
      "creationdate": self.creationdate,
      "creationid": self.creationid,
      "changedate": self.changedate,
      "segtype": self.segtype.value if self.segtype else self.segtype,
      "changeid": self.changeid,
      "o_tmf": self.o_tmf,
      "srclang": self.srclang,
      "props": [prop._to_arrow_dict() for prop in self.props],
      "notes": [note._to_arrow_dict() for note in self.notes],
      "variants": [tuv._to_arrow_dict() for tuv in self.variants],
    }


@dataclass(slots=True)
class Tmx:
  version: str
  header: Header
  body: list[Tu] = field(default_factory=list)

  def _to_arrow_dict(self) -> TmxToArrowDict:
    return {
      "version": self.version,
      "header": self.header._to_arrow_dict(),
      "body": [tu._to_arrow_dict() for tu in self.body],
    }
