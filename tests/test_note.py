import pytest
import xml.etree.ElementTree as et
import lxml.etree as ET

from PythonTmx.classes import Note


@pytest.fixture
def note_elem():
  el = et.Element("note")
  el.text = "test"
  el.attrib["o-encoding"] = "utf-8"
  el.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "en"
  return el


@pytest.fixture
def note_elem_bad_attrib():
  el = et.Element("note")
  el.text = "test"
  el.attrib["encoding"] = "utf-8"
  el.attrib["lang"] = "en"
  return el


@pytest.fixture
def unknown_elem():
  return et.Element("unknown")


@pytest.fixture
def correct_note():
  return Note(text="test", encoding="utf-8", lang="en")


class TestNote:
  def test_init(self):
    with pytest.raises(TypeError):
      Note()
    note = Note(text="test", encoding="utf-8", lang="en")
    assert note.text == "test"
    assert note.encoding == "utf-8"
    assert note.lang == "en"

  def test_init_from_correct_element(self, note_elem):
    note = Note._from_element(note_elem)
    assert note.text == "test"
    assert note.encoding == "utf-8"
    assert note.lang == "en"

  def test_init_from_correct_element_with_args(self, note_elem):
    note = Note._from_element(note_elem, text="override", encoding="utf-16")
    assert note.text == "override"
    assert note.encoding == "utf-16"
    assert note.lang == "en"

  def test_init_from_incorrect_element(self, note_elem_bad_attrib):
    note = Note._from_element(note_elem_bad_attrib)
    assert note.text == "test"
    assert note.encoding is None
    assert note.lang is None

  def test_init_from_incorrect_element_with_args(self, note_elem_bad_attrib):
    note = Note._from_element(note_elem_bad_attrib, text="override", encoding="utf-16")
    assert note.text == "override"
    assert note.encoding == "utf-16"
    assert note.lang is None

  def test_init_from_unknown_element(self, unknown_elem):
    with pytest.raises(ValueError):
      Note._from_element(unknown_elem)

  def testest_bad_bad_attrib(self, correct_note):
    note = correct_note
    with pytest.raises(TypeError):
      note.text = 1
    with pytest.raises(TypeError):
      note.encoding = 1
    with pytest.raises(TypeError):
      note.lang = 1

  def test_export_note_to_element(self, correct_note):
    note = correct_note
    el = Note._to_element(note)
    assert isinstance(el, et.Element)
    assert el.tag == "note"
    assert el.text == "test"
    assert el.attrib["o-encoding"] == "utf-8"
    assert el.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"

  def test_export_note_to_element_with_other_constructor(self, correct_note):
    note = correct_note
    el = Note._to_element(note, constructor=ET.Element)
    assert el.tag == "note"
    assert el.text == "test"
    assert el.attrib["o-encoding"] == "utf-8"
    assert el.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"
    assert isinstance(el, ET._Element)

  def test_export_note_to_element_with_incorrect_constructor(self, correct_note):
    note = correct_note
    with pytest.raises(TypeError):
      Note._to_element(note, constructor=1)
