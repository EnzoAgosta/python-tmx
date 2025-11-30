import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.errors import (
  AttributeDeserializationError,
  InvalidTagError,
  XmlDeserializationError,
)
from python_tmx.base.types import Bpt, Sub
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import BptDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestBptDeserializer[T_XmlElement]:
  handler: BptDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = BptDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_bpt_elem(
    self,
    *,
    tag: str = "bpt",
    text: str | None = "Valid Bpt Content",
    i: int | None = 1,
    x: int | None = 1,
    _type: str | None = "bpt",
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)
    self.backend.set_text(elem, text)
    if i is not None:
      self.backend.set_attr(elem, "i", str(i))
    if x is not None:
      self.backend.set_attr(elem, "x", str(x))
    if _type is not None:
      self.backend.set_attr(elem, "type", _type)
    return elem

  def test_basic_usage(self):
    elem = self.make_bpt_elem()
    bpt = self.handler._deserialize(elem)
    assert isinstance(bpt, Bpt)
    assert bpt.i == 1
    assert bpt.x == 1
    assert bpt.type == "bpt"
    assert bpt.content == ["Valid Bpt Content"]

  def test_mixed_content(self):
    elem = self.make_bpt_elem()
    sub_elem = self.backend.make_elem("sub")
    self.backend.set_text(sub_elem, "Sub Content")
    self.backend.set_tail(sub_elem, "Sub Tail")
    self.backend.append(elem, sub_elem)

    mock_emit = Mock(return_value=Sub(content=["Sub Content"]))
    self.handler._set_emit(mock_emit)

    ept = self.handler._deserialize(elem)
    
    assert isinstance(ept, Bpt)
    assert ept.content == ["Valid Bpt Content", mock_emit.return_value, "Sub Tail"]

    assert mock_emit.call_count == 1
    for i in self.backend.iter_children(elem):
      mock_emit.assert_any_call(i)

  def test_check_tag_raises(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_bpt_elem(tag="prop")

    self.policy.invalid_tag.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_tag.log_level = log_level

    with pytest.raises(InvalidTagError, match="Incorrect tag: expected bpt, got prop"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected bpt, got prop")
    assert caplog.record_tuples == [expected_log]

  def test_check_tag_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_bpt_elem(tag="prop")

    self.policy.invalid_tag.behavior = "ignore"
    self.policy.invalid_tag.log_level = log_level

    bpt = self.handler._deserialize(elem)
    assert isinstance(bpt, Bpt)
    assert bpt.i == 1
    assert bpt.x == 1
    assert bpt.type == "bpt"

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected bpt, got prop")
    assert caplog.record_tuples == [expected_log]

  def test_missing_content_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_bpt_elem(text=None)
    self.policy.empty_content.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.empty_content.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Element <bpt> is empty"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Element <bpt> is empty")
    assert caplog.record_tuples == [expected_log]

  def test_empty_content_empty_string_fallback(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.make_bpt_elem(text=None)

    self.policy.empty_content.behavior = "empty"
    self.policy.empty_content.log_level = log_level
    bpt = self.handler._deserialize(elem)

    assert bpt.content == [""]

    expected_logs = [
      (self.logger.name, log_level, "Element <bpt> is empty"),
      (self.logger.name, log_level, "Falling back to an empty string"),
    ]

    assert caplog.record_tuples == expected_logs

  def test_empty_content_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_bpt_elem(text=None)

    self.policy.empty_content.behavior = "ignore"
    self.policy.empty_content.log_level = log_level

    bpt = self.handler._deserialize(elem)
    assert isinstance(bpt, Bpt)
    assert bpt.content == []

    expected_log = (self.logger.name, log_level, "Element <bpt> is empty")
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_bpt_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_child_element.log_level = log_level

    with pytest.raises(
      XmlDeserializationError,
      match="Incorrect child element in bpt: expected one of sub, got wrong",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Incorrect child element in bpt: expected one of sub, got wrong",
    )
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_bpt_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    bpt = self.handler._deserialize(elem)
    assert isinstance(bpt, Bpt)
    assert bpt.content == ["Valid Bpt Content"]

    expected_log = (
      self.logger.name,
      log_level,
      "Incorrect child element in bpt: expected one of sub, got wrong",
    )
    assert caplog.record_tuples == [expected_log]

  def test_missing_required_attribute_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_bpt_elem(i=None)

    self.policy.required_attribute_missing.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.required_attribute_missing.log_level = log_level

    with pytest.raises(
      AttributeDeserializationError, match="Missing required attribute 'i' on element <bpt>"
    ):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Missing required attribute 'i' on element <bpt>")
    assert caplog.record_tuples == [expected_log]

  @pytest.mark.parametrize("value", ["i", "x"], ids=["i='invalid', ", "x='invalid', "])
  def test_parse_attribute_as_int_raise(self, caplog: pytest.LogCaptureFixture, log_level: int, value:str):
    elem = self.make_bpt_elem(**{f"{value}":"invalid"})  # type: ignore[arg-type]

    self.policy.invalid_attribute_value.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_attribute_value.log_level = log_level

    with pytest.raises(
      AttributeDeserializationError,
      match=f"Cannot convert 'invalid' to an int for attribute {value}",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      f"Cannot convert 'invalid' to an int for attribute {value}",
    )
    assert caplog.record_tuples == [expected_log]
  
  @pytest.mark.parametrize("value", ["i", "x"], ids=["i='invalid', ", "x='invalid', "])
  def test_parse_attribute_as_int_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int, value:str):
    elem = self.make_bpt_elem(**{f"{value}":"invalid"})  # type: ignore[arg-type]

    self.policy.invalid_attribute_value.behavior = "ignore"
    self.policy.invalid_attribute_value.log_level = log_level

    bpt = self.handler._deserialize(elem)
    assert isinstance(bpt, Bpt)
    assert getattr(bpt, value) is None

    expected_log = (
      self.logger.name,
      log_level,
      f"Cannot convert 'invalid' to an int for attribute {value}",
    )
    assert caplog.record_tuples == [expected_log]