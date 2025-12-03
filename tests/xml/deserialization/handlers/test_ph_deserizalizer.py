import logging

import pytest
from pytest_mock import MockerFixture
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
  def setup_method_fixture(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker
    self.handler = PhDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_ph_elem(self) -> T_XmlElement:
    elem = self.backend.make_elem("ph")
    self.backend.set_text(elem, "Valid Ph Content")
    self.backend.set_attr(elem, "assoc", "p")
    self.backend.set_attr(elem, "x", "1")
    self.backend.set_attr(elem, "type", "ph")
    return elem

  def test_returns_Ph(self):
    elem = self.make_ph_elem()
    ph = self.handler._deserialize(elem)
    assert isinstance(ph, Ph)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    ph = self.make_ph_elem()

    self.handler._deserialize(ph)

    spy_check_tag.assert_called_once_with(ph, "ph")

  def test_calls_parse_attribute_as_int(self):
    spy_parse_attribute_as_int = self.mocker.spy(self.handler, "_parse_attribute_as_int")

    ph = self.make_ph_elem()
    self.handler._deserialize(ph)

    spy_parse_attribute_as_int.assert_called_once_with(ph, "x", False)

  def test_calls_parse_attribute_as_enum(self):
    spy_parse_attribute_as_enum = self.mocker.spy(self.handler, "_parse_attribute_as_enum")

    ph = self.make_ph_elem()
    self.handler._deserialize(ph)

    spy_parse_attribute_as_enum.assert_called_once_with(ph, "assoc", Assoc, False)

  def test_calls_parse_attribute(self):
    spy_parse_attribute = self.mocker.spy(self.handler, "_parse_attribute")

    ph = self.make_ph_elem()
    self.handler._deserialize(ph)

    spy_parse_attribute.assert_called_once_with(ph, "type", False)

  def test_calls_emit(self):
    spy_emit = self.mocker.spy(self.handler, "emit")

    ph = self.make_ph_elem()
    sub_elem = self.backend.make_elem("sub")
    self.backend.append(ph, sub_elem)

    self.handler._deserialize(ph)

    assert spy_emit.call_count == 1
    spy_emit.assert_called_with(sub_elem)

  def test_calls_deserialize_content(self):
    spy_deserialize_content = self.mocker.spy(self.handler, "deserialize_content")

    ph = self.make_ph_elem()

    self.handler._deserialize(ph)

    assert spy_deserialize_content.call_count == 1
    spy_deserialize_content.assert_called_with(ph, ("sub",))
