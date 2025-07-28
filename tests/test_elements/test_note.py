# type: ignore
import pytest

from PythonTmx.elements.note import Note
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  RequiredAttributeMissingError,
  SerializationError,
  ValidationError,
  WrongTagError,
)


def test_create_minimal_note():
  note = Note("some text")
  assert note.text == "some text"
  assert note.encoding is None
  assert note.lang is None


def test_create_note_full():
  note = Note("some text", encoding="utf-8", lang="en")
  assert note.text == "some text"
  assert note.encoding == "utf-8"
  assert note.lang == "en"


def test_note_from_minimal_xml(ElementFactory):
  element = ElementFactory("note", {})
  element.text = "test text"
  note = Note.from_xml(element)
  assert note.text == "test text"
  assert note.encoding is None
  assert note.lang is None


def test_note_from_full_xml(ElementFactory):
  element = ElementFactory(
    "note",
    {
      "o-encoding": "utf-8",
      "{http://www.w3.org/XML/1998/namespace}lang": "en",
    },
  )
  element.text = "test text"
  note = Note.from_xml(element)
  assert note.text == "test text"
  assert note.encoding == "utf-8"
  assert note.lang == "en"


def test_note_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("notnote", {})
  with pytest.raises(SerializationError) as e:
    Note.from_xml(element)
  assert e.value.tmx_element is Note
  assert isinstance(e.value.__cause__, WrongTagError)


def test_note_from_xml_missing_text(CustomElementLike):
  element = CustomElementLike("note", {})
  with pytest.raises(SerializationError) as e:
    Note.from_xml(element)
  assert e.value.tmx_element is Note
  assert isinstance(e.value.__cause__, RequiredAttributeMissingError)


def test_note_from_xml_unusable_attrib(CustomElementLike):
  element = CustomElementLike(tag="note", text="text", attrib=object())
  with pytest.raises(SerializationError) as e:
    Note.from_xml(element)
  assert e.value.tmx_element is Note
  assert isinstance(e.value.__cause__, NotMappingLikeError)


def test_note_to_xml_minimal(ElementFactory):
  note = Note("test text")
  element = note.to_xml(ElementFactory)
  assert element.tag == "note"
  assert element.text == "test text"
  assert "o-encoding" not in element.attrib
  assert "{http://www.w3.org/XML/1998/namespace}lang" not in element.attrib


def test_note_to_xml_full(ElementFactory):
  note = Note("test text", encoding="utf-8", lang="en")
  element = note.to_xml(ElementFactory)
  assert element.tag == "note"
  assert element.text == "test text"
  assert element.attrib["o-encoding"] == "utf-8"
  assert element.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"


def test_note_validation_errors(ElementFactory):
  note = Note("text", "utf-8")
  note.encoding = 123
  with pytest.raises(DeserializationError) as e:
    note.to_xml(ElementFactory)
  assert e.value.tmx_element is note
  assert isinstance(e.value.__cause__, ValidationError)
