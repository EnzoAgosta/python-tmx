import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.types import Sub
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import SubDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestSubDeserializer[T_XmlElement]:
  handler: SubDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = SubDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_sub_elem(
    self,
    *,
    tag: str = "sub",
    text: str | None = "Valid Sub Content",
    datatype: str | None = "plaintext",
    _type: str | None = "x-test",
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)
    self.backend.set_text(elem, text)
    if datatype is not None:
      self.backend.set_attr(elem, "datatype", datatype)
    if _type is not None:
      self.backend.set_attr(elem, "type", _type)
    return elem

  def test_returns_Sub(self):
    elem = self.make_sub_elem()
    sub = self.handler._deserialize(elem)
    assert isinstance(sub, Sub)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_sub_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "sub")

  def test_calls_parse_attribute_correctly(self):
    mock_parse_attributes = Mock()
    self.handler._parse_attribute = mock_parse_attributes

    elem = self.make_sub_elem()
    self.handler._deserialize(elem)

    mock_parse_attributes.assert_any_call(elem, "datatype", False)
    mock_parse_attributes.assert_any_call(elem, "type", False)

  def test_calls_deserialize_content(self):
    mock_deserialize_content = Mock()
    self.handler.deserialize_content = mock_deserialize_content
    elem = self.make_sub_elem()

    self.handler._deserialize(elem)

    mock_deserialize_content.assert_called_once_with(elem, ("bpt", "ept", "ph", "it", "hi"))
