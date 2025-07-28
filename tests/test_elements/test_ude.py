# type: ignore
import pytest

from PythonTmx.elements.map import Map
from PythonTmx.elements.ude import Ude
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  SerializationError,
  ValidationError,
  WrongTagError,
)


def test_create_minimal_ude():
  ude = Ude("name")
  assert ude.name == "name"
  assert ude.base is None
  assert isinstance(ude.maps, list) and len(ude.maps) == 0


def test_create_ude_full():
  map = Map(unicode="00A0")
  ude = Ude(name="name", base="base", maps=[map])
  assert ude.name == "name"
  assert ude.base == "base"
  assert isinstance(ude.maps, list) and len(ude.maps) == 1
  assert ude.maps[0] == map


def test_ude_from_minimal_xml(ElementFactory):
  element = ElementFactory("ude", {"name": "name"})
  ude = Ude.from_xml(element)
  assert ude.name == "name"
  assert ude.base is None
  assert isinstance(ude.maps, list) and len(ude.maps) == 0


def test_ude_from_full_xml(ElementFactory):
  map1 = ElementFactory("map", {"unicode": "00A0"})
  map2 = ElementFactory("map", {"unicode": "00A9", "code": "&#169;"})
  element = ElementFactory(
    "ude",
    {
      "name": "name",
      "base": "base",
    },
  )
  element.append(map1)
  element.append(map2)
  ude = Ude.from_xml(element)
  assert ude.name == "name"
  assert ude.base == "base"
  assert isinstance(ude.maps, list) and len(ude.maps) == 2
  assert ude.maps[0].unicode == "00A0"
  assert ude.maps[1].unicode == "00A9"
  assert ude.maps[1].code == "&#169;"


def test_ude_from_xml_extra_text(CustomElementLike):
  element = CustomElementLike("ude", {"name": "name"}, text="extra text")
  with pytest.raises(SerializationError) as e:
    Ude.from_xml(element)
  assert e.value.tmx_element is Ude
  assert isinstance(e.value.__cause__, ValueError)


def test_ude_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("notude", {})
  with pytest.raises(SerializationError) as e:
    Ude.from_xml(element)
  assert e.value.tmx_element is Ude
  assert isinstance(e.value.__cause__, WrongTagError)


def test_ude_from_xml_unusable_attrib(CustomElementLike):
  element = CustomElementLike(tag="ude", attrib=object(), text=None)
  with pytest.raises(SerializationError) as e:
    Ude.from_xml(element)
  assert e.value.tmx_element is Ude
  assert isinstance(e.value.__cause__, NotMappingLikeError)


def test_ude_to_xml_minimal(ElementFactory):
  ude = Ude("test")
  element = ude.to_xml(ElementFactory)
  assert element.tag == "ude"
  assert element.text is None
  assert element.attrib["name"] == "test"
  assert "base" not in element.attrib
  children = [c for c in element]
  assert len(children) == 0


def test_ude_to_xml_full(ElementFactory):
  ude = Ude(
    name="name", base="base", maps=[Map(unicode="map1"), Map(unicode="map2")]
  )
  element = ude.to_xml(ElementFactory)
  assert element.tag == "ude"
  assert element.text is None
  assert element.attrib["name"] == "name"
  assert element.attrib["base"] == "base"
  children = [c for c in element]
  assert len(children) == 2
  child_tags = [c.tag for c in element]
  assert child_tags == ["map", "map"]
  assert children[0].attrib["unicode"] == "map1"
  assert children[1].attrib["unicode"] == "map2"


def test_ude_validation_errors(ElementFactory):
  ude = Ude("test")
  ude.name = 123
  with pytest.raises(DeserializationError) as e:
    ude.to_xml(ElementFactory)
  assert e.value.tmx_element is ude
  assert isinstance(e.value.__cause__, ValidationError)


def test_ude_no_base_when_required(ElementFactory):
  ude = Ude(name="name", maps=[Map(unicode="map1", code="code")])
  with pytest.raises(DeserializationError) as e:
    ude.to_xml(ElementFactory)
  assert e.value.tmx_element is ude
  assert isinstance(e.value.__cause__, ValueError)
