import pytest
import xml.etree.ElementTree as et
import lxml.etree as ET
from PythonTmx.classes import Prop


@pytest.fixture
def prop_elem():
  el = et.Element("prop")
  el.text = "test"
  el.attrib["type"] = "x-test"
  el.attrib["o-encoding"] = "utf-8"
  el.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "en"
  return el


@pytest.fixture
def prop_elem_bad_attrib():
  el = et.Element("prop")
  el.text = "test"
  el.attrib["encoding"] = "utf-8"
  el.attrib["lang"] = "en"
  el.attrib["type"] = "x-test"
  return el


@pytest.fixture
def unknown_elem():
  return et.Element("unknown")


@pytest.fixture
def correct_prop():
  return Prop(text="test", type="x-test", encoding="utf-8", lang="en")


class TestProp:
  def test_init(self):
    with pytest.raises(TypeError):
      Prop()
    prop = Prop(text="test", type="x-test", encoding="utf-8", lang="en")
    assert prop.text == "test"
    assert prop.type == "x-test"
    assert prop.encoding == "utf-8"
    assert prop.lang == "en"

  def test_init_from_correct_element(self, prop_elem):
    prop = Prop._from_element(prop_elem)
    assert prop.text == "test"
    assert prop.type == "x-test"
    assert prop.encoding == "utf-8"
    assert prop.lang == "en"

  def test_init_from_correct_element_with_args(self, prop_elem):
    prop = Prop._from_element(prop_elem, text="override", type="x-override")
    assert prop.text == "override"
    assert prop.type == "x-override"
    assert prop.encoding == "utf-8"
    assert prop.lang == "en"

  def test_init_from_incorrect_element(self, prop_elem_bad_attrib):
    prop = Prop._from_element(prop_elem_bad_attrib)
    assert prop.text == "test"
    assert prop.type == "x-test"
    assert prop.encoding is None
    assert prop.lang is None

  def test_init_from_unknown_element(self, unknown_elem):
    with pytest.raises(ValueError):
      Prop._from_element(unknown_elem)

  def test_eq(self, correct_prop, prop_elem):
    assert correct_prop == Prop._from_element(prop_elem)

  def test_neq(self):
    prop1 = Prop(text="test", type="x-test", encoding="utf-8", lang="en")
    prop2 = Prop(text="test2", type="x-test", encoding="utf-8", lang="en")
    assert prop1 != prop2

  def test_init_incorrect_types(self):
    with pytest.raises(TypeError):
      Prop(text=1, type="x-test", encoding="utf-8", lang="en")
    with pytest.raises(TypeError):
      Prop(text="test", type=1, encoding="utf-8", lang="en")
    with pytest.raises(TypeError):
      Prop(text="test", type="x-test", encoding=1, lang="en")
    with pytest.raises(TypeError):
      Prop(text="test", type="x-test", encoding="utf-8", lang=1)

  def test_update_incorrect_type(self, correct_prop):
    prop = correct_prop
    with pytest.raises(TypeError):
      prop.text = 1

  def test_export_prop_to_element(self, correct_prop):
    prop = correct_prop
    el = Prop._to_element(prop)
    assert isinstance(el, et.Element)
    assert el.tag == "prop"
    assert el.text == "test"
    assert el.attrib["type"] == "x-test"
    assert el.attrib["o-encoding"] == "utf-8"
    assert el.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"

  def test_export_prop_to_element_with_other_constructor(self, correct_prop):
    prop = correct_prop
    el = Prop._to_element(prop, constructor=ET.Element)
    assert el.tag == "prop"
    assert el.text == "test"
    assert el.attrib["type"] == "x-test"
    assert el.attrib["o-encoding"] == "utf-8"
    assert el.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"
    assert isinstance(el, ET._Element)
