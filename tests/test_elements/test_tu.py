# type: ignore
from datetime import datetime

import pytest

from PythonTmx.elements.note import Note
from PythonTmx.elements.prop import Prop
from PythonTmx.elements.tu import Tu
from PythonTmx.elements.tuv import Tuv
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  SerializationError,
  ValidationError,
  WrongTagError,
)


def test_create_minimal_tu():
  tu = Tu()
  assert tu.tuid is None
  assert tu.encoding is None
  assert tu.datatype is None
  assert tu.usagecount is None
  assert tu.lastusagedate is None
  assert tu.creationtool is None
  assert tu.creationtoolversion is None
  assert tu.creationdate is None
  assert tu.creationid is None
  assert tu.changedate is None
  assert tu.segtype is None
  assert tu.changeid is None
  assert tu.tmf is None
  assert tu.srclang is None
  assert tu._children == []


def test_create_full_tu():
  creation_date = datetime(2023, 1, 1, 12, 0, 0)
  change_date = datetime(2023, 1, 2, 12, 0, 0)
  last_usage_date = datetime(2023, 1, 3, 12, 0, 0)

  note = Note("Test note")
  prop = Prop("Test value", "test_type")
  tuv = Tuv("en")

  tu = Tu(
    tuid="tu123",
    encoding="utf-8",
    datatype="plaintext",
    usagecount=5,
    lastusagedate=last_usage_date,
    creationtool="TestTool",
    creationtoolversion="1.0",
    creationdate=creation_date,
    creationid="user123",
    changedate=change_date,
    segtype="block",
    changeid="user456",
    tmf="test-tmf",
    srclang="en",
    children=[note, prop, tuv],
  )

  assert tu.tuid == "tu123"
  assert tu.encoding == "utf-8"
  assert tu.datatype == "plaintext"
  assert tu.usagecount == 5
  assert tu.lastusagedate == last_usage_date
  assert tu.creationtool == "TestTool"
  assert tu.creationtoolversion == "1.0"
  assert tu.creationdate == creation_date
  assert tu.creationid == "user123"
  assert tu.changedate == change_date
  assert tu.segtype == "block"
  assert tu.changeid == "user456"
  assert tu.tmf == "test-tmf"
  assert tu.srclang == "en"
  assert len(tu._children) == 3
  assert note in tu._children
  assert prop in tu._children
  assert tuv in tu._children


def test_tu_properties():
  note = Note("Test note")
  prop = Prop("Test value", "test_type")
  tuv = Tuv("en")

  tu = Tu(children=[note, prop, tuv])

  assert tu.props == [prop]
  assert tu.notes == [note]
  assert tu.tuvs == [tuv]


def test_tu_from_minimal_xml(ElementFactory):
  element = ElementFactory("tu", {})
  tuv_element = ElementFactory(
    "tuv", {"{http://www.w3.org/XML/1998/namespace}lang": "en"}
  )
  seg_element = ElementFactory("seg", {})
  tuv_element.append(seg_element)
  element.append(tuv_element)

  tu = Tu.from_xml(element)
  assert tu.tuid is None
  assert tu.encoding is None
  assert tu.datatype is None
  assert tu.usagecount is None
  assert tu.lastusagedate is None
  assert tu.creationtool is None
  assert tu.creationtoolversion is None
  assert tu.creationdate is None
  assert tu.creationid is None
  assert tu.changedate is None
  assert tu.segtype is None
  assert tu.changeid is None
  assert tu.tmf is None
  assert tu.srclang is None
  assert len(tu._children) == 1
  assert isinstance(tu._children[0], Tuv)


def test_tu_from_full_xml(ElementFactory):
  creation_date = datetime(2023, 1, 1, 12, 0, 0)
  change_date = datetime(2023, 1, 2, 12, 0, 0)
  last_usage_date = datetime(2023, 1, 3, 12, 0, 0)

  element = ElementFactory(
    "tu",
    {
      "tuid": "tu123",
      "o-encoding": "utf-8",
      "datatype": "plaintext",
      "usagecount": "5",
      "lastusagedate": "20230103T120000",
      "creationtool": "TestTool",
      "creationtoolversion": "1.0",
      "creationdate": "20230101T120000",
      "creationid": "user123",
      "changedate": "20230102T120000",
      "segtype": "block",
      "changeid": "user456",
      "o-tmf": "test-tmf",
      "srclang": "en",
    },
  )

  note_element = ElementFactory("note", {})
  note_element.text = "Test note"
  element.append(note_element)

  prop_element = ElementFactory("prop", {"type": "test_type"})
  prop_element.text = "Test value"
  element.append(prop_element)

  tuv_element = ElementFactory(
    "tuv", {"{http://www.w3.org/XML/1998/namespace}lang": "en"}
  )
  seg_element = ElementFactory("seg", {})
  seg_element.text = "Hello world"
  tuv_element.append(seg_element)
  element.append(tuv_element)

  tu = Tu.from_xml(element)
  assert tu.tuid == "tu123"
  assert tu.encoding == "utf-8"
  assert tu.datatype == "plaintext"
  assert tu.usagecount == 5
  assert tu.lastusagedate == last_usage_date
  assert tu.creationtool == "TestTool"
  assert tu.creationtoolversion == "1.0"
  assert tu.creationdate == creation_date
  assert tu.creationid == "user123"
  assert tu.changedate == change_date
  assert tu.segtype == "block"
  assert tu.changeid == "user456"
  assert tu.tmf == "test-tmf"
  assert tu.srclang == "en"
  assert len(tu._children) == 3
  assert len(tu.notes) == 1
  assert len(tu.props) == 1
  assert len(tu.tuvs) == 1


def test_tu_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("nottu", {})
  with pytest.raises(SerializationError) as e:
    Tu.from_xml(element)
  assert e.value.tmx_element is Tu
  assert isinstance(e.value.__cause__, WrongTagError)


def test_tu_from_xml_wrong_child_tag(ElementFactory):
  element = ElementFactory("tu", {})
  wrong_element = ElementFactory("wrong", {})
  element.append(wrong_element)

  with pytest.raises(SerializationError) as e:
    Tu.from_xml(element)
  assert e.value.tmx_element is Tu
  assert isinstance(e.value.__cause__, WrongTagError)


def test_tu_from_xml_unusable_attrib(CustomElementLike):
  element = CustomElementLike(tag="tu", attrib=object(), text=None)
  with pytest.raises(SerializationError) as e:
    Tu.from_xml(element)
  assert e.value.tmx_element is Tu
  assert isinstance(e.value.__cause__, NotMappingLikeError)


def test_tu_to_xml_minimal(ElementFactory):
  tu = Tu()
  element = tu.to_xml(ElementFactory)
  assert element.tag == "tu"
  assert len(element.attrib) == 0
  assert len(list(element)) == 0


def test_tu_to_xml_full(ElementFactory):
  creation_date = datetime(2023, 1, 1, 12, 0, 0)
  change_date = datetime(2023, 1, 2, 12, 0, 0)
  last_usage_date = datetime(2023, 1, 3, 12, 0, 0)

  note = Note("Test note")
  prop = Prop("Test value", "test_type")
  tuv = Tuv("en")

  tu = Tu(
    tuid="tu123",
    encoding="utf-8",
    datatype="plaintext",
    usagecount=5,
    lastusagedate=last_usage_date,
    creationtool="TestTool",
    creationtoolversion="1.0",
    creationdate=creation_date,
    creationid="user123",
    changedate=change_date,
    segtype="block",
    changeid="user456",
    tmf="test-tmf",
    srclang="en",
    children=[note, prop, tuv],
  )

  element = tu.to_xml(ElementFactory)
  assert element.tag == "tu"
  assert element.attrib["tuid"] == "tu123"
  assert element.attrib["o-encoding"] == "utf-8"
  assert element.attrib["datatype"] == "plaintext"
  assert element.attrib["usagecount"] == "5"
  assert element.attrib["lastusagedate"] == "20230103T120000"
  assert element.attrib["creationtool"] == "TestTool"
  assert element.attrib["creationtoolversion"] == "1.0"
  assert element.attrib["creationdate"] == "20230101T120000"
  assert element.attrib["creationid"] == "user123"
  assert element.attrib["changedate"] == "20230102T120000"
  assert element.attrib["segtype"] == "block"
  assert element.attrib["changeid"] == "user456"
  assert element.attrib["o-tmf"] == "test-tmf"
  assert element.attrib["srclang"] == "en"

  children = list(element)
  assert len(children) == 3
  assert children[0].tag == "note"
  assert children[1].tag == "prop"
  assert children[2].tag == "tuv"


def test_tu_validation_errors(ElementFactory):
  tu = Tu()
  tu.tuid = 123
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.encoding = 123
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.datatype = 123
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.usagecount = "not an int"
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.lastusagedate = "not a datetime"
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.creationtool = 123
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.creationtoolversion = 123
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.creationdate = "not a datetime"
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.creationid = 123
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.changedate = "not a datetime"
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.segtype = 123
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.changeid = 123
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.tmf = 123
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)

  tu = Tu()
  tu.srclang = 123
  with pytest.raises(DeserializationError) as e:
    tu.to_xml(ElementFactory)
  assert e.value.tmx_element is tu
  assert isinstance(e.value.__cause__, ValidationError)


def test_tu_with_string_usagecount():
  tu = Tu(usagecount="5")
  assert tu.usagecount == 5


def test_tu_with_datetime_strings():
  tu = Tu(
    lastusagedate="2023-01-03T12:00:00",
    creationdate="2023-01-01T12:00:00",
    changedate="2023-01-02T12:00:00",
  )
  assert tu.lastusagedate == datetime(2023, 1, 3, 12, 0, 0)
  assert tu.creationdate == datetime(2023, 1, 1, 12, 0, 0)
  assert tu.changedate == datetime(2023, 1, 2, 12, 0, 0)


def test_tu_iteration():
  note = Note("Test note")
  prop = Prop("Test value", "test_type")
  tuv = Tuv("en")

  tu = Tu(children=[note, prop, tuv])

  children = list(tu)
  assert len(children) == 3
  assert children[0] == note
  assert children[1] == prop
  assert children[2] == tuv


def test_tu_roundtrip(ElementFactory):
  creation_date = datetime(2023, 1, 1, 12, 0, 0)
  change_date = datetime(2023, 1, 2, 12, 0, 0)
  last_usage_date = datetime(2023, 1, 3, 12, 0, 0)

  note = Note("Test note")
  prop = Prop("Test value", "test_type")
  tuv = Tuv("en")

  original_tu = Tu(
    tuid="tu123",
    encoding="utf-8",
    datatype="plaintext",
    usagecount=5,
    lastusagedate=last_usage_date,
    creationtool="TestTool",
    creationtoolversion="1.0",
    creationdate=creation_date,
    creationid="user123",
    changedate=change_date,
    segtype="block",
    changeid="user456",
    tmf="test-tmf",
    srclang="en",
    children=[note, prop, tuv],
  )

  element = original_tu.to_xml(ElementFactory)
  roundtrip_tu = Tu.from_xml(element)

  assert roundtrip_tu.tuid == original_tu.tuid
  assert roundtrip_tu.encoding == original_tu.encoding
  assert roundtrip_tu.datatype == original_tu.datatype
  assert roundtrip_tu.usagecount == original_tu.usagecount
  assert roundtrip_tu.lastusagedate == original_tu.lastusagedate
  assert roundtrip_tu.creationtool == original_tu.creationtool
  assert roundtrip_tu.creationtoolversion == original_tu.creationtoolversion
  assert roundtrip_tu.creationdate == original_tu.creationdate
  assert roundtrip_tu.creationid == original_tu.creationid
  assert roundtrip_tu.changedate == original_tu.changedate
  assert roundtrip_tu.segtype == original_tu.segtype
  assert roundtrip_tu.changeid == original_tu.changeid
  assert roundtrip_tu.tmf == original_tu.tmf
  assert roundtrip_tu.srclang == original_tu.srclang
  assert len(roundtrip_tu._children) == len(original_tu._children)
