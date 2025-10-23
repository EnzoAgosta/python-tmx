import lxml.etree as et

from python_tmx.base.classes import Prop
from python_tmx.xml.converters import parse_prop


def test_parse_prop_from_full_element(full_prop_lxml_elem: et._Element):
  prop = parse_prop(full_prop_lxml_elem)
  assert isinstance(prop, Prop)
  assert prop.content == full_prop_lxml_elem.text
  assert prop.type == full_prop_lxml_elem.attrib["type"]
  assert prop.lang == full_prop_lxml_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
  assert prop.o_encoding == full_prop_lxml_elem.attrib["o-encoding"]


def test_parse_prop_from_minimal_element(minimal_prop_lxml_elem: et._Element):
  prop = parse_prop(minimal_prop_lxml_elem)
  assert isinstance(prop, Prop)
  assert prop.lang is None
  assert prop.o_encoding is None
  assert prop.type == minimal_prop_lxml_elem.attrib["type"]
  assert prop.content == minimal_prop_lxml_elem.text


def test_parse_prop_with_empty_text_returns_empty_string(full_prop_lxml_elem: et._Element):
  full_prop_lxml_elem.text = None
  prop = parse_prop(full_prop_lxml_elem)
  assert prop.content == ""


def test_parse_prop_missing_type_sets_empty_string(full_prop_lxml_elem: et._Element):
  del full_prop_lxml_elem.attrib["type"]
  prop = parse_prop(full_prop_lxml_elem)
  assert prop.type == ""


def test_parse_prop_ignores_extra_attributes(full_prop_lxml_elem: et._Element):
  full_prop_lxml_elem.attrib["extra"] = "ignore me"
  parse_prop(full_prop_lxml_elem)
