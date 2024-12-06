import xml.etree.ElementTree as ET
from dataclasses import fields
from datetime import datetime
from typing import Literal, TypeAlias, overload

import lxml.etree as et

import PythonTmx.classes as cl
from PythonTmx.utils import _check_seg

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


def from_element(elem: XmlElementLike) -> cl.Structural | cl.Inline:
  match elem.tag:
    case "header":
      return _header_from_element(elem)
    case "tu":
      return _tu_from_element(elem)
    case "tuv":
      return _tuv_from_element(elem)
    case "tu":
      return _tu_from_element(elem)
    case "tmx":
      return _tmx_from_element(elem)
    case "map":
      return _map_from_element(elem)
    case "ude":
      return _ude_from_element(elem)
    case "note":
      return _note_from_element(elem)
    case "prop":
      return _prop_from_element(elem)
    case _:
      raise ValueError(f"Invalid tag: {str(elem.tag)}")


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


@overload
def to_element(
  obj: cl.Structural | cl.Inline, engine: Literal["std"]
) -> ET.Element: ...
@overload
def to_element(
  obj: cl.Structural | cl.Inline, engine: Literal["lxml"]
) -> et._Element: ...
def to_element(obj: cl.Structural | cl.Inline, engine: Literal["std", "lxml"]):
  if engine == "lxml":
    elem = et.Element(obj.__class__.__name__.lower())
  elif engine == "std":
    elem = ET.Element(obj.__class__.__name__.lower())
  else:
    raise ValueError(f"Invalid engine: {engine}")
  for attr in fields(obj):
    value = getattr(obj, attr.name)
    if value is None:
      continue
    if attr.name in ("x", "i", "usagecount"):
      _set_int_attr(elem, attr.name, value)
    elif attr.name in ("changedate", "creationdate", "lastusagedate"):
      _set_dt_attr(elem, attr.name, value)
    elif attr.name == "segment":
      _check_seg(value)
      if engine == "lxml":
        seg = et.SubElement(elem, "seg")
      elif engine == "std":
        seg = ET.SubElement(elem, "seg")
      seg.text = ""
      for item in value:
        if isinstance(item, cl.Inline):
          if item.__class__.__name__ not in attr.type:
            raise TypeError("Invalid item in segment: {item}")
          seg.append(to_element(item, engine))
          seg[-1].tail = ""
        elif isinstance(item, str):
          if len(seg):
            seg[-1].tail += item
          else:
            seg.text += item
    elif attr.name == "text":
      if elem.text is None:
        elem.text = ""
      for item in value:
        if isinstance(item, cl.Inline):
          if item.__class__.__name__ not in attr.type:
            raise TypeError("Invalid item in segment: {item}")
          elem.append(to_element(item, engine))
          elem[-1].tail = ""
        elif isinstance(item, str):
          if len(elem):
            elem[-1].tail += item
          else:
            elem.text += item
    elif "list" in attr.type:
      for item in value:
        elem.append(to_element(item, engine))
    elif attr.name == "header":
      elem.append(to_element(value, engine))
    elif attr.name in ("tmf", "encoding"):
      elem.set(f"o-{attr.name}", value)
    elif attr.name == "lang":
      elem.set("{http://www.w3.org/XML/1998/namespace}lang", value)
    else:
      elem.set(attr.name, value)
  return elem
