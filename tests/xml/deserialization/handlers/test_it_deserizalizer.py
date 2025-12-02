import logging

import pytest
from pytest_mock import MockerFixture
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
  def setup_method_fixture(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker
    self.handler = ItDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_it_elem(self) -> T_XmlElement:
    elem = self.backend.make_elem("it")
    self.backend.set_text(elem, "Valid It Content")
    self.backend.set_attr(elem, "pos", "begin")
    self.backend.set_attr(elem, "x", "1")
    self.backend.set_attr(elem, "type", "it")
    return elem

  def test_returns_It(self):
    elem = self.make_it_elem()
    it = self.handler._deserialize(elem)
    assert isinstance(it, It)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    it = self.make_it_elem()

    self.handler._deserialize(it)

    spy_check_tag.assert_called_once_with(it, "it")

  def test_calls_parse_attribute_correctly(self):
    spy_parse_attributes = self.mocker.spy(self.handler, "_parse_attribute")
    it = self.make_it_elem()
    self.handler._deserialize(it)

    spy_parse_attributes.assert_called_once_with(it, "type", False)

  def test_calls_parse_attribute_as_int_correctly(self):
    spy_parse_attributes_as_int = self.mocker.spy(self.handler, "_parse_attribute_as_int")
    it = self.make_it_elem()
    self.handler._deserialize(it)

    spy_parse_attributes_as_int.assert_called_once_with(it, "x", False)
  
  def test_calls_parse_attribute_as_enum_correctly(self):
    spy_parse_attributes_as_enum = self.mocker.spy(self.handler, "_parse_attribute_as_enum")
    it = self.make_it_elem()
    self.handler._deserialize(it)

    spy_parse_attributes_as_enum.assert_called_once_with(it, "pos", Pos, True)

  def test_calls_emit(self):
    spy_emit = self.mocker.spy(self.handler, "emit")

    it = self.make_it_elem()
    sub_elem = self.backend.make_elem("sub")
    self.backend.append(it, sub_elem)

    self.handler._deserialize(it)

    assert spy_emit.call_count == 1
    spy_emit.assert_called_with(sub_elem)

  def test_calls_deserialize_content(self):
    spy_deserialize_content = self.mocker.spy(self.handler, "deserialize_content")

    it = self.make_it_elem()

    self.handler._deserialize(it)

    assert spy_deserialize_content.call_count == 1
    spy_deserialize_content.assert_called_with(it, ("sub",))
