import logging

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestSerializer[T]:
  backend: hm.XMLBackend[T]
  logger: logging.Logger
  policy: hm.SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup(self, backend: hm.XMLBackend[T], test_logger: logging.Logger, mocker: MockerFixture):
    self.backend = backend
    self.logger = test_logger
    self.policy = hm.SerializationPolicy()
    self.mocker = mocker

  def test_init_setup_emit(self):
    mock_handler = self.mocker.Mock(spec=hm.BaseElementSerializer[T], _emit=None)

    handlers = {"Note": mock_handler}

    serializer = hm.Serializer(self.backend, self.policy, handlers=handlers, logger=self.logger)

    mock_handler._set_emit.assert_called_once_with(serializer.serialize)

  def test_load_default_handlers(self, caplog: pytest.LogCaptureFixture):
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger)

    handlers = serializer.handlers
    assert isinstance(handlers["Note"], hm.NoteSerializer)
    assert isinstance(handlers["Prop"], hm.PropSerializer)
    assert isinstance(handlers["Header"], hm.HeaderSerializer)
    assert isinstance(handlers["Tu"], hm.TuSerializer)
    assert isinstance(handlers["Tuv"], hm.TuvSerializer)
    assert isinstance(handlers["Bpt"], hm.BptSerializer)
    assert isinstance(handlers["Ept"], hm.EptSerializer)
    assert isinstance(handlers["It"], hm.ItSerializer)
    assert isinstance(handlers["Ph"], hm.PhSerializer)
    assert isinstance(handlers["Sub"], hm.SubSerializer)
    assert isinstance(handlers["Hi"], hm.HiSerializer)
    assert isinstance(handlers["Tmx"], hm.TmxSerializer)

    assert caplog.record_tuples == [(self.logger.name, logging.INFO, "Using default handlers")]

  def test_calls_handlers_serialize(self):
    note = hm.Note(text="Success")
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger)
    spy_note_handler = self.mocker.spy(serializer.handlers["Note"], "_serialize")

    serializer.serialize(note)
    spy_note_handler.assert_called_once_with(note)

  def test_missing_handler_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger)

    self.policy.missing_handler.behavior = "raise"
    self.policy.missing_handler.log_level = log_level

    with pytest.raises(hm.MissingHandlerError, match="Missing handler for int"):
      serializer.serialize(1)  # type: ignore

    assert caplog.record_tuples == [
      (self.logger.name, logging.INFO, "Using default handlers"),
      (self.logger.name, logging.DEBUG, "Serializing int"),
      (self.logger.name, log_level, "Missing handler for int"),
    ]

  def test_missing_handler_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger)

    self.policy.missing_handler.behavior = "ignore"
    self.policy.missing_handler.log_level = log_level

    serializer.serialize(1)  # type: ignore

    assert caplog.record_tuples == [
      (self.logger.name, logging.INFO, "Using default handlers"),
      (self.logger.name, logging.DEBUG, "Serializing int"),
      (self.logger.name, log_level, "Missing handler for int"),
    ]

  def test_missing_handler_fallback_default_success(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    handlers = {"Prop": self.mocker.Mock(spec=hm.BaseElementSerializer, _emit=None)}
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger, handlers=handlers)

    self.policy.missing_handler.behavior = "default"
    self.policy.missing_handler.log_level = log_level

    note = hm.Note(text="test")
    serializer.serialize(note)

    assert caplog.record_tuples == [
      (self.logger.name, logging.DEBUG, "Using custom handlers"),
      (self.logger.name, logging.DEBUG, "Serializing Note"),
      (self.logger.name, log_level, "Missing handler for Note"),
      (self.logger.name, log_level, "Falling back to default handler for Note"),
    ]

  def test_missing_handler_fallback_default_failure(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    handlers = {"Prop": self.mocker.Mock(spec=hm.BaseElementSerializer, _emit=None)}
    serializer = hm.Serializer(self.backend, self.policy, logger=self.logger, handlers=handlers)

    self.policy.missing_handler.behavior = "default"
    self.policy.missing_handler.log_level = log_level

    with pytest.raises(hm.MissingHandlerError, match="Missing handler for int"):
      serializer.serialize(1)  # type: ignore

    assert caplog.record_tuples == [
      (self.logger.name, logging.DEBUG, "Using custom handlers"),
      (self.logger.name, logging.DEBUG, "Serializing int"),
      (self.logger.name, log_level, "Missing handler for int"),
      (self.logger.name, log_level, "Falling back to default handler for int"),
    ]
