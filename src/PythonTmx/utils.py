import xml.etree.ElementTree as pyet
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import MISSING, fields
from datetime import datetime
from itertools import chain
from typing import Any, Literal, get_args, get_origin, get_type_hints, overload

import lxml.etree as lxet

from PythonTmx.classes import (
  ASSOC,
  POS,
  SEGTYPE,
  Bpt,
  Ept,
  Header,
  Hi,
  InlineElement,
  It,
  Map,
  Note,
  Ph,
  Prop,
  StructuralElement,
  Sub,
  Tmx,
  TmxElement,
  Tu,
  Tuv,
  Ude,
  Ut,
)
from PythonTmx.errors import ValidationError

__all__ = ["to_element", "from_element"]


def _make_attrib_dict(map_: TmxElement, keep_extra: bool) -> dict[str, str]:
  attrib_dict: dict[str, str] = dict()
  for attr in fields(map_):
    if attr.metadata.get("exclude", False):
      continue
    name, value, func = (
      attr.metadata.get("export_name", attr.name),
      getattr(map_, attr.name),
      attr.metadata.get("export_func", str),
    )
    if value is not None:
      attrib_dict[name] = func(value)
  if keep_extra:
    attrib_dict.update(**map_.extra)
  return attrib_dict


def _fill_inline_content(
  content: Iterable,
  element: lxet._Element | pyet.Element,
  /,
  lxml: Literal[True] | Literal[False],
  keep_extra: bool,
  validate_element: bool,
) -> None:
  parent = None
  for item in content:
    if isinstance(item, InlineElement):
      parent = to_element(
        item,
        lxml,
        keep_extra=keep_extra,
        validate_element=validate_element,
      )
      element.append(parent)  # type: ignore
    else:
      if parent is None:
        if element.text is None:
          element.text = item
        else:
          element.text += item
      else:
        if parent.tail is None:
          parent.tail = item
        else:
          parent.tail += item


def _parse_inline_content(
  element: lxet._Element | pyet.Element, /, keep_extra: bool
) -> list:
  content: list = []
  if element.text is not None:
    content.append(element.text)
  for child in element:
    match child.tag:
      case "bpt":
        content.append(_parse_bpt(child, keep_extra=keep_extra))
      case "ept":
        content.append(_parse_ept(child, keep_extra=keep_extra))
      case "it":
        content.append(_parse_it(child, keep_extra=keep_extra))
      case "ph":
        content.append(_parse_ph(child, keep_extra=keep_extra))
      case "hi":
        content.append(_parse_hi(child, keep_extra=keep_extra))
      case "ut":
        content.append(_parse_ut(child, keep_extra=keep_extra))
      case "sub":
        content.append(_parse_sub(child, keep_extra=keep_extra))
      case _:
        raise ValueError(f"Unknown element {child.tag!r}")
    if child.tail is not None:
      content.append(child.tail)
  return content


def _parse_bpt(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Bpt:
  bpt = Bpt(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    i=int(element.attrib.pop("i")),
    type=element.attrib.pop("type", None),
  )
  if (x := element.attrib.pop("x", None)) is not None:
    bpt.x = int(x)
  if keep_extra:
    bpt.extra = dict(element.attrib)
  return bpt


def _parse_ept(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Ept:
  return Ept(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    i=int(element.attrib.pop("i")),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_it(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> It:
  it = It(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    pos=POS(element.attrib.pop("pos")),
    type=element.attrib.pop("type", None),
  )
  if (x := element.attrib.pop("x", None)) is not None:
    it.x = int(x)
  if keep_extra:
    it.extra = dict(element.attrib)
  return it


def _parse_ph(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Ph:
  ph = Ph(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    type=element.attrib.pop("type", None),
  )
  if (assoc := element.attrib.pop("assoc", None)) is not None:
    ph.assoc = ASSOC(assoc)
  if (x := element.attrib.pop("x", None)) is not None:
    ph.x = int(x)
  if keep_extra:
    ph.extra = dict(element.attrib)
  return ph


def _parse_hi(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Hi:
  hi = Hi(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    type=element.attrib.pop("type", None),
  )
  if (x := element.attrib.pop("x", None)) is not None:
    hi.x = int(x)
  if keep_extra:
    hi.extra = dict(element.attrib)
  return hi


def _parse_ut(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Ut:
  ut = Ut(
    content=_parse_inline_content(element, keep_extra=keep_extra),
  )
  if (x := element.attrib.pop("x", None)) is not None:
    ut.x = int(x)
  if keep_extra:
    ut.extra = dict(element.attrib)
  return ut


def _parse_sub(element: lxet._Element | pyet.Element, /, keep_extra: bool) -> Sub:
  return Sub(
    content=_parse_inline_content(element, keep_extra=keep_extra),
    datatype=element.attrib.pop("datatype", None),
    type=element.attrib.pop("type", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_map(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Map:
  return Map(
    unicode=element.attrib.pop("unicode"),
    code=element.attrib.pop("code", None),
    ent=element.attrib.pop("ent", None),
    subst=element.attrib.pop("subst", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_ude(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Ude:
  ude = Ude(
    name=element.attrib.pop("name"),
    base=element.attrib.get("base", None),
    extra=dict(element.attrib) if keep_extra else {},
    maps=[_parse_map(child, keep_extra=keep_extra) for child in element.iter("map")],
  )
  return ude


def _parse_note(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Note:
  return Note(
    text=element.text,  # type: ignore
    lang=element.attrib.pop(r"{http://www.w3.org/XML/1998/namespace}lang", None),
    encoding=element.attrib.pop("o-encoding", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_prop(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Prop:
  return Prop(
    text=element.text,  # type: ignore
    type=element.attrib.pop("type"),
    lang=element.attrib.pop(r"{http://www.w3.org/XML/1998/namespace}lang", None),
    encoding=element.attrib.pop("o-encoding", None),
    extra=dict(element.attrib) if keep_extra else {},
  )


def _parse_header(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Header:
  header = Header(
    creationtool=element.attrib.pop("creationtool"),
    creationtoolversion=element.attrib.pop("creationtoolversion"),
    segtype=SEGTYPE(element.attrib.pop("segtype")),
    tmf=element.attrib.pop("o-tmf"),
    adminlang=element.attrib.pop("adminlang"),
    srclang=element.attrib.pop("srclang"),
    datatype=element.attrib.pop("datatype"),
    encoding=element.attrib.pop("o-encoding", None),
    creationid=element.attrib.pop("creationid", None),
    changeid=element.attrib.pop("changeid", None),
    notes=[_parse_note(child, keep_extra=keep_extra) for child in element.iter("note")],
    props=[_parse_prop(child, keep_extra=keep_extra) for child in element.iter("prop")],
    udes=[_parse_ude(child, keep_extra=keep_extra) for child in element.iter("ude")],
  )
  if (creationdate := element.attrib.pop("creationdate", None)) is not None:
    header.creationdate = datetime.fromisoformat(creationdate)
  if (changedate := element.attrib.pop("changedate", None)) is not None:
    header.changedate = datetime.fromisoformat(changedate)
  if keep_extra:
    header.extra = dict(element.attrib)
  return header


def _parse_tuv(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Tuv:
  tuv = Tuv(
    lang=element.attrib.pop(r"{http://www.w3.org/XML/1998/namespace}lang"),
    encoding=element.attrib.pop("o-encoding", None),
    datatype=element.attrib.pop("datatype", None),
    creationtool=element.attrib.pop("creationtool", None),
    creationtoolversion=element.attrib.pop("creationtoolversion", None),
    creationid=element.attrib.pop("creationid", None),
    tmf=element.attrib.pop("o-tmf", None),
    changeid=element.attrib.pop("changeid", None),
    props=[
      _parse_prop(child, keep_extra=keep_extra) for child in element.findall("prop")
    ],
    notes=[
      _parse_note(child, keep_extra=keep_extra) for child in element.findall("note")
    ],
  )
  if (seg := element.find("seg")) is not None:
    tuv.content = _parse_inline_content(seg, keep_extra=keep_extra)
  if (creationdate := element.attrib.pop("creationdate", None)) is not None:
    tuv.creationdate = datetime.fromisoformat(creationdate)
  if (changedate := element.attrib.pop("changedate", None)) is not None:
    tuv.changedate = datetime.fromisoformat(changedate)
  if (lastusagedate := element.attrib.pop("lastusagedate", None)) is not None:
    tuv.changedate = datetime.fromisoformat(lastusagedate)
  if (usagecount := element.attrib.pop("usagecount", None)) is not None:
    tuv.usagecount = int(usagecount)
  if keep_extra:
    tuv.extra = dict(element.attrib)
  return tuv


def _parse_tu(element: lxet._Element | pyet.Element, /, keep_extra: bool = False) -> Tu:
  tu = Tu(
    tuid=element.attrib.pop("tuid", None),
    encoding=element.attrib.pop("o-encoding", None),
    datatype=element.attrib.pop("datatype", None),
    creationtool=element.attrib.pop("creationtool", None),
    creationtoolversion=element.attrib.pop("creationtoolversion", None),
    creationid=element.attrib.pop("creationid", None),
    changeid=element.attrib.pop("changeid", None),
    tmf=element.attrib.pop("o-tmf", None),
    srclang=element.attrib.pop("srclang", None),
    notes=[
      _parse_note(child, keep_extra=keep_extra) for child in element.findall("note")
    ],
    props=[
      _parse_prop(child, keep_extra=keep_extra) for child in element.findall("prop")
    ],
    tuvs=[_parse_tuv(child, keep_extra=keep_extra) for child in element.findall("tuv")],
  )
  if lastusagedate := element.attrib.pop("lastusagedate", None):
    tu.lastusagedate = datetime.fromisoformat(lastusagedate)
  if (creationdate := element.attrib.pop("creationdate", None)) is not None:
    tu.creationdate = datetime.fromisoformat(creationdate)
  if (changedate := element.attrib.pop("changedate", None)) is not None:
    tu.changedate = datetime.fromisoformat(changedate)
  if (segtype := element.attrib.pop("segtype", None)) is not None:
    tu.segtype = SEGTYPE(segtype)
  if (usagecount := element.attrib.pop("usagecount", None)) is not None:
    tu.usagecount = int(usagecount)
  if keep_extra:
    tu.extra = dict(element.attrib)
  return tu


def _parse_tmx(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> Tmx:
  if (header_elem := element.find("header")) is None:
    raise ValueError("Missing header element")
  if (body_elem := element.find("body")) is None:
    raise ValueError("Missing body element")
  return Tmx(
    header=_parse_header(header_elem, keep_extra=keep_extra),
    tus=[_parse_tu(tu, keep_extra=keep_extra) for tu in body_elem.iter("tu")],
    extra=dict(element.attrib) if keep_extra else {},
  )


@overload
def _tmx_to_element(
  tmx: Tmx,
  lxml: Literal[True],
  keep_extra: bool,
  validate_element: bool,
) -> lxet._Element: ...
@overload
def _tmx_to_element(
  tmx: Tmx,
  lxml: Literal[False],
  keep_extra: bool,
  validate_element: bool,
) -> pyet.Element: ...
def _tmx_to_element(
  tmx: Tmx,
  lxml: Literal[True] | Literal[False],
  keep_extra: bool,
  validate_element: bool,
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E("tmx", version="1.4")
  elem.append(
    _structural_element_to_element(
      tmx.header,
      lxml,
      keep_extra=keep_extra,
      validate_element=validate_element,
    )  # type: ignore
  )
  body = E("body")
  elem.append(body)  # type: ignore
  body.extend(
    [
      to_element(item, lxml, keep_extra=keep_extra, validate_element=validate_element)  # type: ignore
      for item in tmx.tus
    ]
  )
  return elem


@overload
def _inline_element_to_element(
  element: InlineElement,
  lxml: Literal[True],
  /,
  keep_extra: bool,
  validate_element: bool,
) -> lxet._Element: ...
@overload
def _inline_element_to_element(
  element: InlineElement,
  lxml: Literal[False],
  /,
  keep_extra: bool,
  validate_element: bool,
) -> pyet.Element: ...
def _inline_element_to_element(
  element: InlineElement,
  lxml: Literal[True] | Literal[False],
  /,
  keep_extra: bool,
  validate_element: bool,
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E(
    element.__class__.__name__.lower(),
    attrib=_make_attrib_dict(element, keep_extra=keep_extra),
  )
  _fill_inline_content(
    element.content,
    elem,
    lxml=lxml,
    keep_extra=keep_extra,
    validate_element=validate_element,
  )
  return elem


@overload
def _structural_element_to_element(
  element: StructuralElement,
  lxml: Literal[True],
  /,
  keep_extra: bool,
  validate_element: bool,
) -> lxet._Element: ...
@overload
def _structural_element_to_element(
  element: StructuralElement,
  lxml: Literal[False],
  /,
  keep_extra: bool,
  validate_element: bool,
) -> pyet.Element: ...
def _structural_element_to_element(
  element: StructuralElement,
  lxml: Literal[True] | Literal[False],
  /,
  keep_extra: bool,
  validate_element: bool,
) -> lxet._Element | pyet.Element:
  E = lxet.Element if lxml else pyet.Element
  elem = E(
    element.__class__.__name__.lower(),
    attrib=_make_attrib_dict(element, keep_extra=keep_extra),
  )
  elem.extend(
    [
      to_element(item, lxml, keep_extra=keep_extra, validate_element=validate_element)  # type: ignore
      for item in chain(
        element.notes if hasattr(element, "notes") else [],
        element.props if hasattr(element, "props") else [],
        element.udes if hasattr(element, "udes") else [],
        element.maps if hasattr(element, "maps") else [],
        element.tuvs if hasattr(element, "tuvs") else [],
        element.tus if hasattr(element, "tus") else [],
      )
    ]
  )
  if hasattr(element, "extra"):
    elem.attrib.update(element.extra)
  if hasattr(element, "text"):
    elem.text = element.text
  return elem


@overload
def to_element(
  element: TmxElement,
  lxml: Literal[True],
  /,
  keep_extra: bool = False,
  validate_element: bool = True,
) -> lxet._Element: ...
@overload
def to_element(
  element: TmxElement,
  lxml: Literal[False],
  /,
  keep_extra: bool = False,
  validate_element: bool = True,
) -> pyet.Element: ...
def to_element(
  element: TmxElement,
  lxml: Literal[True] | Literal[False],
  /,
  keep_extra: bool = False,
  validate_element: bool = True,
) -> lxet._Element | pyet.Element:
  """
  Converts a TmxElement to an lxml or ElementTree element.

  If `lxml` is True, the output will be an lxml element, otherwise it will be an
  ElementTree element.

  If `keep_extra` is True, the extra attributes of the element (and its children)
  will be included in the output.

  .. warning::
    Even if `validate_element` is True, the `extra` dict will NOT be validated.
    As this is NOT part of the TMX spec, it is the responsibility of the user to
    ensure that the `extra` dict is a valid mapping of strings to strings.

  Parameters
  ----------
  element : TmxElement
      The TmxElement to convert
  lxml : Literal[True] | Literal[False]
      Whether to use lxml or ElementTree, by default True
  keep_extra : bool, optional
      Whether to include extra attributes present in the element (and its children),
      by default False
  validate_element : bool, optional
      Whether to validate the element before converting it (and its children),
      by default True

  Returns
  -------
  lxet._Element | pyet.Element
      An lxml or ElementTree element representing the TmxElement

  Raises
  ------
  TypeError
      If the TmxElement is not recognized
  """
  if validate_element:
    validate(element)
  match element:
    case Tmx():
      return _tmx_to_element(
        element, lxml, keep_extra=keep_extra, validate_element=validate_element
      )
    case Tuv():
      tuv = _structural_element_to_element(
        element, lxml, keep_extra=keep_extra, validate_element=validate_element
      )
      seg = lxet.Element("seg") if lxml else pyet.Element("seg")
      tuv.append(seg)  # type: ignore
      _fill_inline_content(
        element.content,
        seg,
        lxml=lxml,
        keep_extra=keep_extra,
        validate_element=validate_element,
      )
      return tuv
    case StructuralElement():
      return _structural_element_to_element(
        element, lxml, keep_extra=keep_extra, validate_element=validate_element
      )
    case InlineElement():
      return _inline_element_to_element(
        element, lxml, keep_extra=keep_extra, validate_element=validate_element
      )
    case _:
      raise TypeError(f"Unknown element {element}")


def from_element(
  element: lxet._Element | pyet.Element, /, keep_extra: bool = False
) -> TmxElement:
  """
  Converts an lxml or ElementTree element to a TmxElement object.

  Parameters
  ----------
  element : lxet._Element | pyet.Element
      The element to convert
  keep_extra : bool, optional
      Whether to keep extra attributes present in the element (and its children),
      by default False

  Returns
  -------
  TmxElement
      An instance of the appropriate TmxElement subclass

  Raises
  ------
  ValueError
      If the element is not a valid lxml or ElementTree element or the tag is not recognized
  """
  match element.tag:
    case "map":
      return _parse_map(element, keep_extra=keep_extra)
    case "ude":
      return _parse_ude(element, keep_extra=keep_extra)
    case "note":
      return _parse_note(element, keep_extra=keep_extra)
    case "prop":
      return _parse_prop(element, keep_extra=keep_extra)
    case "header":
      return _parse_header(element, keep_extra=keep_extra)
    case "tuv":
      return _parse_tuv(element, keep_extra=keep_extra)
    case "tu":
      return _parse_tu(element, keep_extra=keep_extra)
    case "tmx":
      return _parse_tmx(element, keep_extra=keep_extra)
    case "bpt":
      return _parse_bpt(element, keep_extra=keep_extra)
    case "ept":
      return _parse_ept(element, keep_extra=keep_extra)
    case "it":
      return _parse_it(element, keep_extra=keep_extra)
    case "ph":
      return _parse_ph(element, keep_extra=keep_extra)
    case "hi":
      return _parse_hi(element, keep_extra=keep_extra)
    case "ut":
      return _parse_ut(element, keep_extra=keep_extra)
    case "sub":
      return _parse_sub(element, keep_extra=keep_extra)
    case _:
      raise ValueError(f"Unknown element {element.tag!r}")


def _check_hex_and_unicode_codepoint(string: str) -> None:
  if not isinstance(string, str):
    raise TypeError(f"Expected str, not {type(string)}")
  if not string.startswith("#x"):
    raise ValueError(f"string should start with '#x' but found {string[:2]!r}")
  try:
    code_point = int(string[2:], 16)
  except ValueError:
    raise ValueError(f"Invalid hexadecimal string {string!r}")
  try:
    chr(code_point)
  except ValueError:
    raise ValueError(f"Invalid Unicode code point {code_point!r}")


def _validate_map(map_: Map) -> None:
  _check_hex_and_unicode_codepoint(map_.unicode)
  if map_.code is not None:
    _check_hex_and_unicode_codepoint(map_.code)
  if map_.ent is not None:
    if not map_.ent.isascii():
      raise ValueError(f"ent should be ASCII but found {map_.ent!r}")
  if map_.subst is not None:
    if not map_.subst.isascii():
      raise ValueError(f"subst should be ASCII but found {map_.subst!r}")


def _validate_balanced_paired_tags(content: Iterable) -> None:
  bpt_count = Counter(bpt.i for bpt in content if isinstance(bpt, Bpt))
  ept_count = Counter(ept.i for ept in content if isinstance(ept, Ept))
  if len(bpt_count) != len(ept_count):
    raise ValueError("Number of Bpt and Ept tags must be equal")
  if not len(bpt_count):
    return
  if bpt_count.most_common(1)[0][1] > 1:
    raise ValueError("Bpt indexes must be unique")
  if ept_count.most_common(1)[0][1] > 1:
    raise ValueError("Ept indexes must be unique")


_type_hints_cache = {}


def _get_type_hints(cls: type) -> dict[str, type]:
  if cls not in _type_hints_cache:
    _type_hints_cache[cls] = get_type_hints(cls)
  return _type_hints_cache[cls]


def _validate_extra(value: dict[str, str]) -> None:
  if not isinstance(value, dict):
    raise TypeError(f"'extra' field must be a dict, got {type(value)}")
  for k, v in value.items():
    if not isinstance(k, str) or not isinstance(v, str):
      raise TypeError(
        f"'extra' dict must contain only string keys and values but found"
        f" {type(k).__name__!r}: {type(v).__name__!r}"
      )


def _validate_sequence(value: Sequence[Any], expected_type: type[Any]) -> None:
  union = get_args(expected_type)[0]
  for item in value:
    if not isinstance(item, union):
      raise TypeError(
        f"Expected all items to be one of {union!r} but found {type(item).__name__!r}"
      )


def validate(obj: TmxElement, /, validate_extra: bool = True) -> None:
  """
  Validates a TmxElement object and its children recursively to ensure proper
  typing.

  If `validate_extra` is True, the `extra` dict will be validated to ensure that
  it only contains string keys and values.

  Parameters
  ----------
  obj : TmxElement
      The TmxElement object to validate
  validate_extra : bool, optional
      Whether to validate the `extra` dict, by default True

  Raises
  ------
  ValidationError
      On validation failure
  """
  stack = [obj]
  while stack:
    current = stack.pop()
    if not isinstance(current, TmxElement):
      raise ValidationError(current) from TypeError(
        f"Expected a TmxElement but got {type(current)}"
      )
    if isinstance(current, Map):
      try:
        _validate_map(current)
      except (TypeError, ValueError) as e:
        raise ValidationError(current) from e
      continue
    hints = _get_type_hints(current.__class__)
    for field in fields(current):
      value = getattr(current, field.name)
      if field.name == "extra" and validate_extra:
        try:
          _validate_extra(value)
        except TypeError as e:
          raise ValidationError(current, field=field.name) from e
        continue
      if value is None:
        if field.default is MISSING:
          raise ValidationError(current, field=field.name) from ValueError(
            f"Attribute {field.name!r} cannot be None"
          )
        continue
      expected_type = hints[field.name]
      if get_origin(expected_type) is Sequence:
        try:
          _validate_sequence(value, expected_type)
          stack.extend([item for item in value if isinstance(item, TmxElement)])
        except TypeError as e:
          raise ValidationError(current, field=field.name) from e
        continue
      if not isinstance(value, expected_type):
        raise ValidationError(current, field=field.name) from TypeError(
          f"{field.name!r} must be of type {expected_type.__name__!r} but got "
          f"{type(value).__name__!r}"
        )
    if isinstance(current, Tuv):
      _validate_balanced_paired_tags(current.content)
      stack.extend([item for item in current.content if isinstance(item, TmxElement)])
