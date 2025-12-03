import logging

import pytest
from pytest_mock import MockerFixture
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
  def setup_method_fixture(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker
    self.handler = SubDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_sub_elem(self) -> T_XmlElement:
    elem = self.backend.make_elem("sub")
    self.backend.set_text(elem, "Valid Sub Content")
    self.backend.set_attr(elem, "datatype", "plaintext")
    self.backend.set_attr(elem, "type", "sub")
    return elem

  def test_returns_Sub(self):
    elem = self.make_sub_elem()
    sub = self.handler._deserialize(elem)
    assert isinstance(sub, Sub)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    sub = self.make_sub_elem()

    self.handler._deserialize(sub)

    spy_check_tag.assert_called_once_with(sub, "sub")

  def test_calls_emit(self):
    spy_emit = self.mocker.spy(self.handler, "emit")

    sub = self.make_sub_elem()
    bpt_elem = self.backend.make_elem("bpt")
    self.backend.append(sub, bpt_elem)

    self.handler._deserialize(sub)

    assert spy_emit.call_count == 1
    spy_emit.assert_called_with(bpt_elem)

  def test_calls_deserialize_content(self):
    spy_deserialize_content = self.mocker.spy(self.handler, "deserialize_content")

    sub = self.make_sub_elem()

    self.handler._deserialize(sub)

    assert spy_deserialize_content.call_count == 1
    spy_deserialize_content.assert_called_with(sub, ("bpt", "ept", "ph", "it", "hi"))
