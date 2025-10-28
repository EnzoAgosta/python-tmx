from typing import TypeVar, cast
import xml.etree.ElementTree as ET
import lxml.etree as LET

from python_tmx.base.types import Note

XmlElement = TypeVar("XmlElement", ET.Element, LET.Element)


def element_to_note(note_element: XmlElement) -> Note:
  return Note(
    text=note_element.text if note_element.text is not None else "",
    lang=note_element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang"),
    o_encoding=note_element.get("o-encoding"),
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


def note_to_element(note_object: Note, /, backend: type[XmlElement] | None = None) -> XmlElement:
  backend = get_backend(backend)
  note_element = backend("note", {})
  note_element.text = note_object.text
  if note_object.lang is not None:
    note_element.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = note_object.lang
  if note_object.o_encoding is not None:
    note_element.attrib["o-encoding"] = note_object.o_encoding

  for _ in range(3):
    note_element.append(backend("test"))
  for _ in note_element:
    pass
  return note_element
