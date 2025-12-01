import logging
from unittest.mock import Mock
import pytest
from python_tmx.base.errors import XmlDeserializationError
from python_tmx.base.types import Prop
from python_tmx.xml import XML_NS
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import PropDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestPropDeserializer[T_XmlElement]:
  handler: PropDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = PropDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_prop_elem(
    self,
    *,
    tag: str = "prop",
    text: str | None = "Valid Prop Content",
    _type: str | None = "x-test",
    o_encoding: str | None = "UTF-8",
    lang: str | None = "en-US",
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)
    self.backend.set_text(elem, text)
    if lang is not None:
      self.backend.set_attr(elem, f"{XML_NS}lang", lang)
    if o_encoding is not None:
      self.backend.set_attr(elem, "o-encoding", o_encoding)
    if _type is not None:
      self.backend.set_attr(elem, "type", _type)
    return elem

  def test_returns_Prop(self):
    elem = self.make_prop_elem()
    prop = self.handler._deserialize(elem)
    assert isinstance(prop, Prop)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_prop_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "prop")

  def test_calls_parses_attribute_correctly(self):
    mock_parse_attributes = Mock()
    self.handler._parse_attribute = mock_parse_attributes

    elem = self.make_prop_elem()
    self.handler._deserialize(elem)

    assert mock_parse_attributes.call_count == 3
    mock_parse_attributes.assert_any_call(elem, "type", True)
    mock_parse_attributes.assert_any_call(elem, f"{XML_NS}lang", False)
    mock_parse_attributes.assert_any_call(elem, "o-encoding", False)

  def test_empty_content_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_prop_elem(text=None)
    log_message = "Element <prop> does not have any text content"

    self.policy.empty_content.behavior = "raise"
    self.policy.empty_content.log_level = log_level

    with pytest.raises(XmlDeserializationError, match=log_message):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_empty_content_empty_string_fallback(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.make_prop_elem(text=None)
    log_message = "Element <prop> does not have any text content"

    self.policy.empty_content.behavior = "empty"
    self.policy.empty_content.log_level = log_level
    prop = self.handler._deserialize(elem)

    assert prop.text == ""

    expected_logs = [
      (self.logger.name, log_level, log_message),
      (self.logger.name, log_level, "Falling back to an empty string"),
    ]

    assert caplog.record_tuples == expected_logs

  def test_empty_content_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_prop_elem(text=None)
    log_message = "Element <prop> does not have any text content"
    self.policy.empty_content.behavior = "ignore"
    self.policy.empty_content.log_level = log_level
    prop = self.handler._deserialize(elem)
    assert prop.text is None

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_prop_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))
    log_message = "Invalid child element <wrong> in <prop>"

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
    elem = self.make_prop_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))
    log_message = "Invalid child element <wrong> in <prop>"

    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    prop = self.handler._deserialize(elem)
    assert prop.text == "Valid Prop Content"

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]
