from typing import no_type_check

import orjson
import pyarrow as pa

from python_tmx.arrow.structs import (
  HEADER_STRUCT,
  NOTE_STRUCT,
  PROP_STRUCT,
  SEGMENT_PART_STRUCT,
  TMX_STRUCT,
  TU_STRUCT,
  TUV_STRUCT,
)
from python_tmx.base.models import (
  Header,
  HeaderArrowDict,
  Note,
  Prop,
  PropArrowDict,
  SegmentPart,
  SegmentPartFromArrowDict,
  SegmentPartType,
  SegType,
  Tmx,
  TmxFromArrowDict,
  Tu,
  TuFromArrowDict,
  Tuv,
  TuvFromArrowDict,
)


def note_to_struct(note: Note) -> pa.StructScalar:
  return pa.scalar(value=note._to_arrow_dict(), type=NOTE_STRUCT)


def prop_to_struct(prop: Prop) -> pa.StructScalar:
  return pa.scalar(value=prop._to_arrow_dict(), type=PROP_STRUCT)


def header_to_struct(header: Header) -> pa.StructScalar:
  return pa.scalar(value=header._to_arrow_dict(), type=HEADER_STRUCT)


def segment_part_to_struct(segment_part: SegmentPart) -> pa.StructScalar:
  return pa.scalar(value=segment_part._to_arrow_dict(), type=SEGMENT_PART_STRUCT)


def tuv_to_struct(tuv: Tuv) -> pa.StructScalar:
  return pa.scalar(value=tuv._to_arrow_dict(), type=TUV_STRUCT)


def tu_to_struct(tu: Tu) -> pa.StructScalar:
  return pa.scalar(value=tu._to_arrow_dict(), type=TU_STRUCT)


def tmx_to_struct(tmx: Tmx) -> pa.StructScalar:
  return pa.scalar(value=tmx._to_arrow_dict(), type=TMX_STRUCT)


def struct_to_note(struct: pa.StructScalar) -> Note:
  @no_type_check
  def _struct_to_note(root):
    return Note(**root)

  return _struct_to_note(struct if isinstance(struct, dict) else struct.as_py())


def struct_to_prop(struct: pa.StructScalar | PropArrowDict) -> Prop:
  @no_type_check
  def _struct_to_note(root):
    return Prop(**root.as_py())

  return _struct_to_note(struct if isinstance(struct, dict) else struct.as_py())


def struct_to_header(struct: pa.StructScalar | HeaderArrowDict) -> Header:
  @no_type_check
  def _struct_to_header(root):
    return Header(
      creationtool=root["creationtool"],
      creationtoolversion=root["creationtoolversion"],
      segtype=SegType(root["segtype"]),
      o_tmf=root["o_tmf"],
      adminlang=root["adminlang"],
      srclang=root["srclang"],
      datatype=root["datatype"],
      o_encoding=root.get("o_encoding"),
      creationdate=root.get("creationdate"),
      creationid=root.get("creationid"),
      changedate=root.get("changedate"),
      changeid=root.get("changeid"),
      props=[struct_to_prop(prop) for prop in root.get("props", [])],
      notes=[struct_to_note(note) for note in root.get("notes", [])],
    )

  return _struct_to_header(root=struct if isinstance(struct, dict) else struct.as_py())


def struct_to_segment_part(struct: pa.StructScalar | SegmentPartFromArrowDict) -> SegmentPart:
  @no_type_check
  def _struct_to_segment_part(root):
    return SegmentPart(
      content=root["content"] if isinstance(root["content"], str) else [_struct_to_segment_part(root=root["content"])],
      type=SegmentPartType(root["type"]),
      attributes=root["attributes"],
    )

  if isinstance(struct, dict):
    root = struct
  else:
    root = struct.as_py()  # type: ignore
    root["content"] = orjson.loads(root["content"])  # type: ignore
  return _struct_to_segment_part(root=root)


def struct_to_tuv(struct: pa.StructScalar | TuvFromArrowDict) -> Tuv:
  @no_type_check
  def _struct_to_tuv(root):
    return Tuv(
      lang=root.get("lang"),
      o_encoding=root.get("o_encoding"),
      datatype=root.get("datatype"),
      usagecount=root.get("usagecount"),
      lastusagedate=root.get("lastusagedate"),
      creationtool=root.get("creationtool"),
      creationtoolversion=root.get("creationtoolversion"),
      creationdate=root.get("creationdate"),
      creationid=root.get("creationid"),
      changedate=root.get("changedate"),
      changeid=root.get("changeid"),
      o_tmf=root.get("o_tmf"),
      props=[struct_to_prop(prop) for prop in root.get("props", [])],
      notes=[struct_to_note(note) for note in root.get("notes", [])],
      segment=[struct_to_segment_part(segment_part) for segment_part in root.get("segment")],
    )

  return _struct_to_tuv(root=struct if isinstance(struct, dict) else struct.as_py())


def struct_to_tu(struct: pa.StructScalar | TuFromArrowDict) -> Tu:
  @no_type_check
  def _struct_to_tu(root):
    return Tu(
      tuid=root.get("tuid"),
      o_encoding=root.get("o_encoding"),
      datatype=root.get("datatype"),
      usagecount=root.get("usagecount"),
      lastusagedate=root.get("lastusagedate"),
      creationtool=root.get("creationtool"),
      creationtoolversion=root.get("creationtoolversion"),
      creationdate=root.get("creationdate"),
      creationid=root.get("creationid"),
      changedate=root.get("changedate"),
      segtype=root.get("segtype"),
      changeid=root.get("changeid"),
      o_tmf=root.get("o_tmf"),
      srclang=root.get("srclang"),
      props=[struct_to_prop(prop) for prop in root.get("props", [])],
      notes=[struct_to_note(note) for note in root.get("notes", [])],
      variants=[struct_to_tuv(tuv) for tuv in root["variants"]],
    )

  return _struct_to_tu(root=struct if isinstance(struct, dict) else struct.as_py())


def struct_to_tmx(struct: pa.StructScalar | TmxFromArrowDict) -> Tmx:
  @no_type_check
  def _struct_to_tmx(root):
    return Tmx(
      version=root.get("version"),
      header=struct_to_header(root.get("header")),
      body=[struct_to_tu(tu) for tu in root.get("body")],
    )

  return _struct_to_tmx(root=struct if isinstance(struct, dict) else struct.as_py())
