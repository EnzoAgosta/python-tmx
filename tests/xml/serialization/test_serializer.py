from typing import Literal
from hypomnema.xml.serialization.base import BaseElementSerializer
from pytest_mock import MockerFixture
from hypomnema.xml.policy import SerializationPolicy, PolicyValue
import logging
import pytest

import hypomnema as hm


class TestSerializer[BackendElementT]:

  backend: hm.XmlBackend[BackendElementT]
  logger: logging.Logger
  policy: SerializationPolicy
  mocker: MockerFixture

  @pytest.fixture(autouse=True)
  def _setup(
    self,
    backend: hm.XmlBackend[BackendElementT],
    test_logger: logging.Logger,
    mocker: MockerFixture,
  ) -> None:
    self.backend = backend
    self.logger = test_logger
    self.policy = SerializationPolicy()
    self.mocker = mocker

  def test_emit_is_wired(self) -> None:
    handlers = {"FakeNote": self.mocker.Mock(spec=BaseElementSerializer, _emit=None)}
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger, handlers=handlers)
    handlers["FakeNote"]._set_emit.assert_called_once_with(serializer.serialize)

  def test_default_handlers_loaded(self, caplog: pytest.LogCaptureFixture) -> None:
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger)
    defaults = serializer.handlers

    expected = {"Note", "Prop", "Header", "Tu", "Tuv", "Bpt", "Ept", "It", "Ph", "Sub", "Hi", "Tmx"}
    assert set(defaults) == expected
    assert all(isinstance(v, BaseElementSerializer) for v in defaults.values())
    assert caplog.record_tuples == [(self.logger.name, logging.DEBUG, "Using default handlers")]

  def test_custom_handlers_loaded(self, caplog: pytest.LogCaptureFixture) -> None:
    custom = {"Mock": self.mocker.Mock(spec=BaseElementSerializer)}
    custom["Mock"]._emit = lambda x: None
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger, handlers=custom)
    assert serializer.handlers is custom
    assert caplog.record_tuples == [(self.logger.name, logging.DEBUG, "Using custom handlers")]

  def test_handler_called(self) -> None:
    note = hm.Note(text="ok")
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger)
    mocked_serialize = self.mocker.Mock()
    serializer.handlers["Note"]._serialize = mocked_serialize

    out = serializer.serialize(note)

    mocked_serialize.assert_called_once_with(note)
    assert out is mocked_serialize.return_value

  @pytest.mark.parametrize(
    "behaviour",
    ["raise", "ignore", "default"],
    ids=["Behaviour=raise", "Behaviour=ignore", "Behaviour=default"],
  )
  def test_missing_handler_policy(
    self,
    behaviour: Literal["raise", "ignore", "default"],
    caplog: pytest.LogCaptureFixture,
    log_level: int,
  ) -> None:
    self.policy.missing_handler = PolicyValue(behaviour, log_level)
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger)
    mock = self.mocker.Mock()

    error_message = "Missing handler for 'Mock'"

    if behaviour == "raise":
      with pytest.raises(hm.MissingHandlerError, match=error_message):
        serializer.serialize(mock)  # type: ignore
      assert len(caplog.record_tuples) == 3
    elif behaviour == "ignore":
      assert serializer.serialize(mock) is None  # type: ignore
      assert len(caplog.record_tuples) == 3
    else:
      with pytest.raises(hm.MissingHandlerError, match=error_message):
        serializer.serialize(mock)  # type: ignore
      assert len(caplog.record_tuples) == 4
