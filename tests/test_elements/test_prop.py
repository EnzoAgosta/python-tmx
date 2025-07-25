# type: ignore
from xml.etree.ElementTree import Element as StdElement

import pytest
from lxml.etree import Element as LxmlElement

from PythonTmx.core import AnyElementFactory, AnyXmlElement
from PythonTmx.elements import Prop
from PythonTmx.errors import (
  SerializationError,
  UnusableElementError,
  ValidationError,
)


class TestPropHappyPath:
  def test_from_xml_minimal(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("prop", {"type": "foo"})
    el.text = "bar"
    prop = Prop.from_xml(el)
    assert prop.type == "foo"
    assert prop.text == "bar"
    assert prop.encoding is None
    assert prop.lang is None

  def test_from_xml_full(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory(
      "prop",
      {
        "type": "foo",
        "encoding": "utf-8",
        "{http://www.w3.org/XML/1998/namespace}lang": "en",
      },
    )
    el.text = "bar"
    prop = Prop.from_xml(el)
    assert prop.type == "foo"
    assert prop.text == "bar"
    assert prop.encoding == "utf-8"
    assert prop.lang == "en"

  def test_to_xml_roundtrip(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    source_el = ElementFactory(
      "prop",
      {
        "type": "foo",
        "encoding": "utf-8",
        "{http://www.w3.org/XML/1998/namespace}lang": "en",
      },
    )
    source_el.text = "bar"
    prop = Prop.from_xml(source_el)

    return_el = prop.to_xml(ElementFactory)
    assert return_el.tag == "prop"
    assert return_el.attrib["type"] == "foo"
    assert return_el.attrib["encoding"] == "utf-8"
    assert (
      return_el.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"
    )


@pytest.mark.parametrize("ElementFactory", [LxmlElement, StdElement])
class TestPropErrorPath:
  def test_wrong_tag(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("notprop", {"type": "foo"})
    el.text = "bar"
    with pytest.raises(UnusableElementError) as excinfo:
      Prop.from_xml(el)
    assert "has a tag attribute with unexpected value" in str(excinfo.value)

  def test_missing_required_attrib_key(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("prop", {})
    el.text = "foo"
    with pytest.raises(SerializationError) as excinfo:
      Prop.from_xml(el)
    assert isinstance(excinfo.value.original_exception, KeyError)
    assert "Missing required attribute" in str(excinfo.value)

  def test_text_is_none(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("prop", {"type": "foo"})
    with pytest.raises(SerializationError) as excinfo:
      Prop.from_xml(el)
    assert isinstance(excinfo.value.original_exception, ValueError)
    assert "Unexpected or missing value encountered" in str(excinfo.value)

  def test_wrong_type(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    prop = Prop(text="foobar", type="custom", encoding="base64", lang="fr")
    prop.type = 1234
    with pytest.raises(ValidationError) as excinfo:
      prop.to_xml(ElementFactory)
    assert "Validation failed" in str(excinfo.value)
    assert excinfo.value.field == "type"
    assert excinfo.value.value == 1234

  def test_wrong_text_type(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    prop = Prop(text=1234, type="custom", encoding="base64", lang="fr")
    with pytest.raises(ValidationError) as excinfo:
      prop.to_xml(ElementFactory)
    assert "Validation failed" in str(excinfo.value)
    assert excinfo.value.field == "text"
    assert excinfo.value.value == 1234


# Malformed input tests use custom/fake classes, not standard XML elements.
class TestPropMalformedInputs:
  def test_missing_attrib_attribute(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(tag="prop", text="foo", tail="")
    with pytest.raises(UnusableElementError) as excinfo:
      Prop.from_xml(el)
    assert excinfo.value.missing_field == "attrib"

  def test_attrib_not_mapping_like(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(tag="prop", text="foo", tail="", attrib=1)
    with pytest.raises(UnusableElementError) as excinfo:
      Prop.from_xml(el)
    assert excinfo.value.missing_field == "attrib"

  def test_not_iterable(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(tag="prop", text="foo", tail="")
    temp = FakeAndBrokenElement.__iter__
    del FakeAndBrokenElement.__iter__
    with pytest.raises(UnusableElementError):
      Prop.from_xml(el)
    FakeAndBrokenElement.__iter__ = temp
