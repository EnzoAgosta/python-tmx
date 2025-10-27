from __future__ import annotations

import xml.etree.ElementTree as py
from abc import abstractmethod
from collections.abc import Generator
from datetime import datetime
from enum import StrEnum
from typing import Any, Callable, ClassVar, Generic, Literal, Self, TypeVar

import lxml.etree as lx

from python_tmx.base.classes import (
  BaseElementAlias,
  Note,
)

T = TypeVar("T", bound=BaseElementAlias)
E = TypeVar("E", bound=StrEnum)
type XmlElement = lx._Element | py.Element


def _handle_notes(obj: XmlWrapper, *args) -> Generator[XmlNote]:
  elem = obj._xml_element
  cache = obj._attribute_cache
  cache["notes"] = []
  for note_elem in elem:
    if note_elem.tag == "note":
      note_wrapper = XmlNote.from_xml(note_elem)
      cache["notes"].append(note_wrapper)
      yield note_wrapper


def _handle_props(obj: XmlWrapper, *args) -> Generator[XmlProp]:
  elem = obj._xml_element
  cache = obj._attribute_cache
  cache["props"] = []
  for prop_elem in elem:
    if prop_elem.tag == "note":
      note_wrapper = XmlProp.from_xml(prop_elem)
      cache["props"].append(note_wrapper)
      yield note_wrapper


def _handle_enums(obj: XmlWrapper, attribute: str, enum: type[E], *args) -> E | None:
  elem = obj._xml_element
  cache = obj._attribute_cache
  value = elem.attrib.get(attribute)
  if value is not None:
    value = enum(value)
  cache[attribute] = value
  return value


def _handle_str(obj: XmlWrapper, attribute: str, *args) -> str | None:
  elem = obj._xml_element
  cache = obj._attribute_cache
  value = elem.attrib.get(attribute)
  cache[attribute] = value
  return value


def _handle_lang(obj: XmlWrapper, *args) -> str | None:
  elem = obj._xml_element
  cache = obj._attribute_cache
  value = elem.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
  cache["lang"] = value
  return value


def _handle_dashed(obj: XmlWrapper, attribute: str, *args) -> str | None:
  elem = obj._xml_element
  cache = obj._attribute_cache
  normalized = attribute.replace("-", "_")
  value = elem.attrib.get(normalized)
  cache[normalized] = value
  return value


def _handle_int(obj: XmlWrapper, attribute: str, *args) -> int | None:
  elem = obj._xml_element
  cache = obj._attribute_cache
  value: str | int | None = elem.attrib.get(attribute)
  if value is not None:
    value = int(value)
  cache[attribute] = value
  return value


def _handle_datetime(obj: XmlWrapper, attribute: str, *args) -> datetime | None:
  elem = obj._xml_element
  cache = obj._attribute_cache
  value = elem.attrib.get(attribute)
  if value is not None:
    parsed = datetime.fromisoformat(value)
  else:
    parsed = None
  cache[attribute] = parsed
  return parsed


def _handle_header(obj: XmlWrapper, *args) -> XmlHeader:
  elem = obj._xml_element
  cache = obj._attribute_cache
  header_elem = elem.find("header")
  if header_elem is None:
    raise ValueError("cannot find header element in given xml element")
  header_wrapper = XmHeader.from_xml(header_elem)
  cache["header"] = header_wrapper
  return header_wrapper


def _handle_cache_tus(obj: XmlWrapper, *args) -> Generator[XmlTu]:
  elem = obj._xml_element
  cache = obj._attribute_cache
  body = elem.find("body")
  if body is None:
    raise ValueError("cannot find body element in given xml element")
  cache["body"] = []
  for child_elem in body:
    if child_elem.tag == "tu":
      tu_wrapper = XmlTu.from_xml(child_elem)
      cache["body"].append(tu_wrapper)
      yield tu_wrapper


def _generate_cache_tuvs(obj: XmlWrapper, *args) -> Generator[XmlTuv]:
  elem = obj._xml_element
  cache = obj._attribute_cache
  cache["variants"] = []
  for child_elem in elem:
    if child_elem.tag == "tuv":
      tuv_wrapper = XmlTuv.from_xml(child_elem)
      cache["variants"].append(tuv_wrapper)
      yield tuv_wrapper


def _handle_content(obj: XmlWrapper) -> Generator[str | XmlBpt | XmlEpt | XmlIt | XmlHi | XmlPh | XmlSub]:
  root_elem = obj._xml_element
  cache = obj._attribute_cache
  if not len(root_elem):
    cache["content"] = root_elem.text
    yield root_elem.text
  else:
    cache["content"] = []
    if root_elem.text is not None:
      cache["content"].append(root_elem.text)
      yield root_elem.text
    for child in root_elem:
      TAG_TO_WRAPPER: dict[str, type[XmlWrapper]] = dict()
      wrapper = TAG_TO_WRAPPER.get(str(child.tag))
      if wrapper is None:
        raise ValueError(
          f"Unexpected tag found. Expected one of <bpt>, <ept>, <it>, <hi>, <ph> or <sub> but got {child.tag!r}"
        )
      wrapped = wrapper.from_xml(child)
      cache["content"].append(wrapped)
      yield wrapped
      if child.tail is not None:
        cache["content"].append(child.tail)
        yield child.tail


class XmlWrapper(Generic[T]):
  __slots__ = ()

  _attribute_getters: ClassVar[dict[str, Callable]]
  _attribute_setters: ClassVar[dict[str, Callable]]

  _tag: ClassVar[str]
  _required_attrs: ClassVar[set[str]]
  _xml_element: lx._Element | py.Element
  _attribute_cache: dict[str, Any]

  def __getattr__(self, name: str) -> Any:
    if name.startswith("_"):
      return object.__getattribute__(self, name)

    cache: dict[str, Any] = object.__getattribute__(self, "_attribute_cache")
    if name in cache:
      return cache[name]

    handler = self._attribute_getters.get(name)
    if handler is not None:
      return handler(self, name)
    else:
      raise AttributeError("Attribute is not handled by the class")

  def __setattr__(self, name: str, value: Any) -> None:
    if name.startswith("_"):
      return object.__setattr__(self, name, value)
    handler = self._attribute_setter.get(name)
    if handler is not None:
      handler(self, name, value)

  def __init__(self, element: XmlElement) -> None:
    self._xml_element = element
    self._attribute_cache = dict()

  @classmethod
  def validate_element(cls, element: XmlElement) -> None:
    if element.tag != cls._tag:
      raise ValueError(f"Expected <{cls._tag}> element, got <{element.tag!r}>")
    missing_required = cls._required_attrs - set(element.attrib.keys())
    if missing_required:
      raise ValueError(f"Element is missing required attributes {missing_required!r}")

  @classmethod
  @abstractmethod
  def from_dataclass(cls, base_element: T, engine: Literal["lxml", "python"] = "lxml") -> XmlWrapper[T]: ...

  @abstractmethod
  def to_dataclass(self) -> T: ...

  @classmethod
  def from_xml(cls, element: XmlElement) -> Self:
    cls.validate_element(element)
    return cls(element)


class XmlNote(XmlWrapper[Note]):
  __slots__ = ("lang", "content", "o_encoding")
  _tag = "note"
  _required_attrs = set()
  _attribute_getters = {"lang": _handle_lang, "o_encoding": _handle_dashed}
  _attribute_setter: ClassVar[dict[str, Callable]]

  content: str
  lang: str
  o_encoding: str

  @classmethod
  def from_dataclass(cls, base_element: Note, engine: Literal["lxml", "python"] = "lxml") -> Self:
    if not isinstance(base_element, Note):
      raise TypeError(f"Expected a Note but got a {type(base_element)}")
    if engine == "lxml":
      factory = lx.Element
    elif engine == "python":
      factory = py.Element  # type:ignore[assignment]

    xml_elem = factory("note")
    xml_elem.text = base_element.text
    if base_element.lang is not None:
      xml_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = base_element.lang
    if base_element.o_encoding is not None:
      xml_elem.attrib["o_encoding"] = base_element.o_encoding
    return cls(xml_elem)

  def to_dataclass(self) -> Note:
    self.validate_element(self._xml_element)
    return Note(
      text=self.content,
      lang=self.lang,
      o_encoding=self.o_encoding,
    )
