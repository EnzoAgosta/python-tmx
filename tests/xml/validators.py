from typing import Never
from python_tmx.base.types import Bpt, Ept, Header, Hi, It, Note, Ph, Prop, Sub, Tu, Tuv
from python_tmx.xml import XmlElement
from python_tmx.xml.utils import normalize_tag
from tests.providers.xml_provider import XML_LANG


def assert_xml_node_attrib_match_note_object(note_object: Note, xml_node: XmlElement) -> None:
  note_tag = normalize_tag(xml_node.tag)
  assert note_tag == "note"
  assert xml_node.text == note_object.text
  assert xml_node.attrib.get(XML_LANG) == note_object.lang
  assert xml_node.attrib.get("o-encoding") == note_object.o_encoding


def assert_xml_node_attrib_match_prop_object(prop_object: Prop, xml_node: XmlElement) -> None:
  prop_tag = normalize_tag(xml_node.tag)
  assert prop_tag == "prop"
  assert xml_node.text == prop_object.text
  assert xml_node.attrib.get(XML_LANG) == prop_object.lang
  assert xml_node.attrib.get("o-encoding") == prop_object.o_encoding


def assert_xml_node_attrib_match_header_object(header_object: Header, xml_node: XmlElement) -> None:
  header_tag = normalize_tag(xml_node.tag)
  assert header_tag == "header"
  assert xml_node.attrib.get("creationtool") == header_object.creationtool
  assert xml_node.attrib.get("creationtoolversion") == header_object.creationtoolversion
  assert xml_node.attrib.get("creationdate") == (
    header_object.creationdate.strftime("%Y%m%dT%H%M%SZ") if header_object.creationdate is not None else None
  )
  assert xml_node.attrib.get("segtype") == header_object.segtype.value if header_object.segtype is not None else None
  assert xml_node.attrib.get("o-tmf") == header_object.o_tmf
  assert xml_node.attrib.get("adminlang") == header_object.adminlang
  assert xml_node.attrib.get("srclang") == header_object.srclang
  assert xml_node.attrib.get("datatype") == header_object.datatype
  assert xml_node.attrib.get("o-encoding") == header_object.o_encoding
  assert xml_node.attrib.get("changedate") == (
    header_object.changedate.strftime("%Y%m%dT%H%M%SZ") if header_object.changedate is not None else None
  )
  assert xml_node.attrib.get("changeid") == header_object.changeid


def assert_xml_node_attrib_match_tuv_object(tuv_object: Tuv, xml_node: XmlElement) -> None:
  tuv_tag = normalize_tag(xml_node.tag)
  assert tuv_tag == "tuv"
  assert xml_node.attrib.get(XML_LANG) == tuv_object.lang
  assert xml_node.attrib.get("o-encoding") == tuv_object.o_encoding
  assert xml_node.attrib.get("datatype") == tuv_object.datatype
  assert (
    int(xml_node.attrib["usagecount"]) if xml_node.attrib.get("usagecount") is not None else None
  ) == tuv_object.usagecount
  assert xml_node.attrib.get("lastusagedate") == (
    tuv_object.lastusagedate.strftime("%Y%m%dT%H%M%SZ") if tuv_object.lastusagedate is not None else None
  )
  assert xml_node.attrib.get("creationtool") == tuv_object.creationtool
  assert xml_node.attrib.get("creationtoolversion") == tuv_object.creationtoolversion
  assert xml_node.attrib.get("creationdate") == (
    tuv_object.creationdate.strftime("%Y%m%dT%H%M%SZ") if tuv_object.creationdate is not None else None
  )
  assert xml_node.attrib.get("creationid") == tuv_object.creationid
  assert xml_node.attrib.get("changedate") == (
    tuv_object.changedate.strftime("%Y%m%dT%H%M%SZ") if tuv_object.changedate is not None else None
  )
  assert xml_node.attrib.get("changeid") == tuv_object.changeid
  assert xml_node.attrib.get("o-tmf") == tuv_object.o_tmf


def assert_xml_node_attrib_match_tu_object(tu_object: Tu, xml_node: XmlElement) -> None:
  tu_tag = normalize_tag(xml_node.tag)
  assert tu_tag == "tu"
  assert xml_node.attrib.get("tuid") == tu_object.tuid
  assert xml_node.attrib.get("o-encoding") == tu_object.o_encoding
  assert xml_node.attrib.get("datatype") == tu_object.datatype
  assert (
    int(xml_node.attrib["usagecount"]) if xml_node.attrib.get("usagecount") is not None else None
  ) == tu_object.usagecount
  assert xml_node.attrib.get("lastusagedate") == (
    tu_object.lastusagedate.strftime("%Y%m%dT%H%M%SZ") if tu_object.lastusagedate is not None else None
  )
  assert xml_node.attrib.get("creationtool") == tu_object.creationtool
  assert xml_node.attrib.get("creationtoolversion") == tu_object.creationtoolversion
  assert xml_node.attrib.get("creationdate") == (
    tu_object.creationdate.strftime("%Y%m%dT%H%M%SZ") if tu_object.creationdate is not None else None
  )
  assert xml_node.attrib.get("creationid") == tu_object.creationid
  assert xml_node.attrib.get("changedate") == (
    tu_object.changedate.strftime("%Y%m%dT%H%M%SZ") if tu_object.changedate is not None else None
  )
  assert xml_node.attrib.get("segtype") == (tu_object.segtype.value if tu_object.segtype is not None else None)
  assert xml_node.attrib.get("changeid") == tu_object.changeid
  assert xml_node.attrib.get("o-tmf") == tu_object.o_tmf
  assert xml_node.attrib.get("srclang") == tu_object.srclang


def assert_xml_node_attrib_match_bpt_object(bpt_object: Bpt, xml_node: XmlElement) -> None:
  bpt_tag = normalize_tag(xml_node.tag)
  assert bpt_tag == "bpt"
  assert int(xml_node.attrib["i"]) == bpt_object.i
  assert (int(xml_node.attrib["x"]) if xml_node.attrib.get("x") is not None else None) == bpt_object.x
  assert xml_node.attrib.get("type") == bpt_object.type


def assert_xml_node_attrib_match_ept_object(ept_object: Ept, xml_node: XmlElement) -> None:
  ept_tag = normalize_tag(xml_node.tag)
  assert ept_tag == "ept"
  assert int(xml_node.attrib["i"]) == ept_object.i


def assert_xml_node_attrib_match_it_object(it_object: It, xml_node: XmlElement) -> None:
  it_tag = normalize_tag(xml_node.tag)
  assert it_tag == "it"
  assert xml_node.attrib["pos"] == it_object.pos.value
  assert (int(xml_node.attrib["x"]) if xml_node.attrib.get("x") is not None else None) == it_object.x
  assert xml_node.attrib.get("type") == it_object.type


def assert_xml_node_attrib_match_sub_object(sub_object: Sub, xml_node: XmlElement) -> None:
  sub_tag = normalize_tag(xml_node.tag)
  assert sub_tag == "sub"
  assert xml_node.attrib.get("datatype") == sub_object.datatype
  assert xml_node.attrib.get("type") == sub_object.type


def assert_xml_node_attrib_match_ph_object(ph_object: Ph, xml_node: XmlElement) -> None:
  ph_tag = normalize_tag(xml_node.tag)
  assert ph_tag == "ph"
  assert (int(xml_node.attrib["x"]) if xml_node.attrib.get("x") is not None else None) == ph_object.x
  assert xml_node.attrib.get("type") == ph_object.type
  assert xml_node.attrib.get("assoc") == (ph_object.assoc.value if ph_object.assoc is not None else None)


def assert_xml_node_attrib_match_hi_object(hi_object: Hi, xml_node: XmlElement) -> None:
  hi_tag = normalize_tag(xml_node.tag)
  assert hi_tag == "hi"
  assert (int(xml_node.attrib["x"]) if xml_node.attrib.get("x") is not None else None) == hi_object.x
  assert xml_node.attrib.get("type") == hi_object.type


def assert_content_matches_xml(
  xml_elem: XmlElement,
  content: list,
  sub_only: bool,
) -> None:
  if xml_elem.text is None and not len(xml_elem):
    assert len(content) == 0
    return
  if xml_elem.text is not None:
    assert xml_elem.text == content[0]
  content_iter = iter(content[1:] if xml_elem.text is not None else content)
  for child in xml_elem:
    tag = normalize_tag(child.tag)
    item = next(content_iter, None)
    assert item is not None
    match tag:
      case "sub":
        assert isinstance(item, Sub)
        assert sub_only
        assert_xml_node_attrib_match_sub_object(item, child)
        assert_content_matches_xml(child, item.content, sub_only=False)
      case "bpt":
        assert isinstance(item, Bpt)
        assert not sub_only
        assert_xml_node_attrib_match_bpt_object(item, child)
        assert_content_matches_xml(child, item.content, sub_only=True)
      case "ept":
        assert isinstance(item, Ept)
        assert not sub_only
        assert_xml_node_attrib_match_ept_object(item, child)
        assert_content_matches_xml(child, item.content, sub_only=True)
      case "it":
        assert isinstance(item, It)
        assert not sub_only
        assert_xml_node_attrib_match_it_object(item, child)
        assert_content_matches_xml(child, item.content, sub_only=True)
      case "ph":
        assert isinstance(item, Ph)
        assert not sub_only
        assert_xml_node_attrib_match_ph_object(item, child)
        assert_content_matches_xml(child, item.content, sub_only=True)
      case "hi":
        assert isinstance(item, Hi)
        assert not sub_only
        assert_xml_node_attrib_match_hi_object(item, child)
        assert_content_matches_xml(child, item.content, sub_only=False)
      case _:
        assert Never
    if child.tail is not None:
      tail = next(content_iter, None)
      assert tail == child.tail
  remaining = list(content_iter)
  assert len(remaining) == 0
