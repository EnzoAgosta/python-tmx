import logging
from unittest.mock import Mock
import pytest

from python_tmx.base.errors import MissingHandlerError
from python_tmx.base.types import Note
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization import Deserializer
from python_tmx.xml.policy import DeserializationPolicy
from python_tmx.xml.deserialization._handlers import (
  NoteDeserializer,
  PropDeserializer,
  HeaderDeserializer,
  BptDeserializer,
  EptDeserializer,
  ItDeserializer,
  PhDeserializer,
  SubDeserializer,
  HiDeserializer,
  TuvDeserializer,
  TuDeserializer,
  TmxDeserializer,
)


class TestDeserializer[T_XmlElement]:
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

  def test_init_setup_emit(self):
    mock_handler = Mock()
    mock_handler._emit = None

    handlers = {"test_tag": mock_handler}

    deserializer = Deserializer(self.backend, self.policy, handlers=handlers, logger=self.logger)  # type: ignore[arg-type]

    mock_handler._set_emit.assert_called_once_with(deserializer.deserialize)

  def test_load_default_handlers(self, caplog: pytest.LogCaptureFixture):
    deserializer = Deserializer(self.backend, self.policy, logger=self.logger)

    handlers = deserializer.handlers
    assert isinstance(handlers["note"], NoteDeserializer)
    assert isinstance(handlers["prop"], PropDeserializer)
    assert isinstance(handlers["header"], HeaderDeserializer)
    assert isinstance(handlers["tu"], TuDeserializer)
    assert isinstance(handlers["tuv"], TuvDeserializer)
    assert isinstance(handlers["bpt"], BptDeserializer)
    assert isinstance(handlers["ept"], EptDeserializer)
    assert isinstance(handlers["it"], ItDeserializer)
    assert isinstance(handlers["ph"], PhDeserializer)
    assert isinstance(handlers["sub"], SubDeserializer)
    assert isinstance(handlers["hi"], HiDeserializer)
    assert isinstance(handlers["tmx"], TmxDeserializer)

    assert caplog.record_tuples == [(self.logger.name, logging.INFO, "Using default handlers")]

  def test_calls_handlers_deserialize(self):
    note = Note(text="Success")
    mock_note_handler = Mock()
    mock_note_handler._deserialize.return_value = note

    handlers = {"note": mock_note_handler}
    deserializer = Deserializer(self.backend, self.policy, handlers=handlers, logger=self.logger)  # type: ignore[arg-type]

    elem = self.backend.make_elem("note")
    result = deserializer.deserialize(elem)

    assert result is note
    mock_note_handler._deserialize.assert_called_once_with(elem)

  def test_missing_handler_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.backend.make_elem("unknown_tag")

    deserializer = Deserializer(self.backend, self.policy, logger=self.logger)

    self.policy.missing_handler.behavior = "raise"
    self.policy.missing_handler.log_level = log_level

    with pytest.raises(MissingHandlerError, match="Missing handler for <unknown_tag>"):
      deserializer.deserialize(elem)

    assert caplog.record_tuples == [
      (self.logger.name, logging.INFO, "Using default handlers"),
      (self.logger.name, logging.DEBUG, "Deserializing <unknown_tag>"),
      (self.logger.name, log_level, "Missing handler for <unknown_tag>"),
    ]

  def test_missing_handler_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.backend.make_elem("unknown_tag")

    deserializer = Deserializer(self.backend, self.policy, logger=self.logger)

    self.policy.missing_handler.behavior = "ignore"
    self.policy.missing_handler.log_level = log_level

    result = deserializer.deserialize(elem)

    assert result is None
    assert caplog.record_tuples == [
      (self.logger.name, logging.INFO, "Using default handlers"),
      (self.logger.name, logging.DEBUG, "Deserializing <unknown_tag>"),
      (self.logger.name, log_level, "Missing handler for <unknown_tag>"),
    ]

  def test_missing_handler_fallback_default_success(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("note")
    self.backend.set_attr(elem, "{http://www.w3.org/XML/1998/namespace}lang", "en")
    self.backend.set_text(elem, "test")

    mock_header_handler = Mock()
    custom_handlers = {"header": mock_header_handler}

    deserializer = Deserializer(
      self.backend,
      self.policy,
      logger=self.logger,
      handlers=custom_handlers,  # type: ignore[arg-type]
    )

    self.policy.missing_handler.behavior = "default"
    self.policy.missing_handler.log_level = log_level

    result = deserializer.deserialize(elem)

    assert isinstance(result, Note)
    assert caplog.record_tuples == [
      (self.logger.name, logging.DEBUG, "Using custom handlers"),
      (self.logger.name, logging.DEBUG, "Deserializing <note>"),
      (self.logger.name, log_level, "Missing handler for <note>"),
      (self.logger.name, log_level, "Falling back to default handler for <note>"),
    ]

  def test_missing_handler_fallback_default_failure(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("wrong")

    mock_header_handler = Mock()
    custom_handlers = {"header": mock_header_handler}

    deserializer = Deserializer(
      self.backend,
      self.policy,
      logger=self.logger,
      handlers=custom_handlers,  # type: ignore[arg-type]
    )

    self.policy.missing_handler.behavior = "default"
    self.policy.missing_handler.log_level = log_level

    with pytest.raises(MissingHandlerError, match="Missing handler for <wrong>"):
      deserializer.deserialize(elem)

    assert caplog.record_tuples == [
      (self.logger.name, logging.DEBUG, "Using custom handlers"),
      (self.logger.name, logging.DEBUG, "Deserializing <wrong>"),
      (self.logger.name, log_level, "Missing handler for <wrong>"),
      (self.logger.name, log_level, "Falling back to default handler for <wrong>"),
    ]
