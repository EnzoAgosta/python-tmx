import logging

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestSubSerializer[T]:
  handler: hm.SubSerializer
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
    self.handler = hm.SubSerializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.mocker = mocker

  def make_it_object(self) -> hm.Sub:
    return hm.Sub(datatype="sub", type="sub", content=["Sub Content"])

  def test_calls_backend_make_elem(self):
    spy_make_elem = self.mocker.spy(self.backend, "make_elem")

    self.handler._serialize(self.make_it_object())

    spy_make_elem.assert_called_once_with("sub")

  def test_calls_set_attribute(self):
    spy_set_attribute = self.mocker.spy(self.handler, "_set_attribute")
    sub = self.make_it_object()

    elem = self.handler._serialize(sub)

    assert spy_set_attribute.call_count == 2
    spy_set_attribute.assert_any_call(elem, "sub", "datatype", False)
    spy_set_attribute.assert_any_call(elem, "sub", "type", False)

  def test_calls_deserialize_content(self):
    spy_deserialize_content = self.mocker.spy(self.handler, "serialize_content")

    sub = self.make_it_object()

    elem = self.handler._serialize(sub)

    assert spy_deserialize_content.call_count == 1
    spy_deserialize_content.assert_called_with(
      sub,
      elem,
      (
        hm.Bpt,
        hm.Ept,
        hm.Ph,
        hm.It,
        hm.Hi,
      ),
    )

  def test_returns_None_if_not_Sub_if_policy_is_ignore(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'SubSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]
