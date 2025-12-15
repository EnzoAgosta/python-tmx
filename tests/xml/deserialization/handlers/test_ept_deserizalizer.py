import logging

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestEptDeserializer[T]:
  handler: hm.EptDeserializer
  backend: hm.XMLBackend[T]
  logger: logging.Logger
  policy: hm.DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: hm.XMLBackend[T], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = hm.DeserializationPolicy()
    self.mocker = mocker
    self.handler = hm.EptDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_ept_elem(self) -> T:
    elem = self.backend.make_elem("ept")
    self.backend.set_text(elem, "Valid Ept Content")
    self.backend.set_attr(elem, "i", "1")
    return elem

  def test_returns_Ept(self):
    elem = self.make_ept_elem()
    ept = self.handler._deserialize(elem)
    assert isinstance(ept, hm.Ept)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    ept = self.make_ept_elem()

    self.handler._deserialize(ept)

    spy_check_tag.assert_called_once_with(ept, "ept")

  def test_calls_parse_attribute_as_int(self):
    spy_parse_attribute_as_int = self.mocker.spy(self.handler, "_parse_attribute_as_int")

    ept = self.make_ept_elem()
    self.handler._deserialize(ept)

    spy_parse_attribute_as_int.assert_called_once_with(ept, "i", True)

  def test_calls_emit(self):
    spy_emit = self.mocker.spy(self.handler, "emit")

    ept = self.make_ept_elem()
    sub_elem = self.backend.make_elem("sub")
    self.backend.append(ept, sub_elem)

    self.handler._deserialize(ept)

    assert spy_emit.call_count == 1
    spy_emit.assert_called_with(sub_elem)

  def test_calls_deserialize_content(self):
    spy_deserialize_content = self.mocker.spy(self.handler, "deserialize_content")

    ept = self.make_ept_elem()

    self.handler._deserialize(ept)

    assert spy_deserialize_content.call_count == 1
    spy_deserialize_content.assert_called_with(ept, ("sub",))
