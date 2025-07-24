from typing import Any

import pytest
from lxml.etree import Element

from PythonTmx.core import AnyXmlElement
from PythonTmx.elements import Prop
from PythonTmx.errors import MalFormedElementError, SerializationError


class TestPropHappyPath:
  def test_from_xml_minimal(self):
    el = Element("prop", type="foo")
    el.text = "bar"
    prop = Prop.from_xml(el)
    assert prop.type == "foo"
    assert prop.value == "bar"
    assert prop.encoding is None
    assert prop.lang is None

  def test_from_xml_full(self):
    el = Element("prop", type="hello", encoding="utf-8", lang="en")
    el.text = "text"
    prop = Prop.from_xml(el)
    assert prop.type == "hello"
    assert prop.value == "text"
    assert prop.encoding == "utf-8"
    assert prop.lang == "en"

  def test_to_xml_roundtrip(self):
    prop = Prop(value="foobar", type="custom", encoding="base64", lang="fr")

    # Use a dummy factory compatible with AnyElementFactory
    def factory(
      tag: str, attrib: dict[str, str], *_: Any, **__: Any
    ) -> AnyXmlElement:
      el = Element(tag, attrib)
      return el

    el = prop.to_xml(factory)
    assert el.tag == "prop"
    assert el.attrib["type"] == "custom"
    assert el.attrib["encoding"] == "base64"
    assert el.attrib["lang"] == "fr"


class TestPropErrorPath:
  def test_wrong_tag(self):
    el = Element("notprop", type="foo")
    el.text = "bar"
    # Wrong tag, should raise MalFormedElementError
    with pytest.raises(MalFormedElementError) as excinfo:
      Prop.from_xml(el)
    assert "expected" in str(excinfo.value).lower()

  def test_missing_required_attrib_key(self):
    el = Element("prop")
    el.text = "foo"
    # Missing required attribute, should raise SerializationError from a KeyError
    with pytest.raises(SerializationError) as excinfo:
      Prop.from_xml(el)
    assert isinstance(excinfo.value.original_exception, KeyError)

  def test_text_is_none(self):
    el = Element("prop", type="foo")
    # No text set, should raise SerializationError from a ValueError
    with pytest.raises(SerializationError) as excinfo:
      Prop.from_xml(el)
    assert isinstance(excinfo.value.original_exception, ValueError)


class TestPropMalformedInputs:
  def test_missing_attrib_attribute(self):
    class NoAttrib:
      attrib: Any  # Only as type hint to shut up Pylance
      tag = "prop"
      text = "foo"
      tail = ""

      def __iter__(self):
        return iter([])

      def __len__(self):
        return 0

    el = NoAttrib()
    with pytest.raises(MalFormedElementError) as excinfo:
      Prop.from_xml(el)
    assert excinfo.value.missing_field == "attrib"

  def test_attrib_not_mapping_like(self):
    class AttribNoGetitem:
      tag = "prop"
      text = "foo"
      tail = ""
      attrib = object()  # No __getitem__

      def __iter__(self):
        return iter([])

      def __len__(self):
        return 0

    el = AttribNoGetitem()
    with pytest.raises(MalFormedElementError) as excinfo:
      Prop.from_xml(el)
    assert excinfo.value.missing_field == "attrib"

  def test_text_wrong_type(self):
    class WrongText:
      tag = "prop"
      text = 1234  # Int instead of str
      tail = ""
      attrib = {"type": "foo"}

      def __iter__(self):
        return iter([])

      def __len__(self):
        return 0

    el = WrongText()
    # We only type check on export so should NOT raise at structure check
    prop = Prop.from_xml(el)
    assert isinstance(prop, Prop)
    assert prop.value == 1234

  def test_attrib_is_weird_mapping(self):
    class CustomAttrib(dict[str, str]):
      def __getitem__(self, key: str):  # Force a KeyError
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

      def __len__(self):
        return 0

    el = WeirdAttrib()
    prop = Prop.from_xml(el)
    assert prop.type == "foo"
    assert prop.value == "val"

  def test_missing_iter_method(self):
    class NoIter:
      tag = "prop"
      text = "foo"
      tail = ""
      attrib = {"type": "bar"}

      def __len__(self):
        return 0

    el = NoIter()
    with pytest.raises(MalFormedElementError) as excinfo:
      Prop.from_xml(el)  # type: ignore # Shutting up Pylance
    assert excinfo.value.missing_field == "__iter__"

  def test_missing_len_method(self):
    class NoLen:
      tag = "prop"
      text = "foo"
      tail = ""
      attrib = {"type": "bar"}

      def __iter__(self):
        return iter([])

    el = NoLen()
    with pytest.raises(MalFormedElementError) as excinfo:
      Prop.from_xml(el)  # type: ignore # Shutting up Pylance
    assert excinfo.value.missing_field == "__len__"
