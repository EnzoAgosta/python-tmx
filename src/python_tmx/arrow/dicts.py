from __future__ import annotations

from datetime import datetime
from typing import Literal, NotRequired, Required, TypedDict


class PropDict(TypedDict):
  text: Required[str]
  type: Required[str]
  lang: NotRequired[str]
  o_encoding: NotRequired[str]


class NoteDict(TypedDict):
  text: Required[str]
  lang: NotRequired[str]
  o_encoding: NotRequired[str]


class HeaderDict(TypedDict):
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
  props: Required[list[PropDict]]
  notes: Required[list[NoteDict]]


class BptDict(TypedDict):
  content: Required[list[SubDict | str]]
  i: Required[int]
  x: NotRequired[int]
  type: NotRequired[str]


class EptDict(TypedDict):
  content: Required[list[SubDict | str]]
  i: Required[int]


class HiDict(TypedDict):
  content: Required[list[str | BptDict | EptDict | ItDict | PhDict | HiDict]]
  x: NotRequired[int]
  type: NotRequired[str]


class ItDict(TypedDict):
  content: Required[list[str | SubDict]]
  pos: Required[Literal["begin", "end"]]
  x: NotRequired[int]
  type: NotRequired[str]


class PhDict(TypedDict):
  content: Required[list[SubDict | str]]
  x: NotRequired[int]
  type: NotRequired[str]
  assoc: NotRequired[Literal["p", "f", "b"]]


class SubDict(TypedDict):
  content: Required[list[BptDict | EptDict | ItDict | PhDict | HiDict | str]]
  datatype: NotRequired[str]
  type: NotRequired[str]


class TuvDict(TypedDict):
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
  props: Required[list[PropDict]]
  notes: Required[list[NoteDict]]
  content: Required[list[str | BptDict | EptDict | HiDict | ItDict | PhDict]]


class TuDict(TypedDict):
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
  props: Required[list[PropDict]]
  notes: Required[list[NoteDict]]
  variants: Required[list[TuvDict]]


class TmxDict(TypedDict):
  version: Required[str]
  header: Required[HeaderDict]
  body: Required[list[TuDict]]
