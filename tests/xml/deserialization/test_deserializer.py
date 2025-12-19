from hypomnema.xml.deserialization.base import BaseElementDeserializer
from hypomnema.xml.policy import DeserializationPolicy, PolicyValue
from typing import Literal
from pytest_mock import MockerFixture
import pytest
import logging

import hypomnema as hm


class TestDeserializer:
  backend: hm.XmlBackend
  logger: logging.Logger
  policy: DeserializationPolicy
  mocker: MockerFixture

  @pytest.fixture(autouse=True)
  def _setup(
    self, backend: hm.XmlBackend, test_logger: logging.Logger, mocker: MockerFixture
  ) -> None:
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker

  def test_emit_is_wired(self) -> None:
    handlers = {"fake": self.mocker.Mock(spec=BaseElementDeserializer, _emit=None)}
    deserializer = hm.Deserializer(self.backend, self.policy, logger=self.logger, handlers=handlers)
    handlers["fake"]._set_emit.assert_called_once_with(deserializer.deserialize)

  def test_default_handlers_loaded(self, caplog: pytest.LogCaptureFixture) -> None:
    deserializer = hm.Deserializer(self.backend, self.policy, logger=self.logger)
    defaults = deserializer.handlers

    expected = {"note", "prop", "header", "tu", "tuv", "bpt", "ept", "it", "ph", "sub", "hi", "tmx"}
    assert set(defaults) == expected
    assert all(isinstance(v, BaseElementDeserializer) for v in defaults.values())
    assert caplog.record_tuples == [(self.logger.name, logging.INFO, "Using default handlers")]

  def test_custom_handlers_loaded(self, caplog: pytest.LogCaptureFixture) -> None:
    custom = {"mock": self.mocker.Mock(spec=BaseElementDeserializer)}
    custom["mock"]._emit = lambda x: None
    deserializer = hm.Deserializer(self.backend, self.policy, logger=self.logger, handlers=custom)
    assert deserializer.handlers is custom
    assert caplog.record_tuples == [(self.logger.name, logging.DEBUG, "Using custom handlers")]

  def test_handler_called(self) -> None:
    elem = self.backend.make_elem("note")
    deserializer = hm.Deserializer(self.backend, self.policy, logger=self.logger)
    mocked_deserialize = self.mocker.Mock()
    deserializer.handlers["note"]._deserialize = mocked_deserialize

    out = deserializer.deserialize(elem)

    mocked_deserialize.assert_called_once_with(elem)
    assert out is mocked_deserialize.return_value

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
    deserializer = hm.Deserializer(self.backend, self.policy, logger=self.logger)
    mock_elem = self.backend.make_elem("unknown")

    error_message = "Missing handler for <unknown>"

    if behaviour == "raise":
      with pytest.raises(hm.MissingHandlerError, match=error_message):
        deserializer.deserialize(mock_elem)
      assert len(caplog.record_tuples) == 3
    elif behaviour == "ignore":
      out = deserializer.deserialize(mock_elem)
      assert out is None
      assert len(caplog.record_tuples) == 3
    else:
      with pytest.raises(hm.MissingHandlerError, match=error_message):
        deserializer.deserialize(mock_elem)
      assert len(caplog.record_tuples) == 4
