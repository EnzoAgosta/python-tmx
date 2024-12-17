import pytest
import xml.etree.ElementTree as et
import lxml.etree as ET

from PythonTmx.classes import Map


@pytest.fixture
def map_elem():
  el = et.Element("map")
  el.attrib["unicode"] = "#xF8FF"
  el.attrib["code"] = "#xF0"
  el.attrib["ent"] = "nbsp"
  el.attrib["subst"] = " "
  return el


@pytest.fixture
def map_elem_bad_attrib():
  el = et.Element("map")
  el.attrib["unicode"] = "#xF8FF"
  el.attrib["x-code"] = "#xF0"
  el.attrib["x-ent"] = "nbsp"
  el.attrib["subst"] = " "
  return el


@pytest.fixture
def unknown_elem():
  return et.Element("unknown")


@pytest.fixture
def correct_map():
  return Map(unicode="#xF8FF", code="#xF0", ent="nbsp", subst=" ")


class TestMap:
  def test_init(self):
    with pytest.raises(TypeError):
      Map()
    map = Map(unicode="#xF8FF", code="#xF0", ent="nbsp", subst=" ")
    assert map.unicode == "#xF8FF"
    assert map.code == "#xF0"
    assert map.ent == "nbsp"
    assert map.subst == " "

  def test_init_from_correct_element(self, map_elem):
    map = Map._from_element(map_elem)
    assert map.unicode == "#xF8FF"
    assert map.code == "#xF0"
    assert map.ent == "nbsp"
    assert map.subst == " "

  def test_init_from_correct_element_with_args(self, map_elem):
    map = Map._from_element(map_elem, unicode="#xF0FF", code="#xF00", ent="x", subst="")
    assert map.unicode == "#xF0FF"
    assert map.code == "#xF00"
    assert map.ent == "x"
    assert map.subst == ""

  def test_init_from_incorrect_element(self, map_elem_bad_attrib):
    map = Map._from_element(map_elem_bad_attrib)
    assert map.unicode == "#xF8FF"
    assert map.code is None
    assert map.ent is None
    assert map.subst == " "

  def test_bad_bad_attrib(self, correct_map):
    map = correct_map
    with pytest.raises(ValueError):
      map.unicode = "F8FF"
    with pytest.raises(TypeError):
      map.unicode = 1
    with pytest.raises(ValueError):
      map.code = "F0"
    with pytest.raises(TypeError):
      map.code = 1
    with pytest.raises(ValueError):
      map.ent = "Ä"
    with pytest.raises(TypeError):
      map.ent = 1
    with pytest.raises(ValueError):
      map.subst = "Ä"
    with pytest.raises(TypeError):
      map.subst = 1
