# type: ignore
import pytest

from PythonTmx.core import AnyElementFactory, AnyXmlElement
from PythonTmx.elements import Map, Ude
from PythonTmx.errors import SerializationError, UnusableElementError


class TestUdeHappyPath:
  def test_from_xml_minimal(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("ude", {"name": "unit1"})
    ude = Ude.from_xml(el)
    assert ude.name == "unit1"
    assert ude.base is None
    assert isinstance(ude.maps, list) and len(ude.maps) == 0
    assert list(ude) == []
    assert len(ude) == 0

  def test_from_xml_with_base_and_children(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    child1 = ElementFactory("map", {"unicode": "00A0"})
    child2 = ElementFactory("map", {"unicode": "00A9", "code": "&#169;"})

    el = ElementFactory("ude", {"name": "unitX", "base": "B"})
    el.text = None
    el.append(child1)
    el.append(child2)

    ude = Ude.from_xml(el)
    assert ude.name == "unitX"
    assert ude.base == "B"
    assert isinstance(ude.maps, list) and len(ude.maps) == 2
    assert isinstance(ude.maps[0], Map) and ude.maps[0].unicode == "00A0"
    assert ude.maps[1].code == "&#169;"
    assert list(ude) == ude.maps
    assert len(ude) == 2

  def test_to_xml_roundtrip_minimal(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    ude = Ude(name="AAA")
    el = ude.to_xml(ElementFactory)
    assert el.tag == "ude"
    assert el.attrib["name"] == "AAA"
    assert "base" not in el.attrib
    children = [c for c in el]
    assert len(children) == 0

  def test_to_xml_with_maps_and_base(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    m1 = Map(unicode="00A1")
    m2 = Map(unicode="00A2", code="&#162;")
    m1.set_default_factory(ElementFactory)
    m2.set_default_factory(ElementFactory)

    ude = Ude(name="U1", base="BASE", maps=[m1, m2])
    el = ude.to_xml(ElementFactory)

    assert el.attrib["name"] == "U1"
    assert el.attrib["base"] == "BASE"
    children = [c for c in el]
    assert len(children) == 2
    child_tags = [c.tag for c in el]
    assert child_tags == ["map", "map"]
    assert children[1].attrib["code"] == "&#162;"


class TestUdeErrorPath:
  def test_wrong_tag(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("notude", {"name": "x"})
    el.text = None
    with pytest.raises(UnusableElementError) as exc:
      Ude.from_xml(el)
    assert (
      "expected_tag" in str(exc.value).lower()
      or "expected" in str(exc.value).lower()
    )

  def test_unexpected_text(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("ude", {"name": "foo"})
    el.text = "oops"
    with pytest.raises(SerializationError) as exc:
      Ude.from_xml(el)
    assert "unexpected text" in str(exc.value).lower()

  def test_missing_required_name(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("ude", {})
    el.text = None
    with pytest.raises(SerializationError) as exc:
      Ude.from_xml(el)
    assert isinstance(exc.value.original_exception, KeyError)

  def test_to_xml_missing_base_for_code(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    m = Map(unicode="00AB", code="&#171;")
    m.set_default_factory(ElementFactory)
    ude = Ude(name="X", maps=[m])
    with pytest.raises(SerializationError) as exc:
      ude.to_xml(ElementFactory)
    assert "cannot export a ude element" in str(exc.value).lower()


class TestUdeMalformedInputs:
  def test_missing_attrib(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(tag="ude", text=None, tail="")
    with pytest.raises(UnusableElementError) as exc:
      Ude.from_xml(el)
    assert exc.value.missing_field == "attrib"

  def test_not_iterable(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(
      tag="ude", text=None, tail="", attrib={"name": "n"}
    )
    temp = FakeAndBrokenElement.__iter__
    del FakeAndBrokenElement.__iter__
    with pytest.raises(UnusableElementError):
      Ude.from_xml(el)
    FakeAndBrokenElement.__iter__ = temp

  def test_child_not_map_raises(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(
      tag="ude", text=None, tail="", attrib={"name": "p"}
    )
    temp = FakeAndBrokenElement.__iter__

    def iter_bad(self):
      yield 1

    FakeAndBrokenElement.__iter__ = iter_bad
    with pytest.raises(SerializationError):
      Ude.from_xml(el)
    FakeAndBrokenElement.__iter__ = temp
