import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.types import It, Pos
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import ItDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestItDeserializer[T_XmlElement]:
  handler: ItDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = ItDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_it_elem(
    self,
    *,
    tag: str = "it",
    text: str | None = "Valid It Content",
    pos: Pos | None = Pos.BEGIN,
    x: int | None = 1,
    _type: str | None = "it",
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)
    self.backend.set_text(elem, text)
    if pos is not None:
      self.backend.set_attr(elem, "pos", pos.value)
    if x is not None:
      self.backend.set_attr(elem, "x", str(x))
    if _type is not None:
      self.backend.set_attr(elem, "type", _type)
    return elem

  def test_returns_It(self):
    elem = self.make_it_elem()
    it = self.handler._deserialize(elem)
    assert isinstance(it, It)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_it_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "it")

  def test_calls_parse_attribute_correctly(self):
    mock_parse_attributes = Mock()
    mock_parse_attributes_as_int = Mock()
    mock_parse_attributes_as_enum = Mock()
    self.handler._parse_attribute = mock_parse_attributes
    self.handler._parse_attribute_as_int = mock_parse_attributes_as_int
    self.handler._parse_attribute_as_enum = mock_parse_attributes_as_enum

    elem = self.make_it_elem()
    self.handler._deserialize(elem)

    mock_parse_attributes.assert_any_call(elem, "type", False)
    mock_parse_attributes_as_int.assert_called_once_with(elem, "x", False)
    mock_parse_attributes_as_enum.assert_called_once_with(elem, "pos", Pos, True)
