from __future__ import annotations

from datetime import datetime
from typing import Literal, NotRequired, Required, TypedDict


class PropArrowDict(TypedDict):
  text: Required[str]
  type: Required[str]
  lang: NotRequired[str]
  o_encoding: NotRequired[str]


class NoteArrowDict(TypedDict):
  text: Required[str]
  lang: NotRequired[str]
  o_encoding: NotRequired[str]


class HeaderArrowDict(TypedDict):
  creationtool: Required[str]
  creationtoolversion: Required[str]
  segtype: Required[Literal["block", "sentence", "phrase", "paragraph"]]
  o_tmf: Required[str]
  adminlang: Required[str]
  srclang: Required[str]
  datatype: Required[str]
  o_encoding: NotRequired[str]
  creationdate: NotRequired[datetime]
  creationid: NotRequired[str]
  changedate: NotRequired[datetime]
  changeid: NotRequired[str]
  props: Required[list[PropArrowDict]]
  notes: Required[list[NoteArrowDict]]


class BptArrowDict(TypedDict):
  tag: Required[Literal["bpt"]]
  content: Required[bytes]
  i: Required[int]
  x: NotRequired[int]
  type: NotRequired[str]


class EptArrowDict(TypedDict):
  tag: Required[Literal["ept"]]
  content: Required[bytes]
  i: Required[int]


class HiArrowDict(TypedDict):
  tag: Required[Literal["hi"]]
  content: Required[bytes]
  x: NotRequired[int]
  type: NotRequired[str]


class ItArrowDict(TypedDict):
  tag: Required[Literal["it"]]
  content: Required[bytes]
  pos: Required[Literal["begin", "end"]]
  x: NotRequired[int]
  type: NotRequired[str]


class PhArrowDict(TypedDict):
  tag: Required[Literal["ph"]]
  content: Required[bytes]
  x: NotRequired[int]
  type: NotRequired[str]
  assoc: NotRequired[Literal["p", "f", "b"]]


class SubArrowDict(TypedDict):
  tag: Required[Literal["sub"]]
  content: Required[bytes]
  datatype: NotRequired[str]
  type: NotRequired[str]


class TuvArrowDict(TypedDict):
  lang: Required[str]
  o_encoding: NotRequired[str]
  datatype: NotRequired[str]
  usagecount: NotRequired[int]
  lastusagedate: NotRequired[datetime]
  creationtool: NotRequired[str]
  creationtoolversion: NotRequired[str]
  creationdate: NotRequired[datetime]
  creationid: NotRequired[str]
  changedate: NotRequired[datetime]
  changeid: NotRequired[str]
  o_tmf: NotRequired[str]
  props: Required[list[PropArrowDict]]
  notes: Required[list[NoteArrowDict]]
  content: Required[bytes]


class TuArrowDict(TypedDict):
  tuid: NotRequired[str]
  o_encoding: NotRequired[str]
  datatype: NotRequired[str]
  usagecount: NotRequired[int]
  lastusagedate: NotRequired[datetime]
  creationtool: NotRequired[str]
  creationtoolversion: NotRequired[str]
  creationdate: NotRequired[datetime]
  creationid: NotRequired[str]
  changedate: NotRequired[datetime]
  segtype: NotRequired[Literal["block", "sentence", "phrase", "paragraph"]]
  changeid: NotRequired[str]
  o_tmf: NotRequired[str]
  srclang: NotRequired[str]
  props: Required[list[PropArrowDict]]
  notes: Required[list[NoteArrowDict]]
  variants: Required[list[TuvArrowDict]]


class TmxArrowDict(TypedDict):
  version: Required[str]
  header: Required[HeaderArrowDict]
  body: Required[list[TuArrowDict]]
