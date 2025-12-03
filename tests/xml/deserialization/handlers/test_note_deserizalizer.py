import logging

import pytest
from pytest_mock import MockerFixture
from python_tmx.base.errors import XmlDeserializationError
from python_tmx.base.types import Note
from python_tmx.xml import XML_NS
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import NoteDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestNoteDeserializer[T_XmlElement]:
  handler: NoteDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker
    self.handler = NoteDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_note_elem(self) -> T_XmlElement:
    elem = self.backend.make_elem("note")
    self.backend.set_text(elem, "Valid Note Content")
    self.backend.set_attr(elem, f"{XML_NS}lang", "en")
    self.backend.set_attr(elem, "o-encoding", "base64")
    return elem

  def test_returns_Note(self):
    elem = self.make_note_elem()
    note = self.handler._deserialize(elem)
    assert isinstance(note, Note)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    note = self.make_note_elem()

    self.handler._deserialize(note)

    spy_check_tag.assert_called_once_with(note, "note")

  def test_calls_parse_attribute_correctly(self):
    spy_parse_attributes = self.mocker.spy(self.handler, "_parse_attribute")
    note = self.make_note_elem()
    self.handler._deserialize(note)

    assert spy_parse_attributes.call_count == 2
    spy_parse_attributes.assert_any_call(note, "o-encoding", False)
    spy_parse_attributes.assert_any_call(note, f"{XML_NS}lang", False)

  def test_calls_parse_backend_get_text(self):
    spy_get_text = self.mocker.spy(self.backend, "get_text")

    note = self.make_note_elem()
    self.handler._deserialize(note)

    assert spy_get_text.call_count == 1
    spy_get_text.assert_called_with(note)

  def test_raises_if_text_is_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.empty_content.log_level = log_level
    self.policy.empty_content.behavior = "raise"

    elem = self.make_note_elem()
    self.backend.set_text(elem, None)

    with pytest.raises(XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Element <note> does not have any text content"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignores_if_text_is_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.empty_content.log_level = log_level
    self.policy.empty_content.behavior = "ignore"

    elem = self.make_note_elem()
    self.backend.set_text(elem, None)

    self.handler._deserialize(elem)

    log_message = "Element <note> does not have any text content"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_fallbacks_to_empty_string_if_text_is_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.empty_content.log_level = log_level
    self.policy.empty_content.behavior = "empty"

    elem = self.make_note_elem()
    self.backend.set_text(elem, None)

    note = self.handler._deserialize(elem)
    assert note.text == ""

    empty_log_message = "Element <note> does not have any text content"
    empty_fallback_log_message = "Falling back to an empty string"
    expected_empty_log = (self.logger.name, log_level, empty_log_message)
    expected_empty_fallback_log = (self.logger.name, log_level, empty_fallback_log_message)

    assert caplog.record_tuples == [expected_empty_log, expected_empty_fallback_log]

  def test_raise_if_any_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "raise"

    elem = self.make_note_elem()
    self.backend.append(elem, self.backend.make_elem("sub"))

    with pytest.raises(XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Invalid child element <sub> in <note>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_any_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "ignore"

    elem = self.make_note_elem()
    self.backend.append(elem, self.backend.make_elem("sub"))

    self.handler._deserialize(elem)

    log_message = "Invalid child element <sub> in <note>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]