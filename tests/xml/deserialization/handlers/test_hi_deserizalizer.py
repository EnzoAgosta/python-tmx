import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.types import Hi
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import HiDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestHiDeserializer[T_XmlElement]:
  handler: HiDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = HiDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_hi_elem(
    self,
    *,
    tag: str = "hi",
    text: str | None = "Valid Hi Content",
    x: int | None = 1,
    _type: str | None = "hi",
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)
    self.backend.set_text(elem, text)
    if x is not None:
      self.backend.set_attr(elem, "x", str(x))
    if _type is not None:
      self.backend.set_attr(elem, "type", _type)
    return elem

  def test_returns_Hi(self):
    elem = self.make_hi_elem()
    hi = self.handler._deserialize(elem)
    assert isinstance(hi, Hi)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_hi_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "hi")

  def test_calls_parse_attribute_correctly(self):
    mock_parse_attributes = Mock()
    mock_parse_attributes_as_int = Mock()
    self.handler._parse_attribute = mock_parse_attributes
    self.handler._parse_attribute_as_int = mock_parse_attributes_as_int

    elem = self.make_hi_elem()
    self.handler._deserialize(elem)

    mock_parse_attributes.assert_any_call(elem, "type", False)
    mock_parse_attributes_as_int.assert_called_once_with(elem, "x", False)

  def test_calls_deserialize_content(self):
    mock_deserialize_content = Mock()
    self.handler.deserialize_content = mock_deserialize_content
    elem = self.make_hi_elem()

    self.handler._deserialize(elem)

    mock_deserialize_content.assert_called_once_with(elem, ("bpt", "ept", "ph", "it", "hi"))
