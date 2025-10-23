from datetime import datetime

import lxml.etree as et
import pytest

from python_tmx.base.classes import InlineTag, Note, Prop, Tuv
from python_tmx.xml.converters import parse_tuv


def test_parse_tuv_from_full_element(full_tuv_lxml_elem: et._Element):
  tuv = parse_tuv(full_tuv_lxml_elem)
  assert isinstance(tuv, Tuv)
  assert isinstance(tuv.segment, list)
  assert all(isinstance(p, InlineTag) for p in tuv.segment)

  assert tuv.lang == full_tuv_lxml_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
  assert tuv.o_encoding == full_tuv_lxml_elem.attrib["o-encoding"]
  assert tuv.datatype == full_tuv_lxml_elem.attrib["datatype"]
  assert isinstance(tuv.usagecount, int)
  assert tuv.usagecount == int(full_tuv_lxml_elem.attrib["usagecount"])
  assert isinstance(tuv.lastusagedate, datetime)
  assert tuv.lastusagedate.strftime("%Y%m%dT%H%M%SZ") == full_tuv_lxml_elem.attrib["lastusagedate"]
  assert tuv.creationtool == full_tuv_lxml_elem.attrib["creationtool"]
  assert tuv.creationtoolversion == full_tuv_lxml_elem.attrib["creationtoolversion"]
  assert isinstance(tuv.creationdate, datetime)
  assert tuv.creationdate.strftime("%Y%m%dT%H%M%SZ") == full_tuv_lxml_elem.attrib["creationdate"]
  assert tuv.creationid == full_tuv_lxml_elem.attrib["creationid"]
  assert isinstance(tuv.changedate, datetime)
  assert tuv.changedate.strftime("%Y%m%dT%H%M%SZ") == full_tuv_lxml_elem.attrib["changedate"]
  assert tuv.changeid == full_tuv_lxml_elem.attrib["changeid"]
  assert tuv.o_tmf == full_tuv_lxml_elem.attrib["o-tmf"]
  assert isinstance(tuv.props, list)
  assert isinstance(tuv.notes, list)
  assert all(isinstance(prop, Prop) for prop in tuv.props)
  assert all(isinstance(note, Note) for note in tuv.notes)


def test_parse_tuv_from_minimal_element(minimal_tuv_lxml_elem: et._Element):
  tuv = parse_tuv(minimal_tuv_lxml_elem)
  assert isinstance(tuv, Tuv)
  assert isinstance(tuv.segment, list)
  assert len(tuv.segment) == 1
  assert tuv.segment[0].content == minimal_tuv_lxml_elem.find("seg").text
  assert tuv.lang == minimal_tuv_lxml_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
  assert tuv.o_encoding is None
  assert tuv.datatype is None
  assert tuv.usagecount is None
  assert tuv.lastusagedate is None
  assert tuv.creationtool is None
  assert tuv.creationtoolversion is None
  assert tuv.creationdate is None
  assert tuv.creationid is None
  assert tuv.changedate is None
  assert tuv.changeid is None
  assert tuv.o_tmf is None


def test_parse_tuv_incorrect_tag_raises(full_tuv_lxml_elem: et._Element):
  full_tuv_lxml_elem.tag = "wrong"
  with pytest.raises(ValueError):
    parse_tuv(full_tuv_lxml_elem)


def test_parse_tuv_missing_required_lang_raises(full_tuv_lxml_elem: et._Element):
  del full_tuv_lxml_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
  with pytest.raises(KeyError):
    parse_tuv(full_tuv_lxml_elem)


def test_parse_tuv_incorrect_child_ignored(full_tuv_lxml_elem: et._Element):
  full_tuv_lxml_elem.append(et.Element("unknown"))
  parse_tuv(full_tuv_lxml_elem)
