from python_tmx.xml.conversion import (
  bpt_to_element,
  dataclass_to_xml_element,
  ept_to_element,
  header_to_element,
  hi_to_element,
  it_to_element,
  note_to_element,
  ph_to_element,
  prop_to_element,
  sub_to_element,
  tmx_to_element,
  tu_to_element,
  tuv_to_element,
)
from python_tmx.xml.utils import normalize_tag
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


class TestDataclassToElement:
  def test_note_dataclass_to_element(self, element_provider):
    note_obj = element_provider.note()
    note_element = note_to_element(note_obj, backend=element_provider.backend)
    assert isinstance(note_element, element_provider.backend)
    assert_xml_node_attrib_match_note_object(note_obj, note_element)

  def test_prop_element_to_dataclass(self, element_provider):
    prop_obj = element_provider.prop()
    prop_element = prop_to_element(prop_obj, backend=element_provider.backend)
    assert isinstance(prop_element, element_provider.backend)
    assert_xml_node_attrib_match_prop_object(prop_obj, prop_element)

  def test_header_element_to_dataclass(self, element_provider):
    header_obj = element_provider.header()
    header_element = header_to_element(header_obj, backend=element_provider.backend)
    assert isinstance(header_element, element_provider.backend)
    assert_xml_node_attrib_match_header_object(header_obj, header_element)
    prop_elements = header_element.findall("prop")
    for prop_element, prop_obj in zip(prop_elements, header_obj.props, strict=True):
      assert_xml_node_attrib_match_prop_object(prop_obj, prop_element)
    note_elements = header_element.findall("note")
    for note_element, note_obj in zip(note_elements, header_obj.notes, strict=True):
      assert_xml_node_attrib_match_note_object(note_obj, note_element)

  def test_tuv_element_to_dataclass(self, element_provider):
    tuv_obj = element_provider.tuv()
    tuv_element = tuv_to_element(tuv_obj, backend=element_provider.backend)
    assert isinstance(tuv_element, element_provider.backend)
    assert_xml_node_attrib_match_tuv_object(tuv_obj, tuv_element)
    prop_elements = tuv_element.findall("prop")
    for prop_element, prop_obj in zip(prop_elements, tuv_obj.props, strict=True):
      assert_xml_node_attrib_match_prop_object(prop_obj, prop_element)
    note_elements = tuv_element.findall("note")
    for note_element, note_obj in zip(note_elements, tuv_obj.notes, strict=True):
      assert_xml_node_attrib_match_note_object(note_obj, note_element)
    seg_elem = tuv_element.find("seg")
    assert seg_elem is not None
    assert_content_matches_xml(seg_elem, tuv_obj.content, sub_only=False)

  def test_tu_to_element(self, element_provider):
    tu_obj = element_provider.tu()
    tu_element = tu_to_element(tu_obj, backend=element_provider.backend)
    assert isinstance(tu_element, element_provider.backend)
    assert_xml_node_attrib_match_tu_object(tu_obj, tu_element)
    prop_elements = tu_element.findall("prop")
    for prop_element, prop_obj in zip(prop_elements, tu_obj.props, strict=True):
      assert_xml_node_attrib_match_prop_object(prop_obj, prop_element)
    note_elements = tu_element.findall("note")
    for note_element, note_obj in zip(note_elements, tu_obj.notes, strict=True):
      assert_xml_node_attrib_match_note_object(note_obj, note_element)
    tuv_elements = tu_element.findall("tuv")
    for tuv_element, tuv_obj in zip(tuv_elements, tu_obj.variants, strict=True):
      assert_xml_node_attrib_match_tuv_object(tuv_obj, tuv_element)

  def test_tmx_to_element(self, element_provider):
    tmx_obj = element_provider.tmx()
    tmx_element = tmx_to_element(tmx_obj, backend=element_provider.backend)
    assert isinstance(tmx_element, element_provider.backend)
    assert tmx_obj.version == tmx_element.attrib["version"]
    header_element = tmx_element.find("header")
    assert header_element is not None
    assert_xml_node_attrib_match_header_object(tmx_obj.header, header_element)
    header_prop_elements = header_element.findall("prop")
    for header_prop_element, header_prop_obj in zip(header_prop_elements, tmx_obj.header.props, strict=True):
      assert_xml_node_attrib_match_prop_object(header_prop_obj, header_prop_element)
    header_note_elements = header_element.findall("note")
    for header_note_element, header_note_obj in zip(header_note_elements, tmx_obj.header.notes, strict=True):
      assert_xml_node_attrib_match_note_object(header_note_obj, header_note_element)
    body_element = tmx_element.find("body")
    assert body_element is not None
    body_tu_elements = body_element.findall("tu")
    assert len(body_tu_elements) == len(tmx_obj.body)
    for body_tu_element, body_tu_obj in zip(body_tu_elements, tmx_obj.body, strict=True):
      assert_xml_node_attrib_match_tu_object(body_tu_obj, body_tu_element)
      body_tu_prop_elements = body_tu_element.findall("prop")
      for body_tu_prop_element, body_tu_prop_obj in zip(body_tu_prop_elements, body_tu_obj.props, strict=True):
        assert_xml_node_attrib_match_prop_object(body_tu_prop_obj, body_tu_prop_element)
      body_tu_note_elements = body_tu_element.findall("note")
      for body_tu_note_element, body_tu_note_obj in zip(body_tu_note_elements, body_tu_obj.notes, strict=True):
        assert_xml_node_attrib_match_note_object(body_tu_note_obj, body_tu_note_element)
      body_tuv_elements = body_tu_element.findall("tuv")
      for body_tuv_element, body_tuv_obj in zip(body_tuv_elements, body_tu_obj.variants, strict=True):
        assert_xml_node_attrib_match_tuv_object(body_tuv_obj, body_tuv_element)
        body_tuv_prop_elements = body_tuv_element.findall("prop")
        for body_tuv_prop_element, body_tuv_prop_obj in zip(body_tuv_prop_elements, body_tuv_obj.props, strict=True):
          assert_xml_node_attrib_match_prop_object(body_tuv_prop_obj, body_tuv_prop_element)
        body_tuv_note_elements = body_tuv_element.findall("note")
        for body_tuv_note_element, body_tuv_note_obj in zip(body_tuv_note_elements, body_tuv_obj.notes, strict=True):
          assert_xml_node_attrib_match_note_object(body_tuv_note_obj, body_tuv_note_element)

  def test_bpt_to_element(self, element_provider):
    bpt_obj = element_provider.bpt()
    bpt_element = bpt_to_element(bpt_obj, backend=element_provider.backend)
    assert isinstance(bpt_element, element_provider.backend)
    assert_xml_node_attrib_match_bpt_object(bpt_obj, bpt_element)
    assert_content_matches_xml(bpt_element, bpt_obj.content, sub_only=True)

  def test_ept_to_element(self, element_provider):
    ept_obj = element_provider.ept()
    ept_element = ept_to_element(ept_obj, backend=element_provider.backend)
    assert isinstance(ept_element, element_provider.backend)
    assert_xml_node_attrib_match_ept_object(ept_obj, ept_element)
    assert_content_matches_xml(ept_element, ept_obj.content, sub_only=True)

  def test_it_to_element(self, element_provider):
    it_obj = element_provider.it()
    it_element = it_to_element(it_obj, backend=element_provider.backend)
    assert isinstance(it_element, element_provider.backend)
    assert_xml_node_attrib_match_it_object(it_obj, it_element)
    assert_content_matches_xml(it_element, it_obj.content, sub_only=True)

  def test_sub_to_element(self, element_provider):
    sub_obj = element_provider.sub()
    sub_element = sub_to_element(sub_obj, backend=element_provider.backend)
    assert isinstance(sub_element, element_provider.backend)
    assert_xml_node_attrib_match_sub_object(sub_obj, sub_element)
    assert_content_matches_xml(sub_element, sub_obj.content, sub_only=False)

  def test_ph_to_element(self, element_provider):
    ph_obj = element_provider.ph()
    ph_element = ph_to_element(ph_obj, backend=element_provider.backend)
    assert isinstance(ph_element, element_provider.backend)
    assert_xml_node_attrib_match_ph_object(ph_obj, ph_element)
    assert_content_matches_xml(ph_element, ph_obj.content, sub_only=True)

  def test_hi_to_element(self, element_provider):
    hi_obj = element_provider.hi()
    hi_element = hi_to_element(hi_obj, backend=element_provider.backend)
    assert isinstance(hi_element, element_provider.backend)
    assert_xml_node_attrib_match_hi_object(hi_obj, hi_element)
    assert_content_matches_xml(hi_element, hi_obj.content, sub_only=False)

  def test_dataclass_to_element(self, element_provider):
    elements = {
      element_provider.bpt,
      element_provider.ept,
      element_provider.it,
      element_provider.sub,
      element_provider.ph,
      element_provider.hi,
      element_provider.note,
      element_provider.prop,
      element_provider.tuv,
      element_provider.tu,
      element_provider.header,
      element_provider.tmx,
    }
    for item in elements:
      base_object = item()
      element = dataclass_to_xml_element(base_object, backend=element_provider.backend)
      assert isinstance(element, element_provider.backend)
      assert normalize_tag(tag=element.tag) == base_object.__class__.__name__.lower()
