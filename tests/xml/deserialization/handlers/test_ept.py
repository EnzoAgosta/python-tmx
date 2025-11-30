import logging

import pytest
from python_tmx.base.errors import (
  AttributeDeserializationError,
  InvalidTagError,
  XmlDeserializationError,
)
from python_tmx.base.types import Ept
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import EptDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestEptDeserializer[T_XmlElement]:
  handler: EptDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = EptDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_ept_elem(
    self,
    *,
    tag: str = "ept",
    text: str | None = "Valid Ept Content",
    i: int | None = 1,
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)
    self.backend.set_text(elem, text)
    if i is not None:
      self.backend.set_attr(elem, "i", str(i))
    return elem

  def test_basic_usage(self):
    elem = self.make_ept_elem()
    ept = self.handler._deserialize(elem)
    assert isinstance(ept, Ept)
    assert ept.i == 1
    assert ept.content == ["Valid Ept Content"]

  def test_check_tag_raises(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ept_elem(tag="prop")

    self.policy.invalid_tag.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_tag.log_level = log_level

    with pytest.raises(InvalidTagError, match="Incorrect tag: expected ept, got prop"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected ept, got prop")
    assert caplog.record_tuples == [expected_log]

  def test_check_tag_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ept_elem(tag="prop")

    self.policy.invalid_tag.behavior = "ignore"
    self.policy.invalid_tag.log_level = log_level

    ept = self.handler._deserialize(elem)
    assert isinstance(ept, Ept)
    assert ept.i == 1

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected ept, got prop")
    assert caplog.record_tuples == [expected_log]

  def test_missing_content_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ept_elem(text=None)
    self.policy.empty_content.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.empty_content.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Element <ept> is empty"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Element <ept> is empty")
    assert caplog.record_tuples == [expected_log]

  def test_empty_content_empty_string_fallback(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.make_ept_elem(text=None)

    self.policy.empty_content.behavior = "empty"
    self.policy.empty_content.log_level = log_level
    ept = self.handler._deserialize(elem)

    assert ept.content == [""]

    expected_logs = [
      (self.logger.name, log_level, "Element <ept> is empty"),
      (self.logger.name, log_level, "Falling back to an empty string"),
    ]

    assert caplog.record_tuples == expected_logs

  def test_empty_content_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ept_elem(text=None)

    self.policy.empty_content.behavior = "ignore"
    self.policy.empty_content.log_level = log_level

    ept = self.handler._deserialize(elem)
    assert isinstance(ept, Ept)
    assert ept.content == []

    expected_log = (self.logger.name, log_level, "Element <ept> is empty")
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ept_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_child_element.log_level = log_level

    with pytest.raises(
      XmlDeserializationError,
      match="Incorrect child element in ept: expected one of sub, got wrong",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Incorrect child element in ept: expected one of sub, got wrong",
    )
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ept_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    ept = self.handler._deserialize(elem)
    assert isinstance(ept, Ept)
    assert ept.content == ["Valid Ept Content"]

    expected_log = (
      self.logger.name,
      log_level,
      "Incorrect child element in ept: expected one of sub, got wrong",
    )
    assert caplog.record_tuples == [expected_log]

  def test_missing_required_attribute_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ept_elem(i=None)

    self.policy.required_attribute_missing.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.required_attribute_missing.log_level = log_level

    with pytest.raises(
      AttributeDeserializationError, match="Missing required attribute 'i' on element <ept>"
    ):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Missing required attribute 'i' on element <ept>")
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_int_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ept_elem(i="invalid")  # type: ignore[arg-type]

    self.policy.invalid_attribute_value.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_attribute_value.log_level = log_level

    with pytest.raises(
      AttributeDeserializationError,
      match="Cannot convert 'invalid' to an int for attribute i",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Cannot convert 'invalid' to an int for attribute i",
    )
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_int_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ept_elem(i="invalid")  # type: ignore[arg-type]

    self.policy.invalid_attribute_value.behavior = "ignore"
    self.policy.invalid_attribute_value.log_level = log_level

    ept = self.handler._deserialize(elem)
    assert isinstance(ept, Ept)
    assert ept.i is None

    expected_log = (
      self.logger.name,
      log_level,
      "Cannot convert 'invalid' to an int for attribute i",
    )
    assert caplog.record_tuples == [expected_log]
