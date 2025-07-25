# type: ignore
import pytest

from PythonTmx.core import AnyElementFactory, AnyXmlElement
from PythonTmx.elements import Map
from PythonTmx.errors import SerializationError, UnusableElementError


class TestMapHappyPath:
  def test_from_xml_minimal(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("map", {"unicode": "00A0"})
    el.text = None
    m = Map.from_xml(el)
    assert m.unicode == "00A0"
    assert m.code is None
    assert m.ent is None
    assert m.subst is None

  def test_from_xml_full(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    attrs = {
      "unicode": "00A9",
      "code": "&#169;",
      "ent": "&copy;",
      "subst": "(c)",
    }
    el = ElementFactory("map", attrs)
    el.text = None
    m = Map.from_xml(el)
    assert m.unicode == "00A9"
    assert m.code == "&#169;"
    assert m.ent == "&copy;"
    assert m.subst == "(c)"

  def test_to_xml_roundtrip(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    m = Map(unicode="00AE", code="&#174;", ent="&reg;")
    el = m.to_xml(ElementFactory)
    assert el.tag == "map"
    assert el.attrib["unicode"] == "00AE"
    assert el.attrib["code"] == "&#174;"
    assert el.attrib["ent"] == "&reg;"
    assert "subst" not in el.attrib


class TestMapErrorPath:
  def test_wrong_tag(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("notmap", {"unicode": "00A0"})
    el.text = None
    with pytest.raises(UnusableElementError) as exc:
      Map.from_xml(el)
    assert (
      "expected_tag" in str(exc.value).lower()
      or "expected" in str(exc.value).lower()
    )

  def test_unexpected_text(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("map", {"unicode": "00A0"})
    el.text = "oops"
    with pytest.raises(SerializationError) as exc:
      Map.from_xml(el)
    assert "unexpected text" in str(exc.value).lower()

  def test_missing_required_unicode(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory("map", {})
    el.text = None
    with pytest.raises(SerializationError) as exc:
      Map.from_xml(el)
    assert isinstance(exc.value.original_exception, KeyError)


class TestMapMalformedInputs:
  def test_missing_attrib(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(tag="map", text=None, tail="")
    with pytest.raises(UnusableElementError) as exc:
      Map.from_xml(el)
    assert exc.value.missing_field == "attrib"

  def test_attrib_not_mapping_like(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(tag="map", text=None, tail="", attrib=123)
    with pytest.raises(UnusableElementError) as exc:
      Map.from_xml(el)
    assert exc.value.missing_field == "attrib"

  def test_not_iterable(
    self, FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement]
  ):
    el = FakeAndBrokenElement(tag="map", text="foo", tail="")
    temp = FakeAndBrokenElement.__iter__
    del FakeAndBrokenElement.__iter__
    with pytest.raises(UnusableElementError):
      Map.from_xml(el)
    FakeAndBrokenElement.__iter__ = temp
