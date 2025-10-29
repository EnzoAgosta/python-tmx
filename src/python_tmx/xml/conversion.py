from datetime import datetime
import logging
from typing import Literal, Never, TypeVar, cast, overload
import xml.etree.ElementTree as ET
import lxml.etree as LET

from python_tmx.base.types import (
  Assoc,
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

XmlElement = TypeVar("XmlElement", ET.Element, LET.Element)
DT_FORMAT = "%Y%m%dT%H%M%SZ"
XML_NS = "{http://www.w3.org/XML/1998/namespace}"

logger = logging.getLogger(__name__)


def _check_tag(tag: str, expected: str, strict: bool) -> None:
  if tag == expected:
    return
  if strict:
    raise ValueError(f"Unexpected tag {tag!r}, expected {expected}")
  logger.warning(f"Unexpected tag {tag!r}, expected {expected}")
  logger.debug(
    f"Treating as if it were {expected} and trying to convert it to a dataclass nonetheless. Use strict=True to raise an error."
  )


def _set_attribute(
  elem: XmlElement,
  key: str,
  value: str | int | datetime | Pos | Assoc | Segtype | None,
  optional: bool,
  expected: type | tuple[type, ...],
  strict: bool,
) -> None:
  if value is None:
    if optional:
      return
    if strict:
      raise TypeError(f"Missing required attribute {key}")
    logger.warning(f"Missing required attribute {key}")
    logger.debug("Treating as optional; use strict=True to raise an error.")
    return
  if not isinstance(value, expected):
    if strict:
      raise TypeError(f"Expected {expected}, got {type(value)}")
    logger.warning(f"Expected {expected}, got {type(value)}")
    logger.debug("Treating value as if it were None and optional. Use strict=True to raise an error.")
    return
  match value:
    case str():
      elem.attrib[key] = value
    case int():
      elem.attrib[key] = str(value)
    case datetime():
      elem.attrib[key] = value.strftime(DT_FORMAT)
    case Pos() | Segtype() | Assoc():
      elem.attrib[key] = value.value
    case _:
      assert Never, (
        f"Unexpected type: {type(value)}, expected one of str, int, datetime, Pos, Segtype, Assoc. Got: {type(value)}"
      )


def get_backend(value: type[XmlElement] | None) -> type[XmlElement]:
  if value is None:
    return cast(type[XmlElement], LET.Element)
  elif value is ET.Element:
    return cast(type[XmlElement], ET.Element)
  elif value is LET.Element:
    return cast(type[XmlElement], LET.Element)
  else:
    raise ValueError(
      f"Unsupported XML backend: {value!r}. Expected xml.etree.ElementTree.Element, or lxml.etree.Element."
    )


def content_to_element(
  source: BaseInlineElementAlias | Tuv,
  target: XmlElement,
  only_sub: bool,
  strict: bool = True,
  /,
  backend: type[XmlElement] | None = None,
) -> XmlElement:
  backend = get_backend(backend)
  error_message = (
    f"Found unexpected element: %s in {source.__class__.__name__!r} element, expected only str, Bpt, Ept, It, Ph, Hi"
  )
  if only_sub:
    error_message = f"Found unexpected element: %s in {source.__class__.__name__!r} element, expected only str or Sub"
  debug_message = "Ignoring. Use strict=True to raise an error."
  for item in source.content:
    match item:
      case str():
        if len(target) == 0:
          if target.text is None:
            target.text = ""
          target.text += item
        else:
          if target[-1].tail is None:
            target[-1].tail = ""
          target[-1].tail += item
      case Sub():
        if only_sub:
          target.append(sub_to_element(item, backend=backend, strict=strict))
          continue
        if strict:
          raise ValueError(error_message.format(item))
        logger.warning(error_message.format(item))
        logger.debug(debug_message)
      case Bpt():
        if not only_sub:
          target.append(bpt_to_element(item, backend=backend, strict=strict))
          continue
        if strict:
          raise ValueError(error_message.format(item))
        logger.warning(error_message.format(item))
        logger.debug(debug_message)
      case Ept():
        if not only_sub:
          target.append(ept_to_element(item, backend=backend, strict=strict))
          continue
        if strict:
          raise ValueError(error_message.format(item))
        logger.warning(error_message.format(item))
        logger.debug(debug_message)
      case It():
        if not only_sub:
          target.append(it_to_element(item, backend=backend, strict=strict))
          continue
        if strict:
          raise ValueError(error_message.format(item))
        logger.warning(error_message.format(item))
        logger.debug(debug_message)
      case Ph():
        if not only_sub:
          target.append(ph_to_element(item, backend=backend, strict=strict))
          continue
        if strict:
          raise ValueError(error_message.format(item))
        logger.warning(error_message.format(item))
        logger.debug(debug_message)
      case Hi():
        if not only_sub:
          target.append(hi_to_element(item, backend=backend, strict=strict))
          continue
        if strict:
          raise ValueError(error_message.format(item))
        logger.warning(error_message.format(item))
        logger.debug(debug_message)
      case _:
        if strict:
          raise ValueError(
            f"Found Unexpected element: {item!r} in {source.__class__.__name__!r} element, Expected str, Bpt, Ept, It, Ph, Hi or Sub"
          )
        logger.warning(
          f"Found Unexpected element: {item!r} in {source.__class__.__name__!r} element, Expected str, Bpt, Ept, It, Ph, Hi or Sub"
        )
        logger.debug(debug_message)
  return target


def note_to_element(note_object: Note, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  elem = backend("note", {})
  if not isinstance(note_object.text, str):
    if strict:
      raise ValueError(f"Expected str, got {type(note_object.text)}")
    logger.warning(f"Expected str, got {type(note_object.text)}")
    logger.debug("Treating value as if it were an empty string. Use strict=True to raise an error.")
    elem.text = ""
  else:
    elem.text = note_object.text
  _set_attribute(elem, f"{XML_NS}lang", note_object.lang, True, str, strict)
  _set_attribute(elem, "o-encoding", note_object.o_encoding, True, str, strict)
  return elem


def prop_to_element(prop_object: Prop, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  elem = backend("prop", {})
  if not isinstance(prop_object.text, str):
    if strict:
      raise ValueError(f"Expected str, got {type(prop_object.text)}")
    logger.warning(f"Expected str, got {type(prop_object.text)}")
    logger.debug("Treating value as if it were an empty string. Use strict=True to raise an error.")
    elem.text = ""
  else:
    elem.text = prop_object.text
  _set_attribute(elem, "type", prop_object.lang, False, str, strict)
  _set_attribute(elem, f"{XML_NS}lang", prop_object.lang, True, str, strict)
  _set_attribute(elem, "o-encoding", prop_object.o_encoding, True, str, strict)
  return elem


def header_to_element(
  header_object: Header, /, backend: type[XmlElement] | None = None, strict: bool = True
) -> XmlElement:
  backend = get_backend(backend)
  elem = backend("header", {})
  _set_attribute(elem, "creationtool", header_object.creationtool, False, str, strict)
  _set_attribute(elem, "creationtoolversion", header_object.creationtoolversion, False, str, strict)
  _set_attribute(elem, "segtype", header_object.segtype, False, Segtype, strict)
  _set_attribute(elem, "o-tmf", header_object.o_tmf, False, str, strict)
  _set_attribute(elem, "adminlang", header_object.adminlang, False, str, strict)
  _set_attribute(elem, "srclang", header_object.srclang, False, str, strict)
  _set_attribute(elem, "datatype", header_object.datatype, False, str, strict)
  _set_attribute(elem, "creationdate", header_object.creationdate, True, datetime, strict)
  _set_attribute(elem, "creationid", header_object.creationid, True, str, strict)
  _set_attribute(elem, "changedate", header_object.changedate, True, datetime, strict)
  _set_attribute(elem, "changeid", header_object.changeid, True, str, strict)
  _set_attribute(elem, "o-encoding", header_object.o_encoding, True, str, strict)
  for prop in header_object.props:
    elem.append(prop_to_element(prop, backend=backend, strict=strict))
  for note in header_object.notes:
    elem.append(note_to_element(note, backend=backend, strict=strict))
  return elem


def sub_to_element(sub_object: Sub, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  sub_element = backend("sub", {})
  _set_attribute(sub_element, "datatype", sub_object.datatype, False, str, strict)
  _set_attribute(sub_element, "type", sub_object.type, False, str, strict)
  content_to_element(sub_object.content, sub_element, True, backend=backend)
  return sub_element


def bpt_to_element(bpt_object: Bpt, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  bpt_element = backend("bpt", {})
  _set_attribute(bpt_element, "i", bpt_object.i, False, int, strict)
  _set_attribute(bpt_element, "x", bpt_object.x, True, int, strict)
  _set_attribute(bpt_element, "type", bpt_object.type, True, str, strict)
  content_to_element(bpt_object.content, bpt_element, True, backend=backend)
  return bpt_element


def ept_to_element(ept_object: Ept, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  ept_element = backend("ept", {})
  _set_attribute(ept_element, "i", ept_object.i, False, int, strict)
  content_to_element(ept_object.content, ept_element, True, backend=backend, strict=strict)
  return ept_element


def it_to_element(it_object: It, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  it_element = backend("it", {})
  _set_attribute(it_element, "pos", it_object.pos, False, Pos, strict)
  _set_attribute(it_element, "x", it_object.x, True, int, strict)
  _set_attribute(it_element, "type", it_object.type, True, str, strict)
  content_to_element(it_object.content, it_element, True, backend=backend)
  return it_element


def ph_to_element(ph_object: Ph, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  ph_element = backend("ph", {})
  _set_attribute(ph_element, "x", ph_object.x, True, int, strict)
  _set_attribute(ph_element, "type", ph_object.type, True, str, strict)
  _set_attribute(ph_element, "assoc", ph_object.assoc, True, Assoc, strict)
  content_to_element(ph_object.content, ph_element, True, backend=backend)
  return ph_element


def hi_to_element(hi_object: Hi, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  hi_element = backend("hi", {})
  _set_attribute(hi_element, "x", hi_object.x, True, int, strict)
  _set_attribute(hi_element, "type", hi_object.type, True, str, strict)
  content_to_element(hi_object.content, hi_element, True, backend=backend)
  return hi_element


def tuv_to_element(tuv_object: Tuv, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  tuv_element = backend("tuv", {})
  _set_attribute(tuv_element, f"{XML_NS}lang", tuv_object.lang, False, str, strict)
  _set_attribute(tuv_element, "o-encoding", tuv_object.o_encoding, True, str, strict)
  _set_attribute(tuv_element, "datatype", tuv_object.datatype, True, str, strict)
  _set_attribute(tuv_element, "usagecount", tuv_object.usagecount, True, int, strict)
  _set_attribute(tuv_element, "lastusagedate", tuv_object.lastusagedate, True, datetime, strict)
  _set_attribute(tuv_element, "creationtool", tuv_object.creationtool, True, str, strict)
  _set_attribute(tuv_element, "creationtoolversion", tuv_object.creationtoolversion, True, str, strict)
  _set_attribute(tuv_element, "creationdate", tuv_object.creationdate, True, datetime, strict)
  _set_attribute(tuv_element, "creationid", tuv_object.creationid, True, str, strict)
  _set_attribute(tuv_element, "changedate", tuv_object.changedate, True, datetime, strict)
  _set_attribute(tuv_element, "changeid", tuv_object.changeid, True, str, strict)
  _set_attribute(tuv_element, "o-tmf", tuv_object.o_tmf, True, str, strict)
  for prop in tuv_object.props:
    tuv_element.append(prop_to_element(prop, backend=backend))
  for note in tuv_object.notes:
    tuv_element.append(note_to_element(note, backend=backend))
  seg_element = backend("seg", {})
  content_to_element(tuv_object.content, seg_element, False, backend=backend)
  tuv_element.append(seg_element)
  return tuv_element


def tu_to_element(tu_object: Tu, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  tu_element = backend("tu", {})
  _set_attribute(tu_element, "tuid", tu_object.tuid, True, str, strict)
  _set_attribute(tu_element, "o-encoding", tu_object.o_encoding, True, str, strict)
  _set_attribute(tu_element, "datatype", tu_object.datatype, True, str, strict)
  _set_attribute(tu_element, "usagecount", tu_object.usagecount, True, int, strict)
  _set_attribute(tu_element, "lastusagedate", tu_object.lastusagedate, True, datetime, strict)
  _set_attribute(tu_element, "creationtool", tu_object.creationtool, True, str, strict)
  _set_attribute(tu_element, "creationtoolversion", tu_object.creationtoolversion, True, str, strict)
  _set_attribute(tu_element, "creationdate", tu_object.creationdate, True, datetime, strict)
  _set_attribute(tu_element, "creationid", tu_object.creationid, True, str, strict)
  _set_attribute(tu_element, "changedate", tu_object.changedate, True, datetime, strict)
  _set_attribute(tu_element, "segtype", tu_object.segtype, True, Segtype, strict)
  _set_attribute(tu_element, "changeid", tu_object.changeid, True, str, strict)
  _set_attribute(tu_element, "o-tmf", tu_object.o_tmf, True, str, strict)
  _set_attribute(tu_element, "srclang", tu_object.srclang, True, str, strict)
  for prop in tu_object.props:
    tu_element.append(prop_to_element(prop, backend=backend))
  for note in tu_object.notes:
    tu_element.append(note_to_element(note, backend=backend))
  for variant in tu_object.variants:
    tu_element.append(tuv_to_element(variant, backend=backend))
  return tu_element


def tmx_to_element(tmx_object: Tmx, /, backend: type[XmlElement] | None = None, strict: bool = True) -> XmlElement:
  backend = get_backend(backend)
  tmx_element = backend("tmx", {})
  _set_attribute(tmx_element, "version", tmx_object.version, False, str, strict)
  tmx_element.append(header_to_element(tmx_object.header, backend=backend, strict=strict))
  body = backend("body", {})
  for tu in tmx_object.body:
    body.append(tu_to_element(tu, backend=backend, strict=strict))
  tmx_element.append(body)
  return tmx_element


@overload
def element_to_content(
  source: XmlElement, sub_only: Literal[False], strict: bool = True
) -> list[Bpt | Ept | It | Ph | Hi | str]: ...
@overload
def element_to_content(source: XmlElement, sub_only: Literal[True], strict: bool = True) -> list[Sub | str]: ...
def element_to_content(
  source: XmlElement, only_sub: bool, strict: bool = True
) -> list[Bpt | Ept | It | Ph | Hi | str] | list[Sub | str]:
  parts: list = []
  error_message = (
    f"Found unexpected element: %s in {source.__class__.__name__!r} element, expected only str, Bpt, Ept, It, Ph or Hi"
  )
  if only_sub:
    error_message = f"Found unexpected element: %s in {source.__class__.__name__!r} element, expected only str or Sub"
  debug_message = "Ignoring. Use strict=True to raise an error."
  if source.text is not None:
    parts.append(source.text)
  for child in source:
    match child.tag:
      case "sub":
        if not only_sub:
          if strict:
            raise ValueError(error_message.format(child.tag))
          logger.warning(error_message.format(child.tag))
          logger.debug(debug_message)
          continue
        parts.append(element_to_sub(child))
      case "bpt":
        if only_sub:
          if strict:
            raise ValueError(error_message.format(child.tag))
          logger.warning(error_message.format(child.tag))
          logger.debug(debug_message)
          continue
        parts.append(element_to_bpt(child))
      case "ept":
        if only_sub:
          if strict:
            raise ValueError(error_message.format(child.tag))
          logger.warning(error_message.format(child.tag))
          logger.debug(debug_message)
          continue
        parts.append(element_to_ept(child))
      case "it":
        if only_sub:
          if strict:
            raise ValueError(error_message.format(child.tag))
          logger.warning(error_message.format(child.tag))
          logger.debug(debug_message)
          continue
        parts.append(element_to_it(child))
      case "ph":
        if only_sub:
          if strict:
            raise ValueError(error_message.format(child.tag))
          logger.warning(error_message.format(child.tag))
          logger.debug(debug_message)
          continue
        parts.append(element_to_ph(child))
      case "hi":
        if only_sub:
          if strict:
            raise ValueError(error_message.format(child.tag))
          logger.warning(error_message.format(child.tag))
          logger.debug(debug_message)
          continue
        parts.append(element_to_hi(child))
      case _:
        if strict:
          raise ValueError(
            f"Found unexpected element: {child.tag!r} in {source.__class__.__name__!r} element, expected only str, Bpt, Ept, It, Ph, Hi or Sub"
          )
        logger.warning(
          f"Found unexpected element: {child.tag!r} in {source.__class__.__name__!r} element, expected only str, Bpt, Ept, It, Ph, Hi or Sub"
        )
        logger.debug(debug_message)
    if child.tail is not None:
      parts.append(child.tail)
  return parts


def element_to_note(note_element: XmlElement, strict: bool = True) -> Note:
  _check_tag(note_element.tag, "note", strict)
  return Note(
    text=note_element.text if note_element.text is not None else "",
    lang=note_element.attrib.get(f"{XML_NS}lang"),
    o_encoding=note_element.get("o-encoding"),
  )


def element_to_prop(prop_element: XmlElement, strict: bool = True) -> Prop:
  _check_tag(prop_element.tag, "prop", strict)
  return Prop(
    type=prop_element.attrib["type"],
    text=prop_element.text if prop_element.text is not None else "",
    lang=prop_element.attrib.get(f"{XML_NS}lang"),
    o_encoding=prop_element.get("o-encoding"),
  )


def element_to_header(header_element: XmlElement, strict: bool = True) -> Header:
  _check_tag(header_element.tag, "header", strict)
  header_object = Header(
    creationtool=header_element.attrib["creationtool"],
    creationtoolversion=header_element.attrib["creationtoolversion"],
    segtype=Segtype(header_element.attrib["segtype"]),
    o_tmf=header_element.attrib["o-tmf"],
    adminlang=header_element.attrib["adminlang"],
    srclang=header_element.attrib["srclang"],
    datatype=header_element.attrib["datatype"],
    creationdate=datetime.strptime(header_element.attrib["creationdate"], DT_FORMAT)
    if header_element.attrib.get("creationdate") is not None
    else None,
    creationid=header_element.attrib.get("creationid"),
    changedate=datetime.strptime(header_element.attrib["changedate"], DT_FORMAT)
    if header_element.attrib.get("changedate") is not None
    else None,
    changeid=header_element.attrib.get("changeid"),
  )
  for child in header_element:
    if child.tag == "prop":
      header_object.props.append(element_to_prop(child))
    elif child.tag == "note":
      header_object.notes.append(element_to_note(child))
    else:
      if strict:
        raise ValueError(f"Unexpected element {child.tag!r} in header, expected prop or note")
      logger.warning(f"Unexpected element {child.tag!r} in header, expected prop or note")
      logger.debug("Treating as if it were prop or note. Use strict=True to raise an error.")
  return header_object


def element_to_sub(sub_element: XmlElement, strict: bool = True) -> Sub:
  _check_tag(sub_element.tag, "sub", strict)
  return Sub(
    content=element_to_content(sub_element, sub_only=False),
    datatype=sub_element.attrib.get("datatype"),
    type=sub_element.attrib.get("type"),
  )


def element_to_bpt(bpt_element: XmlElement, strict: bool = True) -> Bpt:
  _check_tag(bpt_element.tag, "bpt", strict)
  return Bpt(
    content=element_to_content(bpt_element, sub_only=True),
    i=int(bpt_element.attrib["i"]),
    x=int(bpt_element.attrib["x"]) if bpt_element.attrib.get("x") is not None else None,
    type=bpt_element.attrib.get("type"),
  )


def element_to_ept(ept_element: XmlElement, strict: bool = True) -> Ept:
  _check_tag(ept_element.tag, "ept", strict)
  return Ept(
    content=element_to_content(ept_element, sub_only=True),
    i=int(ept_element.attrib["i"]),
  )


def element_to_it(it_element: XmlElement, strict: bool = True) -> It:
  _check_tag(it_element.tag, "it", strict)
  return It(
    content=element_to_content(it_element, sub_only=True),
    pos=Pos(it_element.attrib["pos"]),
    x=int(it_element.attrib["x"]) if it_element.attrib.get("x") is not None else None,
    type=it_element.attrib.get("type"),
  )


def element_to_ph(ph_element: XmlElement, strict: bool = True) -> Ph:
  _check_tag(ph_element.tag, "ph", strict)
  return Ph(
    content=element_to_content(ph_element, sub_only=True),
    x=int(ph_element.attrib["x"]) if ph_element.attrib.get("x") is not None else None,
    type=ph_element.attrib.get("type"),
    assoc=Assoc(ph_element.attrib["assoc"]) if ph_element.attrib.get("assoc") is not None else None,
  )


def element_to_hi(hi_element: XmlElement, strict: bool = True) -> Hi:
  _check_tag(hi_element.tag, "hi", strict)
  return Hi(
    content=element_to_content(hi_element, sub_only=False),
    x=int(hi_element.attrib["x"]) if hi_element.attrib.get("x") is not None else None,
    type=hi_element.attrib.get("type"),
  )


def element_to_tuv(tuv_element: XmlElement, strict: bool = True) -> Tuv:
  _check_tag(tuv_element.tag, "tuv", strict)
  tuv_object = Tuv(
    lang=tuv_element.attrib[f"{XML_NS}lang"],
    o_encoding=tuv_element.get("o-encoding"),
    datatype=tuv_element.attrib.get("datatype"),
    usagecount=int(tuv_element.attrib["usagecount"]) if tuv_element.attrib.get("usagecount") is not None else None,
    lastusagedate=datetime.strptime(tuv_element.attrib["lastusagedate"], DT_FORMAT)
    if tuv_element.attrib.get("lastusagedate") is not None
    else None,
    creationtool=tuv_element.attrib.get("creationtool"),
    creationtoolversion=tuv_element.attrib.get("creationtoolversion"),
    creationdate=datetime.strptime(tuv_element.attrib["creationdate"], DT_FORMAT)
    if tuv_element.attrib.get("creationdate") is not None
    else None,
    creationid=tuv_element.attrib.get("creationid"),
    changedate=datetime.strptime(tuv_element.attrib["changedate"], DT_FORMAT)
    if tuv_element.attrib.get("changedate") is not None
    else None,
    changeid=tuv_element.attrib.get("changeid"),
    o_tmf=tuv_element.attrib.get("o-tmf"),
  )
  seg_found = False
  for child in tuv_element:
    if child.tag == "prop":
      tuv_object.props.append(element_to_prop(child))
    elif child.tag == "note":
      tuv_object.notes.append(element_to_note(child))
    elif child.tag == "seg":
      if seg_found:
        if strict:
          raise ValueError("Found multiple <seg> elements found in <tuv>")
        logger.warning("Found multiple <seg> elements found in <tuv>")
        logger.debug("Only the first <seg> will be used. Use strict=True to raise an error.")
        continue
      seg_found = True
      tuv_object.content = element_to_content(child, sub_only=False)
    else:
      if strict:
        raise ValueError(f"Found unexpected element {child.tag!r} in tuv, expected prop, note or seg")
      logger.warning(f"Found unexpected element {child.tag!r} in tuv, expected prop, note or seg")
      logger.debug("Ignoring. Use strict=True to raise an error.")
  if not seg_found:
    if strict:
      raise ValueError("Missing <seg> element in <tuv>")
    logger.warning("Missing <seg> element in <tuv>")
    logger.debug("Treating as if it were a <seg> with an empty text. Use strict=True to raise an error.")
    tuv_object.content.append("")
  return tuv_object


def element_to_tu(tu_element: XmlElement, strict: bool = True) -> Tu:
  _check_tag(tu_element.tag, "tu", strict)
  tu_object = Tu(
    tuid=tu_element.attrib.get("tuid"),
    o_encoding=tu_element.get("o-encoding"),
    datatype=tu_element.attrib.get("datatype"),
    usagecount=int(tu_element.attrib["usagecount"]) if tu_element.attrib.get("usagecount") is not None else None,
    lastusagedate=datetime.strptime(tu_element.attrib["lastusagedate"], DT_FORMAT)
    if tu_element.attrib.get("lastusagedate") is not None
    else None,
    creationtool=tu_element.attrib.get("creationtool"),
    creationtoolversion=tu_element.attrib.get("creationtoolversion"),
    creationdate=datetime.strptime(tu_element.attrib["creationdate"], DT_FORMAT)
    if tu_element.attrib.get("creationdate") is not None
    else None,
    creationid=tu_element.attrib.get("creationid"),
    changedate=datetime.strptime(tu_element.attrib["changedate"], DT_FORMAT)
    if tu_element.attrib.get("changedate") is not None
    else None,
    segtype=Segtype(tu_element.attrib["segtype"]) if tu_element.attrib.get("segtype") is not None else None,
    changeid=tu_element.attrib.get("changeid"),
    o_tmf=tu_element.attrib.get("o-tmf"),
    srclang=tu_element.attrib.get("srclang"),
  )
  for child in tu_element:
    if child.tag == "prop":
      tu_object.props.append(element_to_prop(child))
    elif child.tag == "note":
      tu_object.notes.append(element_to_note(child))
    elif child.tag == "tuv":
      tu_object.variants.append(element_to_tuv(child))
    else:
      if strict:
        raise ValueError(f"Found unexpected element {child.tag!r} in tu, expected prop or note or tuv")
      logger.warning(f"Found unexpected element {child.tag!r} in tu, expected prop or note or tuv")
      logger.debug("Ignoring. Use strict=True to raise an error.")
  return tu_object


def element_to_tmx(tmx_element: XmlElement, strict: bool = True) -> Tmx:
  _check_tag(tmx_element.tag, "tmx", strict)
  body_found = False
  header: Header | None = None
  body: list[Tu] = []
  for child in tmx_element:
    if child.tag == "header":
      if header is not None:
        if strict:
          raise ValueError("Multiple <header> elements found in <tmx>")
        logger.warning("Multiple <header> elements found in <tmx>")
        logger.debug("Only considering the first <header> element. Use strict=True to raise an error.")
        continue
      header = element_to_header(child)
    elif child.tag == "body":
      if body_found:
        if strict:
          raise ValueError("Multiple <body> elements found in <tmx>")
        logger.warning("Multiple <body> elements found in <tmx>")
        logger.debug("tus from all <body> elements will be included. Use strict=True to raise an error.")
        body_found = False
      body_found = True
      for tu in child:
        if tu.tag == "tu":
          body.append(element_to_tu(tu))
        else:
          if strict:
            raise ValueError(f"Found unexpected element {tu.tag!r} in body, expected tu")
          logger.warning(f"Found unexpected element {tu.tag!r} in body, expected tu")
          logger.debug("Ignoring. Use strict=True to raise an error.")
    else:
      if strict:
        raise ValueError(f"Found unexpected element {child.tag!r} in tmx, expected header or body")
      logger.warning(f"Found unexpected element {child.tag!r} in tmx, expected header or body")
      logger.debug("Ignoring. Use strict=True to raise an error.")
  if header is None:
    if strict:
      raise ValueError("Missing <header> element in <tmx>")
    logger.warning("Missing <header> element in <tmx>")
    logger.debug("Creating minimal header. Use strict=True to raise an error.")
    header = Header(
      creationtool="python-tmx",
      creationtoolversion="0.4",
      segtype=Segtype.PARAGRAPH,
      o_tmf="unknown",
      adminlang="en",
      srclang="en",
      datatype="unknown",
    )
  if not body_found:
    if strict:
      raise ValueError("Missing <body> element in <tmx>")
    logger.warning("Missing <body> element in <tmx>")
    logger.debug("Body will be an empty list. Use strict=True to raise an error.")
  return Tmx(version=tmx_element.attrib["version"], header=header, body=body)
