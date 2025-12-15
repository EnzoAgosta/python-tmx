import logging

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestBptSerializer[T]:
  handler: hm.BptSerializer
  backend: hm.XMLBackend[T]
  logger: logging.Logger
  policy: hm.SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: hm.XMLBackend[T], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = hm.SerializationPolicy()
    self.handler = hm.BptSerializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.mocker = mocker

  def make_bpt_object(self) -> hm.Bpt:
    return hm.Bpt(i=1, x=1, type="bpt", content=["Bpt Content"])

  def test_calls_backend_make_elem(self):
    spy_make_elem = self.mocker.spy(self.backend, "make_elem")

    self.handler._serialize(self.make_bpt_object())

    spy_make_elem.assert_called_once_with("bpt")

  def test_calls_set_attribute(self):
    spy_set_attribute = self.mocker.spy(self.handler, "_set_attribute")
    bpt = self.make_bpt_object()

    elem = self.handler._serialize(bpt)

    spy_set_attribute.assert_called_once_with(elem, "bpt", "type", False)

  def test_calls_set_int_attribute(self):
    spy_set_int_attribute = self.mocker.spy(self.handler, "_set_int_attribute")
    bpt = self.make_bpt_object()

    elem = self.handler._serialize(bpt)

    assert spy_set_int_attribute.call_count == 2
    spy_set_int_attribute.assert_any_call(elem, bpt.i, "i", True)
    spy_set_int_attribute.assert_any_call(elem, bpt.x, "x", False)

  def test_calls_deserialize_content(self):
    spy_deserialize_content = self.mocker.spy(self.handler, "serialize_content")

    bpt = self.make_bpt_object()

    elem = self.handler._serialize(bpt)

    assert spy_deserialize_content.call_count == 1
    spy_deserialize_content.assert_called_with(bpt, elem, (hm.Sub,))

  def test_returns_None_if_not_Bpt_if_policy_is_ignore(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'BptSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]
