import logging
import pytest
from pytest_mock import MockerFixture

from python_tmx.base.errors import MissingHandlerError
from python_tmx.base.types import Note
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.serialization import Serializer
from python_tmx.xml.serialization.base import BaseElementSerializer
from python_tmx.xml.policy import SerializationPolicy
from python_tmx.xml.serialization._handlers import (
  NoteSerializer,
  PropSerializer,
  HeaderSerializer,
  BptSerializer,
  EptSerializer,
  ItSerializer,
  PhSerializer,
  SubSerializer,
  HiSerializer,
  TuvSerializer,
  TuSerializer,
  TmxSerializer,
)


class TestSerializer[T_XmlElement]:
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = SerializationPolicy()
    self.mocker = mocker

  def test_init_setup_emit(self):
    mock_handler = self.mocker.Mock(spec=BaseElementSerializer[T_XmlElement], _emit=None)

    handlers = {"Note": mock_handler}

    serializer = Serializer(self.backend, self.policy, handlers=handlers, logger=self.logger)

    mock_handler._set_emit.assert_called_once_with(serializer.serialize)

  def test_load_default_handlers(self, caplog: pytest.LogCaptureFixture):
    serializer = Serializer(self.backend, self.policy, logger=self.logger)

    handlers = serializer.handlers
    assert isinstance(handlers["Note"], NoteSerializer)
    assert isinstance(handlers["Prop"], PropSerializer)
    assert isinstance(handlers["Header"], HeaderSerializer)
    assert isinstance(handlers["Tu"], TuSerializer)
    assert isinstance(handlers["Tuv"], TuvSerializer)
    assert isinstance(handlers["Bpt"], BptSerializer)
    assert isinstance(handlers["Ept"], EptSerializer)
    assert isinstance(handlers["It"], ItSerializer)
    assert isinstance(handlers["Ph"], PhSerializer)
    assert isinstance(handlers["Sub"], SubSerializer)
    assert isinstance(handlers["Hi"], HiSerializer)
    assert isinstance(handlers["Tmx"], TmxSerializer)

    assert caplog.record_tuples == [(self.logger.name, logging.INFO, "Using default handlers")]

  def test_calls_handlers_serialize(self):
    note = Note(text="Success")
    serializer = Serializer(self.backend, self.policy, logger=self.logger)
    spy_note_handler = self.mocker.spy(serializer.handlers["Note"], "_serialize")

    serializer.serialize(note)
    spy_note_handler.assert_called_once_with(note)

  def test_missing_handler_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    serializer = Serializer(self.backend, self.policy, logger=self.logger)

    self.policy.missing_handler.behavior = "raise"
    self.policy.missing_handler.log_level = log_level

    with pytest.raises(MissingHandlerError, match="Missing handler for int"):
      serializer.serialize(1)  # type: ignore

    assert caplog.record_tuples == [
      (self.logger.name, logging.INFO, "Using default handlers"),
      (self.logger.name, logging.DEBUG, "Serializing int"),
      (self.logger.name, log_level, "Missing handler for int"),
    ]

  def test_missing_handler_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    serializer = Serializer(self.backend, self.policy, logger=self.logger)

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
    handlers = {"Prop": self.mocker.Mock(spec=BaseElementSerializer, _emit=None)}
    serializer = Serializer(self.backend, self.policy, logger=self.logger, handlers=handlers)

    self.policy.missing_handler.behavior = "default"
    self.policy.missing_handler.log_level = log_level

    note = Note(text="test")
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
    handlers = {"Prop": self.mocker.Mock(spec=BaseElementSerializer, _emit=None)}
    serializer = Serializer(self.backend, self.policy, logger=self.logger, handlers=handlers)

    self.policy.missing_handler.behavior = "default"
    self.policy.missing_handler.log_level = log_level

    with pytest.raises(MissingHandlerError, match="Missing handler for int"):
      serializer.serialize(1)  # type: ignore

    assert caplog.record_tuples == [
      (self.logger.name, logging.DEBUG, "Using custom handlers"),
      (self.logger.name, logging.DEBUG, "Serializing int"),
      (self.logger.name, log_level, "Missing handler for int"),
      (self.logger.name, log_level, "Falling back to default handler for int"),
    ]
