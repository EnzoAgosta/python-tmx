import xml.etree.ElementTree as pyet

import lxml.etree as lxet
import pytest

from PythonTmx import ENGINE, Prop


@pytest.fixture
def correct_elem_python():
  elem = pyet.Element("prop")
  elem.text = "test"
  elem.set("{http://www.w3.org/XML/1998/namespace}lang", "en")
  elem.set("o-encoding", "utf-8")
  elem.set("type", "x-test")
  return elem


@pytest.fixture
def correct_elem_lxml():
  elem = lxet.Element("prop")
  elem.text = "test"
  elem.set("{http://www.w3.org/XML/1998/namespace}lang", "en")
  elem.set("o-encoding", "utf-8")
  elem.set("type", "x-test")
  return elem


class TestProp:
  def test_init(self):
    prop = Prop(text="test", lang="en", encoding="utf-8", type="x-test")
    assert prop.text == "test"
    assert prop.lang == "en"
    assert prop.encoding == "utf-8"
    assert prop.type == "x-test"

  def test_empy_init(self):
    with pytest.raises(TypeError):
      Prop()

  def test_minimum_init(self):
    prop = Prop(text="test", type="x-test")
    assert prop.text == "test"
    assert prop.type == "x-test"
    assert prop.lang is None
    assert prop.encoding is None

  def test_from_element_python(self, correct_elem_python):
    prop = Prop.from_element(correct_elem_python)
    assert prop.text == "test" == correct_elem_python.text
    assert (
      prop.lang
      == "en"
      == correct_elem_python.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    assert prop.encoding == "utf-8" == correct_elem_python.attrib.get("o-encoding")
    assert prop.type == "x-test" == correct_elem_python.attrib.get("type")

  def test_from_element_python_kwargs(self, correct_elem_python):
    prop = Prop.from_element(
      correct_elem_python, lang="es", encoding="utf-16", type="x-test2"
    )
    assert prop.text == "test" == correct_elem_python.text
    assert (
      prop.lang
      == "es"
      != correct_elem_python.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    assert prop.encoding == "utf-16" != correct_elem_python.attrib.get("o-encoding")
    assert prop.type == "x-test2" != correct_elem_python.attrib.get("type")

  def test_from_element_lxml(self, correct_elem_lxml):
    prop = Prop.from_element(correct_elem_lxml)
    assert prop.text == "test" == correct_elem_lxml.text
    assert (
      prop.lang
      == "en"
      == correct_elem_lxml.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    assert prop.encoding == "utf-8" == correct_elem_lxml.attrib.get("o-encoding")
    assert prop.type == "x-test" == correct_elem_lxml.attrib.get("type")

  def test_from_element_lxml_kwargs(self, correct_elem_lxml):
    prop = Prop.from_element(
      correct_elem_lxml, lang="es", encoding="utf-16", type="x-test2"
    )
    assert prop.text == "test" == correct_elem_lxml.text
    assert (
      prop.lang
      == "es"
      != correct_elem_lxml.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    )
    assert prop.encoding == "utf-16" != correct_elem_lxml.attrib.get("o-encoding")
    assert prop.type == "x-test2" != correct_elem_lxml.attrib.get("type")

  def test_to_element_python(self, correct_elem_python):
    prop = Prop.from_element(correct_elem_python)
    prop_elem = prop.to_element(ENGINE.PYTHON)
    assert prop_elem.tag == correct_elem_python.tag == "prop"
    assert prop_elem.text == correct_elem_python.text == "test"
    assert dict(prop_elem.attrib) == correct_elem_python.attrib

  def test_to_element_python_kwargs(self, correct_elem_python):
    prop = Prop.from_element(correct_elem_python)
    prop_elem = prop.to_element(
      ENGINE.PYTHON, lang="es", encoding="utf-16", type="x-test2"
    )
    assert prop_elem.tag == correct_elem_python.tag == "prop"
    assert prop_elem.text == correct_elem_python.text == "test"
    assert dict(prop_elem.attrib) != dict(correct_elem_python.attrib)
    assert prop_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "es"
    assert prop_elem.attrib["o-encoding"] == "utf-16"
    assert prop_elem.attrib["type"] == "x-test2"

  def test_to_element_python_kwargs_add_extra(self, correct_elem_python):
    prop = Prop.from_element(correct_elem_python)
    prop_elem = prop.to_element(
      ENGINE.PYTHON,
      add_extra=True,
      lang="es",
      encoding="utf-16",
      extra="test",
      type="x-test2",
    )
    assert prop_elem.tag == correct_elem_python.tag == "prop"
    assert prop_elem.text == correct_elem_python.text == "test"
    assert dict(prop_elem.attrib) != dict(correct_elem_python.attrib)
    assert prop_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "es"
    assert prop_elem.attrib["o-encoding"] == "utf-16"
    assert prop_elem.attrib["extra"] == "test"
    assert prop_elem.attrib["type"] == "x-test2"

  def test_to_element_lxml(self, correct_elem_lxml):
    prop = Prop.from_element(correct_elem_lxml)
    prop_elem = prop.to_element(ENGINE.LXML)
    assert prop_elem.tag == correct_elem_lxml.tag == "prop"
    assert prop_elem.text == correct_elem_lxml.text == "test"
    assert dict(prop_elem.attrib) == dict(correct_elem_lxml.attrib)

  def test_to_element_lxml_kwargs_add_extra(self, correct_elem_lxml):
    prop = Prop.from_element(correct_elem_lxml)
    prop_elem = prop.to_element(
      ENGINE.LXML,
      add_extra=True,
      lang="es",
      encoding="utf-16",
      extra="test",
      type="x-test2",
    )
    assert prop_elem.tag == correct_elem_lxml.tag == "prop"
    assert prop_elem.text == correct_elem_lxml.text == "test"
    assert dict(prop_elem.attrib) != dict(correct_elem_lxml.attrib)
    assert prop_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "es"
    assert prop_elem.attrib["o-encoding"] == "utf-16"
    assert prop_elem.attrib["extra"] == "test"
    assert prop_elem.attrib["type"] == "x-test2"

  def test_to_element_lxml_kwargs(self, correct_elem_lxml):
    prop = Prop.from_element(correct_elem_lxml)
    prop_elem = prop.to_element(
      ENGINE.LXML, lang="es", encoding="utf-16", type="x-test2"
    )
    assert prop_elem.tag == correct_elem_lxml.tag == "prop"
    assert prop_elem.text == correct_elem_lxml.text == "test"
    assert dict(prop_elem.attrib) != dict(correct_elem_lxml.attrib)
    assert prop_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "es"
    assert prop_elem.attrib["o-encoding"] == "utf-16"
    assert prop_elem.attrib["type"] == "x-test2"

  def test_from_element_invalid(self):
    with pytest.raises(ValueError):
      Prop.from_element(pyet.Element("test"))

  def test_incorrect_attrib_type_export(self):
    prop = Prop(text="test", type=123)
    with pytest.raises(TypeError):
      prop.to_element()

  def test_incorrect_text_export(self):
    prop = Prop(text=13, type="123")
    with pytest.raises(TypeError):
      prop.to_element()

  def test_extra_attrib(self):
    with pytest.raises(TypeError):
      Prop(text="test", lang="en", encoding="utf-8", extra="test", type="x-test")

  def test_extra_attrib_from_element_python(self, correct_elem_python):
    elem = correct_elem_python
    elem.set("extra", "test")
    prop = Prop.from_element(elem)
    assert hasattr(prop, "extra") is False

  def test_extra_attrib_from_element_lxml(self, correct_elem_lxml):
    elem = correct_elem_lxml
    elem.set("extra", "test")
    prop = Prop.from_element(elem)
    assert hasattr(prop, "extra") is False

  def test_wrong_engine(self):
    with pytest.raises(ValueError):
      Prop(text="test", type="123").to_element("wrong")

  def test_engines(self):
    prop = Prop(text="test", type="123")
    assert isinstance(prop.to_element(ENGINE.LXML), lxet._Element)
    assert isinstance(prop.to_element(ENGINE.PYTHON), pyet.Element)
