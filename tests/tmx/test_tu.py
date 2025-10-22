from datetime import datetime

import lxml.etree as et
import pytest

from python_tmx.tmx.models import Note, Prop, Tu, Tuv
from python_tmx.tmx.parse import parse_tu


def test_parse_tu_from_full_element(full_tu_lxml_elem: et._Element):
  tu = parse_tu(full_tu_lxml_elem)
  assert isinstance(tu, Tu)
  assert tu.tuid == full_tu_lxml_elem.attrib["tuid"]
  assert tu.o_encoding == full_tu_lxml_elem.attrib["o-encoding"]
  assert tu.datatype == full_tu_lxml_elem.attrib["datatype"]
  assert tu.usagecount == int(full_tu_lxml_elem.attrib["usagecount"])
  assert isinstance(tu.lastusagedate, datetime)
  assert tu.lastusagedate.strftime("%Y%m%dT%H%M%SZ") == full_tu_lxml_elem.attrib["lastusagedate"]
  assert tu.creationtool == full_tu_lxml_elem.attrib["creationtool"]
  assert tu.creationtoolversion == full_tu_lxml_elem.attrib["creationtoolversion"]
  assert isinstance(tu.creationdate, datetime)
  assert tu.creationdate.strftime("%Y%m%dT%H%M%SZ") == full_tu_lxml_elem.attrib["creationdate"]
  assert tu.creationid == full_tu_lxml_elem.attrib["creationid"]
  assert isinstance(tu.changedate, datetime)
  assert tu.changedate.strftime("%Y%m%dT%H%M%SZ") == full_tu_lxml_elem.attrib["changedate"]
  assert tu.segtype.value == full_tu_lxml_elem.attrib["segtype"]
  assert tu.changeid == full_tu_lxml_elem.attrib["changeid"]
  assert tu.o_tmf == full_tu_lxml_elem.attrib["o-tmf"]
  assert tu.srclang == full_tu_lxml_elem.attrib["srclang"]
  assert isinstance(tu.props, list)
  assert isinstance(tu.notes, list)
  assert all(isinstance(prop, Prop) for prop in tu.props)
  assert all(isinstance(note, Note) for note in tu.notes)
  assert tu.variants and all(isinstance(v, Tuv) for v in tu.variants)


def test_parse_tu_from_minimal_element(minimal_tu_lxml_elem: et._Element):
  tu = parse_tu(minimal_tu_lxml_elem)
  assert isinstance(tu, Tu)
  assert tu.variants and len(tu.variants) == 2
  assert tu.tuid is None
  assert tu.o_encoding is None
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
  assert tu.o_tmf is None
  assert tu.srclang is None


def test_parse_tu_incorrect_tag_raises(full_tu_lxml_elem: et._Element):
  full_tu_lxml_elem.tag = "wrong"
  with pytest.raises(ValueError):
    parse_tu(full_tu_lxml_elem)


def test_parse_tu_incorrect_child_ignored(full_tu_lxml_elem: et._Element):
  full_tu_lxml_elem.append(et.Element("ignoreme"))
  parse_tu(full_tu_lxml_elem)


def test_parse_tu_missing_tuvs_returns_empty_variants(minimal_tu_lxml_elem: et._Element):
  for child in list(minimal_tu_lxml_elem.iterchildren("tuv")):
    minimal_tu_lxml_elem.remove(child)
  tu = parse_tu(minimal_tu_lxml_elem)
  assert isinstance(tu, Tu)
  assert tu.variants == []
