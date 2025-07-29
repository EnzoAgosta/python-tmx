# type: ignore
from datetime import datetime, timezone

import pytest

from PythonTmx.elements.inline import Bpt, Ept, Ph
from PythonTmx.elements.note import Note
from PythonTmx.elements.prop import Prop
from PythonTmx.elements.tuv import Tuv
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  SerializationError,
  ValidationError,
  WrongTagError,
)


def test_create_minimal_tuv():
  tuv = Tuv("en")
  assert tuv.lang == "en"
  assert tuv.encoding is None
  assert tuv.datatype is None
  assert tuv.usagecount is None
  assert tuv.lastusagedate is None
  assert tuv.creationtool is None
  assert tuv.creationtoolversion is None
  assert tuv.creationdate is None
  assert tuv.creationid is None
  assert tuv.changedate is None
  assert tuv.changeid is None
  assert tuv.tmf is None
  assert tuv._children == []
  assert tuv.segment == []


def test_create_full_tuv():
  creation_date = datetime(2023, 1, 1, 12, 0, 0)
  change_date = datetime(2023, 1, 2, 12, 0, 0)
  last_usage_date = datetime(2023, 1, 3, 12, 0, 0)

  note = Note("Test note")
  prop = Prop("Test value", "test_type")

  tuv = Tuv(
    lang="en",
    encoding="utf-8",
    datatype="plaintext",
    usagecount=5,
    lastusagedate=last_usage_date,
    creationtool="TestTool",
    creationtoolversion="1.0",
    creationdate=creation_date,
    creationid="user123",
    changedate=change_date,
    changeid="user456",
    tmf="test-tmf",
    children=[note, prop],
    segment=["Hello", " ", "world"],
  )

  assert tuv.lang == "en"
  assert tuv.encoding == "utf-8"
  assert tuv.datatype == "plaintext"
  assert tuv.usagecount == 5
  assert tuv.lastusagedate == last_usage_date
  assert tuv.creationtool == "TestTool"
  assert tuv.creationtoolversion == "1.0"
  assert tuv.creationdate == creation_date
  assert tuv.creationid == "user123"
  assert tuv.changedate == change_date
  assert tuv.changeid == "user456"
  assert tuv.tmf == "test-tmf"
  assert len(tuv._children) == 2
  assert note in tuv._children
  assert prop in tuv._children
  assert tuv.segment == ["Hello", " ", "world"]


def test_tuv_from_minimal_xml(ElementFactory):
  element = ElementFactory("tuv", {"{http://www.w3.org/XML/1998/namespace}lang": "en"})
  seg_element = ElementFactory("seg", {})
  element.append(seg_element)

  tuv = Tuv.from_xml(element)
  assert tuv.lang == "en"
  assert tuv.encoding is None
  assert tuv.datatype is None
  assert tuv.usagecount is None
  assert tuv.lastusagedate is None
  assert tuv.creationtool is None
  assert tuv.creationtoolversion is None
  assert tuv.creationdate is None
  assert tuv.creationid is None
  assert tuv.changedate is None
  assert tuv.changeid is None
  assert tuv.tmf is None
  assert tuv._children == []
  assert tuv.segment == []


def test_tuv_from_full_xml(ElementFactory):
  creation_date = "20230101T120000Z"
  change_date = "20230102T120000Z"
  last_usage_date = "20230103T120000Z"

  element = ElementFactory(
    "tuv",
    {
      "{http://www.w3.org/XML/1998/namespace}lang": "en",
      "o-encoding": "utf-8",
      "datatype": "plaintext",
      "usagecount": "5",
      "lastusagedate": last_usage_date,
      "creationtool": "TestTool",
      "creationtoolversion": "1.0",
      "creationdate": creation_date,
      "creationid": "user123",
      "changedate": change_date,
      "changeid": "user456",
      "o-tmf": "test-tmf",
    },
  )

  note_element = ElementFactory("note", {})
  note_element.text = "Test note"
  element.append(note_element)

  prop_element = ElementFactory("prop", {"type": "test_type"})
  prop_element.text = "Test value"
  element.append(prop_element)

  seg_element = ElementFactory("seg", {})
  seg_element.text = "Hello world"
  element.append(seg_element)

  tuv = Tuv.from_xml(element)
  assert tuv.lang == "en"
  assert tuv.encoding == "utf-8"
  assert tuv.datatype == "plaintext"
  assert tuv.usagecount == 5
  assert tuv.lastusagedate == datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc)
  assert tuv.creationtool == "TestTool"
  assert tuv.creationtoolversion == "1.0"
  assert tuv.creationdate == datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
  assert tuv.creationid == "user123"
  assert tuv.changedate == datetime(2023, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
  assert tuv.changeid == "user456"
  assert tuv.tmf == "test-tmf"
  assert len(tuv._children) == 2
  assert isinstance(tuv._children[0], Note)
  assert isinstance(tuv._children[1], Prop)
  assert tuv.segment == ["Hello world"]


def test_tuv_from_xml_with_inline_elements(ElementFactory):
  element = ElementFactory("tuv", {"{http://www.w3.org/XML/1998/namespace}lang": "en"})

  seg_element = ElementFactory("seg", {})
  seg_element.text = "Hello "

  bpt_element = ElementFactory("bpt", {"i": "1"})
  bpt_element.text = "bold"
  seg_element.append(bpt_element)
  bpt_element.tail = " world"

  element.append(seg_element)

  tuv = Tuv.from_xml(element)
  assert tuv.lang == "en"
  assert len(tuv.segment) == 3
  assert tuv.segment[0] == "Hello "
  assert isinstance(tuv.segment[1], Bpt)
  assert tuv.segment[1].i == 1
  assert tuv.segment[1]._children == ["bold"]
  assert tuv.segment[2] == " world"


def test_tuv_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("wrong", {})
  with pytest.raises(SerializationError) as e:
    Tuv.from_xml(element)
  assert e.value.tmx_element is Tuv
  assert isinstance(e.value.__cause__, WrongTagError)


def test_tuv_from_xml_missing_lang(ElementFactory):
  element = ElementFactory("tuv", {})
  seg_element = ElementFactory("seg", {})
  element.append(seg_element)

  with pytest.raises(SerializationError) as e:
    Tuv.from_xml(element)
  assert e.value.tmx_element is Tuv
  assert isinstance(e.value.__cause__, KeyError)


def test_tuv_from_xml_with_text(ElementFactory):
  element = ElementFactory("tuv", {"{http://www.w3.org/XML/1998/namespace}lang": "en"})
  element.text = "This should not be here"
  seg_element = ElementFactory("seg", {})
  element.append(seg_element)

  with pytest.raises(SerializationError) as e:
    Tuv.from_xml(element)
  assert e.value.tmx_element is Tuv
  assert isinstance(e.value.__cause__, ValueError)


def test_tuv_from_xml_unusable_attrib(CustomElementLike):
  element = CustomElementLike(tag="tuv", text=None, attrib=object())
  with pytest.raises(SerializationError) as e:
    Tuv.from_xml(element)
  assert e.value.tmx_element is Tuv
  assert isinstance(e.value.__cause__, NotMappingLikeError)


def test_tuv_from_xml_wrong_child_tag(ElementFactory):
  element = ElementFactory("tuv", {"{http://www.w3.org/XML/1998/namespace}lang": "en"})
  wrong_element = ElementFactory("wrong", {})
  element.append(wrong_element)

  with pytest.raises(SerializationError) as e:
    Tuv.from_xml(element)
  assert e.value.tmx_element is Tuv
  assert isinstance(e.value.__cause__, WrongTagError)


def test_tuv_from_xml_wrong_seg_child_tag(ElementFactory):
  element = ElementFactory("tuv", {"{http://www.w3.org/XML/1998/namespace}lang": "en"})
  seg_element = ElementFactory("seg", {})
  wrong_element = ElementFactory("wrong", {})
  seg_element.append(wrong_element)
  element.append(seg_element)

  with pytest.raises(SerializationError) as e:
    Tuv.from_xml(element)
  assert e.value.tmx_element is Tuv
  assert isinstance(e.value.__cause__, WrongTagError)


def test_tuv_to_xml_minimal(ElementFactory):
  tuv = Tuv("en")
  element = tuv.to_xml(ElementFactory)
  assert element.tag == "tuv"
  assert element.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"
  assert len(element.attrib) == 1
  assert len(list(element)) == 1


def test_tuv_to_xml_full(ElementFactory):
  creation_date = datetime(2023, 1, 1, 12, 0, 0)
  change_date = datetime(2023, 1, 2, 12, 0, 0)
  last_usage_date = datetime(2023, 1, 3, 12, 0, 0)

  note = Note("Test note")
  prop = Prop("Test value", "test_type")

  tuv = Tuv(
    lang="en",
    encoding="utf-8",
    datatype="plaintext",
    usagecount=5,
    lastusagedate=last_usage_date,
    creationtool="TestTool",
    creationtoolversion="1.0",
    creationdate=creation_date,
    creationid="user123",
    changedate=change_date,
    changeid="user456",
    tmf="test-tmf",
    children=[note, prop],
    segment=["Hello", " ", "world"],
  )

  element = tuv.to_xml(ElementFactory)
  assert element.tag == "tuv"
  assert element.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"
  assert element.attrib["o-encoding"] == "utf-8"
  assert element.attrib["datatype"] == "plaintext"
  assert element.attrib["usagecount"] == "5"
  assert element.attrib["lastusagedate"] == "20230103T120000Z"
  assert element.attrib["creationtool"] == "TestTool"
  assert element.attrib["creationtoolversion"] == "1.0"
  assert element.attrib["creationdate"] == "20230101T120000Z"
  assert element.attrib["creationid"] == "user123"
  assert element.attrib["changedate"] == "20230102T120000Z"
  assert element.attrib["changeid"] == "user456"
  assert element.attrib["o-tmf"] == "test-tmf"

  children = [c for c in element]
  assert len(children) == 3
  assert children[0].tag == "note"
  assert children[0].text == "Test note"
  assert children[1].tag == "prop"
  assert children[1].text == "Test value"
  assert children[1].attrib["type"] == "test_type"
  assert children[2].tag == "seg"
  assert children[2].text == "Hello world"


def test_tuv_to_xml_with_inline_elements(ElementFactory):
  bpt = Bpt(i=1, children=["bold"])
  tuv = Tuv("en", segment=["Hello ", bpt, " world"])

  element = tuv.to_xml(ElementFactory)
  assert element.tag == "tuv"
  assert element.attrib["{http://www.w3.org/XML/1998/namespace}lang"] == "en"

  children = [c for c in element]
  assert len(children) == 1
  seg_element = children[0]
  assert seg_element.tag == "seg"
  assert seg_element.text == "Hello "

  seg_children = [c for c in seg_element]
  assert len(seg_children) == 1
  bpt_element = seg_children[0]
  assert bpt_element.tag == "bpt"
  assert bpt_element.attrib["i"] == "1"
  assert bpt_element.text == "bold"
  assert bpt_element.tail == " world"


def test_tuv_to_xml_with_complex_segment(ElementFactory):
  bpt = Bpt(i=1, children=["bold"])
  ept = Ept(i=1, children=["/bold"])
  ph = Ph(x=1, children=["placeholder"])

  tuv = Tuv("en", segment=["Text ", bpt, "more text", ept, " ", ph, " end"])

  element = tuv.to_xml(ElementFactory)
  children = list(element)
  assert len(children) == 1

  seg_element = children[0]
  assert seg_element.text == "Text "

  seg_children = list(seg_element)
  assert len(seg_children) == 3

  assert seg_children[0].tag == "bpt"
  assert seg_children[0].text == "bold"
  assert seg_children[0].tail == "more text"

  assert seg_children[1].tag == "ept"
  assert seg_children[1].text == "/bold"
  assert seg_children[1].tail == " "

  assert seg_children[2].tag == "ph"
  assert seg_children[2].text == "placeholder"
  assert seg_children[2].tail == " end"


def test_tuv_validation_errors(ElementFactory):
  tuv = Tuv("en")

  tuv.lang = 123
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.lang = "en"
  tuv.encoding = 123
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.encoding = "utf-8"
  tuv.datatype = 123
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.datatype = "plaintext"
  tuv.usagecount = "not a number"
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.usagecount = 5
  tuv.lastusagedate = "not a datetime"
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.lastusagedate = datetime(2023, 1, 1, 12, 0, 0)
  tuv.creationtool = 123
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.creationtool = "TestTool"
  tuv.creationtoolversion = 123
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.creationtoolversion = "1.0"
  tuv.creationdate = "not a datetime"
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.creationdate = datetime(2023, 1, 1, 12, 0, 0)
  tuv.creationid = 123
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.creationid = "user123"
  tuv.changedate = "not a datetime"
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.changedate = datetime(2023, 1, 2, 12, 0, 0)
  tuv.changeid = 123
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)

  tuv.changeid = "user456"
  tuv.tmf = 123
  with pytest.raises(DeserializationError) as e:
    tuv.to_xml(ElementFactory)
  assert e.value.tmx_element is tuv
  assert isinstance(e.value.__cause__, ValidationError)


def test_tuv_with_string_usagecount():
  tuv = Tuv("en", usagecount="5")
  assert tuv.usagecount == 5


def test_tuv_with_datetime_strings():
  tuv = Tuv(
    "en",
    lastusagedate="20230101T120000Z",
    creationdate="20230102T120000Z",
    changedate="20230103T120000Z",
  )
  assert tuv.lastusagedate == datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
  assert tuv.creationdate == datetime(2023, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
  assert tuv.changedate == datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc)


def test_tuv_iteration():
  note = Note("Test note")
  prop = Prop("Test value", "test_type")
  tuv = Tuv("en", children=[note, prop])

  children = list(tuv)
  assert len(children) == 2
  assert children[0] is note
  assert children[1] is prop


def test_tuv_roundtrip(ElementFactory):
  creation_date = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
  change_date = datetime(2023, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
  last_usage_date = datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc)

  note = Note("Test note")
  prop = Prop("Test value", "test_type")
  bpt = Bpt(i=1, children=["bold"])

  original_tuv = Tuv(
    lang="en",
    encoding="utf-8",
    datatype="plaintext",
    usagecount=5,
    lastusagedate=last_usage_date,
    creationtool="TestTool",
    creationtoolversion="1.0",
    creationdate=creation_date,
    creationid="user123",
    changedate=change_date,
    changeid="user456",
    tmf="test-tmf",
    children=[note, prop],
    segment=["Hello ", bpt, " world"],
  )

  element = original_tuv.to_xml(ElementFactory)
  roundtrip_tuv = Tuv.from_xml(element)

  assert roundtrip_tuv.lang == original_tuv.lang
  assert roundtrip_tuv.encoding == original_tuv.encoding
  assert roundtrip_tuv.datatype == original_tuv.datatype
  assert roundtrip_tuv.usagecount == original_tuv.usagecount
  assert roundtrip_tuv.lastusagedate == original_tuv.lastusagedate
  assert roundtrip_tuv.creationtool == original_tuv.creationtool
  assert roundtrip_tuv.creationtoolversion == original_tuv.creationtoolversion
  assert roundtrip_tuv.creationdate == original_tuv.creationdate
  assert roundtrip_tuv.creationid == original_tuv.creationid
  assert roundtrip_tuv.changedate == original_tuv.changedate
  assert roundtrip_tuv.changeid == original_tuv.changeid
  assert roundtrip_tuv.tmf == original_tuv.tmf
  assert len(roundtrip_tuv._children) == len(original_tuv._children)
  assert len(roundtrip_tuv.segment) == len(original_tuv.segment)
