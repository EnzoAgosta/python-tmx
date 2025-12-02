import logging

import pytest
from pytest_mock import MockerFixture
from python_tmx.base.types import Ept, Sub
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.policy import SerializationPolicy
from python_tmx.xml.serialization._handlers import EptSerializer


class TestEptSerializer[T_XmlElement]:
  handler: EptSerializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = SerializationPolicy()
    self.handler = EptSerializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.mocker = mocker

  def make_ept_object(self) -> Ept:
    return Ept(i=1, content=["Ept Content"])

  def test_calls_backend_make_elem(self):
    spy_make_elem = self.mocker.spy(self.backend, "make_elem")

    self.handler._serialize(self.make_ept_object())

    spy_make_elem.assert_called_once_with("ept")

  def test_calls_set_int_attribute(self):
    spy_set_int_attribute = self.mocker.spy(self.handler, "_set_int_attribute")
    ept = self.make_ept_object()

    elem = self.handler._serialize(ept)

    spy_set_int_attribute.assert_called_once_with(elem, ept.i, "i", True)

  def test_calls_deserialize_content(self):
    spy_deserialize_content = self.mocker.spy(self.handler, "serialize_content")

    ept = self.make_ept_object()

    elem = self.handler._serialize(ept)

    assert spy_deserialize_content.call_count == 1
    spy_deserialize_content.assert_called_with(ept, elem, (Sub,))

  def test_returns_None_if_not_Ept_if_policy_is_ignore(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'EptSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]
