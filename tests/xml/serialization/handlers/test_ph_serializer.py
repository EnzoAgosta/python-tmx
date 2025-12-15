import logging

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestPhSerializer[T_XmlElement]:
  handler: hm.PhSerializer
  backend: hm.XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: hm.SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: hm.XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = hm.SerializationPolicy()
    self.handler = hm.PhSerializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.mocker = mocker

  def make_it_object(self) -> hm.Ph:
    return hm.Ph(assoc=hm.Assoc.P, x=1, type="ph", content=["Ph Content"])

  def test_calls_backend_make_elem(self):
    spy_make_elem = self.mocker.spy(self.backend, "make_elem")

    self.handler._serialize(self.make_it_object())

    spy_make_elem.assert_called_once_with("ph")

  def test_calls_set_int_attribute(self):
    spy_set_int_attribute = self.mocker.spy(self.handler, "_set_int_attribute")
    ph = self.make_it_object()

    elem = self.handler._serialize(ph)

    spy_set_int_attribute.assert_called_once_with(elem, ph.x, "x", False)

  def test_calls_set_enum_attribute(self):
    spy_set_enum_attribute = self.mocker.spy(self.handler, "_set_enum_attribute")
    ph = self.make_it_object()

    elem = self.handler._serialize(ph)

    spy_set_enum_attribute.assert_called_once_with(elem, ph.assoc, "assoc", hm.Assoc, False)

  def test_calls_set_attribute(self):
    spy_set_attribute = self.mocker.spy(self.handler, "_set_attribute")
    ph = self.make_it_object()

    elem = self.handler._serialize(ph)

    spy_set_attribute.assert_called_once_with(elem, ph.type, "type", False)

  def test_calls_deserialize_content(self):
    spy_deserialize_content = self.mocker.spy(self.handler, "serialize_content")

    ph = self.make_it_object()

    elem = self.handler._serialize(ph)

    assert spy_deserialize_content.call_count == 1
    spy_deserialize_content.assert_called_with(ph, elem, (hm.Sub,))

  def test_returns_None_if_not_Ph_if_policy_is_ignore(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'PhSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]
