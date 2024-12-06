import xml.etree.ElementTree as ET
from dataclasses import fields
from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Literal, TypeAlias, overload

import lxml.etree as et

import PythonTmx.classes as cl
from PythonTmx.utils import _check_bpt_ept

XmlElementLike: TypeAlias = et._Element | ET.Element


def _parse_segment(elem: XmlElementLike) -> list:
  result: list[cl.Inline | str] = []
  if elem is None:
    return result
  if elem.text is not None:
    result.append(elem.text)
  for child in elem:
    match child.tag:
      case "bpt":
        result.append(cl.Bpt(text=_parse_segment(child), **child.attrib))
      case "ept":
        result.append(cl.Ept(text=_parse_segment(child), **child.attrib))
      case "it":
        result.append(cl.It(text=_parse_segment(child), **child.attrib))
      case "ph":
        result.append(cl.Ph(text=_parse_segment(child), **child.attrib))
      case "sub":
        result.append(cl.Sub(text=_parse_segment(child), **child.attrib))
      case "ut":
        result.append(cl.Ut(text=_parse_segment(child), **child.attrib))
      case "hi":
        result.append(cl.Hi(text=_parse_segment(child), **child.attrib))
    if child.tail is not None:
      result.append(child.tail)
  return result


def _note_from_element(elem: XmlElementLike) -> cl.Note:
  return cl.Note(
    elem.text,
    elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
    elem.get("o-encoding"),
  )


def _prop_from_element(elem: XmlElementLike) -> cl.Prop:
  return cl.Prop(
    elem.text,
    elem.get("type"),
    elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
    elem.get("o-encoding"),
  )


def _map_from_element(elem: XmlElementLike) -> cl.Map:
  return cl.Map(
    elem.get("unicode"),
    elem.get("code"),
    elem.get("ent"),
    elem.get("subst"),
  )


def _ude_from_element(elem: XmlElementLike) -> cl.Ude:
  return cl.Ude(
    elem.get("name"),
    elem.get("base"),
    [_map_from_element(x) for x in elem.iter("map")],
  )


def _header_from_element(elem: XmlElementLike) -> cl.Header:
  return cl.Header(
    elem.get("creationtool"),
    elem.get("creationtoolversion"),
    elem.get("segtype"),
    elem.get("o-tmf"),
    elem.get("adminlang"),
    elem.get("srclang"),
    elem.get("datatype"),
    elem.get("o-encoding"),
    elem.get("creationdate"),
    elem.get("creationid"),
    elem.get("changedate"),
    elem.get("changeid"),
    [_prop_from_element(x) for x in elem.iter("prop")],
    [_note_from_element(x) for x in elem.iter("note")],
    [_ude_from_element(x) for x in elem.iter("ude")],
  )


def _tuv_from_element(elem: XmlElementLike) -> cl.Tuv:
  return cl.Tuv(
    _parse_segment(elem.find("seg")),
    elem.get("o-encoding"),
    elem.get("datatype"),
    elem.get("usagecount"),
    elem.get("lastusagedate"),
    elem.get("creationtool"),
    elem.get("creationtoolversion"),
    elem.get("creationdate"),
    elem.get("creationid"),
    elem.get("changedate"),
    elem.get("changeid"),
    elem.get("o-tmf"),
    [_note_from_element(x) for x in elem.iter("note")],
    [_prop_from_element(x) for x in elem.iter("prop")],
  )


def _tu_from_element(elem: XmlElementLike) -> cl.Tu:
  return cl.Tu(
    elem.get("tuid"),
    elem.get("o-encoding"),
    elem.get("datatype"),
    elem.get("usagecount"),
    elem.get("lastusagedate"),
    elem.get("creationtool"),
    elem.get("creationtoolversion"),
    elem.get("creationdate"),
    elem.get("creationid"),
    elem.get("changedate"),
    elem.get("segtype"),
    elem.get("changeid"),
    elem.get("o-tmf"),
    elem.get("srclang"),
    [_tuv_from_element(x) for x in elem.iter("tuv")],
    [_note_from_element(x) for x in elem.iter("note")],
    [_prop_from_element(x) for x in elem.iter("prop")],
  )


def _tmx_from_element(elem: XmlElementLike) -> cl.Tmx:
  return cl.Tmx(
    _header_from_element(elem.find("header")),
    [_tu_from_element(x) for x in elem.find("body").iter("tu")],
  )


def _set_int_attr(
  elem: et._Element | ET.Element, attr: str, value: int | str | None
) -> None:
  if value is None:
    return
  if isinstance(value, int):
    elem.set(attr, str(value))
  else:
    value = int(value)
    elem.set(attr, str(value))


def _set_dt_attr(
  elem: et._Element | ET.Element, attr: str, value: datetime | str | None
) -> None:
  if value is None:
    return
  if isinstance(value, datetime):
    elem.set(attr, value.strftime(r"%Y%m%dT%H%M%SZ"))
  else:
    value = datetime.strptime(value, r"%Y%m%dT%H%M%SZ")
    elem.set(attr, value.strftime(r"%Y%m%dT%H%M%SZ"))


def _export_inline(
  elem: et._Element | ET.Element,
  content: list[cl.Inline | str],
  xml_engine: Literal["lxml", "std"],
) -> None:
  if elem.tag in ("Bpt", "Ept", "It", "Ph", "Ut"):
    allowed_tags = {"sub"}
  else:
    allowed_tags = {"Bpt", "Ept", "It", "Ph", "Hi", "Ut"}
  for item in content:
    if isinstance(item, cl.Inline):
      if item.__class__.__name__ not in allowed_tags:
        raise TypeError("Invalid item in segment: {item}")
      elem.append(to_element(item, xml_engine))
      elem[-1].tail = ""
    elif isinstance(item, str):
      if len(elem):
        elem[-1].tail += item
      else:
        elem.text += item


@overload
def to_element(
  obj: cl.Structural | cl.Inline, xml_engine: Literal["std"]
) -> ET.Element: ...
@overload
def to_element(
  obj: cl.Structural | cl.Inline, xml_engine: Literal["lxml"]
) -> et._Element: ...
def to_element(
  obj: cl.Structural | cl.Inline, xml_engine: Literal["std", "lxml"] = "lxml"
):
  elem: et._Element | ET.Element | None = (
    et.Element(obj.__class__.__name__.lower())
    if xml_engine == "lxml"
    else ET.Element(obj.__class__.__name__.lower())
    if xml_engine == "std"
    else None
  )
  if elem is None:
    raise ValueError(f"Invalid xml_engine: {xml_engine}")
  for attr in fields(obj):
    value = getattr(obj, attr.name)
    if value is None:
      continue
    if attr.name in ("x", "i", "usagecount"):
      _set_int_attr(elem, attr.name, value)
    elif attr.name in ("changedate", "creationdate", "lastusagedate"):
      _set_dt_attr(elem, attr.name, value)
    elif attr.name == "segment":
      _check_bpt_ept(value)
      seg: et._Element | ET.Element | None = (
        et.SubElement(elem, "seg")
        if isinstance(elem, et._Element)
        else ET.SubElement(elem, "seg")
        if isinstance(elem, ET.Element)
        else None
      )
      if seg is None:
        raise ValueError("Invalid xml_engine")
      seg.text = ""
      _export_inline(seg, value, xml_engine)
    elif attr.name == "text":
      if elem.text is None:
        elem.text = ""
      _export_inline(elem, value, xml_engine)
    elif "list" in attr.type:
      for item in value:
        elem.append(to_element(item, xml_engine))
    elif attr.name == "header":
      elem.append(to_element(value, xml_engine))
    elif attr.name in ("tmf", "encoding"):
      elem.set(f"o-{attr.name}", value)
    elif attr.name == "lang":
      elem.set("{http://www.w3.org/XML/1998/namespace}lang", value)
    else:
      elem.set(attr.name, value)
  return elem


def read_tmx_file(
  file: PathLike, xml_engine: Literal["std", "lxml"] = "lxml"
) -> cl.Tmx:
  if not isinstance(file, Path):
    file = Path(file)
  if not file.exists():
    raise FileNotFoundError(f"File {file} does not exist")
  if not file.is_file():
    raise IsADirectoryError(f"{file} is not a file")
  if xml_engine == "lxml":
    tree = (
      et.parse(source=file)
      if xml_engine == "lxml"
      else ET.ElementTree(file=file)
      if xml_engine == "std"
      else None
    )
    if tree is None:
      raise ValueError("Invalid xml_engine")
    root = tree.getroot()
  return _tmx_from_element(root)


et.ElementTree(to_element(read_tmx_file(Path("a.tmx")), "lxml")).write(
  "b.tmx", xml_declaration=True
)
