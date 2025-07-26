# type: ignore
from xml.etree.ElementTree import Element as StdElement

import pytest
from lxml.etree import Element as LxmlElement

from PythonTmx.core import AnyElementFactory, AnyXmlElement
from PythonTmx.elements import Note
from PythonTmx.errors import (
  SerializationError,
  UnusableElementError,
  ValidationError,
)


class TestNoteHappyPath:
  def test_from_xml_minimal(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("note", {"type": "foo"})
    el.text = "bar"
    note = Note.from_xml(el)
    assert note.text == "bar"
    assert note.encoding is None
    assert note.lang is None

  def test_from_xml_full(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory(
      "note",
      {
        "type": "foo",
        "o-encoding": "utf-8",
        "{http://www.w3.org/XML/1998/namespace}lang": "en",
      },
    )
    el.text = "bar"
    note = Note.from_xml(el)
    assert note.text == "bar"
    assert note.encoding == "utf-8"
    assert note.lang == "en"

  def test_to_xml_roundtrip(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    source_el = ElementFactory(
      "note",
      {
        "o-encoding": "utf-8",
        "{http://www.w3.org/XML/1998/namespace}lang": "en",
      },
    )
    source_el.text = "bar"
    note = Note.from_xml(source_el)

    return_el = note.to_xml(ElementFactory)
    assert return_el.tag == "note"
    assert return_el.attrib["o-encoding"] == "utf-8"
    assert (
      return_el.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"
    )


@pytest.mark.parametrize("ElementFactory", [LxmlElement, StdElement])
class TestNoteErrorPath:
  def test_wrong_tag(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("notnote", {})
    el.text = "bar"
    with pytest.raises(UnusableElementError) as excinfo:
      Note.from_xml(el)
    assert "has a tag attribute with unexpected value" in str(excinfo.value)

  def test_text_is_none(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("note", {})
    with pytest.raises(SerializationError) as excinfo:
      Note.from_xml(el)
    assert isinstance(excinfo.value.original_exception, ValueError)
    assert "Unexpected or missing value encountered" in str(excinfo.value)

  def test_wrong_text_type(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    note = Note(text=1234, encoding="base64", lang="fr")
    with pytest.raises(ValidationError) as excinfo:
      note.to_xml(ElementFactory)
    assert "Validation failed" in str(excinfo.value)
    assert excinfo.value.field == "text"
    assert excinfo.value.value == 1234


# Malformed input tests use custom/fake classes, not standard XML elements.
class TestNoteMalformedInputs:
  def test_missing_attrib_attribute(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(tag="note", text="foo", tail="")
    with pytest.raises(UnusableElementError) as excinfo:
      Note.from_xml(el)
    assert excinfo.value.missing_field == "attrib"

  def test_attrib_not_mapping_like(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(tag="note", text="foo", tail="", attrib=1)
    with pytest.raises(UnusableElementError) as excinfo:
      Note.from_xml(el)
    assert excinfo.value.missing_field == "attrib"

  def test_not_iterable(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(tag="note", text="foo", tail="")
    temp = FakeAndBrokenElement.__iter__
    del FakeAndBrokenElement.__iter__
    with pytest.raises(UnusableElementError):
      Note.from_xml(el)
    FakeAndBrokenElement.__iter__ = temp
