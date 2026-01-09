import pytest
import xml.etree.ElementTree as et
from hypomnema.xml.backends.standard import StandardBackend
from hypomnema.xml.utils import QName


class TestStandardXmlBackendHappy:
  """Tests for the successful execution of StandardBackend methods."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.backend = StandardBackend()
    self.mocker = mocker

  def test_create_element_simple_tag(self):
    """Test creating an element with a simple tag name."""
    elem = self.backend.create_element("root")
    assert isinstance(elem, et.Element)
    assert self.backend.get_tag(elem) == "root"

  def test_create_element_with_attributes(self):
    """Test creating an element with attributes."""
    elem = self.backend.create_element("root", attributes={"id": "1", "class": "test"})
    assert self.backend.get_attribute(elem, "id") == "1"
    assert self.backend.get_attribute(elem, "class") == "test"

  def test_create_element_namespaced_clark_notation(self):
    """Test creating an element with namespace in Clark notation."""
    ns = "http://example.com"
    tag = f"{{{ns}}}root"
    elem = self.backend.create_element(tag)
    assert self.backend.get_tag(elem) == tag

  def test_create_element_namespaced_prefix(self):
    """Test creating an element with namespace using prefix."""
    self.backend.register_namespace("ex", "http://example.com")
    elem = self.backend.create_element("ex:root")
    assert self.backend.get_tag(elem) == "{http://example.com}root"

  def test_create_element_with_qname_object(self):
    """Test creating an element using a QName object."""
    qname = QName("{http://example.com}root", self.backend._global_nsmap)
    elem = self.backend.create_element(qname)
    assert self.backend.get_tag(elem) == "{http://example.com}root"

  def test_get_tag_simple(self):
    """Test getting a simple tag."""
    elem = self.backend.create_element("root")
    assert self.backend.get_tag(elem) == "root"

  def test_get_tag_namespaced(self):
    """Test getting a namespaced tag."""
    elem = self.backend.create_element("{http://example.com}root")
    assert self.backend.get_tag(elem) == "{http://example.com}root"

  def test_get_tag_as_qname(self):
    """Test getting tag as QName object."""
    elem = self.backend.create_element("{http://example.com}root")
    qname = self.backend.get_tag(elem, as_qname=True)
    assert isinstance(qname, QName)
    assert qname.uri == "http://example.com"
    assert qname.local_name == "root"

  def test_get_tag_as_qname_simple(self):
    """Test getting simple tag as QName object."""
    elem = self.backend.create_element("root")
    qname = self.backend.get_tag(elem, as_qname=True)
    assert isinstance(qname, QName)
    assert qname.uri is None
    assert qname.local_name == "root"

  def test_get_text_initial_none(self):
    """Test that initial text is None."""
    elem = self.backend.create_element("root")
    assert self.backend.get_text(elem) is None

  def test_set_text_and_get_text(self):
    """Test setting and getting text."""
    elem = self.backend.create_element("root")
    self.backend.set_text(elem, "Hello, World!")
    assert self.backend.get_text(elem) == "Hello, World!"

  def test_set_text_to_none(self):
    """Test setting text to None clears it."""
    elem = self.backend.create_element("root")
    self.backend.set_text(elem, "content")
    self.backend.set_text(elem, None)
    assert self.backend.get_text(elem) is None

  def test_set_text_empty_string(self):
    """Test setting text to empty string."""
    elem = self.backend.create_element("root")
    self.backend.set_text(elem, "")
    assert self.backend.get_text(elem) == ""

  def test_get_tail_initial_none(self):
    """Test that initial tail is None."""
    elem = self.backend.create_element("root")
    assert self.backend.get_tail(elem) is None

  def test_set_tail_and_get_tail(self):
    """Test setting and getting tail."""
    elem = self.backend.create_element("root")
    self.backend.set_tail(elem, " tail text")
    assert self.backend.get_tail(elem) == " tail text"

  def test_set_tail_to_none(self):
    """Test setting tail to None clears it."""
    elem = self.backend.create_element("root")
    self.backend.set_tail(elem, "tail")
    self.backend.set_tail(elem, None)
    assert self.backend.get_tail(elem) is None

  def test_get_attribute_existing(self):
    """Test getting an existing attribute."""
    elem = self.backend.create_element("root", attributes={"key": "value"})
    assert self.backend.get_attribute(elem, "key") == "value"

  def test_get_attribute_missing_returns_none(self):
    """Test getting a missing attribute returns None."""
    elem = self.backend.create_element("root")
    assert self.backend.get_attribute(elem, "missing") is None

  def test_get_attribute_missing_returns_default(self):
    """Test getting a missing attribute returns default."""
    elem = self.backend.create_element("root")
    assert self.backend.get_attribute(elem, "missing", default="default") == "default"

  def test_set_attribute_new(self):
    """Test setting a new attribute."""
    elem = self.backend.create_element("root")
    self.backend.set_attribute(elem, "key", "value")
    assert self.backend.get_attribute(elem, "key") == "value"

  def test_set_attribute_overwrite(self):
    """Test overwriting an existing attribute."""
    elem = self.backend.create_element("root", attributes={"key": "old"})
    self.backend.set_attribute(elem, "key", "new")
    assert self.backend.get_attribute(elem, "key") == "new"

  def test_set_attribute_to_none_removes(self):
    """Test setting attribute to None removes it."""
    elem = self.backend.create_element("root", attributes={"key": "value"})
    self.backend.set_attribute(elem, "key", None)
    assert self.backend.get_attribute(elem, "key") is None

  def test_set_attribute_namespaced(self):
    """Test setting a namespaced attribute."""
    elem = self.backend.create_element("root")
    self.backend.set_attribute(elem, "{http://www.w3.org/XML/1998/namespace}lang", "en")
    assert self.backend.get_attribute(elem, "xml:lang") == "en"

  def test_get_attribute_map_empty(self):
    """Test getting attribute map from element with no attributes."""
    elem = self.backend.create_element("root")
    assert self.backend.get_attribute_map(elem) == {}

  def test_get_attribute_map_with_attributes(self):
    """Test getting attribute map from element with attributes."""
    elem = self.backend.create_element("root", attributes={"a": "1", "b": "2"})
    attr_map = self.backend.get_attribute_map(elem)
    assert attr_map == {"a": "1", "b": "2"}

  def test_append_child_single(self):
    """Test appending a single child."""
    parent = self.backend.create_element("parent")
    child = self.backend.create_element("child")
    self.backend.append_child(parent, child)

    children = list(self.backend.iter_children(parent))
    assert len(children) == 1
    assert self.backend.get_tag(children[0]) == "child"

  def test_append_child_multiple(self):
    """Test appending multiple children."""
    parent = self.backend.create_element("parent")
    child1 = self.backend.create_element("child1")
    child2 = self.backend.create_element("child2")
    self.backend.append_child(parent, child1)
    self.backend.append_child(parent, child2)

    children = list(self.backend.iter_children(parent))
    assert len(children) == 2
    assert self.backend.get_tag(children[0]) == "child1"
    assert self.backend.get_tag(children[1]) == "child2"

  def test_iter_children_empty(self):
    """Test iterating children of element with no children."""
    parent = self.backend.create_element("parent")
    children = list(self.backend.iter_children(parent))
    assert children == []

  def test_iter_children_with_filter_single_tag(self):
    """Test iterating children with single tag filter."""
    parent = self.backend.create_element("parent")
    self.backend.append_child(parent, self.backend.create_element("a"))
    self.backend.append_child(parent, self.backend.create_element("b"))
    self.backend.append_child(parent, self.backend.create_element("a"))

    filtered = list(self.backend.iter_children(parent, tag_filter="a"))
    assert len(filtered) == 2
    for child in filtered:
      assert self.backend.get_tag(child) == "a"

  def test_iter_children_with_filter_multiple_tags(self):
    """Test iterating children with multiple tag filter."""
    parent = self.backend.create_element("parent")
    self.backend.append_child(parent, self.backend.create_element("a"))
    self.backend.append_child(parent, self.backend.create_element("b"))
    self.backend.append_child(parent, self.backend.create_element("c"))

    filtered = list(self.backend.iter_children(parent, tag_filter=["a", "c"]))
    assert len(filtered) == 2
    tags = [self.backend.get_tag(c) for c in filtered]
    assert "a" in tags
    assert "c" in tags

  def test_clear_removes_children(self):
    """Test that clear removes children."""
    parent = self.backend.create_element("parent")
    child = self.backend.create_element("child")
    self.backend.append_child(parent, child)

    self.backend.clear(parent)
    assert list(self.backend.iter_children(parent)) == []

  def test_clear_removes_text(self):
    """Test that clear removes text."""
    elem = self.backend.create_element("root")
    self.backend.set_text(elem, "content")

    self.backend.clear(elem)
    assert self.backend.get_text(elem) is None

  def test_clear_removes_attributes(self):
    """Test that clear removes attributes."""
    elem = self.backend.create_element("root", attributes={"key": "value"})

    self.backend.clear(elem)
    assert self.backend.get_attribute_map(elem) == {}

  def test_to_bytes_simple_element(self):
    """Test converting a simple element to bytes."""
    elem = self.backend.create_element("root")
    result = self.backend.to_bytes(elem)
    assert b"<root" in result
    assert b"</root>" in result

  def test_to_bytes_with_text(self):
    """Test converting an element with text to bytes."""
    elem = self.backend.create_element("root")
    self.backend.set_text(elem, "Hello")
    result = self.backend.to_bytes(elem)
    assert b">Hello</root>" in result

  def test_to_bytes_with_attributes(self):
    """Test converting an element with attributes to bytes."""
    elem = self.backend.create_element("root", attributes={"id": "1"})
    result = self.backend.to_bytes(elem)
    assert b'id="1"' in result

  def test_to_bytes_self_closing_false(self):
    """Test that empty elements are not self-closing by default."""
    elem = self.backend.create_element("root")
    result = self.backend.to_bytes(elem, self_closing=False)
    assert b"<root></root>" in result

  def test_to_bytes_self_closing_true(self):
    """Test that empty elements can be self-closing."""
    elem = self.backend.create_element("root")
    result = self.backend.to_bytes(elem, self_closing=True)
    assert b"<root />" in result or b"<root/>" in result

  def test_write_and_parse_roundtrip(self, tmp_path):
    """Test writing and parsing an XML file."""
    output_file = tmp_path / "test.xml"

    root = self.backend.create_element("root")
    child = self.backend.create_element("child")
    self.backend.set_text(child, "content")
    self.backend.append_child(root, child)

    self.backend.write(root, output_file)
    assert output_file.exists()

    parsed_root = self.backend.parse(output_file)
    assert self.backend.get_tag(parsed_root) == "root"
    children = list(self.backend.iter_children(parsed_root))
    assert len(children) == 1
    assert self.backend.get_text(children[0]) == "content"

  def test_iterparse_yields_elements(self, tmp_path):
    """Test that iterparse yields elements."""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text('<?xml version="1.0"?><root><child>A</child><child>B</child></root>')

    elements = list(self.backend.iterparse(xml_file, tag_filter="child"))
    assert len(elements) == 2

  def test_iterparse_with_no_filter(self, tmp_path):
    """Test iterparse without filter yields all elements."""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text('<?xml version="1.0"?><root><a/><b/></root>')

    elements = list(self.backend.iterparse(xml_file))
    assert len(elements) >= 2


class TestStandardXmlBackendError:
  """Tests for error conditions in StandardBackend methods."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.backend = StandardBackend()
    self.mocker = mocker

  def test_create_element_invalid_tag_type(self):
    """Test that invalid tag type raises TypeError."""
    with pytest.raises(TypeError, match="Unexpected tag type"):
      self.backend.create_element(123)

  def test_create_element_invalid_attribute_value_type(self):
    """Test that non-string attribute value raises TypeError."""
    with pytest.raises(TypeError, match="Unexpected value type"):
      self.backend.create_element("root", attributes={"key": 123})

  def test_append_child_invalid_parent(self):
    """Test that invalid parent type raises TypeError."""
    child = self.backend.create_element("child")
    with pytest.raises(TypeError, match="Parent is not an xml.ElementTree.Element"):
      self.backend.append_child("not_an_element", child)

  def test_append_child_invalid_child(self):
    """Test that invalid child type raises TypeError."""
    parent = self.backend.create_element("parent")
    with pytest.raises(TypeError, match="Child is not an xml.ElementTree.Element"):
      self.backend.append_child(parent, "not_an_element")

  def test_get_attribute_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      self.backend.get_attribute("not_an_element", "key")

  def test_get_attribute_invalid_attribute_name_type(self):
    """Test that invalid attribute name type raises TypeError."""
    elem = self.backend.create_element("root")
    with pytest.raises(TypeError, match="Unexpected attribute name type"):
      self.backend.get_attribute(elem, 123)

  def test_set_attribute_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      self.backend.set_attribute("not_an_element", "key", "value")

  def test_get_attribute_map_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      self.backend.get_attribute_map("not_an_element")

  def test_get_text_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      self.backend.get_text("not_an_element")

  def test_set_text_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      self.backend.set_text("not_an_element", "text")

  def test_get_tail_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      self.backend.get_tail("not_an_element")

  def test_set_tail_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      self.backend.set_tail("not_an_element", "tail")

  def test_iter_children_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      list(self.backend.iter_children("not_an_element"))

  def test_clear_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      self.backend.clear("not_an_element")

  def test_to_bytes_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      self.backend.to_bytes("not_an_element")

  def test_write_invalid_element(self):
    """Test that invalid element type raises TypeError."""
    with pytest.raises(TypeError, match="Element is not an xml.ElementTree.Element"):
      self.backend.write("not_an_element", "/tmp/test.xml")
