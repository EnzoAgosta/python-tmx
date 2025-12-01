import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.errors import XmlDeserializationError
from python_tmx.base.types import Header, Tmx
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import TmxDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestTmxDeserializer[T_XmlElement]:
  handler: TmxDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = TmxDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_tmx_elem(
    self,
    tag: str = "tmx",
    version: str | None = "1.4",
    header: int | None = 1,
    tus: int | None = 1,
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)
    if version:
      self.backend.set_attr(elem, "version", version)
    if header is not None:
      for _ in range(header):
        self.backend.append(elem, self.backend.make_elem("header"))
    if tus is not None:
      body = self.backend.make_elem("body")
      for _ in range(tus):
        self.backend.append(body, self.backend.make_elem("tu"))
      self.backend.append(elem, body)
    return elem

  def test_returns_Tmx(self):
    elem = self.make_tmx_elem()
    tmx = self.handler._deserialize(elem)
    assert isinstance(tmx, Tmx)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_tmx_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "tmx")

  def test_calls_parse_attribute_correctly(self):
    mock_parse_attributes = Mock()
    self.handler._parse_attribute = mock_parse_attributes

    elem = self.make_tmx_elem()
    self.handler._deserialize(elem)
    mock_parse_attributes.assert_called_once_with(elem, "version", True)

  def test_calls_emit(self):
    mock_emit = Mock()
    self.handler._set_emit(mock_emit)

    elem = self.make_tmx_elem(header=None, tus=None)

    body = self.backend.make_elem("body")
    self.backend.append(elem, body)
    tu = self.backend.make_elem("tu")
    self.backend.append(body, tu)

    header = self.backend.make_elem("header")
    self.backend.append(elem, header)

    self.handler._deserialize(elem)

    assert mock_emit.call_count == 2
    mock_emit.assert_any_call(tu)
    mock_emit.assert_any_call(header)

  def test_mutliple_headers_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem(header=2)
    self.policy.multiple_headers.behavior = "raise"
    self.policy.multiple_headers.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Multiple <header> elements in <tmx>"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Multiple <header> elements in <tmx>")
    assert caplog.record_tuples == [expected_log]

  def test_multiple_headers_keep_first(self, caplog: pytest.LogCaptureFixture, log_level: int):
    mock_header = Mock(spec=Header)
    mock_emit = Mock(return_value=mock_header)
    self.handler._set_emit(mock_emit)

    elem = self.make_tmx_elem(header=None, tus=None)
    head1 = self.backend.make_elem("header")
    self.backend.append(elem, head1)
    head2 = self.backend.make_elem("header")
    self.backend.append(elem, head2)

    self.policy.multiple_headers.behavior = "keep_first"
    self.policy.multiple_headers.log_level = log_level

    tmx = self.handler._deserialize(elem)

    assert isinstance(tmx, Tmx)
    assert tmx.header == mock_header

    mock_emit.assert_called_once_with(head1)

    expected_log = (self.logger.name, log_level, "Multiple <header> elements in <tmx>")
    assert caplog.record_tuples == [expected_log]

  def test_multiple_headers_keep_last(self, caplog: pytest.LogCaptureFixture, log_level: int):
    mock_header = Mock(spec=Header)
    mock_emit = Mock(return_value=mock_header)
    self.handler._set_emit(mock_emit)

    elem = self.make_tmx_elem(header=None, tus=None)
    head1 = self.backend.make_elem("header")
    self.backend.append(elem, head1)
    head2 = self.backend.make_elem("header")
    self.backend.append(elem, head2)
    self.policy.multiple_headers.behavior = "keep_last"
    self.policy.multiple_headers.log_level = log_level

    tmx = self.handler._deserialize(elem)

    assert isinstance(tmx, Tmx)
    assert tmx.header == mock_header

    assert mock_emit.call_count == 2
    mock_emit.assert_any_call(head1)
    mock_emit.assert_any_call(head2)

    expected_log = (self.logger.name, log_level, "Multiple <header> elements in <tmx>")
    assert caplog.record_tuples == [expected_log]

  def test_missing_header_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem(header=None)
    self.policy.missing_header.behavior = "raise"
    self.policy.missing_header.log_level = log_level

    with pytest.raises(
      XmlDeserializationError, match="Element <tmx> is missing a <header> child element."
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <tmx> is missing a <header> child element.",
    )
    assert caplog.record_tuples == [expected_log]

  def test_missing_header_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem(header=None)
    self.policy.missing_header.behavior = "ignore"
    self.policy.missing_header.log_level = log_level

    tmx = self.handler._deserialize(elem)

    assert isinstance(tmx, Tmx)
    assert tmx.header is None

    expected_log = (
      self.logger.name,
      log_level,
      "Element <tmx> is missing a <header> child element.",
    )
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Invalid child element <wrong> in <tmx>"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Invalid child element <wrong> in <tmx>")
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Invalid child element <wrong> in <tmx>")
    assert caplog.record_tuples == [expected_log]

  def test_extra_text_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "raise"
    self.policy.extra_text.log_level = log_level

    with pytest.raises(
      XmlDeserializationError,
      match="Element <tmx> has extra text content '  I should not be here  '",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <tmx> has extra text content '  I should not be here  '",
    )
    assert caplog.record_tuples == [expected_log]

  def test_extra_text_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "ignore"
    self.policy.extra_text.log_level = log_level

    self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <tmx> has extra text content '  I should not be here  '",
    )
    assert caplog.record_tuples == [expected_log]
