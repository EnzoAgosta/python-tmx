from __future__ import annotations

import datetime as dt
import xml.etree.ElementTree as et
from collections.abc import MutableSequence
from dataclasses import field
from typing import Literal

from PythonTmx.errors import ValidationError
from PythonTmx.validation import validate_unicode_value


class Note:
  def __init__(
    self,
    text: str,
    lang: str | None = None,
    encoding: str | None = None,
    *,
    init_validate: bool = False,
  ):
    self.text = text
    self.lang = lang
    self.encoding = encoding


class Prop:
  def __init__(
    self,
    text: str,
    type: str,
    lang: str | None = None,
    encoding: str | None = None,
    *,
    init_validate: bool = False,
  ):
    self.text = text
    self.lang = lang
    self.type = type
    self.encoding = encoding


class Map:
  __slots__ = ("unicode", "code", "ent", "subst")

  def __init__(
    self,
    unicode: str,
    code: str | None = None,
    ent: str | None = None,
    subst: str | None = None,
    *,
    init_validate: bool = False,
  ):
    self.unicode = unicode
    self.code = code
    self.ent = ent
    self.subst = subst
    if init_validate:
      self.validate()

  def validate(self):
    try:
      validate_unicode_value(self.unicode)
    except (ValueError, TypeError) as e:
      raise ValidationError("unicode") from e
    if self.code is not None:
      try:
        validate_unicode_value(self.code)
      except (ValueError, TypeError) as e:
        raise ValidationError("code") from e
    if self.ent is not None:
      try:
        if not self.ent.isascii():
          raise ValueError("value must be ASCII")
      except (ValueError, TypeError) as e:
        raise ValidationError("ent") from e
    if self.subst is not None:
      try:
        if not self.subst.isascii():
          raise ValueError("value must be ASCII")
      except (ValueError, TypeError) as e:
        raise ValidationError("subst") from e

  def to_element(self) -> et.Element:
    self.validate(**{s: getattr(self, s) for s in self.__slots__})
    return et.Element(
      "map",
      {s: getattr(self, s) for s in self.__slots__ if getattr(self, s) is not None},
    )

  @classmethod
  def from_element(cls, element: et.Element, init_validate: bool = False) -> Map:
    if not element.tag == "map":
      raise ValueError("element's tag must be 'map'")
    return cls(**element.attrib, init_validate=init_validate)


class Ude:
  __slots__ = ("name", "base", "maps")

  def __init__(
    self,
    name: str,
    base: str | None = None,
    maps: MutableSequence[Map] | None = None,
    *,
    init_validate: bool = False,
  ) -> None:
    self.name = name
    self.base = base
    self.maps = maps if maps is not None else []
    if init_validate:
      self.validate()

  def validate(self):
    if not isinstance(self.name, str):
      raise ValidationError("name") from TypeError(
        "value must be a string but got", type(self.name)
      )
    if len(self.maps) and any(map.code is not None for map in self.maps):
      if not isinstance(self.base, str):
        raise ValidationError("base") from TypeError(
          "value must be a string if at least one map has a code but got",
          type(self.base),
        )
    if self.base is not None and not isinstance(self.base, str):
      raise ValidationError("base") from TypeError(
        "value must be a string but got", type(self.base)
      )


class Header:
  creationtool: str
  creationtoolversion: str
  segtype: Literal["block", "paragraph", "sentence", "phrase"]
  tmf: str
  adminlang: str
  srclang: str
  datatype: str
  encoding: str | None = None
  creationdate: dt.datetime | None = None
  creationid: str | None = None
  changedate: dt.datetime | None = None
  changeid: str | None = None
  notes: MutableSequence[Note] = field(default_factory=list)
  props: MutableSequence[Prop] = field(default_factory=list)
  udes: MutableSequence[Ude] = field(default_factory=list)


class Tuv:
  lang: str
  segment: MutableSequence[str] = field(default_factory=list)
  encoding: str | None = None
  datatype: str | None = None
  usagecount: str | None = None
  lastusagedate: dt.datetime | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: dt.datetime | None = None
  creationid: str | None = None
  changedate: dt.datetime | None = None
  tmf: str | None = None
  changeid: str | None = None
  notes: MutableSequence[str] = field(default_factory=list)
  props: MutableSequence[str] = field(default_factory=list)


class Tu:
  tuvs: MutableSequence[Tuv] = field(default_factory=list)
  notes: MutableSequence[Note] = field(default_factory=list)
  props: MutableSequence[Prop] = field(default_factory=list)
  tuid: str | None = None
  encoding: str | None = None
  datatype: str | None = None
  usagecount: str | None = None
  lastusagedate: str | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: str | None = None
  creationid: str | None = None
  changedate: str | None = None
  segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None
  changeid: str | None = None
  tmf: str | None = None
  srclang: str | None = None


class Tmx:
  header: Header
  tus: MutableSequence[Tu] = field(default_factory=list)


class Sub:
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    default_factory=list
  )
  type: str | None = None
  datatype: str | None = None


class Bpt:
  i: int
  content: MutableSequence[str | Sub] = field(default_factory=list)
  x: int | None = None
  type: str | None = None


class Ept:
  i: int
  content: MutableSequence[str | Sub] = field(default_factory=list)


class It:
  pos: Literal["begin", "end"]
  content: MutableSequence[str | Sub] = field(default_factory=list)
  x: int | None = None
  type: str | None = None


class Ph:
  content: MutableSequence[str | Sub] = field(default_factory=list)
  x: int | None = None
  assoc: Literal["p", "f", "b"] | None = None
  type: str | None = None


class Hi:
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    default_factory=list
  )
  x: int | None = None
  type: str | None = None


class Ut:
  content: MutableSequence[str | Sub] = field(default_factory=list)
  x: int | None = None
