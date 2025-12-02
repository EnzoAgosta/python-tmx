import logging

import pytest
from pytest_mock import MockerFixture
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
  def setup_method_fixture(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker
    self.handler = BptDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_bpt_elem(
    self) -> T_XmlElement:
    elem = self.backend.make_elem("bpt")
    self.backend.set_text(elem, "Valid Bpt Content")
    self.backend.set_attr(elem, "i", "1")
    self.backend.set_attr(elem, "x", "1")
    self.backend.set_attr(elem, "type", "bpt")
    return elem

  def test_returns_Bpt(self):
    elem = self.make_bpt_elem()
    bpt = self.handler._deserialize(elem)
    assert isinstance(bpt, Bpt)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    bpt = self.make_bpt_elem()

    self.handler._deserialize(bpt)

    spy_check_tag.assert_called_once_with(bpt, "bpt")

  def test_calls_parse_attribute_correctly(self):
    spy_parse_attributes = self.mocker.spy(self.handler, "_parse_attribute")
    bpt = self.make_bpt_elem()
    self.handler._deserialize(bpt)

    spy_parse_attributes.assert_called_once_with(bpt, "type", False)

  def test_calls_parse_attribute_as_int_correctly(self):
    spy_parse_attributes_as_int = self.mocker.spy(self.handler, "_parse_attribute_as_int")
    bpt = self.make_bpt_elem()
    self.handler._deserialize(bpt)

    assert spy_parse_attributes_as_int.call_count == 2
    spy_parse_attributes_as_int.assert_any_call(bpt, "i", True)
    spy_parse_attributes_as_int.assert_any_call(bpt, "x", False)

  def test_calls_emit(self):
    spy_emit = self.mocker.spy(self.handler, "emit")

    bpt = self.make_bpt_elem()
    sub_elem = self.backend.make_elem("sub")
    self.backend.append(bpt, sub_elem)

    self.handler._deserialize(bpt)

    assert spy_emit.call_count == 1
    spy_emit.assert_called_with(sub_elem)

  def test_calls_deserialize_content(self):
    spy_deserialize_content = self.mocker.spy(self.handler, "deserialize_content")

    bpt = self.make_bpt_elem()

    self.handler._deserialize(bpt)

    assert spy_deserialize_content.call_count == 1
    spy_deserialize_content.assert_called_with(bpt, ("sub",))
