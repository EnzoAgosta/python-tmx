from datetime import UTC, datetime
import logging
from unittest.mock import Mock
import pytest
from python_tmx.base.types import Header, Note, Prop, Segtype
from python_tmx.base.errors import AttributeDeserializationError, InvalidTagError, XmlDeserializationError
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import HeaderDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestHeaderDeserializer[T_XmlElement]:
  handler: HeaderDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = HeaderDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)

  def make_header_elem(
    self,
    *,
    tag: str = "header",
    creationtool: str | None = "pytest",
    creationtoolversion: str | None = "v1",
    segtype: str | None = "sentence",
    o_tmf: str | None = "TestTMF",
    adminlang: str | None = "en-US",
    srclang: str | None = "en-US",
    datatype: str | None = "plaintext",
    o_encoding: str | None = "UTF-8",
    creationdate: datetime | None = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
    creationid: str | None = "User1",
    changedate: datetime | None = datetime(2025, 2, 1, 14, 30, 0, tzinfo=UTC),
    changeid: str | None = "User2",
    props: int = 0,
    notes: int = 0,
  ) -> T_XmlElement:
    """
    Creates a <header> element.

    extra kwargs:
    tag: The tag to use for the element (default: "header")
    creationtool: The creationtool attribute to use (default: "pytest")
    creationtoolversion: The creationtoolversion attribute to use (default: "v1")
    segtype: The segtype attribute to use (default: "sentence"). Must be one of "block", "paragraph", "sentence", "phrase".
    o_tmf: The o-tmf attribute to use (default: "TestTMF")
    adminlang: The adminlang attribute to use (default: "en-US")
    srclang: The srclang attribute to use (default: "en-US")
    datatype: The datatype attribute to use (default: "plaintext")
    o_encoding: The o-encoding attribute to use (default: "UTF-8" if full is True)
    creationdate: The creationdate attribute to use (default: January 1st, 2025 at 12:00:00 UTC)
    creationid: The creationid attribute to use (default: "User1")
    changedate: The changedate attribute to use (default: February 1st, 2025 at 14:30:00 UTC)
    changeid: The changeid attribute to use (default: "User2")
    props: The number of props to add to the header (default: 1)
    notes: The number of notes to add to the header (default: 1)
    """
    elem = self.backend.make_elem(tag)
    if creationtool is not None:
      self.backend.set_attr(elem, "creationtool", creationtool)
    if creationtoolversion is not None:
      self.backend.set_attr(elem, "creationtoolversion", creationtoolversion)
    if segtype is not None:
      self.backend.set_attr(elem, "segtype", segtype)
    if o_tmf is not None:
      self.backend.set_attr(elem, "o-tmf", o_tmf)
    if adminlang is not None:
      self.backend.set_attr(elem, "adminlang", adminlang)
    if srclang is not None:
      self.backend.set_attr(elem, "srclang", srclang)
    if datatype is not None:
      self.backend.set_attr(elem, "datatype", datatype)
    if o_encoding is not None:
      self.backend.set_attr(elem, "o-encoding", o_encoding)
    if creationdate is not None:
      self.backend.set_attr(elem, "creationdate", creationdate.strftime("%Y%m%dT%H%M%SZ"))
    if creationid is not None:
      self.backend.set_attr(elem, "creationid", creationid)
    if changedate is not None:
      self.backend.set_attr(elem, "changedate", changedate.strftime("%Y%m%dT%H%M%SZ"))
    if changeid is not None:
      self.backend.set_attr(elem, "changeid", changeid)
    for _ in range(props):
      self.backend.append(elem, self.backend.make_elem("prop"))
    for _ in range(notes):
      self.backend.append(elem, self.backend.make_elem("note"))
    return elem

  def test_basic_usage(self, caplog: pytest.LogCaptureFixture):
    """
    Simple and most common usage of the Header deserializer.
    Tests that the Header is correctly constructed from the XML element.
    """
    mock_prop_obj = Prop(text="P", type="T")
    mock_note_obj = Note(text="N")

    def side_effect(child_id):
      tag = self.backend.get_tag(child_id)
      if tag == "prop":
        return mock_prop_obj
      if tag == "note":
        return mock_note_obj
      return None

    mock_emit = Mock(side_effect=side_effect)
    self.handler._set_emit(mock_emit)
    elem = self.make_header_elem(props=1, notes=1)
    header = self.handler._deserialize(elem)

    assert isinstance(header, Header)
    assert header.creationtool == "pytest"
    assert header.creationtoolversion == "v1"
    assert header.segtype == Segtype.SENTENCE
    assert header.o_tmf == "TestTMF"
    assert header.adminlang == "en-US"
    assert header.srclang == "en-US"
    assert header.datatype == "plaintext"
    assert header.o_encoding == "UTF-8"
    assert header.creationdate == datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    assert header.creationid == "User1"
    assert header.changedate == datetime(2025, 2, 1, 14, 30, 0, tzinfo=UTC)
    assert header.changeid == "User2"

    assert header.props == [mock_prop_obj]
    assert header.notes == [mock_note_obj]

    assert mock_emit.call_count == 2
    for i in self.backend.iter_children(elem):
      mock_emit.assert_any_call(i)

    assert caplog.records == []

  def test_check_tag_raises(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Header deserializer raises an error when the tag is incorrect
    if the policy says so and that the error is logged using the policy's log level
    for that event.
    """
    elem = self.make_header_elem(tag="note")
    self.policy.invalid_tag.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.invalid_tag.log_level = log_level
    with pytest.raises(InvalidTagError, match="Incorrect tag: expected header, got note"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected header, got note")

    assert caplog.record_tuples == [expected_log]

  def test_check_tag_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Header deserializer ignores an incorrect tag if the policy says so
    and that the error is logged using the policy's log level for that event.

    Note: This creates a Header element that doesn't reflect the original XML.
    """
    elem = self.make_header_elem(tag="note")
    self.policy.invalid_tag.behavior = "ignore"
    self.policy.invalid_tag.log_level = log_level
    header = self.handler._deserialize(elem)
    assert isinstance(header, Header)

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected header, got note")
    assert caplog.record_tuples == [expected_log]

  def test_missing_required_attribute_raises(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Header deserializer raises an error when the required attribute is missing
    if the policy says so and that the error is logged using the policy's log level
    for that event.
    """
    elem = self.make_header_elem(creationtool=None)
    self.policy.required_attribute_missing.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.required_attribute_missing.log_level = log_level
    with pytest.raises(AttributeDeserializationError, match="Missing required attribute 'creationtool'"):
      self.handler._deserialize(elem)
    assert caplog.records[-1].levelno == log_level
    assert caplog.records[-1].message == "Missing required attribute 'creationtool' on element <header>"

  def test_missing_required_attribute_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Header deserializer ignores an error when the required attribute is missing
    if the policy says so and that the error is logged using the policy's log level
    for that event.

    Note: This creates a invalid Header element that doesn't reflect the original XML.
    """
    elem = self.make_header_elem(creationtool=None)
    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level
    header = self.handler._deserialize(elem)
    assert isinstance(header, Header)
    assert header.creationtool is None

    expected_log = (self.logger.name, log_level, "Missing required attribute 'creationtool' on element <header>")
    assert caplog.record_tuples == [expected_log]

  def test_extra_missing_text_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Header deserializer raises an error when there is extra text content
    if the policy says so and that the error is logged using the policy's log level
    for that event.
    """
    elem = self.make_header_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.extra_text.log_level = log_level

    with pytest.raises(
      XmlDeserializationError, match="Element <header> has extra text content '  I should not be here  '"
    ):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Element <header> has extra text content '  I should not be here  '")
    assert caplog.record_tuples == [expected_log]

  def test_extra_text_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Header deserializer ignores an error when there is extra text content
    if the policy says so and that the error is logged using the policy's log level
    for that event.

    Note: This creates a invalid Header element that doesn't reflect the original XML.
    """
    elem = self.make_header_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "ignore"
    self.policy.extra_text.log_level = log_level

    self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Element <header> has extra text content '  I should not be here  '")
    assert caplog.record_tuples == [expected_log]
