from datetime import datetime

import pytest

from PythonTmx.elements.header import Header
from PythonTmx.elements.note import Note
from PythonTmx.elements.prop import Prop
from PythonTmx.elements.ude import Ude
from PythonTmx.enums import SEGTYPE
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  SerializationError,
  ValidationError,
  WrongTagError,
)


def test_create_minimal_header():
  header = Header(
    creationtool="Tool",
    creationtoolversion="1.0",
    segtype="sentence",
    tmf="tmf",
    adminlang="en",
    srclang="en-US",
    datatype="plaintext",
  )
  assert header.creationtool == "Tool"
  assert header.creationtoolversion == "1.0"
  assert header.segtype == SEGTYPE.SENTENCE
  assert header.tmf == "tmf"
  assert header.adminlang == "en"
  assert header.srclang == "en-US"
  assert header.datatype == "plaintext"
  assert header.encoding is None
  assert header.creationdate is None
  assert header.creationid is None
  assert header.changedate is None
  assert header.changeid is None
  assert header.notes == []
  assert header.props == []
  assert header.udes == []


def test_create_full_header():
  note = Note("Header note")
  prop = Prop("client", "Acme")
  ude = Ude("u1")
  dt = datetime(2023, 1, 1, 12, 0, 0)
  header = Header(
    creationtool="Tool",
    creationtoolversion="1.0",
    segtype=SEGTYPE.BLOCK,
    tmf="tmf",
    adminlang="en",
    srclang="fr",
    datatype="xhtml",
    encoding="UTF-8",
    creationdate=dt,
    creationid="creator",
    changedate=dt,
    changeid="changer",
    children=[note, prop, ude],
  )
  assert header.creationdate == dt
  assert header.changedate == dt
  assert header.notes == [note]
  assert header.props == [prop]
  assert header.udes == [ude]


def test_header_from_minimal_xml(ElementFactory):
  element = ElementFactory(
    "header",
    {
      "creationtool": "Tool",
      "creationtoolversion": "1.0",
      "segtype": "block",
      "o-tmf": "tmf",
      "adminlang": "en",
      "srclang": "en",
      "datatype": "xml",
    },
  )
  header = Header.from_xml(element)
  assert header.creationtool == "Tool"
  assert header.segtype == SEGTYPE.BLOCK


def test_header_from_full_xml(ElementFactory):
  note = ElementFactory("note", {})
  prop = ElementFactory("prop", {"type": "client"})
  ude = ElementFactory("ude", {"name": "u1"})
  note.text = "Header note"
  prop.text = "Acme"
  element = ElementFactory(
    "header",
    {
      "creationtool": "Tool",
      "creationtoolversion": "1.0",
      "segtype": "phrase",
      "o-tmf": "tmf",
      "adminlang": "en",
      "srclang": "fr",
      "datatype": "txt",
      "o-encoding": "UTF-8",
      "creationid": "user1",
      "creationdate": "20230101T120000Z",
      "changeid": "user2",
      "changedate": "20240101T120000Z",
    },
  )
  element.append(note)
  element.append(prop)
  element.append(ude)
  header = Header.from_xml(element)
  assert len(header.notes) == 1
  assert len(header.props) == 1
  assert len(header.udes) == 1
  assert header.encoding == "UTF-8"
  assert header.creationid == "user1"
  assert header.changeid == "user2"


def test_header_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("notheader", {})
  with pytest.raises(SerializationError) as e:
    Header.from_xml(element)
  assert e.value.tmx_element is Header
  assert isinstance(e.value.__cause__, WrongTagError)


def test_header_from_xml_bad_child_tag(ElementFactory):
  element = ElementFactory(
    "header",
    {
      "creationtool": "Tool",
      "creationtoolversion": "1.0",
      "segtype": "block",
      "o-tmf": "tmf",
      "adminlang": "en",
      "srclang": "en",
      "datatype": "xml",
    },
  )
  element.append(ElementFactory("badchild", {}))
  with pytest.raises(SerializationError) as e:
    Header.from_xml(element)
  assert isinstance(e.value.__cause__, WrongTagError)


def test_header_from_xml_unusable_attrib(CustomElementLike):
  element = CustomElementLike("header", attrib=object(), text=None)
  with pytest.raises(SerializationError) as e:
    Header.from_xml(element)
  assert isinstance(e.value.__cause__, NotMappingLikeError)


def test_header_to_xml_minimal(ElementFactory):
  header = Header(
    creationtool="Tool",
    creationtoolversion="1.0",
    segtype="block",
    tmf="tmf",
    adminlang="en",
    srclang="en",
    datatype="plain",
  )
  element = header.to_xml(ElementFactory)
  assert element.tag == "header"
  assert element.attrib["creationtool"] == "Tool"
  assert element.attrib["segtype"] == "block"
  assert element.attrib["adminlang"] == "en"


def test_header_to_xml_full(ElementFactory):
  dt = datetime(2024, 1, 1, 12, 0, 0)
  header = Header(
    creationtool="Tool",
    creationtoolversion="2.0",
    segtype="sentence",
    tmf="tmf",
    adminlang="en",
    srclang="de",
    datatype="xlf",
    encoding="utf-8",
    creationdate=dt,
    creationid="me",
    changedate=dt,
    changeid="you",
    children=[Note("text"), Prop("client", "acme"), Ude("custom")],
  )
  element = header.to_xml(ElementFactory)
  assert element.attrib["creationid"] == "me"
  assert element.attrib["changedate"] == "20240101T120000Z"
  tags = [c.tag for c in element]
  assert tags == ["note", "prop", "ude"]


def test_header_validation_errors(ElementFactory):
  header = Header(
    creationtool="Tool",
    creationtoolversion="1.0",
    segtype="block",
    tmf="tmf",
    adminlang="en",
    srclang="en",
    datatype="txt",
  )
  header.creationtool = 123  # type: ignore
  with pytest.raises(DeserializationError) as e:
    header.to_xml(ElementFactory)
  assert isinstance(e.value.__cause__, ValidationError)


def test_header_invalid_child_type(ElementFactory):
  class Dummy:
    def to_xml(self): ...

  header = Header(
    creationtool="Tool",
    creationtoolversion="1.0",
    segtype="block",
    tmf="tmf",
    adminlang="en",
    srclang="en",
    datatype="txt",
    children=[Dummy()],  # type: ignore
  )
  with pytest.raises(DeserializationError) as e:
    header.to_xml(ElementFactory)
  assert isinstance(e.value.__cause__, TypeError)
