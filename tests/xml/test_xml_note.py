import lxml.etree as et

from python_tmx.base.models import Note
from python_tmx.xml.converters import parse_note


def test_parse_note_from_full_element(full_note_lxml_elem: et._Element):
  note = parse_note(full_note_lxml_elem)
  assert isinstance(note, Note)
  assert note.content == full_note_lxml_elem.text
  assert note.lang == full_note_lxml_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
  assert note.o_encoding == full_note_lxml_elem.attrib["o-encoding"]


def test_parse_note_from_minimal_element(minimal_note_lxml_elem: et._Element):
  note = parse_note(minimal_note_lxml_elem)
  assert isinstance(note, Note)
  assert note.lang is None
  assert note.o_encoding is None
  assert note.content == minimal_note_lxml_elem.text


def test_parse_note_with_empty_text_returns_empty_string(full_note_lxml_elem: et._Element):
  full_note_lxml_elem.text = None
  note = parse_note(full_note_lxml_elem)
  assert note.content == ""


def test_parse_note_ignores_extra_attributes(full_note_lxml_elem: et._Element):
  full_note_lxml_elem.attrib["extra"] = "ignore me"
  parse_note(full_note_lxml_elem)
