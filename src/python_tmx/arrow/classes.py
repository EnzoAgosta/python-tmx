from __future__ import annotations

from abc import abstractmethod
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Self, Type

import orjson
import pyarrow as pa

from python_tmx.arrow.structs import (
  BPT_STRUCT,
  EPT_STRUCT,
  HEADER_STRUCT,
  HI_STRUCT,
  IT_STRUCT,
  NOTE_STRUCT,
  PH_STRUCT,
  PROP_STRUCT,
  SUB_STRUCT,
  TMX_STRUCT,
  TU_STRUCT,
  TUV_STRUCT,
)
from python_tmx.base.classes import (
  Assoc,
  BaseElement,
  BaseInlineElement,
  Bpt,
  Ept,
  Hi,
  It,
  Note,
  Ph,
  Pos,
  Prop,
  SegType,
  Sub,
)


def _parse_inline_dict(value: dict) -> BaseInlineElement:
  content = value.pop("content")
  content = [_parse_inline_dict(child) for child in content]
  elem: Type[BaseInlineElement]
  if value.get("i") is not None:
    if value.get("x") is not None:
      elem = Bpt
    else:
      elem = Ept
  elif value.get("pos") is not None:
    elem = It
  elif value.get("assoc") is not None:
    elem = Ph
  elif value.get("x") is not None:
    elem = Hi
  else:
    elem = Sub
  return elem(content=content, **value)


def _asdict(obj) -> dict[str, str | int | datetime | bytes]:
  if isinstance(obj, Enum):
    return obj.value
  return asdict(obj, dict_factory=_asdict)


def validate_scalar(scalar: pa.StructScalar, struct: pa.StructType) -> None:
  if not scalar.type.equals(struct):
    raise TypeError(f"Expected struct {struct} but got {scalar.type}")
  if not all(val.is_valid for val in scalar.values()):
    raise ValueError("Scalar has invalid fields")


class ArrowStructWrapper:
  _struct: ClassVar[pa.StructType]
  _scalar: pa.StructScalar
  _attribute_cache: dict[str, Any]

  def __getattr__(self, name):
    if name.startswith("_"):
      return object.__getattribute__(self, name)

    struct = object.__getattribute__(self, "_struct")
    if name not in struct.names:
      return object.__getattribute__(self, name)

    cache = object.__getattribute__(self, "_attribute_cache")

    if name not in cache:
      scalar = object.__getattribute__(self, "_scalar")
      if name == "notes":
        cache[name] = [ArrowNote.from_scalar(note) for note in scalar[name]]
      elif name == "props":
        cache[name] = [ArrowProp.from_scalar(note) for note in scalar[name]]
      elif name == "segtype":
        cache[name] = SegType(scalar[name].as_py())
      elif name == "pos":
        cache[name] = Pos(scalar[name].as_py())
      elif name == "assoc":
        cache[name] = Assoc(scalar[name].as_py())
      elif name in ("segment", "content"):
        content = scalar[name].as_py()
        cache[name] = (
          content
          if isinstance(content, str)
          else [_parse_inline_dict(child) if isinstance(child, dict) else child for child in orjson.loads(content)]
        )
      elif name == "variants":
        cache[name] = [ArrowTuv.from_scalar(variant for variant in scalar[name])]
      elif name == "body":
        cache[name] = [ArrowTu.from_scalar(variant for variant in scalar[name])]
      else:
        cache[name] = scalar[name].as_py()

    return cache[name]

  def __setattr__(self, name, value):
    _struct = object.__getattribute__(self, "_struct")

    if name not in _struct.names:
      return super().__setattr__(name, value)
    self._update(name=value)

  def __init__(self, scalar: pa.StructScalar):
    self._scalar = scalar
    self._attribute_cache = dict()

  @classmethod
  def from_scalar(cls: Type[Self], scalar: pa.StructScalar) -> Self:
    validate_scalar(scalar=scalar, struct=cls._struct)
    return cls(scalar=scalar)

  def _update(self, **updates):
    fields = {name: self._scalar[name] for name in self._scalar.type.names}
    fields.update(updates)
    self._attribute_cache.clear()
    self._scalar = pa.scalar(fields, type=self._struct)

  @classmethod
  @abstractmethod
  def from_dataclass(cls: Type[Self], element: Any) -> Self: ...

  @abstractmethod
  def to_dataclass(self) -> BaseElement: ...


class ArrowNote(ArrowStructWrapper):
  _struct = NOTE_STRUCT
  content: str
  lang: str
  o_encoding: str

  def to_dataclass(self) -> Note:
    return Note(
      content=self.content,
      lang=self.lang,
      o_encoding=self.o_encoding,
    )

  @classmethod
  def from_dataclass(cls, element: Note) -> ArrowNote:
    return cls.from_scalar(pa.scalar(asdict(element)))


class ArrowProp(ArrowStructWrapper):
  _struct = PROP_STRUCT
  content: str
  type: str
  lang: str | None
  o_encoding: str | None

  def to_dataclass(self) -> Prop:
    return Prop(
      content=self.content,
      type=self.type,
      lang=self.lang,
      o_encoding=self.o_encoding,
    )

  @classmethod
  def from_dataclass(cls, element: Prop) -> ArrowProp:
    return cls.from_scalar(pa.scalar(asdict(element)))


class ArrowHeader(ArrowStructWrapper):
  _struct = HEADER_STRUCT
  creationtool: str
  creationtoolversion: str
  segtype: SegType
  o_tmf: str
  adminlang: str
  srclang: str
  datatype: str
  o_encoding: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  changeid: str | None
  props: list[ArrowProp]
  notes: list[ArrowNote]


class ArrowBpt(ArrowStructWrapper):
  _struct = BPT_STRUCT
  content: list[ArrowSub | str]
  i: int
  x: int | None
  type: str | None


class ArrowEpt(ArrowStructWrapper):
  _struct = EPT_STRUCT
  content: list[str | ArrowBpt | ArrowEpt | ArrowIt | ArrowPh | Self]
  x: int | None
  type: str | None


class ArrowIt(ArrowStructWrapper):
  _struct = IT_STRUCT
  content: list[str | ArrowSub]
  pos: Pos
  x: int | None
  type: str | None


class ArrowPh(ArrowStructWrapper):
  _struct = PH_STRUCT
  content: list[ArrowSub | str]
  x: int | None
  type: str | None
  assoc: Assoc | None


class ArrowHi(ArrowStructWrapper):
  _struct = HI_STRUCT
  content: list[str | ArrowBpt | ArrowEpt | ArrowIt | ArrowPh | ArrowHi]
  x: int | None
  type: str | None


class ArrowSub(ArrowStructWrapper):
  _struct = SUB_STRUCT
  content: list[ArrowBpt | ArrowEpt | ArrowIt | ArrowPh | ArrowHi | str]
  datatype: str | None
  type: str | None


class ArrowTuv(ArrowStructWrapper):
  _struct = TUV_STRUCT
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
  props: list[ArrowProp]
  notes: list[ArrowNote]
  segment: list[str | Bpt | Ept | Hi | It | Ph]


class ArrowTu(ArrowStructWrapper):
  _struct = TU_STRUCT
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
  segtype: SegType | None
  changeid: str | None
  o_tmf: str | None
  srclang: str | None
  props: list[ArrowProp]
  notes: list[ArrowNote]
  variants: list[ArrowTuv]


class ArrowTmx(ArrowStructWrapper):
  _struct = TMX_STRUCT
  version: str
  header: ArrowHeader
  body: list[ArrowTu]
