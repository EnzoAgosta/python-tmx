from xml.etree.ElementTree import Element as StdElement

import pytest
from lxml.etree import Element as LxmlElement

from PythonTmx.core import AnyElementFactory, AnyXmlElement
from PythonTmx.elements import Note
from PythonTmx.errors import SerializationError, UnusableElementError


@pytest.mark.parametrize("ElementClass", [LxmlElement, StdElement])
class TestNoteHappyPath:
  def test_from_xml_minimal(
    self, ElementClass: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementClass("note", {})
    el.text = "hello"
    note = Note.from_xml(el)
    assert note.value == "hello"
    assert note.lang is None

  def test_from_xml_full(
    self, ElementClass: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementClass(
      "note",
      {"{http://www.w3.org/XML/1998/namespace}lang": "fr"},
    )
    el.text = "bonjour"
    note = Note.from_xml(el)
    assert note.value == "bonjour"
    assert note.lang == "fr"

  def test_to_xml_roundtrip(
    self, ElementClass: AnyElementFactory[..., AnyXmlElement]
  ):
    note = Note(value="Hello, world!", lang="es")

    def factory(
      tag: str, attrib: dict[str, str], *_: object, **__: object
    ) -> AnyXmlElement:
      return ElementClass(tag, attrib)

    el = note.to_xml(factory)
    assert el.tag == "note"
    assert el.text == "Hello, world!"
    assert el.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "es"


@pytest.mark.parametrize("ElementClass", [LxmlElement, StdElement])
class TestNoteErrorPath:
  def test_wrong_tag(self, ElementClass: AnyElementFactory[..., AnyXmlElement]):
    el = ElementClass("notnote", {})
    el.text = "should fail"
    with pytest.raises(UnusableElementError) as excinfo:
      Note.from_xml(el)
    assert "expected" in str(excinfo.value).lower()

  def test_missing_text(
    self, ElementClass: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementClass("note", {})
    # No text set
    with pytest.raises(SerializationError) as excinfo:
      Note.from_xml(el)
    assert isinstance(excinfo.value.original_exception, ValueError)


class TestNoteMalformedInputs:
  def test_missing_attrib_attribute(self):
    class NoAttrib:
      tag = "note"
      text = "foo"
      tail = ""

      def __iter__(self):
        return iter([])

    el = NoAttrib()
    with pytest.raises(UnusableElementError) as excinfo:
      Note.from_xml(el)  # type: ignore # This is supposed to fail
    assert excinfo.value.missing_field == "attrib"

  def test_not_iterable(self):
    class NoIter:
      tag = "note"
      text = "foo"
      tail = ""
      attrib = {}

    el = NoIter()
    with pytest.raises(UnusableElementError):
      Note.from_xml(el)  # type: ignore # This is supposed to fail

  def test_text_wrong_type(self):
    class WrongText:
      tag = "note"
      text = 1234
      tail = ""
      attrib = {}

      def __iter__(self):
        return iter([])

    el = WrongText()
    note = Note.from_xml(el)
    assert isinstance(note, Note)
    assert note.value == 1234

  def test_lang_attribute_present(self):
    class WithLang:
      tag = "note"
      text = "salut"
      tail = ""
      attrib = {"{http://www.w3.org/XML/1998/namespace}lang": "fr"}

      def __iter__(self):
        return iter([])

    el = WithLang()
    note = Note.from_xml(el)
    assert note.lang == "fr"
    assert note.value == "salut"
