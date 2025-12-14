import logging
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestNoteSerializer[T]:
  handler: hm.NoteSerializer
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
    self.mocker = mocker
    self.handler = hm.NoteSerializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_note_object(self) -> hm.Note:
    return hm.Note(text="Valid Note Content", lang="en-US", o_encoding="UTF-8")

  def test_calls_backend_make_elem(self):
    original = self.backend.make_elem
    spy_make_elem = Mock(side_effect=lambda x: original(x))
    self.backend.make_elem = spy_make_elem

    note = self.make_note_object()
    self.handler._serialize(note)

    spy_make_elem.assert_called_once_with("note")

  def test_calls_set_attribute(self):
    spy_set_attribute = self.mocker.spy(self.handler, "_set_attribute")

    note = self.make_note_object()

    elem = self.handler._serialize(note)

    assert spy_set_attribute.call_count == 2
    # optional attributes
    spy_set_attribute.assert_any_call(elem, note.o_encoding, "o-encoding", False)
    spy_set_attribute.assert_any_call(elem, note.lang, f"{hm.XML_NS}lang", False)

  def test_calls_backend_set_text(self):
    spy_set_text = self.mocker.spy(self.backend, "set_text")
    note = self.make_note_object()

    elem = self.handler._serialize(note)

    spy_set_text.assert_called_once_with(elem, note.text)

  def test_returns_None_if_not_Note_if_policy_is_ignore(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'NoteSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]
