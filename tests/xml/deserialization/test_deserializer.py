import logging

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestDeserializer[T_XmlElement]:
  backend: hm.XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: hm.DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup(
    self, backend: hm.XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = hm.DeserializationPolicy()
    self.mocker = mocker

  def test_init_setup_emit(self):
    mock_handler = self.mocker.Mock(spec=hm.BaseElementDeserializer)
    mock_handler._emit = None

    handlers = {"test_tag": mock_handler}

    deserializer = hm.Deserializer(self.backend, self.policy, handlers=handlers, logger=self.logger)

    mock_handler._set_emit.assert_called_once_with(deserializer.deserialize)

  def test_load_default_handlers(self, caplog: pytest.LogCaptureFixture):
    deserializer = hm.Deserializer(self.backend, self.policy, logger=self.logger)

    handlers = deserializer.handlers
    assert isinstance(handlers["note"], hm.NoteDeserializer)
    assert isinstance(handlers["prop"], hm.PropDeserializer)
    assert isinstance(handlers["header"], hm.HeaderDeserializer)
    assert isinstance(handlers["tu"], hm.TuDeserializer)
    assert isinstance(handlers["tuv"], hm.TuvDeserializer)
    assert isinstance(handlers["bpt"], hm.BptDeserializer)
    assert isinstance(handlers["ept"], hm.EptDeserializer)
    assert isinstance(handlers["it"], hm.ItDeserializer)
    assert isinstance(handlers["ph"], hm.PhDeserializer)
    assert isinstance(handlers["sub"], hm.SubDeserializer)
    assert isinstance(handlers["hi"], hm.HiDeserializer)
    assert isinstance(handlers["tmx"], hm.TmxDeserializer)

    assert caplog.record_tuples == [(self.logger.name, logging.INFO, "Using default handlers")]

  def test_calls_handlers_deserialize(self):
    note = hm.Note(text="Success")
    mock_handler = self.mocker.Mock(spec=hm.BaseElementDeserializer, _emit=None)
    mock_handler._deserialize.return_value = note

    handlers = {"note": mock_handler}
    deserializer = hm.Deserializer(self.backend, self.policy, handlers=handlers, logger=self.logger)

    elem = self.backend.make_elem("note")
    result = deserializer.deserialize(elem)

    assert result is note
    mock_handler._deserialize.assert_called_once_with(elem)

  def test_missing_handler_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.backend.make_elem("unknown_tag")

    deserializer = hm.Deserializer(self.backend, self.policy, logger=self.logger)

    self.policy.missing_handler.behavior = "raise"
    self.policy.missing_handler.log_level = log_level

    with pytest.raises(hm.MissingHandlerError, match="Missing handler for <unknown_tag>"):
      deserializer.deserialize(elem)

    assert caplog.record_tuples == [
      (self.logger.name, logging.INFO, "Using default handlers"),
      (self.logger.name, logging.DEBUG, "Deserializing <unknown_tag>"),
      (self.logger.name, log_level, "Missing handler for <unknown_tag>"),
    ]

  def test_missing_handler_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.backend.make_elem("unknown_tag")

    deserializer = hm.Deserializer(self.backend, self.policy, logger=self.logger)

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

    mock_header_handler = self.mocker.Mock(spec=hm.BaseElementDeserializer, _emit=None)
    custom_handlers = {"header": mock_header_handler}

    deserializer = hm.Deserializer(
      self.backend, self.policy, logger=self.logger, handlers=custom_handlers
    )

    self.policy.missing_handler.behavior = "default"
    self.policy.missing_handler.log_level = log_level

    result = deserializer.deserialize(elem)

    assert isinstance(result, hm.Note)
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

    mock_header_handler = self.mocker.Mock(spec=hm.BaseElementDeserializer, _emit=None)
    custom_handlers = {"header": mock_header_handler}

    deserializer = hm.Deserializer(
      self.backend, self.policy, logger=self.logger, handlers=custom_handlers
    )

    self.policy.missing_handler.behavior = "default"
    self.policy.missing_handler.log_level = log_level

    with pytest.raises(hm.MissingHandlerError, match="Missing handler for <wrong>"):
      deserializer.deserialize(elem)

    assert caplog.record_tuples == [
      (self.logger.name, logging.DEBUG, "Using custom handlers"),
      (self.logger.name, logging.DEBUG, "Deserializing <wrong>"),
      (self.logger.name, log_level, "Missing handler for <wrong>"),
      (self.logger.name, log_level, "Falling back to default handler for <wrong>"),
    ]
