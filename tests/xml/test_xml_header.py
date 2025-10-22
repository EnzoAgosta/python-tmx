from datetime import datetime

import lxml.etree as et
import pytest

from python_tmx.base.models import Header, Note, Prop, SegType
from python_tmx.xml.converters import parse_header


def test_parse_header_from_lxml_element(full_header_lxml_elem: et._Element) -> None:
  """
  Test that all attributes and props/notes are parsed from a header element
  """
  header = parse_header(elem=full_header_lxml_elem)
  assert isinstance(header, Header)
  assert header.creationtool == full_header_lxml_elem.attrib["creationtool"]
  assert header.creationtoolversion == full_header_lxml_elem.attrib["creationtoolversion"]
  assert isinstance(header.segtype, SegType)
  assert header.segtype.value == full_header_lxml_elem.attrib["segtype"]
  assert header.o_tmf == full_header_lxml_elem.attrib["o-tmf"]
  assert header.adminlang == full_header_lxml_elem.attrib["adminlang"]
  assert header.srclang == full_header_lxml_elem.attrib["srclang"]
  assert header.datatype == full_header_lxml_elem.attrib["datatype"]
  assert header.o_encoding == full_header_lxml_elem.attrib["o-encoding"]
  assert isinstance(header.creationdate, datetime)
  assert header.creationdate.strftime("%Y%m%dT%H%M%SZ") == full_header_lxml_elem.attrib["creationdate"]
  assert header.creationid == full_header_lxml_elem.attrib["creationid"]
  assert isinstance(header.changedate, datetime)
  assert header.changedate.strftime("%Y%m%dT%H%M%SZ") == full_header_lxml_elem.attrib["changedate"]
  assert header.changeid == full_header_lxml_elem.attrib["changeid"]
  prop_elems, note_elems = [], []
  for child in full_header_lxml_elem.iter("prop", "note"):
    if child.tag == "prop":
      prop_elems.append(child)
    else:
      note_elems.append(child)
  assert len(prop_elems) == len(header.props)
  assert all(isinstance(prop, Prop) for prop in header.props)
  assert len(note_elems) == len(header.notes)
  assert all(isinstance(note, Note) for note in header.notes)


def test_parse_header_from_lxml_element_minimal(minimal_header_lxml_elem: et._Element) -> None:
  header = parse_header(minimal_header_lxml_elem)
  assert header.o_encoding is None
  assert header.creationdate is None
  assert header.creationid is None
  assert header.changedate is None
  assert header.changeid is None


def test_parse_header_from_lxml_element_missing_required_attributes_raises(full_header_lxml_elem: et._Element) -> None:
  del full_header_lxml_elem.attrib["creationtool"]
  with pytest.raises(KeyError):
    parse_header(elem=full_header_lxml_elem)


def test_parse_header_from_lxml_element_incorrect_segtype_raises(full_header_lxml_elem: et._Element) -> None:
  full_header_lxml_elem.attrib["segtype"] = "wrong"
  with pytest.raises(ValueError):
    parse_header(elem=full_header_lxml_elem)


def test_parse_header_incorrect_attributes_are_ignored(full_header_lxml_elem: et._Element) -> None:
  full_header_lxml_elem.attrib["extra"] = "ignore me"
  parse_header(elem=full_header_lxml_elem)


def test_parse_header_incorrect_children_are_ignored(full_header_lxml_elem: et._Element) -> None:
  full_header_lxml_elem.append(et.Element("hello"))
  parse_header(elem=full_header_lxml_elem)


def test_parse_header_incorrect_dt_raises(full_header_lxml_elem: et._Element) -> None:
  full_header_lxml_elem.attrib["creationdate"] = "wrong"
  with pytest.raises(ValueError):
    parse_header(elem=full_header_lxml_elem)


def test_parse_header_incorrect_tag_raises(full_header_lxml_elem: et._Element) -> None:
  full_header_lxml_elem.tag = "wrong"
  with pytest.raises(ValueError):
    parse_header(full_header_lxml_elem)
