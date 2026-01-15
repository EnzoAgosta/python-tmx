import logging
import pytest
from pathlib import Path
from hypomnema.xml.utils import (
  normalize_encoding,
  prep_tag_set,
  assert_object_type,
  check_tag,
  make_usable_path,
  is_ncname,
  QName,
)
from hypomnema.xml.policy import SerializationPolicy, DeserializationPolicy, PolicyValue
from hypomnema.base.errors import XmlSerializationError, InvalidTagError


class TestNormalizeEncodingHappy:
  """Tests for successful encoding normalization."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker

  def test_normalize_encoding_utf8(self):
    """Test normalizing utf-8."""
    assert normalize_encoding("utf-8") == "utf-8"

  def test_normalize_encoding_utf8_uppercase(self):
    """Test normalizing UTF-8 (uppercase)."""
    assert normalize_encoding("UTF-8") == "utf-8"

  def test_normalize_encoding_utf8_no_hyphen(self):
    """Test normalizing utf8 (without hyphen)."""
    assert normalize_encoding("utf8") == "utf-8"

  def test_normalize_encoding_none_defaults_to_utf8(self):
    """Test that None defaults to utf-8."""
    assert normalize_encoding(None) == "utf-8"

  def test_normalize_encoding_unicode_to_utf8(self):
    """Test that 'unicode' is converted to utf-8."""
    assert normalize_encoding("unicode") == "utf-8"

  def test_normalize_encoding_latin1(self):
    """Test normalizing latin-1."""
    result = normalize_encoding("latin-1")
    assert result == "iso8859-1"

  def test_normalize_encoding_ascii(self):
    """Test normalizing ascii."""
    assert normalize_encoding("ascii") == "ascii"

  def test_normalize_encoding_iso8859_1(self):
    """Test normalizing iso-8859-1."""
    result = normalize_encoding("iso-8859-1")
    assert result == "iso8859-1"

  def test_normalize_encoding_cp1252(self):
    """Test normalizing cp1252 (Windows encoding)."""
    assert normalize_encoding("cp1252") == "cp1252"

  def test_normalize_encoding_utf16(self):
    """Test normalizing utf-16."""
    assert normalize_encoding("utf-16") == "utf-16"


class TestNormalizeEncodingError:
  """Tests for encoding normalization errors."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker

  def test_normalize_encoding_unknown(self):
    """Test that unknown encoding raises ValueError."""
    with pytest.raises(ValueError, match="Unknown encoding"):
      normalize_encoding("not-a-real-encoding")

  def test_normalize_encoding_gibberish(self):
    """Test that gibberish encoding raises ValueError."""
    with pytest.raises(ValueError, match="Unknown encoding"):
      normalize_encoding("xyz123abc")


class TestIsNcnameHappy:
  """Tests for valid NCName checking."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker

  def test_is_ncname_simple(self):
    """Test simple valid NCName."""
    assert is_ncname("element") is True

  def test_is_ncname_with_underscore_start(self):
    """Test NCName starting with underscore."""
    assert is_ncname("_element") is True

  def test_is_ncname_with_digits(self):
    """Test NCName containing digits."""
    assert is_ncname("element123") is True

  def test_is_ncname_with_hyphen(self):
    """Test NCName containing hyphen."""
    assert is_ncname("my-element") is True

  def test_is_ncname_with_period(self):
    """Test NCName containing period."""
    assert is_ncname("my.element") is True

  def test_is_ncname_with_underscore_middle(self):
    """Test NCName with underscore in middle."""
    assert is_ncname("my_element") is True

  def test_is_ncname_unicode_letter(self):
    """Test NCName with unicode letter at start."""
    assert is_ncname("élément") is True

  def test_is_ncname_mixed(self):
    """Test NCName with mixed valid characters."""
    assert is_ncname("_my-element.name123") is True


class TestIsNcnameError:
  """Tests for invalid NCName detection."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker

  def test_is_ncname_empty_string(self):
    """Test that empty string is not valid."""
    assert is_ncname("") is False

  def test_is_ncname_starts_with_digit(self):
    """Test that NCName cannot start with digit."""
    assert is_ncname("1element") is False

  def test_is_ncname_starts_with_hyphen(self):
    """Test that NCName cannot start with hyphen."""
    assert is_ncname("-element") is False

  def test_is_ncname_starts_with_period(self):
    """Test that NCName cannot start with period."""
    assert is_ncname(".element") is False

  def test_is_ncname_contains_colon(self):
    """Test that NCName cannot contain colon."""
    assert is_ncname("prefix:element") is False

  def test_is_ncname_contains_space(self):
    """Test that NCName cannot contain space."""
    assert is_ncname("my element") is False


class TestQNameHappy:
  """Tests for successful QName creation and operations."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker
    self.nsmap = {
      "tmx": "http://www.lisa.org/TMX14",
      "ex": "http://example.com",
      None: "http://default.ns",
    }

  def test_qname_simple_tag(self):
    """Test QName with simple tag (no namespace)."""
    qname = QName("element", self.nsmap)
    assert qname.uri is None
    assert qname.prefix is None
    assert qname.local_name == "element"

  def test_qname_clark_notation(self):
    """Test QName with Clark notation."""
    qname = QName("{http://example.com}element", self.nsmap)
    assert qname.uri == "http://example.com"
    assert qname.prefix == "ex"
    assert qname.local_name == "element"

  def test_qname_clark_notation_unknown_uri(self):
    """Test QName with Clark notation and unknown URI."""
    qname = QName("{http://unknown.com}element", self.nsmap)
    assert qname.uri == "http://unknown.com"
    assert qname.prefix is None
    assert qname.local_name == "element"

  def test_qname_prefixed(self):
    """Test QName with prefixed notation."""
    qname = QName("tmx:header", self.nsmap)
    assert qname.uri == "http://www.lisa.org/TMX14"
    assert qname.prefix == "tmx"
    assert qname.local_name == "header"

  def test_qname_prefixed_unknown_prefix(self):
    """Test QName with unknown prefix (prefix preserved, uri is None)."""
    qname = QName("unknown:element", self.nsmap)
    assert qname.uri is None
    assert qname.prefix == "unknown"
    assert qname.local_name == "element"

  def test_qname_xml_prefix(self):
    """Test QName with xml: prefix (reserved namespace)."""
    qname = QName("xml:lang", self.nsmap)
    assert qname.uri == "http://www.w3.org/XML/1998/namespace"
    assert qname.prefix == "xml"
    assert qname.local_name == "lang"

  def test_qname_xml_namespace_clark(self):
    """Test QName with xml namespace in Clark notation."""
    qname = QName("{http://www.w3.org/XML/1998/namespace}lang", self.nsmap)
    assert qname.uri == "http://www.w3.org/XML/1998/namespace"
    assert qname.prefix == "xml"
    assert qname.local_name == "lang"

  def test_qname_from_bytes(self):
    """Test QName created from bytes."""
    qname = QName(b"element", self.nsmap)
    assert qname.local_name == "element"

  def test_qname_from_bytearray(self):
    """Test QName created from bytearray."""
    qname = QName(bytearray(b"element"), self.nsmap)
    assert qname.local_name == "element"

  def test_qname_from_qname(self):
    """Test QName created from another QName (copy)."""
    original = QName("{http://example.com}element", self.nsmap)
    copy = QName(original, {})
    assert copy.uri == original.uri
    assert copy.prefix == original.prefix
    assert copy.local_name == original.local_name

  def test_qname_qualified_name_with_namespace(self):
    """Test qualified_name property with namespace."""
    qname = QName("ex:element", self.nsmap)
    assert qname.qualified_name == "{http://example.com}element"

  def test_qname_qualified_name_without_namespace(self):
    """Test qualified_name property without namespace."""
    qname = QName("element", self.nsmap)
    assert qname.qualified_name == "element"

  def test_qname_prefixed_name_with_prefix(self):
    """Test prefixed_name property with prefix."""
    qname = QName("{http://example.com}element", self.nsmap)
    assert qname.prefixed_name == "ex:element"

  def test_qname_prefixed_name_without_prefix(self):
    """Test prefixed_name property without prefix."""
    qname = QName("element", self.nsmap)
    assert qname.prefixed_name == "element"

  def test_qname_bytes_with_encoding(self):
    """Test QName from bytes with specific encoding."""
    qname = QName(b"\xc3\xa9l\xc3\xa9ment", self.nsmap, encoding="utf-8")
    assert qname.local_name == "élément"


class TestQNameError:
  """Tests for QName error conditions."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker
    self.nsmap = {"ex": "http://example.com"}

  def test_qname_invalid_type(self):
    """Test that invalid tag type raises TypeError."""
    with pytest.raises(TypeError, match="Unexpected tag type"):
      QName(123, self.nsmap)

  def test_qname_invalid_localname_in_clark(self):
    """Test that invalid localname in Clark notation raises ValueError."""
    with pytest.raises(ValueError, match="is not a valid xml localname"):
      QName("{http://example.com}1invalid", self.nsmap)

  def test_qname_invalid_localname_in_prefix(self):
    """Test that invalid localname in prefixed notation raises ValueError."""
    with pytest.raises(ValueError, match="is not a valid xml localname"):
      QName("ex:1invalid", self.nsmap)

  def test_qname_invalid_prefix(self):
    """Test that invalid prefix raises ValueError."""
    with pytest.raises(ValueError, match="is not a valid xml prefix"):
      QName("1invalid:element", self.nsmap)


class TestPrepTagSetHappy:
  """Tests for successful tag set preparation."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker
    self.nsmap = {"ex": "http://example.com"}

  def test_prep_tag_set_none(self):
    """Test that None returns None."""
    assert prep_tag_set(None, self.nsmap) is None

  def test_prep_tag_set_empty_string(self):
    """Test that empty string returns None."""
    assert prep_tag_set("", self.nsmap) is None

  def test_prep_tag_set_single_string(self):
    """Test single string tag."""
    result = prep_tag_set("element", self.nsmap)
    assert result == {"element"}

  def test_prep_tag_set_single_prefixed(self):
    """Test single prefixed tag."""
    result = prep_tag_set("ex:element", self.nsmap)
    assert result == {"{http://example.com}element"}

  def test_prep_tag_set_single_qname(self):
    """Test single QName."""
    qname = QName("{http://example.com}element", self.nsmap)
    result = prep_tag_set(qname, self.nsmap)
    assert result == {"{http://example.com}element"}

  def test_prep_tag_set_list_of_strings(self):
    """Test list of string tags."""
    result = prep_tag_set(["a", "b", "c"], self.nsmap)
    assert result == {"a", "b", "c"}

  def test_prep_tag_set_list_of_qnames(self):
    """Test list of QNames."""
    qnames = [QName("a", self.nsmap), QName("ex:b", self.nsmap)]
    result = prep_tag_set(qnames, self.nsmap)
    assert result == {"a", "{http://example.com}b"}

  def test_prep_tag_set_mixed_list(self):
    """Test mixed list of strings and QNames."""
    qname = QName("ex:element", self.nsmap)
    result = prep_tag_set(["simple", qname], self.nsmap)
    assert result == {"simple", "{http://example.com}element"}

  def test_prep_tag_set_empty_list(self):
    """Test that empty list returns None."""
    assert prep_tag_set([], self.nsmap) is None

  def test_prep_tag_set_none_nsmap(self):
    """Test with None nsmap (uses empty dict)."""
    result = prep_tag_set("element", None)
    assert result == {"element"}


class TestPrepTagSetError:
  """Tests for tag set preparation errors."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker
    self.nsmap = {"ex": "http://example.com"}

  def test_prep_tag_set_invalid_type_in_list(self):
    """Test that invalid type in list raises TypeError."""
    with pytest.raises(TypeError, match="Unexpected tag type"):
      prep_tag_set(["valid", 123], self.nsmap)


class TestMakeUsablePathHappy:
  """Tests for successful path normalization."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker

  def test_make_usable_path_string(self):
    """Test with string path."""
    result = make_usable_path("/tmp/test.xml", mkdir=False)
    assert isinstance(result, Path)
    assert result == Path("/tmp/test.xml")

  def test_make_usable_path_bytes(self):
    """Test with bytes path."""
    result = make_usable_path(b"/tmp/test.xml", mkdir=False)
    assert isinstance(result, Path)
    assert result == Path("/tmp/test.xml")

  def test_make_usable_path_pathlike(self):
    """Test with PathLike object."""
    result = make_usable_path(Path("/tmp/test.xml"), mkdir=False)
    assert isinstance(result, Path)
    assert result == Path("/tmp/test.xml")

  def test_make_usable_path_expands_user(self):
    """Test that ~ is expanded."""
    result = make_usable_path("~/test.xml", mkdir=False)
    assert "~" not in str(result)
    assert result.is_absolute()

  def test_make_usable_path_creates_parent_dirs(self, tmp_path):
    """Test that parent directories are created when mkdir=True."""
    nested_path = tmp_path / "a" / "b" / "c" / "test.xml"
    result = make_usable_path(nested_path, mkdir=True)
    assert result.parent.exists()

  def test_make_usable_path_no_mkdir(self, tmp_path):
    """Test that parent directories are not created when mkdir=False."""
    nested_path = tmp_path / "nonexistent" / "test.xml"
    result = make_usable_path(nested_path, mkdir=False)
    assert not result.parent.exists()

  def test_make_usable_path_resolves_symlink(self, tmp_path):
    """Test that symlinks are resolved when path itself is a symlink."""
    real_file = tmp_path / "real.xml"
    real_file.touch()
    link = tmp_path / "link.xml"
    link.symlink_to(real_file)

    result = make_usable_path(link, mkdir=False)
    assert result == real_file.resolve()


class TestAssertObjectTypeHappy:
  """Tests for successful type assertions."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker
    self.logger = logging.getLogger("test")
    self.policy = SerializationPolicy()

  def test_assert_object_type_correct_type(self):
    """Test that correct type returns True."""
    result = assert_object_type("hello", str, logger=self.logger, policy=self.policy)
    assert result is True

  def test_assert_object_type_subclass(self):
    """Test that subclass is accepted."""
    result = assert_object_type(True, int, logger=self.logger, policy=self.policy)
    assert result is True

  def test_assert_object_type_wrong_type_ignore(self):
    """Test that wrong type with ignore policy returns False."""
    policy = SerializationPolicy(invalid_object_type=PolicyValue("ignore", logging.DEBUG))
    result = assert_object_type(123, str, logger=self.logger, policy=policy)
    assert result is False


class TestAssertObjectTypeError:
  """Tests for type assertion errors."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker
    self.logger = logging.getLogger("test")

  def test_assert_object_type_wrong_type_raise(self):
    """Test that wrong type with raise policy raises error."""
    policy = SerializationPolicy(invalid_object_type=PolicyValue("raise", logging.DEBUG))
    with pytest.raises(XmlSerializationError, match="is not an instance of"):
      assert_object_type(123, str, logger=self.logger, policy=policy)


class TestCheckTagHappy:
  """Tests for successful tag checking."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker
    self.logger = logging.getLogger("test")
    self.policy = DeserializationPolicy()

  def test_check_tag_matching(self):
    """Test that matching tags pass without error."""
    check_tag("element", "element", self.logger, self.policy)

  def test_check_tag_mismatch_ignore(self):
    """Test that mismatching tags with ignore policy pass."""
    policy = DeserializationPolicy(invalid_tag=PolicyValue("ignore", logging.DEBUG))
    check_tag("wrong", "expected", self.logger, policy)


class TestCheckTagError:
  """Tests for tag checking errors."""

  @pytest.fixture(autouse=True)
  def setup(self, mocker):
    self.mocker = mocker
    self.logger = logging.getLogger("test")

  def test_check_tag_mismatch_raise(self):
    """Test that mismatching tags with raise policy raises error."""
    policy = DeserializationPolicy(invalid_tag=PolicyValue("raise", logging.DEBUG))
    with pytest.raises(InvalidTagError, match="expected expected, got wrong"):
      check_tag("wrong", "expected", self.logger, policy)
