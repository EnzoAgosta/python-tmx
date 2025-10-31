from collections.abc import Callable
import logging
from typing import Any, overload

import orjson
import pyarrow as pa

from python_tmx.arrow.dicts import (
  BptArrowDict,
  EptArrowDict,
  HeaderArrowDict,
  HiArrowDict,
  ItArrowDict,
  NoteArrowDict,
  PhArrowDict,
  PropArrowDict,
  SubArrowDict,
  TmxArrowDict,
  TuArrowDict,
  TuvArrowDict,
)
from python_tmx.arrow.structs import (
  BPT_STRUCT,
  EPT_STRUCT,
  HEADER_STRUCT,
  HI_STRUCT,
  IT_STRUCT,
  NOTE_STRUCT,
  PH_STRUCT,
  PROP_STRUCT,
  STRUCT_FROM_DATACLASS,
  SUB_STRUCT,
  TMX_STRUCT,
  TU_STRUCT,
  TUV_STRUCT,
)
from python_tmx.base.errors import IncorrectArrowContentError, IncorrectArrowTypeError, MissingArrowStructError
from python_tmx.base.types import (
  Assoc,
  BaseElementAlias,
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

logger = logging.getLogger(__name__)


def prop_from_arrow_dict(prop_dict: PropArrowDict) -> Prop:
  return Prop(**prop_dict)


def note_from_arrow_dict(note_dict: NoteArrowDict) -> Note:
  return Note(**note_dict)


def header_from_arrow_dict(header_dict: HeaderArrowDict) -> Header:
  return Header(
    creationtool=header_dict["creationtool"],
    creationtoolversion=header_dict["creationtoolversion"],
    segtype=Segtype(header_dict["segtype"]),
    o_tmf=header_dict["o_tmf"],
    adminlang=header_dict["adminlang"],
    srclang=header_dict["srclang"],
    datatype=header_dict["datatype"],
    o_encoding=header_dict.get("o_encoding"),
    creationdate=header_dict.get("creationdate"),
    creationid=header_dict.get("creationid"),
    changedate=header_dict.get("changedate"),
    changeid=header_dict.get("changeid"),
    props=[prop_from_arrow_dict(prop) for prop in header_dict["props"]],
    notes=[note_from_arrow_dict(note) for note in header_dict["notes"]],
  )


def _parse_inline_no_sub(source: bytes) -> list[str | Bpt | Ept | Ph | It | Hi]:
  parts: list[str | Bpt | Ept | Ph | It | Hi] = []
  content = orjson.loads(source)
  part: str | BptArrowDict | EptArrowDict | PhArrowDict | ItArrowDict | HiArrowDict
  for part in content:
    if isinstance(part, str):
      parts.append(part)
      continue
    if part["tag"] == "bpt":
      parts.append(bpt_from_arrow_dict(part))
    elif part["tag"] == "ept":
      parts.append(ept_from_arrow_dict(part))
    elif part["tag"] == "it":
      parts.append(it_from_arrow_dict(part))
    elif part["tag"] == "hi":
      parts.append(hi_from_arrow_dict(part))
    elif part["tag"] == "ph":
      parts.append(ph_from_arrow_dict(part))
    else:
      raise IncorrectArrowContentError(f"Unexpected inline element {part.get('tag')!r}")
  return parts


def _parse_inline_only_sub(
  source: bytes,
) -> list[str | Sub]:
  parts: list[str | Sub] = []
  content = orjson.loads(source)
  part: str | SubArrowDict
  for part in content:
    if isinstance(part, str):
      parts.append(part)
    else:
      parts.append(
        Sub(
          content=_parse_inline_no_sub(orjson.loads(part["content"])),
          datatype=part.get("datatype"),
          type=part["type"],
        )
      )
  return parts


def tuv_from_arrow_dict(tuv_dict: TuvArrowDict) -> Tuv:
  return Tuv(
    lang=tuv_dict["lang"],
    o_encoding=tuv_dict.get("o_encoding"),
    datatype=tuv_dict.get("datatype"),
    usagecount=tuv_dict.get("usagecount"),
    lastusagedate=tuv_dict.get("lastusagedate"),
    creationtool=tuv_dict.get("creationtool"),
    creationtoolversion=tuv_dict.get("creationtoolversion"),
    creationdate=tuv_dict.get("creationdate"),
    creationid=tuv_dict.get("creationid"),
    changedate=tuv_dict.get("changedate"),
    changeid=tuv_dict.get("changeid"),
    o_tmf=tuv_dict.get("o_tmf"),
    props=[prop_from_arrow_dict(prop) for prop in tuv_dict["props"]],
    notes=[note_from_arrow_dict(note) for note in tuv_dict["notes"]],
    content=_parse_inline_no_sub(tuv_dict["content"]),
  )


def bpt_from_arrow_dict(bpt_dict: BptArrowDict) -> Bpt:
  return Bpt(
    content=_parse_inline_only_sub(bpt_dict["content"]),
    i=bpt_dict["i"],
    x=bpt_dict.get("x"),
    type=bpt_dict.get("type"),
  )


def ept_from_arrow_dict(ept_dict: EptArrowDict) -> Ept:
  return Ept(
    content=_parse_inline_only_sub(ept_dict["content"]),
    i=ept_dict["i"],
  )


def it_from_arrow_dict(it_dict: ItArrowDict) -> It:
  return It(
    content=_parse_inline_only_sub(it_dict["content"]),
    pos=Pos(it_dict["pos"]),
    x=it_dict.get("x"),
    type=it_dict.get("type"),
  )


def hi_from_arrow_dict(hi_dict: HiArrowDict) -> Hi:
  return Hi(
    content=_parse_inline_no_sub(hi_dict["content"]),
    x=hi_dict.get("x"),
    type=hi_dict.get("type"),
  )


def ph_from_arrow_dict(ph_dict: PhArrowDict) -> Ph:
  return Ph(
    content=_parse_inline_only_sub(ph_dict["content"]),
    assoc=None if ph_dict.get("assoc") is None else Assoc(ph_dict["assoc"]),
    x=ph_dict.get("x"),
    type=ph_dict.get("type"),
  )


def sub_from_arrow_dict(sub_dict: SubArrowDict) -> Sub:
  return Sub(
    content=_parse_inline_no_sub(sub_dict["content"]),
    type=sub_dict.get("type"),
    datatype=sub_dict.get("datatype"),
  )


def tu_from_arrow_dict(tu_dict: TuArrowDict) -> Tu:
  return Tu(
    tuid=tu_dict.get("tuid"),
    o_encoding=tu_dict.get("o_encoding"),
    datatype=tu_dict.get("datatype"),
    usagecount=tu_dict.get("usagecount"),
    lastusagedate=tu_dict.get("lastusagedate"),
    creationtool=tu_dict.get("creationtool"),
    creationtoolversion=tu_dict.get("creationtoolversion"),
    creationdate=tu_dict.get("creationdate"),
    creationid=tu_dict.get("creationid"),
    changedate=tu_dict.get("changedate"),
    segtype=None if tu_dict.get("segtype") is None else Segtype(tu_dict["segtype"]),
    changeid=tu_dict.get("changeid"),
    o_tmf=tu_dict.get("o_tmf"),
    srclang=tu_dict.get("srclang"),
    props=[prop_from_arrow_dict(prop) for prop in tu_dict["props"]],
    notes=[note_from_arrow_dict(note) for note in tu_dict["notes"]],
    variants=[tuv_from_arrow_dict(tuv) for tuv in tu_dict["variants"]],
  )


def tmx_from_arrow_dict(tmx_dict: TmxArrowDict) -> Tmx:
  return Tmx(
    version=tmx_dict["version"],
    header=header_from_arrow_dict(tmx_dict["header"]),
    body=[tu_from_arrow_dict(tu) for tu in tmx_dict["body"]],
  )


@overload
def dataclass_to_arrow_dict(obj: Tmx, *, strict: bool = True) -> TmxArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: Tu, *, strict: bool = True) -> TuArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: Tuv, *, strict: bool = True) -> TuvArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: Header, *, strict: bool = True) -> HeaderArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: Prop, *, strict: bool = True) -> PropArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: Note, *, strict: bool = True) -> NoteArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: Bpt, *, strict: bool = True) -> BptArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: Ept, *, strict: bool = True) -> EptArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: Hi, *, strict: bool = True) -> HiArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: It, *, strict: bool = True) -> ItArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: Ph, *, strict: bool = True) -> PhArrowDict: ...
@overload
def dataclass_to_arrow_dict(obj: Sub, *, strict: bool = True) -> SubArrowDict: ...
def dataclass_to_arrow_dict(
  obj: Tmx | Tu | Tuv | Header | Prop | Note | Bpt | Ept | Hi | It | Ph | Sub, *, strict: bool = True
) -> (
  TmxArrowDict
  | TuArrowDict
  | TuvArrowDict
  | HeaderArrowDict
  | PropArrowDict
  | NoteArrowDict
  | BptArrowDict
  | EptArrowDict
  | HiArrowDict
  | ItArrowDict
  | PhArrowDict
  | SubArrowDict
):
  struct = STRUCT_FROM_DATACLASS.get(type(obj))
  if struct is None:
    raise MissingArrowStructError(f"{type(obj).__name__} has no registered Arrow struct")

  out: dict[str, Any] = {}
  for field in struct:
    name = field.name
    value = getattr(obj, name)
    type_ = field.type

    if value is None:
      if not field.nullable and strict:
        raise IncorrectArrowTypeError(f"{name!r} is not nullable")
      logger.debug(f"{name!r} is not nullable")
      logger.debug("Treating as if it were None and optional.")
      logger.debug("This is not recommended and can lead to the creation of invalid TMX files.")
      logger.debug("Use strict=True to raise an error.")
      out[name] = None
      continue

    if pa.types.is_struct(type_):
      out[name] = dataclass_to_arrow_dict(value, strict=strict)
    elif pa.types.is_list(type_):
      item_t = type_.value_type
      if pa.types.is_struct(item_t):
        out[name] = [dataclass_to_arrow_dict(v, strict=strict) for v in value]
      else:
        out[name] = value
    elif pa.types.is_binary(type_):
      out[name] = orjson.dumps(value)
    elif pa.types.is_timestamp(type_):
      out[name] = value
    elif pa.types.is_timestamp(type_) or pa.types.is_string(type_) or pa.types.is_integer(type_):
      out[name] = value
    else:
      raise IncorrectArrowTypeError(f"Unexpected type {type_}")
  return out  # type: ignore[return-value]


STRUCT_TO_ARROW_DICT_HANDLER: dict[pa.StructType, Callable[..., BaseElementAlias]] = {
  PROP_STRUCT: prop_from_arrow_dict,
  NOTE_STRUCT: note_from_arrow_dict,
  HEADER_STRUCT: header_from_arrow_dict,
  BPT_STRUCT: bpt_from_arrow_dict,
  EPT_STRUCT: ept_from_arrow_dict,
  HI_STRUCT: hi_from_arrow_dict,
  IT_STRUCT: it_from_arrow_dict,
  PH_STRUCT: ph_from_arrow_dict,
  SUB_STRUCT: sub_from_arrow_dict,
  TUV_STRUCT: tuv_from_arrow_dict,
  TU_STRUCT: tu_from_arrow_dict,
  TMX_STRUCT: tmx_from_arrow_dict,
}


def arrow_struct_scalar_to_dataclass(struct_scalar: pa.StructScalar) -> BaseElementAlias:
  handler = None
  for struct in STRUCT_TO_ARROW_DICT_HANDLER:
    if struct_scalar.type.equals(struct):
      handler = STRUCT_TO_ARROW_DICT_HANDLER[struct]
  if handler is None:
    raise MissingArrowStructError("scalar's struct doesn't correspond to any known struct")
  return handler(struct_scalar.as_py())
