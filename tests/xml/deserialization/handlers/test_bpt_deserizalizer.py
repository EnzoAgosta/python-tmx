import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.types import Bpt
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

  def test_returns_Bpt(self):
    elem = self.make_bpt_elem()
    bpt = self.handler._deserialize(elem)
    assert isinstance(bpt, Bpt)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_bpt_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "bpt")

  def test_calls_parse_attribute_correctly(self):
    mock_parse_attributes = Mock()
    mock_parse_attributes_as_int = Mock()
    self.handler._parse_attribute = mock_parse_attributes
    self.handler._parse_attribute_as_int = mock_parse_attributes_as_int

    elem = self.make_bpt_elem()
    self.handler._deserialize(elem)

    mock_parse_attributes.assert_any_call(elem, "type", False)

    assert mock_parse_attributes_as_int.call_count == 2
    mock_parse_attributes_as_int.assert_any_call(elem, "i", True)
    mock_parse_attributes_as_int.assert_any_call(elem, "x", False)

  def test_calls_deserialize_content(self):
    mock_deserialize_content = Mock()
    self.handler.deserialize_content = mock_deserialize_content
    elem = self.make_bpt_elem()

    self.handler._deserialize(elem)

    mock_deserialize_content.assert_called_once_with(elem, ("sub",))
