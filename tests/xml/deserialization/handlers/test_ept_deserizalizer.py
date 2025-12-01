import logging
from unittest.mock import Mock

import pytest
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

  def test_returns_Ept(self):
    elem = self.make_ept_elem()
    ept = self.handler._deserialize(elem)
    assert isinstance(ept, Ept)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_ept_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "ept")

  def test_calls_parse_attribute_correctly(self):
    mock_parse_attributes_as_int = Mock()
    self.handler._parse_attribute_as_int = mock_parse_attributes_as_int

    elem = self.make_ept_elem()
    self.handler._deserialize(elem)

    mock_parse_attributes_as_int.assert_called_once_with(elem, "i", True)
  
  def test_calls_deserialize_content(self):
    mock_deserialize_content = Mock()
    self.handler.deserialize_content = mock_deserialize_content
    elem = self.make_ept_elem()
    
    self.handler._deserialize(elem)

    mock_deserialize_content.assert_called_once_with(elem, ("sub",))