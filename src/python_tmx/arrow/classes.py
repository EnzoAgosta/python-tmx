from __future__ import annotations

from abc import abstractmethod
from collections.abc import Generator
from dataclasses import asdict
from datetime import datetime
from typing import Any, ClassVar, Generic, Self, Type, TypeVar

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
  BaseElementAlias,
  BaseInlineElementAlias,
  Bpt,
  Ept,
  Header,
  Hi,
  It,
  Note,
  Ph,
  Pos,
  Prop,
  Segtype,
  Sub,
  Tmx,
  Tu,
  Tuv,
)

T = TypeVar("T", bound=BaseElementAlias)


class ArrowStructWrapper(Generic[T]):
  __slots__ = ()
  _struct: ClassVar[pa.StructType]
  _scalar: pa.StructScalar
  _attribute_cache: dict[str, Any]

  @staticmethod
  def _parse_inline_dict(value: dict) -> BaseInlineElementAlias:
    content = value.pop("content")
    content = [ArrowStructWrapper._parse_inline_dict(child) for child in content]
    elem: Type[BaseInlineElementAlias]
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

  @staticmethod
  def _generate_arrow_struct_wrappers(
    obj: ArrowStructWrapper, name: str, wrapper_type: type[ArrowStructWrapper[T]]
  ) -> Generator[ArrowStructWrapper[T]]:
    cache = obj._attribute_cache
    cache[name] = []
    array = obj._scalar[name]
    assert isinstance(array, pa.StructArray)
    for item in array:
      wrapper = wrapper_type.from_scalar(item)
      cache[name].append(wrapper)
      yield wrapper

  def __getattr__(self, name):
    if name.startswith("_"):
      return object.__getattribute__(self, name)
    
    struct = object.__getattribute__(self, "_struct")
    if name not in struct.names:
      return object.__getattribute__(self, name)

    cache = object.__getattribute__(self, "_attribute_cache")

    if name in cache:
      return cache[name]

    scalar = object.__getattribute__(self, "_scalar")
    if name == "notes":
      return ArrowStructWrapper._generate_arrow_struct_wrappers(self, name, ArrowNote)
    elif name == "props":
      return ArrowStructWrapper._generate_arrow_struct_wrappers(self, name, ArrowProp)
    elif name == "segtype":
      val = scalar[name].as_py()
      if val is not None:
        val = Segtype(val)
      cache[name] = val
      return cache[name]
    elif name == "pos":
      val = scalar[name].as_py()
      if val is not None:
        val = Pos(val)
      cache[name] = val
      return cache[name]
    elif name == "assoc":
      val = scalar[name].as_py()
      if val is not None:
        val = Assoc(val)
      cache[name] = val
      return cache[name]
    elif name in ("segment", "content"):
      content = scalar[name].as_py()
      cache[name] = (
        content
        if isinstance(content, str)
        else [
          ArrowStructWrapper._parse_inline_dict(child) if isinstance(child, dict) else child
          for child in orjson.loads(content)
        ]
      )
      return cache[name]
    elif name == "variants":
      return ArrowStructWrapper._generate_arrow_struct_wrappers(self, name, ArrowTuv)
    elif name == "body":
      return ArrowStructWrapper._generate_arrow_struct_wrappers(self, name, ArrowTu)
    elif name == "header":
      cache[name] = ArrowHeader.from_scalar(scalar[name])
      return cache[name]
    else:
      cache[name] = scalar[name].as_py()
      return cache[name]

  def __setattr__(self, name, value):
    _struct = object.__getattribute__(self, "_struct")

    if name not in _struct.names:
      return object.__setattr__(self, name, value)
    self._update(name=value)

  def __init__(self, scalar: pa.StructScalar):
    self._scalar = scalar
    self._attribute_cache = dict()

  @staticmethod
  def validate_scalar(scalar: pa.StructScalar, struct: pa.StructType) -> None:
    if not scalar.type.equals(struct):
      raise TypeError(f"Expected struct {struct} but got {scalar.type}")
    if not all(val.is_valid for val in scalar.values()):
      raise ValueError("Scalar has invalid fields")

  @classmethod
  def from_scalar(cls, scalar: pa.StructScalar) -> Self:
    cls.validate_scalar(scalar=scalar, struct=cls._struct)
    return cls(scalar=scalar)

  def _update(self, **updates):
    fields = {name: self._scalar[name] for name in self._scalar.type.names}
    fields.update(updates)
    self._attribute_cache.clear()
    self._scalar = pa.scalar(fields, type=self._struct)

  @classmethod
  def from_dataclass(cls, element: T) -> Self:
    """Create wrapper from a dataclass instance."""
    if not isinstance(element, DATACLASS_TO_ARROW_STRUCT_MAP[cls]):
      raise TypeError(
        f"{cls.__name__} expects {DATACLASS_TO_ARROW_STRUCT_MAP[cls].__name__}, got {type(element).__name__}"
      )

    data = asdict(element)
    scalar = pa.scalar(data, type=cls._struct)
    return cls.from_scalar(scalar)

  @abstractmethod
  def to_dataclass(self) -> T: ...


class ArrowNote(ArrowStructWrapper[Note]):
  __slots__ = (
    "content",
    "lang",
    "o_encoding",
  )
  _struct = NOTE_STRUCT
  _dataclass_type = Note
  content: str
  lang: str
  o_encoding: str

  @classmethod
  def from_dataclass(cls, element: Note) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Note:
    return Note(
      content=self.content,
      lang=self.lang,
      o_encoding=self.o_encoding,
    )


class ArrowProp(ArrowStructWrapper[Prop]):
  __slots__ = (
    "content",
    "lang",
    "o_encoding",
    "type",
  )
  _struct = PROP_STRUCT
  content: str
  type: str
  lang: str | None
  o_encoding: str | None

  @classmethod
  def from_dataclass(cls, element: Prop) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Prop:
    return Prop(
      content=self.content,
      type=self.type,
      lang=self.lang,
      o_encoding=self.o_encoding,
    )


class ArrowHeader(ArrowStructWrapper[Header]):
  __slots__ = (
    "creationtool",
    "creationtoolversion",
    "segtype",
    "o_tmf",
    "adminlang",
    "srclang",
    "datatype",
    "o_encoding",
    "creationdate",
    "creationid",
    "changedate",
    "changeid",
    "props",
    "notes",
  )
  _struct = HEADER_STRUCT
  creationtool: str
  creationtoolversion: str
  segtype: Segtype
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

  @classmethod
  def from_dataclass(cls, element: Header) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Header:
    return Header(
      creationtool=self.creationtool,
      creationtoolversion=self.creationtoolversion,
      segtype=self.segtype,
      o_tmf=self.o_tmf,
      adminlang=self.adminlang,
      srclang=self.srclang,
      datatype=self.datatype,
      o_encoding=self.o_encoding,
      creationdate=self.creationdate,
      creationid=self.creationid,
      changedate=self.changedate,
      changeid=self.changeid,
      props=[prop.to_dataclass() for prop in self.props],
      notes=[note.to_dataclass() for note in self.notes],
    )


class ArrowBpt(ArrowStructWrapper[Bpt]):
  __slots__ = (
    "i",
    "x",
    "type",
    "content",
  )
  _struct = BPT_STRUCT
  content: list[ArrowSub | str]
  i: int
  x: int | None
  type: str | None

  @classmethod
  def from_dataclass(cls, element: Bpt) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Bpt:
    return Bpt(
      content=self.content
      if isinstance(self.content, str)
      else [part.to_dataclass() if not isinstance(part, str) else part for part in self.content],
      i=self.i,
      x=self.x,
      type=self.type,
    )


class ArrowEpt(ArrowStructWrapper[Ept]):
  __slots__ = (
    "i",
    "content",
  )
  _struct = EPT_STRUCT
  content: list[ArrowSub | str]
  i: int

  @classmethod
  def from_dataclass(cls, element: Ept) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Ept:
    return Ept(
      content=self.content
      if isinstance(self.content, str)
      else [part.to_dataclass() if not isinstance(part, str) else part for part in self.content],
      i=self.i,
    )


class ArrowIt(ArrowStructWrapper[It]):
  __slots__ = (
    "content",
    "pos",
    "x",
    "type",
  )
  _struct = IT_STRUCT
  content: list[str | ArrowSub]
  pos: Pos
  x: int | None
  type: str | None

  @classmethod
  def from_dataclass(cls, element: It) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> It:
    return It(
      content=self.content
      if isinstance(self.content, str)
      else [part.to_dataclass() if not isinstance(part, str) else part for part in self.content],
      x=self.x,
      pos=self.pos,
      type=self.type,
    )


class ArrowPh(ArrowStructWrapper[Ph]):
  __slots__ = (
    "content",
    "x",
    "type",
    "assoc",
  )
  _struct = PH_STRUCT
  content: list[ArrowSub | str]
  x: int | None
  type: str | None
  assoc: Assoc | None

  @classmethod
  def from_dataclass(cls, element: Ph) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Ph:
    return Ph(
      content=self.content
      if isinstance(self.content, str)
      else [part.to_dataclass() if not isinstance(part, str) else part for part in self.content],
      x=self.x,
      type=self.type,
      assoc=self.assoc,
    )


class ArrowHi(ArrowStructWrapper[Hi]):
  __slots__ = (
    "content",
    "x",
    "type",
  )
  _struct = HI_STRUCT
  content: list[str | ArrowBpt | ArrowEpt | ArrowIt | ArrowPh | ArrowHi]
  x: int | None
  type: str | None

  @classmethod
  def from_dataclass(cls, element: Hi) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Hi:
    return Hi(
      content=self.content
      if isinstance(self.content, str)
      else [part.to_dataclass() if not isinstance(part, str) else part for part in self.content],
      x=self.x,
      type=self.type,
    )


class ArrowSub(ArrowStructWrapper[Sub]):
  __slots__ = (
    "content",
    "type",
    "datatype",
  )
  _struct = SUB_STRUCT
  content: list[ArrowBpt | ArrowEpt | ArrowIt | ArrowPh | ArrowHi | str]
  datatype: str | None
  type: str | None

  @classmethod
  def from_dataclass(cls, element: Sub) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Sub:
    return Sub(
      content=self.content
      if isinstance(self.content, str)
      else [part.to_dataclass() if not isinstance(part, str) else part for part in self.content],
      datatype=self.datatype,
      type=self.type,
    )


class ArrowTuv(ArrowStructWrapper[Tuv]):
  __slots__ = (
    "lang",
    "o_encoding",
    "datatype",
    "usagecount",
    "lastusagedate",
    "creationtool",
    "creationtoolversion",
    "creationdate",
    "creationid",
    "changedate",
    "changeid",
    "o_tmf",
    "props",
    "notes",
    "segment",
  )
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

  @classmethod
  def from_dataclass(cls, element: Tuv) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Tuv:
    return Tuv(
      lang=self.lang,
      o_encoding=self.o_encoding,
      datatype=self.datatype,
      usagecount=self.usagecount,
      lastusagedate=self.lastusagedate,
      creationtool=self.creationtool,
      creationtoolversion=self.creationtoolversion,
      creationdate=self.creationdate,
      creationid=self.creationid,
      changedate=self.changedate,
      changeid=self.changeid,
      o_tmf=self.o_tmf,
      props=[prop.to_dataclass() for prop in self.props],
      notes=[note.to_dataclass() for note in self.notes],
      segment=self.segment,
    )


class ArrowTu(ArrowStructWrapper[Tu]):
  __slots__ = (
    "tuid",
    "o_encoding",
    "datatype",
    "usagecount",
    "lastusagedate",
    "creationtool",
    "creationtoolversion",
    "creationdate",
    "creationid",
    "changedate",
    "segtype",
    "changeid",
    "o_tmf",
    "srclang",
    "props",
    "notes",
    "variants",
  )
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
  segtype: Segtype | None
  changeid: str | None
  o_tmf: str | None
  srclang: str | None
  props: list[ArrowProp]
  notes: list[ArrowNote]
  variants: list[ArrowTuv]

  @classmethod
  def from_dataclass(cls, element: Tu) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Tu:
    return Tu(
      tuid=self.tuid,
      o_encoding=self.o_encoding,
      datatype=self.datatype,
      usagecount=self.usagecount,
      lastusagedate=self.lastusagedate,
      creationtool=self.creationtool,
      creationtoolversion=self.creationtoolversion,
      creationdate=self.creationdate,
      creationid=self.creationid,
      changedate=self.changedate,
      segtype=self.segtype,
      changeid=self.changeid,
      o_tmf=self.o_tmf,
      srclang=self.srclang,
      props=[prop.to_dataclass() for prop in self.props],
      notes=[note.to_dataclass() for note in self.notes],
      variants=[variant.to_dataclass() for variant in self.variant],
    )


class ArrowTmx(ArrowStructWrapper[Tmx]):
  __slots__ = (
    "version",
    "header",
    "body",
  )
  _struct = TMX_STRUCT
  version: str
  header: ArrowHeader
  body: list[ArrowTu]

  @classmethod
  def from_dataclass(cls, element: Tmx) -> Self:
    return super().from_dataclass(element)

  def to_dataclass(self) -> Tmx:
    return Tmx(
      version=self.version,
      header=self.header.to_dataclass(),
      body=[tu.to_dataclass() for tu in self.body],
    )


DATACLASS_TO_ARROW_STRUCT_MAP: dict[type[ArrowStructWrapper], type[BaseElementAlias]] = {
  ArrowNote: Note,
  ArrowProp: Prop,
  ArrowHeader: Header,
  ArrowBpt: Bpt,
  ArrowEpt: Ept,
  ArrowIt: It,
  ArrowPh: Ph,
  ArrowHi: Hi,
  ArrowSub: Sub,
  ArrowTuv: Tuv,
  ArrowTu: Tu,
  ArrowTmx: Tmx,
}
