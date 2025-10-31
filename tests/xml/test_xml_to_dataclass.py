from python_tmx.base.types import Bpt, Ept, Header, Hi, It, Note, Ph, Prop, Sub, Tmx, Tu, Tuv
from python_tmx.xml.conversion import (
  element_to_bpt,
  element_to_ept,
  element_to_header,
  element_to_hi,
  element_to_it,
  element_to_note,
  element_to_ph,
  element_to_prop,
  element_to_sub,
  element_to_tmx,
  element_to_tu,
  element_to_tuv,
  xml_element_to_dataclass,
)
from tests.xml.validators import (
  assert_content_matches_xml,
  assert_xml_node_attrib_match_bpt_object,
  assert_xml_node_attrib_match_ept_object,
  assert_xml_node_attrib_match_header_object,
  assert_xml_node_attrib_match_hi_object,
  assert_xml_node_attrib_match_it_object,
  assert_xml_node_attrib_match_note_object,
  assert_xml_node_attrib_match_ph_object,
  assert_xml_node_attrib_match_prop_object,
  assert_xml_node_attrib_match_sub_object,
  assert_xml_node_attrib_match_tu_object,
  assert_xml_node_attrib_match_tuv_object,
)

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


class TestElementToDataclass:
  def test_note_element_to_dataclass(self, xml_provider):
    note_element = xml_provider.note_element()
    note_obj = element_to_note(note_element)
    assert isinstance(note_obj, Note)
    assert_xml_node_attrib_match_note_object(note_obj, note_element)

  def test_prop_element_to_dataclass(self, xml_provider):
    prop_element = xml_provider.prop_element()
    prop_obj = element_to_prop(prop_element)
    assert isinstance(prop_obj, Prop)
    assert_xml_node_attrib_match_prop_object(prop_obj, prop_element)

  def test_header_element_to_dataclass(self, xml_provider):
    header_element = xml_provider.header_element()
    header_obj = element_to_header(header_element)
    assert isinstance(header_obj, Header)
    assert_xml_node_attrib_match_header_object(header_obj, header_element)
    prop_elements = header_element.findall("prop")
    for prop_element, prop_obj in zip(prop_elements, header_obj.props, strict=True):
      assert isinstance(prop_obj, Prop)
      assert_xml_node_attrib_match_prop_object(prop_obj, prop_element)
    note_elements = header_element.findall("note")
    for note_element, note_obj in zip(note_elements, header_obj.notes, strict=True):
      assert isinstance(note_obj, Note)
      assert_xml_node_attrib_match_note_object(note_obj, note_element)

  def test_tuv_element_to_dataclass(self, xml_provider):
    tuv_element = xml_provider.tuv_element()
    tuv_obj = element_to_tuv(tuv_element)
    assert isinstance(tuv_obj, Tuv)
    assert_xml_node_attrib_match_tuv_object(tuv_obj, tuv_element)
    prop_elements = tuv_element.findall("prop")
    for prop_element, prop_obj in zip(prop_elements, tuv_obj.props, strict=True):
      assert isinstance(prop_obj, Prop)
      assert_xml_node_attrib_match_prop_object(prop_obj, prop_element)
    note_elements = tuv_element.findall("note")
    for note_element, note_obj in zip(note_elements, tuv_obj.notes, strict=True):
      assert isinstance(note_obj, Note)
      assert_xml_node_attrib_match_note_object(note_obj, note_element)
    seg_elem = tuv_element.find("seg")
    assert seg_elem is not None
    assert_content_matches_xml(seg_elem, tuv_obj.content, sub_only=False)

  def test_tu_to_element(self, xml_provider):
    tu_element = xml_provider.tu_element()
    tu_obj = element_to_tu(tu_element)
    assert isinstance(tu_obj, Tu)
    assert_xml_node_attrib_match_tu_object(tu_obj, tu_element)
    prop_elements = tu_element.findall("prop")
    for prop_element, prop_obj in zip(prop_elements, tu_obj.props, strict=True):
      assert isinstance(prop_obj, Prop)
      assert_xml_node_attrib_match_prop_object(prop_obj, prop_element)
    note_elements = tu_element.findall("note")
    for note_element, note_obj in zip(note_elements, tu_obj.notes, strict=True):
      assert isinstance(note_obj, Note)
      assert_xml_node_attrib_match_note_object(note_obj, note_element)
    tuv_elements = tu_element.findall("tuv")
    for tuv_element, tuv_obj in zip(tuv_elements, tu_obj.variants, strict=True):
      assert isinstance(tuv_obj, Tuv)
      assert_xml_node_attrib_match_tuv_object(tuv_obj, tuv_element)

  def test_tmx_to_element(self, xml_provider):
    tmx_element = xml_provider.tmx_element()
    tmx_obj = element_to_tmx(tmx_element)
    assert isinstance(tmx_obj, Tmx)
    assert tmx_obj.version == tmx_element.attrib["version"]
    header_element = tmx_element.find("header")
    assert header_element is not None
    assert_xml_node_attrib_match_header_object(tmx_obj.header, header_element)
    header_prop_elements = header_element.findall("prop")
    for header_prop_element, header_prop_obj in zip(header_prop_elements, tmx_obj.header.props, strict=True):
      assert isinstance(header_prop_obj, Prop)
      assert_xml_node_attrib_match_prop_object(header_prop_obj, header_prop_element)
    header_note_elements = header_element.findall("note")
    for header_note_element, header_note_obj in zip(header_note_elements, tmx_obj.header.notes, strict=True):
      assert isinstance(header_note_obj, Note)
      assert_xml_node_attrib_match_note_object(header_note_obj, header_note_element)
    body_element = tmx_element.find("body")
    assert body_element is not None
    body_tu_elements = body_element.findall("tu")
    assert len(body_tu_elements) == len(tmx_obj.body)
    for body_tu_element, body_tu_obj in zip(body_tu_elements, tmx_obj.body, strict=True):
      assert isinstance(body_tu_obj, Tu)
      assert_xml_node_attrib_match_tu_object(body_tu_obj, body_tu_element)
      body_tu_prop_elements = body_tu_element.findall("prop")
      for body_tu_prop_element, body_tu_prop_obj in zip(body_tu_prop_elements, body_tu_obj.props, strict=True):
        assert isinstance(body_tu_prop_obj, Prop)
        assert_xml_node_attrib_match_prop_object(body_tu_prop_obj, body_tu_prop_element)
      body_tu_note_elements = body_tu_element.findall("note")
      for body_tu_note_element, body_tu_note_obj in zip(body_tu_note_elements, body_tu_obj.notes, strict=True):
        assert isinstance(body_tu_note_obj, Note)
        assert_xml_node_attrib_match_note_object(body_tu_note_obj, body_tu_note_element)
      body_tuv_elements = body_tu_element.findall("tuv")
      for body_tuv_element, body_tuv_obj in zip(body_tuv_elements, body_tu_obj.variants, strict=True):
        assert isinstance(body_tuv_obj, Tuv)
        assert_xml_node_attrib_match_tuv_object(body_tuv_obj, body_tuv_element)
        body_tuv_prop_elements = body_tuv_element.findall("prop")
        for body_tuv_prop_element, body_tuv_prop_obj in zip(body_tuv_prop_elements, body_tuv_obj.props, strict=True):
          assert isinstance(body_tuv_prop_obj, Prop)
          assert_xml_node_attrib_match_prop_object(body_tuv_prop_obj, body_tuv_prop_element)
        body_tuv_note_elements = body_tuv_element.findall("note")
        for body_tuv_note_element, body_tuv_note_obj in zip(body_tuv_note_elements, body_tuv_obj.notes, strict=True):
          assert isinstance(body_tuv_note_obj, Note)
          assert_xml_node_attrib_match_note_object(body_tuv_note_obj, body_tuv_note_element)

  def test_bpt_to_element(self, xml_provider):
    bpt_element = xml_provider.bpt_element()
    bpt_obj = element_to_bpt(bpt_element)
    assert isinstance(bpt_obj, Bpt)
    assert_xml_node_attrib_match_bpt_object(bpt_obj, bpt_element)
    assert_content_matches_xml(bpt_element, bpt_obj.content, sub_only=True)

  def test_ept_to_element(self, xml_provider):
    ept_element = xml_provider.ept_element()
    ept_obj = element_to_ept(ept_element)
    assert isinstance(ept_obj, Ept)
    assert_xml_node_attrib_match_ept_object(ept_obj, ept_element)
    assert_content_matches_xml(ept_element, ept_obj.content, sub_only=True)

  def test_it_to_element(self, xml_provider):
    it_element = xml_provider.it_element()
    it_obj = element_to_it(it_element)
    assert isinstance(it_obj, It)
    assert_xml_node_attrib_match_it_object(it_obj, it_element)
    assert_content_matches_xml(it_element, it_obj.content, sub_only=True)

  def test_sub_to_element(self, xml_provider):
    sub_element = xml_provider.sub_element()
    sub_obj = element_to_sub(sub_element)
    assert isinstance(sub_obj, Sub)
    assert_xml_node_attrib_match_sub_object(sub_obj, sub_element)
    assert_content_matches_xml(sub_element, sub_obj.content, sub_only=False)

  def test_ph_to_element(self, xml_provider):
    ph_element = xml_provider.ph_element()
    ph_obj = element_to_ph(ph_element)
    assert isinstance(ph_obj, Ph)
    assert_xml_node_attrib_match_ph_object(ph_obj, ph_element)
    assert_content_matches_xml(ph_element, ph_obj.content, sub_only=True)

  def test_hi_to_element(self, xml_provider):
    hi_element = xml_provider.hi_element()
    hi_obj = element_to_hi(hi_element)
    assert isinstance(hi_obj, Hi)
    assert_xml_node_attrib_match_hi_object(hi_obj, hi_element)
    assert_content_matches_xml(hi_element, hi_obj.content, sub_only=False)

  def test_element_to_dataclass(self, xml_provider):
    elements = {
      xml_provider.bpt_element: Bpt, 
      xml_provider.ept_element: Ept, 
      xml_provider.it_element: It, 
      xml_provider.sub_element: Sub, 
      xml_provider.ph_element: Ph, 
      xml_provider.hi_element: Hi, 
      xml_provider.note_element: Note, 
      xml_provider.prop_element: Prop, 
      xml_provider.tuv_element: Tuv, 
      xml_provider.tu_element: Tu, 
      xml_provider.header_element: Header, 
      xml_provider.tmx_element: Tmx, 
    }
    for xml_element, dataclass in elements.items():
      obj = xml_element_to_dataclass(xml_element())
      assert isinstance(obj, dataclass)