from __future__ import annotations

from datetime import datetime
from os import PathLike
from typing import Iterator

from lxml import etree

from python_tmx.tmx.models import (
  Header,
  Note,
  Prop,
  SegmentPart,
  SegmentPartType,
  SegType,
  Tu,
  Tuv,
)


def generate_tus(path: PathLike) -> Iterator[Tu]:
  """Stream-parse a TMX file yielding Tu objects."""
  context = etree.iterparse(path, events=("end",), recover=True, tag="tu")

  for _, elem in context:
    yield _parse_tu(elem)
    elem.clear()

  del context


def _parse_header(elem: etree._Element) -> Header:
  return Header(
    creationtool=elem.attrib["creationtool"],
    creationtoolversion=elem.attrib["creationtoolversion"],
    segtype=_parse_segtype(elem.attrib["segtype"]),
    o_tmf=elem.attrib["o-tmf"],
    adminlang=elem.attrib["adminlang"],
    srclang=elem.attrib["srclang"],
    datatype=elem.attrib["datatype"],
    o_encoding=elem.attrib.get("o-encoding"),
    creationdate=_parse_dt(elem.attrib.get("creationdate")),
    creationid=elem.attrib.get("creationid"),
    changedate=_parse_dt(elem.attrib.get("changedate")),
    changeid=elem.attrib.get("changeid"),
    metadata=[
      _parse_prop(child) if child.tag == "prop" else _parse_note(child) for child in elem.iterchildren("prop", "note")
    ],
  )


def _parse_tu(elem: etree._Element) -> Tu:
  tu = Tu(
    tuid=elem.get("tuid"),
    o_encoding=elem.get("o-encoding"),
    datatype=elem.get("datatype"),
    usagecount=_parse_int(elem.get("usagecount")),
    lastusagedate=_parse_dt(elem.get("lastusagedate")),
    creationtool=elem.get("creationtool"),
    creationtoolversion=elem.get("creationtoolversion"),
    creationdate=_parse_dt(elem.get("creationdate")),
    creationid=elem.get("creationid"),
    changedate=_parse_dt(elem.get("changedate")),
    segtype=_parse_segtype(elem.get("segtype")),
    changeid=elem.get("changeid"),
    o_tmf=elem.get("o-tmf"),
    srclang=elem.get("srclang"),
  )

  for child in elem.iterchildren("tuv", "prop", "note"):
    if child.tag == "tuv":
      tu.variants.append(_parse_tuv(child))
    elif child.tag == "prop":
      tu.props.append(_parse_prop(child))
    else:
      tu.notes.append(_parse_note(child))

  return tu


def _parse_tuv(elem: etree._Element) -> Tuv:
  tuv = Tuv(
    segment=_parse_segment_parts(elem.find("seg")),
    lang=elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
    o_encoding=elem.get("o-encoding"),
    datatype=elem.get("datatype"),
    usagecount=_parse_int(elem.get("usagecount")),
    lastusagedate=_parse_dt(elem.get("lastusagedate")),
    creationtool=elem.get("creationtool"),
    creationtoolversion=elem.get("creationtoolversion"),
    creationdate=_parse_dt(elem.get("creationdate")),
    creationid=elem.get("creationid"),
    changedate=_parse_dt(elem.get("changedate")),
    changeid=elem.get("changeid"),
    o_tmf=elem.get("o-tmf"),
  )

  for child in elem.iterchildren("prop", "note"):
    if child.tag == "prop":
      tuv.props.append(_parse_prop(child))
    else:
      tuv.notes.append(_parse_note(child))

  return tuv


def _parse_segment_parts(elem: etree._Element) -> list[SegmentPart]:
  parts: list[SegmentPart] = []

  if elem is None:
    return parts

  if elem.text:
    parts.append(
      SegmentPart(
        content=elem.text,
        type=SegmentPartType.STRING,
      )
    )
  for child in elem.iterchildren():
    if child.text:
      parts.append(
        SegmentPart(
          content=child.text,
          type=SegmentPartType(child.tag),
          attributes={**child.attrib},
        )
      )
    parts.append(
      SegmentPart(
        content=_parse_segment_parts(child),
        type=SegmentPartType(child.tag),
        attributes={**child.attrib},
      )
    )
    if child.tail:
      parts.append(
        SegmentPart(content=child.tail, type=SegmentPartType.STRING),
      )

  return parts


def _parse_dt(value: str | None) -> datetime | None:
  try:
    return datetime.fromisoformat(value)
  except Exception:
    return None


def _parse_segtype(value: str | None) -> SegType | None:
  if not value:
    return None
  try:
    return SegType(value)
  except ValueError:
    return None


def _parse_prop(elem: etree._Element) -> Prop:
  return Prop(
    content=elem.text or "",
    type=elem.get("type", ""),
    lang=elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
    o_encoding=elem.get("o-encoding"),
  )


def _parse_note(elem: etree._Element) -> Note:
  return Note(
    content=elem.text or "",
    lang=elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
    o_encoding=elem.get("o-encoding"),
  )


def _parse_int(value: str | None) -> int | None:
  try:
    return int(value)
  except (TypeError, ValueError):
    return None
