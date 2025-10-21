from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Self


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


@dataclass(slots=True)
class Note:
  content: str
  lang: str | None = None
  o_encoding: str | None = None


@dataclass(slots=True)
class SegmentPart:
  content: str | list[Self]
  type: SegmentPartType
  attributes: dict[str, str] = field(default_factory=dict)


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

  def _arrow_attributes(self) -> dict[str, str | int | datetime]:
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
class TmxFile:
  header: Header
  body: list[Tu] = field(default_factory=list)
