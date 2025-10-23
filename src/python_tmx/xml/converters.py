from datetime import datetime
from os import PathLike
from typing import Iterator

from lxml import etree

from python_tmx.base.classes import (
  Header,
  InlineTag,
  Note,
  Prop,
  SegmentPartType,
  SegType,
  Tmx,
  Tu,
  Tuv,
)


def generate_tus_from_file(path: PathLike[str] | str) -> Iterator[Tu]:
  """Stream-parse a TMX file yielding Tu objects."""
  for _, elem in etree.iterparse(source=path, events=("end",), recover=True, tag="tu"):
    yield parse_tu(elem=elem)
    elem.clear()


def parse_tmx(elem: etree._Element) -> Tmx:
  if not elem.tag == "tmx":
    raise ValueError(f"expected a tmx element got {elem.tag!r}")
  header, body = elem.find("header"), elem.find("body")
  if body is None:
    raise ValueError("no body found")
  if header is None:
    raise ValueError("no header found")
  return Tmx(
    version=elem.attrib["version"],
    header=parse_header(header),
    body=[parse_tu(child) for child in body.iter("tu")],
  )


def parse_header(elem: etree._Element) -> Header:
  if not elem.tag == "header":
    raise ValueError(f"expected a header element got {elem.tag!r}")
  header: Header = Header(
    creationtool=elem.attrib["creationtool"],
    creationtoolversion=elem.attrib["creationtoolversion"],
    segtype=SegType(value=elem.attrib["segtype"]),
    o_tmf=elem.attrib["o-tmf"],
    adminlang=elem.attrib["adminlang"],
    srclang=elem.attrib["srclang"],
    datatype=elem.attrib["datatype"],
    o_encoding=elem.attrib.get(key="o-encoding"),
    creationdate=parse_dt(value=elem.attrib.get(key="creationdate")),
    creationid=elem.attrib.get(key="creationid"),
    changedate=parse_dt(value=elem.attrib.get(key="changedate")),
    changeid=elem.attrib.get(key="changeid"),
  )

  for child in elem.iterchildren("prop", "note"):
    if child.tag == "note":
      header.notes.append(parse_note(elem=child))
    else:
      header.props.append(parse_prop(elem=child))

  return header


def parse_tu(elem: etree._Element) -> Tu:
  if not elem.tag == "tu":
    raise ValueError(f"expected a tu element got {elem.tag!r}")
  tu: Tu = Tu(
    tuid=elem.attrib.get(key="tuid"),
    o_encoding=elem.attrib.get(key="o-encoding"),
    datatype=elem.attrib.get(key="datatype"),
    usagecount=parse_int(value=elem.attrib.get(key="usagecount")),
    lastusagedate=parse_dt(value=elem.attrib.get(key="lastusagedate")),
    creationtool=elem.attrib.get(key="creationtool"),
    creationtoolversion=elem.attrib.get(key="creationtoolversion"),
    creationdate=parse_dt(value=elem.attrib.get(key="creationdate")),
    creationid=elem.attrib.get(key="creationid"),
    changedate=parse_dt(value=elem.attrib.get(key="changedate")),
    segtype=parse_segtype(value=elem.attrib.get(key="segtype")),
    changeid=elem.attrib.get(key="changeid"),
    o_tmf=elem.attrib.get(key="o-tmf"),
    srclang=elem.attrib.get(key="srclang"),
  )

  for child in elem.iterchildren("tuv", "prop", "note"):
    if child.tag == "tuv":
      tu.variants.append(parse_tuv(elem=child))
    elif child.tag == "prop":
      tu.props.append(parse_prop(elem=child))
    else:
      tu.notes.append(parse_note(elem=child))

  return tu


def parse_tuv(elem: etree._Element) -> Tuv:
  if not elem.tag == "tuv":
    raise ValueError(f"expected a tuv element got {elem.tag!r}")
  tuv: Tuv = Tuv(
    segment=parse_segment_parts(elem=elem.find(path="seg")),
    lang=elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"],
    o_encoding=elem.attrib.get(key="o-encoding"),
    datatype=elem.attrib.get(key="datatype"),
    usagecount=parse_int(value=elem.attrib.get(key="usagecount")),
    lastusagedate=parse_dt(value=elem.attrib.get(key="lastusagedate")),
    creationtool=elem.attrib.get(key="creationtool"),
    creationtoolversion=elem.attrib.get(key="creationtoolversion"),
    creationdate=parse_dt(value=elem.attrib.get(key="creationdate")),
    creationid=elem.attrib.get(key="creationid"),
    changedate=parse_dt(value=elem.attrib.get(key="changedate")),
    changeid=elem.attrib.get(key="changeid"),
    o_tmf=elem.attrib.get(key="o-tmf"),
  )

  for child in elem.iterchildren("prop", "note"):
    if child.tag == "prop":
      tuv.props.append(parse_prop(elem=child))
    else:
      tuv.notes.append(parse_note(elem=child))

  return tuv


def parse_segment_parts(elem: etree._Element | None) -> list[InlineTag]:
  parts: list[InlineTag] = []
  if elem is None:
    return parts
  if elem.text:
    parts.append(
      InlineTag(
        content=elem.text,
        type=SegmentPartType.STRING,
      )
    )
  for child in elem.iterchildren():
    parts.append(
      InlineTag(
        content=parse_segment_parts(elem=child),
        type=SegmentPartType(value=child.tag),
        attributes={**child.attrib},
      )
    )
    if child.tail:
      parts.append(
        InlineTag(content=child.tail, type=SegmentPartType.STRING),
      )
  if elem.tail:
    parts.append(
      InlineTag(content=elem.tail, type=SegmentPartType.STRING),
    )
  return parts


def parse_dt(value: str | None) -> datetime | None:
  if value is None:
    return None
  return datetime.fromisoformat(value)


def parse_segtype(value: str | None) -> SegType | None:
  if not value:
    return None
  return SegType(value=value)


def parse_prop(elem: etree._Element) -> Prop:
  if not elem.tag == "prop":
    raise ValueError(f"expected a prop element got {elem.tag!r}")
  return Prop(
    content=elem.text or "",
    type=elem.attrib.get(key="type", default=""),
    lang=elem.attrib.get(key="{http://www.w3.org/XML/1998/namespace}lang"),
    o_encoding=elem.attrib.get(key="o-encoding"),
  )


def parse_note(elem: etree._Element) -> Note:
  if not elem.tag == "note":
    raise ValueError(f"expected a note element got {elem.tag!r}")
  return Note(
    content=elem.text or "",
    lang=elem.attrib.get(key="{http://www.w3.org/XML/1998/namespace}lang"),
    o_encoding=elem.attrib.get(key="o-encoding"),
  )


def parse_int(value: str | None) -> int | None:
  if value is None:
    return None
  try:
    return int(value)
  except (TypeError, ValueError):
    return None
