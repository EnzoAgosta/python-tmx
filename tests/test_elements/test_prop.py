from xml.etree.ElementTree import Element as StdElement

import pytest
from lxml.etree import Element as LxmlElement

from PythonTmx.core import AnyElementFactory, AnyXmlElement
from PythonTmx.elements import Prop
from PythonTmx.errors import SerializationError, UnusableElementError


@pytest.mark.parametrize("ElementClass", [LxmlElement, StdElement])
class TestPropHappyPath:
  def test_from_xml_minimal(
    self, ElementClass: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementClass("prop", {"type": "foo"})
    el.text = "bar"
    prop = Prop.from_xml(el)
    assert prop.type == "foo"
    assert prop.text == "bar"
    assert prop.encoding is None
    assert prop.lang is None

  def test_from_xml_full(
    self, ElementClass: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementClass(
      "prop",
      {
        "type": "foo",
        "encoding": "utf-8",
        "{http://www.w3.org/XML/1998/namespace}lang": "en",
      },
    )
    el.text = "text"
    prop = Prop.from_xml(el)
    assert prop.type == "foo"
    assert prop.text == "text"
    assert prop.encoding == "utf-8"
    assert prop.lang == "en"

  def test_to_xml_roundtrip(
    self, ElementClass: AnyElementFactory[..., AnyXmlElement]
  ):
    prop = Prop(text="foobar", type="custom", encoding="base64", lang="fr")

    def factory(
      tag: str, attrib: dict[str, str], *_: object, **__: object
    ) -> AnyXmlElement:
      return ElementClass(tag, attrib)

    el = prop.to_xml(factory)
    assert el.tag == "prop"
    assert el.attrib["type"] == "custom"
    assert el.attrib["encoding"] == "base64"
    assert el.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "fr"


@pytest.mark.parametrize("ElementClass", [LxmlElement, StdElement])
class TestPropErrorPath:
  def test_wrong_tag(self, ElementClass: AnyElementFactory[..., AnyXmlElement]):
    el = ElementClass("notprop", {"type": "foo"})
    el.text = "bar"
    with pytest.raises(UnusableElementError) as excinfo:
      Prop.from_xml(el)
    assert "expected" in str(excinfo.value).lower()

  def test_missing_required_attrib_key(
    self, ElementClass: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementClass("prop", {})
    el.text = "foo"
    with pytest.raises(SerializationError) as excinfo:
      Prop.from_xml(el)
    assert isinstance(excinfo.value.original_exception, KeyError)

  def test_text_is_none(
    self, ElementClass: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementClass("prop", {"type": "foo"})
    with pytest.raises(SerializationError) as excinfo:
      Prop.from_xml(el)
    assert isinstance(excinfo.value.original_exception, ValueError)


# Malformed input tests use custom/fake classes, not standard XML elements.
class TestPropMalformedInputs:
  def test_missing_attrib_attribute(self):
    class NoAttrib:
      tag = "prop"
      text = "foo"
      tail = ""

      def __iter__(self):
        return iter([])

    el = NoAttrib()
    with pytest.raises(UnusableElementError) as excinfo:
      Prop.from_xml(el)  # type: ignore # This is supposed to fail
    assert excinfo.value.missing_field == "attrib"

  def test_attrib_not_mapping_like(self):
    class AttribNoGetitem:
      tag = "prop"
      text = "foo"
      tail = ""
      attrib = 1

      def __iter__(self):
        return iter([])
      
      def append(self, element: AnyXmlElement) -> None: ...

    el = AttribNoGetitem()
    with pytest.raises(UnusableElementError) as excinfo:
      Prop.from_xml(el)  # type: ignore # This is supposed to fail
    assert excinfo.value.missing_field == "attrib"

  def test_text_wrong_type(self):
    class WrongText:
      tag = "prop"
      text = 1234
      tail = ""
      attrib = {"type": "foo"}

      def __iter__(self):
        return iter([])

      def append(self, element: AnyXmlElement) -> None: ...

    el = WrongText()
    prop = Prop.from_xml(el)
    assert isinstance(prop, Prop)
    assert prop.text == 1234

  def test_attrib_is_weird_mapping(self):
    class CustomAttrib(dict[str, str]):
      def __getitem__(self, key: str):
        if key == "type":
          return "foo"
        raise KeyError(key)

    class WeirdAttrib:
      tag = "prop"
      text = "val"
      tail = ""
      attrib = CustomAttrib()

      def __iter__(self):
        return iter([])

      def append(self, element: AnyXmlElement) -> None: ...

    el = WeirdAttrib()
    prop = Prop.from_xml(el)
    assert prop.type == "foo"
    assert prop.text == "val"

  def test_not_iterable_method(self):
    class NoIter:
      tag = "prop"
      text = "foo"
      tail = ""
      attrib = {"type": "bar"}

    el = NoIter()
    with pytest.raises(UnusableElementError):
      Prop.from_xml(el)  # type: ignore # This is supposed to fail
