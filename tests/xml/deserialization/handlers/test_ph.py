import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.types import Assoc, Ph
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

  def test_returns_Ph(self):
    elem = self.make_ph_elem()
    ph = self.handler._deserialize(elem)
    assert isinstance(ph, Ph)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_ph_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "ph")

  def test_calls_parse_attribute_correctly(self):
    mock_parse_attributes = Mock()
    mock_parse_attributes_as_int = Mock()
    mock_parse_attributes_as_enum = Mock()
    self.handler._parse_attribute = mock_parse_attributes
    self.handler._parse_attribute_as_int = mock_parse_attributes_as_int
    self.handler._parse_attribute_as_enum = mock_parse_attributes_as_enum

    elem = self.make_ph_elem()
    self.handler._deserialize(elem)

    mock_parse_attributes.assert_any_call(elem, "type", False)
    mock_parse_attributes_as_int.assert_called_once_with(elem, "x", False)
    mock_parse_attributes_as_enum.assert_called_once_with(elem, "assoc", Assoc, False)

  def test_calls_deserialize_content(self):
    mock_deserialize_content = Mock()
    self.handler.deserialize_content = mock_deserialize_content
    elem = self.make_ph_elem()

    self.handler._deserialize(elem)

    mock_deserialize_content.assert_called_once_with(elem, ("sub",))
