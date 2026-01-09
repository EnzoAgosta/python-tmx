import pytest
from io import BytesIO
from hypomnema.xml.backends.base import XmlBackend


class MockBackend(XmlBackend):
  """
  A concrete implementation of XmlBackend for testing the base class logic.
  Abstract methods are implemented as minimal stubs.
  """

  def get_tag(self, element, *, as_qname=False, nsmap=None):
    return "tag"

  def create_element(self, tag, attributes=None, *, nsmap=None):
    return "element"

  def append_child(self, parent, child):
    pass

  def get_attribute(self, element, attribute_name, default=None, *, nsmap=None):
    return None

  def set_attribute(self, element, attribute_name, attribute_value, *, nsmap=None, unsafe=False):
    pass

  def get_attribute_map(self, element):
    return {}

  def get_text(self, element):
    return ""

  def set_text(self, element, text):
    pass

  def get_tail(self, element):
    return ""

  def set_tail(self, element, tail):
    pass

  def iter_children(self, element, tag_filter=None, *, nsmap=None):
    yield from []

  def parse(self, path, encoding="utf-8"):
    return "root"

  def write(self, element, path, encoding="utf-8"):
    pass

  def clear(self, element):
    pass

  def to_bytes(self, element, encoding="utf-8", self_closing=False):
    return b"<element></element>"

  def iterparse(self, path, tag_filter=None, *, nsmap=None):
    yield from []


class TestBaseXmlBackendHappy:
  """Tests for the successful execution of concrete XmlBackend methods."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.backend = MockBackend()
    self.mocker = mocker

  def test_register_namespace_valid_prefix(self):
    """Test valid namespace registration with a prefix."""
    self.backend.register_namespace("ex", "http://example.com")
    assert self.backend._global_nsmap["ex"] == "http://example.com"

  def test_register_namespace_none_prefix(self):
    """Test registering default namespace (None prefix)."""
    self.backend.register_namespace(None, "http://example.com/default")
    assert self.backend._global_nsmap[None] == "http://example.com/default"

  def test_register_namespace_multiple(self):
    """Test registering multiple namespaces."""
    self.backend.register_namespace("ns1", "http://ns1.example.com")
    self.backend.register_namespace("ns2", "http://ns2.example.com")
    assert self.backend._global_nsmap["ns1"] == "http://ns1.example.com"
    assert self.backend._global_nsmap["ns2"] == "http://ns2.example.com"

  def test_register_namespace_overwrite(self):
    """Test overwriting an existing namespace."""
    self.backend.register_namespace("ex", "http://old.example.com")
    self.backend.register_namespace("ex", "http://new.example.com")
    assert self.backend._global_nsmap["ex"] == "http://new.example.com"

  def test_iterwrite_writes_to_file(self, tmp_path):
    """Test that iterwrite writes elements to a file."""
    output_file = tmp_path / "output.xml"
    elements = []
    self.backend.iterwrite(output_file, elements)

    assert output_file.exists()
    content = output_file.read_bytes()
    assert b'<?xml version="1.0"' in content
    assert b"<!DOCTYPE tmx" in content
    assert b"<element" in content

  def test_iterwrite_buffered_io(self):
    """Test iterwrite with a BufferedIOBase (BytesIO)."""
    buffer = BytesIO()
    elements = []
    self.backend.iterwrite(buffer, elements)

    buffer.seek(0)
    content = buffer.read()
    assert b'<?xml version="1.0"' in content
    assert b"<element" in content

  def test_iterwrite_no_declaration(self, tmp_path):
    """Test iterwrite without XML declaration."""
    output_file = tmp_path / "output.xml"
    self.backend.iterwrite(output_file, [], write_xml_declaration=False)

    content = output_file.read_bytes()
    assert b"<?xml version" not in content

  def test_iterwrite_no_doctype(self, tmp_path):
    """Test iterwrite without DOCTYPE."""
    output_file = tmp_path / "output.xml"
    self.backend.iterwrite(output_file, [], write_doctype=False)

    content = output_file.read_bytes()
    assert b"<!DOCTYPE" not in content

  def test_iterwrite_custom_root(self, tmp_path):
    """Test iterwrite with a custom root element."""
    custom_root = "custom_root"

    def custom_to_bytes(element, encoding="utf-8", self_closing=False):
      if element == custom_root:
        return b"<custom version='2.0'></custom>"
      return b"<elem></elem>"

    self.backend.to_bytes = custom_to_bytes

    output_file = tmp_path / "output.xml"
    self.backend.iterwrite(output_file, [], root_elem=custom_root)

    content = output_file.read_bytes()
    assert b"<custom version='2.0'>" in content
    assert b"</custom>" in content


class TestBaseXmlBackendError:
  """Tests for error conditions in XmlBackend methods."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.backend = MockBackend()
    self.mocker = mocker

  def test_register_namespace_invalid_uri_type(self):
    """Test that non-string URI raises TypeError."""
    with pytest.raises(TypeError, match="given uri is not a str"):
      self.backend.register_namespace("prefix", 123)

  def test_register_namespace_invalid_prefix_type(self):
    """Test that non-string prefix raises TypeError."""
    with pytest.raises(TypeError, match="given prefix is not a str"):
      self.backend.register_namespace(123, "http://example.com")

  def test_register_namespace_invalid_ncname_with_colon(self):
    """Test that prefix containing colon raises ValueError."""
    with pytest.raises(ValueError, match="is not a valid xml prefix"):
      self.backend.register_namespace("invalid:prefix", "http://example.com")

  def test_register_namespace_invalid_ncname_starts_with_digit(self):
    """Test that prefix starting with digit raises ValueError."""
    with pytest.raises(ValueError, match="is not a valid xml prefix"):
      self.backend.register_namespace("1invalid", "http://example.com")

  def test_register_namespace_reserved_xml_prefix(self):
    """Test that 'xml' prefix raises ValueError."""
    with pytest.raises(ValueError, match="reserved for the xml namespace"):
      self.backend.register_namespace("xml", "http://example.com")

  def test_iterwrite_invalid_buffer_size_zero(self):
    """Test that buffer_size=0 raises ValueError."""
    with pytest.raises(ValueError, match="buffer_size must be >= 1"):
      self.backend.iterwrite("path", [], max_number_of_elements_in_buffer=0)

  def test_iterwrite_invalid_buffer_size_negative(self):
    """Test that negative buffer_size raises ValueError."""
    with pytest.raises(ValueError, match="buffer_size must be >= 1"):
      self.backend.iterwrite("path", [], max_number_of_elements_in_buffer=-5)

  def test_iterwrite_invalid_root_element_no_closing_tag(self):
    """Test iterwrite fails if root has no closing tag."""

    def bad_to_bytes(element, encoding="utf-8", self_closing=False):
      return b"<unclosed"

    self.backend.to_bytes = bad_to_bytes

    with pytest.raises(ValueError, match="Cannot find closing tag"):
      self.backend.iterwrite(BytesIO(), [], root_elem="bad_root")
