from datetime import UTC, datetime
import logging
from unittest.mock import Mock
import pytest
from python_tmx.base.errors import XmlDeserializationError
from python_tmx.base.types import Header, Segtype
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
    self.handler._set_emit(lambda x: None)

  def make_header_elem(
    self,
    *,
    tag: str = "header",
    creationtool: str | None = "pytest",
    creationtoolversion: str | None = "v1",
    segtype: Segtype | None = Segtype.SENTENCE,
    o_tmf: str | None = "TestTMF",
    adminlang: str | None = "en-US",
    srclang: str | None = "en-US",
    datatype: str | None = "plaintext",
    o_encoding: str | None = "UTF-8",
    creationdate: datetime | None = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
    creationid: str | None = "User1",
    changedate: datetime | None = datetime(2025, 2, 1, 14, 30, 0, tzinfo=UTC),
    changeid: str | None = "User2",
    props: int = 1,
    notes: int = 1,
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)
    if creationtool is not None:
      self.backend.set_attr(elem, "creationtool", creationtool)
    if creationtoolversion is not None:
      self.backend.set_attr(elem, "creationtoolversion", creationtoolversion)
    if segtype is not None:
      self.backend.set_attr(elem, "segtype", segtype.value)
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
      self.backend.set_attr(elem, "creationdate", creationdate.isoformat())
    if creationid is not None:
      self.backend.set_attr(elem, "creationid", creationid)
    if changedate is not None:
      self.backend.set_attr(elem, "changedate", changedate.isoformat())
    if changeid is not None:
      self.backend.set_attr(elem, "changeid", changeid)
    for _ in range(props):
      self.backend.append(elem, self.backend.make_elem("prop"))
    for _ in range(notes):
      self.backend.append(elem, self.backend.make_elem("note"))
    return elem
  
  def test_returns_Header(self):
    elem = self.make_header_elem()
    header = self.handler._deserialize(elem)
    assert isinstance(header, Header)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_header_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "header")

  def test_calls_parses_attribute_correctly(self):
    mock_parse_attributes = Mock()
    mock_parse_attributes_as_enum = Mock()
    mock_parse_attributes_as_dt = Mock()
    self.handler._parse_attribute = mock_parse_attributes
    self.handler._parse_attribute_as_enum = mock_parse_attributes_as_enum
    self.handler._parse_attribute_as_dt = mock_parse_attributes_as_dt

    elem = self.make_header_elem()
    self.handler._deserialize(elem)

    assert mock_parse_attributes.call_count == 9
    mock_parse_attributes.assert_any_call(elem, "creationtool", True)
    mock_parse_attributes.assert_any_call(elem, "creationtoolversion", True)
    mock_parse_attributes.assert_any_call(elem, "o-tmf", True)
    mock_parse_attributes.assert_any_call(elem, "adminlang", True)
    mock_parse_attributes.assert_any_call(elem, "srclang", True)
    mock_parse_attributes.assert_any_call(elem, "datatype", True)
    mock_parse_attributes.assert_any_call(elem, "o-encoding", False)
    mock_parse_attributes.assert_any_call(elem, "creationid", False)
    mock_parse_attributes.assert_any_call(elem, "changeid", False)

    mock_parse_attributes_as_enum.assert_called_once_with(elem, "segtype", Segtype, True)

    assert mock_parse_attributes_as_dt.call_count == 2
    mock_parse_attributes_as_dt.assert_any_call(elem, "creationdate", False)
    mock_parse_attributes_as_dt.assert_any_call(elem, "changedate", False)

  def test_emits_correctly(self):
    mock_emit = Mock()
    self.handler._set_emit(mock_emit)
    elem = self.make_header_elem()
    self.handler._deserialize(elem)

    assert mock_emit.call_count == 2
    for i in self.backend.iter_children(elem):
      mock_emit.assert_any_call(i)

  def test_extra_text_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_header_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "raise"
    self.policy.extra_text.log_level = log_level

    with pytest.raises(
      XmlDeserializationError,
      match="Element <header> has extra text content '  I should not be here  '",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <header> has extra text content '  I should not be here  '",
    )
    assert caplog.record_tuples == [expected_log]

  def test_extra_text_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_header_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "ignore"
    self.policy.extra_text.log_level = log_level

    self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <header> has extra text content '  I should not be here  '",
    )
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_header_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))
    log_message = "Invalid child element <wrong> in <header>"

    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    with pytest.raises(
      XmlDeserializationError,
      match=log_message,
    ):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_header_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))
    log_message = "Invalid child element <wrong> in <header>"

    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    header = self.handler._deserialize(elem)
    
    assert isinstance(header, Header)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]