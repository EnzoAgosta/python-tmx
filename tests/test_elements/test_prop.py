# type: ignore
import pytest

from PythonTmx.elements.prop import Prop
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  RequiredAttributeMissingError,
  SerializationError,
  ValidationError,
  WrongTagError,
)


def test_create_minimal_prop():
  prop = Prop("some text", "property type")
  assert prop.text == "some text"
  assert prop.type == "property type"
  assert prop.encoding is None
  assert prop.lang is None


def test_create_prop_full():
  prop = Prop("some text", "property type", encoding="utf-8", lang="en")
  assert prop.text == "some text"
  assert prop.type == "property type"
  assert prop.encoding == "utf-8"
  assert prop.lang == "en"


def test_prop_from_minimal_xml(ElementFactory):
  element = ElementFactory("prop", {"type": "test"})
  element.text = "test text"
  prop = Prop.from_xml(element)
  assert prop.text == "test text"
  assert prop.type == "test"
  assert prop.encoding is None
  assert prop.lang is None


def test_prop_from_full_xml(ElementFactory):
  element = ElementFactory(
    "prop",
    {
      "type": "test",
      "o-encoding": "utf-8",
      "{http://www.w3.org/XML/1998/namespace}lang": "en",
    },
  )
  element.text = "test text"
  prop = Prop.from_xml(element)
  assert prop.text == "test text"
  assert prop.type == "test"
  assert prop.encoding == "utf-8"
  assert prop.lang == "en"


def test_prop_from_xml_missing_text(CustomElementLike):
  element = CustomElementLike("prop", {"type": "test"})
  with pytest.raises(SerializationError) as e:
    Prop.from_xml(element)
  assert e.value.tmx_element is Prop
  assert isinstance(e.value.__cause__, RequiredAttributeMissingError)


def test_prop_from_xml_unusable_attrib(CustomElementLike):
  element = CustomElementLike(tag="prop", text="text", attrib=object())
  with pytest.raises(SerializationError) as e:
    Prop.from_xml(element)
  assert e.value.tmx_element is Prop
  assert isinstance(e.value.__cause__, NotMappingLikeError)


def test_prop_to_xml_minimal(ElementFactory):
  prop = Prop("test text", "test type")
  element = prop.to_xml(ElementFactory)
  assert element.tag == "prop"
  assert element.text == "test text"
  assert element.attrib["type"] == "test type"
  assert "o-encoding" not in element.attrib
  assert "{http://www.w3.org/XML/1998/namespace}lang" not in element.attrib


def test_prop_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("notprop", {})
  with pytest.raises(SerializationError) as e:
    Prop.from_xml(element)
  assert e.value.tmx_element is Prop
  assert isinstance(e.value.__cause__, WrongTagError)


def test_prop_to_xml_full(ElementFactory):
  prop = Prop("test text", "test type", encoding="utf-8", lang="en")
  element = prop.to_xml(ElementFactory)
  assert element.tag == "prop"
  assert element.text == "test text"
  assert element.attrib["type"] == "test type"
  assert element.attrib["o-encoding"] == "utf-8"
  assert element.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"


def test_prop_validation_errors(ElementFactory):
  prop = Prop("text", "type")
  prop.type = 123
  with pytest.raises(DeserializationError) as e:
    prop.to_xml(ElementFactory)
  assert e.value.tmx_element is prop
  assert isinstance(e.value.__cause__, ValidationError)
