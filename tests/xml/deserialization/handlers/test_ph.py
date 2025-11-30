import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.errors import (
  AttributeDeserializationError,
  InvalidTagError,
  XmlDeserializationError,
)
from python_tmx.base.types import Assoc, Ph, Sub
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import PhDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestPhDeserializer[T_XmlElement]:
  handler: PhDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = PhDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_ph_elem(
    self,
    *,
    tag: str = "ph",
    text: str | None = "Valid Ph Content",
    x: int | None = 1,
    _type: str | None = "ph",
    assoc: Assoc | None = Assoc.P,
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)
    self.backend.set_text(elem, text)
    if x is not None:
      self.backend.set_attr(elem, "x", str(x))
    if _type is not None:
      self.backend.set_attr(elem, "type", _type)
    if assoc is not None:
      self.backend.set_attr(elem, "assoc", assoc.value)
    return elem

  def test_basic_usage(self):
    elem = self.make_ph_elem()
    ph = self.handler._deserialize(elem)
    assert isinstance(ph, Ph)
    assert ph.x == 1
    assert ph.type == "ph"
    assert ph.assoc is Assoc.P
    assert ph.content == ["Valid Ph Content"]

  def test_mixed_content(self):
    elem = self.make_ph_elem()
    sub_elem = self.backend.make_elem("sub")
    self.backend.set_text(sub_elem, "Sub Content")
    self.backend.set_tail(sub_elem, "Sub Tail")
    self.backend.append(elem, sub_elem)

    mock_emit = Mock(return_value=Sub(content=["Sub Content"]))
    self.handler._set_emit(mock_emit)

    ept = self.handler._deserialize(elem)
    
    assert isinstance(ept, Ph)
    assert ept.content == ["Valid Ph Content", mock_emit.return_value, "Sub Tail"]

    assert mock_emit.call_count == 1
    for i in self.backend.iter_children(elem):
      mock_emit.assert_any_call(i)

  def test_check_tag_raises(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ph_elem(tag="prop")

    self.policy.invalid_tag.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_tag.log_level = log_level

    with pytest.raises(InvalidTagError, match="Incorrect tag: expected ph, got prop"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected ph, got prop")
    assert caplog.record_tuples == [expected_log]

  def test_check_tag_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ph_elem(tag="prop")

    self.policy.invalid_tag.behavior = "ignore"
    self.policy.invalid_tag.log_level = log_level

    ph = self.handler._deserialize(elem)
    assert isinstance(ph, Ph)

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected ph, got prop")
    assert caplog.record_tuples == [expected_log]

  def test_missing_content_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ph_elem(text=None)
    self.policy.empty_content.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.empty_content.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Element <ph> is empty"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Element <ph> is empty")
    assert caplog.record_tuples == [expected_log]

  def test_empty_content_empty_string_fallback(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.make_ph_elem(text=None)

    self.policy.empty_content.behavior = "empty"
    self.policy.empty_content.log_level = log_level
    ph = self.handler._deserialize(elem)

    assert ph.content == [""]

    expected_logs = [
      (self.logger.name, log_level, "Element <ph> is empty"),
      (self.logger.name, log_level, "Falling back to an empty string"),
    ]

    assert caplog.record_tuples == expected_logs

  def test_empty_content_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ph_elem(text=None)

    self.policy.empty_content.behavior = "ignore"
    self.policy.empty_content.log_level = log_level

    ph = self.handler._deserialize(elem)
    assert isinstance(ph, Ph)
    assert ph.content == []

    expected_log = (self.logger.name, log_level, "Element <ph> is empty")
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ph_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_child_element.log_level = log_level

    with pytest.raises(
      XmlDeserializationError,
      match="Incorrect child element in ph: expected one of sub, got wrong",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Incorrect child element in ph: expected one of sub, got wrong",
    )
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ph_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    ph = self.handler._deserialize(elem)
    assert isinstance(ph, Ph)
    assert ph.content == ["Valid Ph Content"]

    expected_log = (
      self.logger.name,
      log_level,
      "Incorrect child element in ph: expected one of sub, got wrong",
    )
    assert caplog.record_tuples == [expected_log]


  def test_parse_attribute_as_int_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ph_elem(x="invalid")  # type: ignore[arg-type]

    self.policy.invalid_attribute_value.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_attribute_value.log_level = log_level

    with pytest.raises(
      AttributeDeserializationError,
      match="Cannot convert 'invalid' to an int for attribute x",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Cannot convert 'invalid' to an int for attribute x",
    )
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_int_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ph_elem(x="invalid")  # type: ignore[arg-type]

    self.policy.invalid_attribute_value.behavior = "ignore"
    self.policy.invalid_attribute_value.log_level = log_level

    ph = self.handler._deserialize(elem)
    assert isinstance(ph, Ph)
    assert ph.x is None

    expected_log = (
      self.logger.name,
      log_level,
      "Cannot convert 'invalid' to an int for attribute x",
    )
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_enum_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ph_elem()
    self.backend.set_attr(elem, "assoc", "invalid")

    self.policy.invalid_attribute_value.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_attribute_value.log_level = log_level

    with pytest.raises(
      AttributeDeserializationError,
      match="Value 'invalid' is not a valid enum value for attribute assoc",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Value 'invalid' is not a valid enum value for attribute assoc",
    )
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_enum_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_ph_elem()
    self.backend.set_attr(elem, "assoc", "invalid")

    self.policy.invalid_attribute_value.behavior = "ignore"
    self.policy.invalid_attribute_value.log_level = log_level

    ph = self.handler._deserialize(elem)
    assert isinstance(ph, Ph)
    assert ph.assoc is None

    expected_log = (
      self.logger.name,
      log_level,
      "Value 'invalid' is not a valid enum value for attribute assoc",
    )
    assert caplog.record_tuples == [expected_log]