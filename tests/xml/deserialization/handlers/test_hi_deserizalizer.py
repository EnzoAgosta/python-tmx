import logging

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestHiDeserializer[T_XmlElement]:
  handler: hm.HiDeserializer
  backend: hm.XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: hm.DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: hm.XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = hm.DeserializationPolicy()
    self.mocker = mocker
    self.handler = hm.HiDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_hi_elem(self) -> T_XmlElement:
    elem = self.backend.make_elem("hi")
    self.backend.set_text(elem, "Valid Hi Content")
    self.backend.set_attr(elem, "i", "1")
    self.backend.set_attr(elem, "type", "hi")
    return elem

  def test_returns_Hi(self):
    elem = self.make_hi_elem()
    hi = self.handler._deserialize(elem)
    assert isinstance(hi, hm.Hi)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    hi = self.make_hi_elem()

    self.handler._deserialize(hi)

    spy_check_tag.assert_called_once_with(hi, "hi")

  def test_calls_parse_attribute_as_int(self):
    spy_parse_attribute_as_int = self.mocker.spy(self.handler, "_parse_attribute_as_int")

    hi = self.make_hi_elem()
    self.handler._deserialize(hi)

    spy_parse_attribute_as_int.assert_called_once_with(hi, "x", False)

  def test_calls_emit(self):
    spy_emit = self.mocker.spy(self.handler, "emit")

    hi = self.make_hi_elem()
    bpt_elem = self.backend.make_elem("bpt")
    self.backend.append(hi, bpt_elem)

    self.handler._deserialize(hi)

    assert spy_emit.call_count == 1
    spy_emit.assert_called_with(bpt_elem)

  def test_calls_deserialize_content(self):
    spy_deserialize_content = self.mocker.spy(self.handler, "deserialize_content")

    hi = self.make_hi_elem()

    self.handler._deserialize(hi)

    assert spy_deserialize_content.call_count == 1
    spy_deserialize_content.assert_called_with(hi, ("bpt", "ept", "ph", "it", "hi"))
