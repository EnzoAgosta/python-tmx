from python_tmx.base.types import Header, Note, Prop
from python_tmx.xml.conversion import element_to_header, element_to_note, element_to_prop

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


class TestElementToDataclass:
  def test_note_element_to_dataclass(self, xml_provider):
    note_element = xml_provider.note_element()
    note_obj = element_to_note(note_element)
    assert isinstance(note_obj, Note)
    assert note_obj.text == note_element.text
    assert note_obj.lang == note_element.attrib.get(XML_LANG)
    assert note_obj.o_encoding == note_element.attrib.get("o-encoding")

  def test_prop_element_to_dataclass(self, xml_provider):
    prop_element = xml_provider.prop_element()
    prop_obj = element_to_prop(prop_element)
    assert isinstance(prop_obj, Prop)
    assert prop_obj.text == prop_element.text
    assert prop_obj.type == prop_element.attrib["type"]
    assert prop_obj.lang == prop_element.attrib.get(XML_LANG)
    assert prop_obj.o_encoding == prop_element.attrib.get("o-encoding")

  def test_header_element_to_dataclass(self, xml_provider):
    header_element = xml_provider.header_element()
    header_obj = element_to_header(header_element)
    assert isinstance(header_obj, Header)
    assert header_obj.creationtool == header_element.attrib["creationtool"]
    assert header_obj.creationtoolversion == header_element.attrib["creationtoolversion"]
    assert header_obj.segtype.value == header_element.attrib["segtype"]
    assert header_obj.o_tmf == header_element.attrib["o-tmf"]
    assert header_obj.adminlang == header_element.attrib["adminlang"]
    assert header_obj.srclang == header_element.attrib["srclang"]
    assert header_obj.datatype == header_element.attrib["datatype"]
    assert header_obj.o_encoding == header_element.attrib.get("o-encoding")
    assert (
      header_obj.creationdate.strftime("%Y%m%dT%H%M%SZ") if header_obj.creationdate is not None else None
    ) == header_element.attrib.get("creationdate")
    assert header_obj.creationid == header_element.attrib.get("creationid")
    assert (
      header_obj.changedate.strftime("%Y%m%dT%H%M%SZ") if header_obj.changedate is not None else None
    ) == header_element.attrib.get("changedate")
    assert header_obj.changeid == header_element.attrib.get("changeid")
    prop_elements = header_element.findall("prop")
    assert len(prop_elements) == len(header_obj.props)
    for prop_element, prop_obj in zip(prop_elements, header_obj.props):
      assert prop_obj.text == prop_element.text
      assert prop_obj.type == prop_element.attrib["type"]
      assert prop_obj.lang == prop_element.attrib.get(XML_LANG)
      assert prop_obj.o_encoding == prop_element.attrib.get("o-encoding")
    note_elements = header_element.findall("note")
    assert len(note_elements) == len(header_obj.notes)
    for note_element, note_obj in zip(note_elements, header_obj.notes):
      assert note_obj.text == note_element.text
      assert note_obj.lang == note_element.attrib.get(XML_LANG)
      assert note_obj.o_encoding == note_element.attrib.get("o-encoding")
