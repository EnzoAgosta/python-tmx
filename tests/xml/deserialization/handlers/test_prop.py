import logging
import pytest
from python_tmx.base.types import Prop
from python_tmx.base.errors import (
  AttributeDeserializationError,
  InvalidTagError,
  XmlDeserializationError,
)
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
    _type: str | None = "x-test-type",
    o_encoding: str | None = "UTF-8",
    lang: str | None = "en-US",
  ) -> T_XmlElement:
    
    elem = self.backend.make_elem(tag)
    self.backend.set_text(elem, text)
    if _type is not None:
      self.backend.set_attr(elem, "type", _type)
    if lang is not None:
      self.backend.set_attr(elem, f"{XML_NS}lang", lang)
    if o_encoding is not None:
      self.backend.set_attr(elem, "o-encoding", o_encoding)
    return elem

  def test_basic_usage(self, caplog: pytest.LogCaptureFixture):
    
    elem = self.make_prop_elem()
    prop = self.handler._deserialize(elem)

    assert isinstance(prop, Prop)
    assert prop.text == "Valid Prop Content"
    assert prop.type == "x-test-type"
    assert prop.lang == "en-US"
    assert prop.o_encoding == "UTF-8"

    assert caplog.records == []

  def test_check_tag_raises(self, caplog: pytest.LogCaptureFixture, log_level: int):
    
    elem = self.make_prop_elem(tag="note")
    self.policy.invalid_tag.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_tag.log_level = log_level
    with pytest.raises(InvalidTagError, match="Incorrect tag: expected prop, got note"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected prop, got note")

    assert caplog.record_tuples == [expected_log]

  def test_check_tag_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    
    elem = self.make_prop_elem(tag="note")
    self.policy.invalid_tag.behavior = "ignore"
    self.policy.invalid_tag.log_level = log_level
    prop = self.handler._deserialize(elem)
    assert isinstance(prop, Prop)
    assert prop.text == "Valid Prop Content"
    assert prop.type == "x-test-type"
    assert prop.lang == "en-US"
    assert prop.o_encoding == "UTF-8"

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected prop, got note")
    assert caplog.record_tuples == [expected_log]

  def test_missing_required_attribute_raises(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    
    elem = self.make_prop_elem(_type=None)
    self.policy.required_attribute_missing.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.required_attribute_missing.log_level = log_level
    with pytest.raises(AttributeDeserializationError, match="Missing required attribute 'type'"):
      self.handler._deserialize(elem)
    expected_log = (
      self.logger.name,
      log_level,
      "Missing required attribute 'type' on element <prop>",
    )
    assert caplog.record_tuples == [expected_log]

  def test_missing_required_attribute_ignores(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    
    elem = self.make_prop_elem(_type=None)
    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level
    prop = self.handler._deserialize(elem)
    assert isinstance(prop, Prop)
    assert prop.type is None

    expected_log = (
      self.logger.name,
      log_level,
      "Missing required attribute 'type' on element <prop>",
    )
    assert caplog.record_tuples == [expected_log]

  def test_empty_content_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    
    elem = self.make_prop_elem(text=None)

    self.policy.empty_content.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.empty_content.log_level = log_level

    with pytest.raises(
      XmlDeserializationError, match="Element <prop> does not have any text content"
    ):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Element <prop> does not have any text content")
    assert caplog.record_tuples == [expected_log]

  def test_empty_content_empty_string_fallback(self, caplog: pytest.LogCaptureFixture, log_level: int):
    
    elem = self.make_prop_elem(text=None)

    self.policy.empty_content.behavior = "empty"
    self.policy.empty_content.log_level = log_level
    prop = self.handler._deserialize(elem)

    assert prop.text == ""

    expected_logs = [
      (self.logger.name, log_level, "Element <prop> does not have any text content"),
      (self.logger.name, log_level, "Falling back to an empty string"),
    ]

    assert caplog.record_tuples == expected_logs

  def test_empty_content_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    
    elem = self.make_prop_elem(text=None)
    self.policy.empty_content.behavior = "ignore"
    self.policy.empty_content.log_level = log_level
    prop = self.handler._deserialize(elem)
    assert prop.text is None

    expected_log = (self.logger.name, log_level, "Element <prop> does not have any text content")
    assert caplog.record_tuples == [expected_log]
