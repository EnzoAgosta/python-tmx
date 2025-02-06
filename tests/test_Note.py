import xml.etree.ElementTree as pyet

import lxml.etree as lxet
import pytest

from PythonTmx import ENGINE, Note


@pytest.fixture
def correct_elem_python():
  elem = pyet.Element("note")
  elem.text = "test"
  elem.set("{http://www.w3.org/XML/1998/namespace}lang", "en")
  elem.set("o-encoding", "utf-8")
  return elem


@pytest.fixture
def correct_elem_lxml():
  elem = lxet.Element("note")
  elem.text = "test"
  elem.set("{http://www.w3.org/XML/1998/namespace}lang", "en")
  elem.set("o-encoding", "utf-8")
  return elem


class TestNote:
  def test_init(self):
    note = Note(text="test", lang="en", encoding="utf-8")
    assert note.text == "test"
    assert note.lang == "en"
    assert note.encoding == "utf-8"

  def test_empy_init(self):
    with pytest.raises(TypeError):
      Note()

  def test_minimum_init(self):
    note = Note(text="test")
    assert note.text == "test"
    assert note.lang is None
    assert note.encoding is None

  def test_from_element_python(self, correct_elem_python):
    note = Note.from_element(correct_elem_python)
    assert note.text == "test" == correct_elem_python.text
    assert (
      note.lang
      == "en"
      == correct_elem_python.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    assert note.encoding == "utf-8" == correct_elem_python.attrib.get("o-encoding")

  def test_from_element_python_kwargs(self, correct_elem_python):
    note = Note.from_element(correct_elem_python, lang="es", encoding="utf-16")
    assert note.text == "test" == correct_elem_python.text
    assert (
      note.lang
      == "es"
      != correct_elem_python.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    assert note.encoding == "utf-16" != correct_elem_python.attrib.get("o-encoding")

  def test_from_element_lxml(self, correct_elem_lxml):
    note = Note.from_element(correct_elem_lxml)
    assert note.text == "test" == correct_elem_lxml.text
    assert (
      note.lang
      == "en"
      == correct_elem_lxml.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    assert note.encoding == "utf-8" == correct_elem_lxml.attrib.get("o-encoding")

  def test_from_element_lxml_kwargs(self, correct_elem_lxml):
    note = Note.from_element(correct_elem_lxml, lang="es", encoding="utf-16")
    assert note.text == "test" == correct_elem_lxml.text
    assert (
      note.lang
      == "es"
      != correct_elem_lxml.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    assert note.encoding == "utf-16" != correct_elem_lxml.attrib.get("o-encoding")

  def test_to_element_python(self, correct_elem_python):
    note = Note.from_element(correct_elem_python)
    note_elem = note.to_element(ENGINE.PYTHON)
    assert note_elem.tag == correct_elem_python.tag == "note"
    assert note_elem.text == correct_elem_python.text == "test"
    assert dict(note_elem.attrib) == correct_elem_python.attrib

  def test_to_element_python_kwargs(self, correct_elem_python):
    note = Note.from_element(correct_elem_python)
    note_elem = note.to_element(ENGINE.PYTHON, lang="es", encoding="utf-16")
    assert note_elem.tag == correct_elem_python.tag == "note"
    assert note_elem.text == correct_elem_python.text == "test"
    assert dict(note_elem.attrib) != dict(correct_elem_python.attrib)
    assert note_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "es"
    assert note_elem.attrib["o-encoding"] == "utf-16"

  def test_to_element_python_kwargs_add_extra(self, correct_elem_python):
    note = Note.from_element(correct_elem_python)
    note_elem = note.to_element(
      ENGINE.PYTHON, add_extra=True, lang="es", encoding="utf-16", extra="test"
    )
    assert note_elem.tag == correct_elem_python.tag == "note"
    assert note_elem.text == correct_elem_python.text == "test"
    assert dict(note_elem.attrib) != dict(correct_elem_python.attrib)
    assert note_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "es"
    assert note_elem.attrib["o-encoding"] == "utf-16"
    assert note_elem.attrib["extra"] == "test"

  def test_to_element_lxml(self, correct_elem_lxml):
    note = Note.from_element(correct_elem_lxml)
    note_elem = note.to_element(ENGINE.LXML)
    assert note_elem.tag == correct_elem_lxml.tag == "note"
    assert note_elem.text == correct_elem_lxml.text == "test"
    assert dict(note_elem.attrib) == dict(correct_elem_lxml.attrib)

  def test_to_element_lxml_kwargs_add_extra(self, correct_elem_lxml):
    note = Note.from_element(correct_elem_lxml)
    note_elem = note.to_element(
      ENGINE.LXML, add_extra=True, lang="es", encoding="utf-16", extra="test"
    )
    assert note_elem.tag == correct_elem_lxml.tag == "note"
    assert note_elem.text == correct_elem_lxml.text == "test"
    assert dict(note_elem.attrib) != dict(correct_elem_lxml.attrib)
    assert note_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "es"
    assert note_elem.attrib["o-encoding"] == "utf-16"
    assert note_elem.attrib["extra"] == "test"

  def test_to_element_lxml_kwargs(self, correct_elem_lxml):
    note = Note.from_element(correct_elem_lxml)
    note_elem = note.to_element(ENGINE.LXML, lang="es", encoding="utf-16")
    assert note_elem.tag == correct_elem_lxml.tag == "note"
    assert note_elem.text == correct_elem_lxml.text == "test"
    assert dict(note_elem.attrib) != dict(correct_elem_lxml.attrib)
    assert note_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "es"
    assert note_elem.attrib["o-encoding"] == "utf-16"

  def test_from_element_invalid(self):
    with pytest.raises(ValueError):
      Note.from_element(pyet.Element("test"))

  def test_incorrect_attrib_type_export(self):
    note = Note(text="test", lang="en", encoding=123)
    with pytest.raises(TypeError):
      note.to_element()

  def test_incorrect_text_export(self):
    note = Note(text=13)
    with pytest.raises(TypeError):
      note.to_element()

  def test_extra_attrib(self):
    with pytest.raises(TypeError):
      Note(text="test", lang="en", encoding="utf-8", extra="test")

  def test_extra_attrib_from_element_python(self, correct_elem_python):
    elem = correct_elem_python
    elem.set("extra", "test")
    note = Note.from_element(elem)
    assert hasattr(note, "extra") is False

  def test_extra_attrib_from_element_lxml(self, correct_elem_lxml):
    elem = correct_elem_lxml
    elem.set("extra", "test")
    note = Note.from_element(elem)
    assert hasattr(note, "extra") is False

  def test_wrong_engine(self):
    with pytest.raises(ValueError):
      Note(text="test").to_element("wrong")

  def test_engines(self):
    note = Note(text="test")
    assert isinstance(note.to_element(ENGINE.LXML), lxet._Element)
    assert isinstance(note.to_element(ENGINE.PYTHON), pyet.Element)
