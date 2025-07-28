# type: ignore
from datetime import datetime

import pytest

from PythonTmx.core import AnyElementFactory, AnyXmlElement
from PythonTmx.elements import Header, Note, Prop, Ude
from PythonTmx.elements.map import Map
from PythonTmx.enums import SEGTYPE
from PythonTmx.errors import SerializationError, UnusableElementError


class TestHeaderHappyPath:
  def test_from_xml_minimal(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    el = ElementFactory(
      "header",
      {
        "creationtool": "ToolX",
        "creationtoolversion": "1.0",
        "segtype": "block",
        "o-tmf": "tmx",
        "adminlang": "en-US",
        "srclang": "fr-FR",
        "datatype": "plaintext",
      },
    )
    hdr = Header.from_xml(el)

    assert hdr.creationtool == "ToolX"
    assert hdr.creationtoolversion == "1.0"
    assert hdr.segtype == SEGTYPE.BLOCK
    assert hdr.tmf == "tmx"
    assert hdr.adminlang == "en-US"
    assert hdr.srclang == "fr-FR"
    assert hdr.datatype == "plaintext"

    assert hdr.encoding is None
    assert hdr.creationdate is None
    assert hdr.creationid is None
    assert hdr.changedate is None
    assert hdr.changeid is None

    assert list(hdr) == []
    assert len(hdr) == 0
    assert hdr.udes == []
    assert hdr.notes == []
    assert hdr.props == []

  def test_from_xml_full_and_child_order(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    ude_el = ElementFactory("ude", {"name": "U1"})
    note_el = ElementFactory("note", {"type": "t"})
    note_el.text = "hello"
    prop_el = ElementFactory("prop", {"type": "p"})
    prop_el.text = "world"

    el = ElementFactory(
      "header",
      {
        "creationtool": "ToolY",
        "creationtoolversion": "2.1",
        "segtype": "block",
        "o-tmf": "fmt",
        "adminlang": "es",
        "srclang": "de",
        "datatype": "html",
        "o-encoding": "utf-8",
        "creationdate": "20250728T120000Z",
        "creationid": "creator",
        "changedate": "20250729T130000Z",
        "changeid": "changer",
      },
    )
    el.append(note_el)
    el.append(ude_el)
    el.append(prop_el)

    hdr = Header.from_xml(el)

    assert hdr.encoding == "utf-8"
    assert isinstance(hdr.creationdate, datetime)
    assert hdr.creationid == "creator"
    assert isinstance(hdr.changedate, datetime)
    assert hdr.changeid == "changer"

    types_in_order = [type(c) for c in hdr]
    assert types_in_order == [Note, Ude, Prop]

    assert [type(x) for x in hdr.notes] == [Note]
    assert [type(x) for x in hdr.udes] == [Ude]
    assert [type(x) for x in hdr.props] == [Prop]


class TestHeaderSerialization:
  def test_to_xml_minimal(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    hdr = Header(
      creationtool="Z",
      creationtoolversion="0.1",
      segtype=SEGTYPE.BLOCK,
      tmf="x",
      adminlang="en",
      srclang="en",
      datatype="txt",
      _children=[],
    )
    xml = hdr.to_xml(ElementFactory)

    assert xml.tag == "header"
    for k, v in {
      "creationtool": "Z",
      "creationtoolversion": "0.1",
      "segtype": "block",
      "o-tmf": "x",
      "adminlang": "en",
      "srclang": "en",
      "datatype": "txt",
    }.items():
      assert xml.attrib[k] == v

    assert list(xml) == []

  def test_to_xml_with_children(
    self, ElementFactory: AnyElementFactory[..., AnyXmlElement]
  ):
    ude = Ude(name="U1", _children=[])
    note = Note(text="hi",)
    prop = Prop(text="pv", type="pt")

    for child in (ude, note, prop):
      child.set_default_factory(ElementFactory)

    hdr = Header(
      creationtool="H",
      creationtoolversion="9.9",
      segtype=SEGTYPE.BLOCK,
      tmf="f",
      adminlang="xx",
      srclang="yy",
      datatype="data",
      _children=[ude, note, prop],
    )

    xml = hdr.to_xml(ElementFactory)
    assert xml.tag == "header"

    assert [c.tag for c in xml] == ["ude", "note", "prop"]

    ude_el, note_el, prop_el = list(xml)
    assert ude_el.attrib["name"] == "U1"
    assert note_el.text == "hi"
    assert prop_el.text == "pv"


class TestHeaderErrorPath:
  def test_wrong_tag(self, ElementFactory: AnyElementFactory[..., AnyXmlElement]):
    el = ElementFactory("notheader", {})
    with pytest.raises(UnusableElementError):
      Header.from_xml(el)

  def test_unexpected_text(self, ElementFactory: AnyElementFactory[..., AnyXmlElement]):
    el = ElementFactory(
      "header",
      {
        "creationtool": "x",
        "creationtoolversion": "y",
        "segtype": "block",
        "tmf": "t",
        "adminlang": "a",
        "srclang": "b",
        "datatype": "c",
      },
    )
    el.text = "oops"
    with pytest.raises(SerializationError):
      Header.from_xml(el)

  def test_missing_required_attr(self, ElementFactory: AnyElementFactory[..., AnyXmlElement]):
    el = ElementFactory(
      "header",
      {
        "creationtool": "x",
        "segtype": "block",
        "tmf": "t",
        "adminlang": "a",
        "srclang": "b",
        "datatype": "c",
      },
    )
    with pytest.raises(SerializationError) as exc:
      Header.from_xml(el)
    assert isinstance(exc.value.original_exception, KeyError)

  def test_to_xml_child_type_violation(self, ElementFactory: AnyElementFactory[..., AnyXmlElement]):
    hdr = Header(
      _children=[Map(unicode="00A0")],  # type: ignore
      creationtool="X",
      creationtoolversion="Y",
      segtype=SEGTYPE.BLOCK,
      tmf="t",
      adminlang="a",
      srclang="b",
      datatype="c",
    )
    with pytest.raises(SerializationError) as exc:
      hdr.to_xml(ElementFactory)


def test_header_missing_attrib(
  FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement],
):
  el = FakeAndBrokenElement(tag="header", text=None, tail="")
  with pytest.raises(UnusableElementError) as exc:
    Header.from_xml(el)
  assert exc.value.missing_field == "attrib"


def test_header_not_iterable(
  FakeAndBrokenElement: AnyElementFactory[..., AnyXmlElement],
):
  el = FakeAndBrokenElement(
    tag="header",
    text=None,
    tail="",
    attrib={
      "creationtool": "x",
      "creationtoolversion": "y",
      "segtype": "block",
      "tmf": "t",
      "adminlang": "a",
      "srclang": "b",
      "datatype": "c",
    },
  )
  temp = FakeAndBrokenElement.__iter__
  del FakeAndBrokenElement.__iter__
  with pytest.raises(UnusableElementError):
    Header.from_xml(el)
  FakeAndBrokenElement.__iter__ = temp
