# type: ignore
import pytest

from PythonTmx.elements.map import Map
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  SerializationError,
  ValidationError,
  WrongTagError,
)


def test_create_minimal_map():
  map = Map(unicode="test")
  assert map.unicode == "test"
  assert map.code is None
  assert map.ent is None
  assert map.subst is None


def test_create_map_full():
  map = Map(unicode="test", code="code", ent="ent", subst="subst")
  assert map.unicode == "test"
  assert map.code == "code"
  assert map.ent == "ent"
  assert map.subst == "subst"


def test_map_from_minimal_xml(ElementFactory):
  element = ElementFactory("map", {"unicode": "00A0"})
  map = Map.from_xml(element)
  assert map.unicode == "00A0"
  assert map.code is None
  assert map.ent is None
  assert map.subst is None


def test_map_from_full_xml(ElementFactory):
  element = ElementFactory(
    "map",
    {
      "unicode": "00A9",
      "code": "&#169;",
      "ent": "&copy;",
      "subst": "(c)",
    },
  )
  map = Map.from_xml(element)
  assert map.unicode == "00A9"
  assert map.code == "&#169;"
  assert map.ent == "&copy;"
  assert map.subst == "(c)"


def test_map_from_xml_extra_text(CustomElementLike):
  element = CustomElementLike("map", {"unicode": "00A0"}, text="extra text")
  with pytest.raises(SerializationError) as e:
    Map.from_xml(element)
  assert e.value.tmx_element is Map
  assert isinstance(e.value.__cause__, ValueError)


def test_map_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("notmap", {})
  with pytest.raises(SerializationError) as e:
    Map.from_xml(element)
  assert e.value.tmx_element is Map
  assert isinstance(e.value.__cause__, WrongTagError)


def test_map_from_xml_unusable_attrib(CustomElementLike):
  element = CustomElementLike(tag="map", text="text", attrib=object())
  with pytest.raises(SerializationError) as e:
    Map.from_xml(element)
  assert e.value.tmx_element is Map
  assert isinstance(e.value.__cause__, NotMappingLikeError)


def test_map_to_xml_minimal(ElementFactory):
  map = Map("test")
  element = map.to_xml(ElementFactory)
  assert element.tag == "map"
  assert element.text is None
  assert element.attrib["unicode"] == "test"
  assert "code" not in element.attrib
  assert "ent" not in element.attrib
  assert "subst" not in element.attrib


def test_map_to_xml_full(ElementFactory):
  map = Map(unicode="test", code="code", ent="ent", subst="subst")
  element = map.to_xml(ElementFactory)
  assert element.tag == "map"
  assert element.text is None
  assert element.attrib["unicode"] == "test"
  assert element.attrib["code"] == "code"
  assert element.attrib["ent"] == "ent"
  assert element.attrib["subst"] == "subst"


def test_note_validation_errors(ElementFactory):
  map = Map("test")
  map.unicode = 123
  with pytest.raises(DeserializationError) as e:
    map.to_xml(ElementFactory)
  assert e.value.tmx_element is map
  assert isinstance(e.value.__cause__, ValidationError)
