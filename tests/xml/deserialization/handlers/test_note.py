import logging
import pytest
from python_tmx.base.types import Note
from python_tmx.base.errors import InvalidTagError, XmlDeserializationError
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
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = NoteDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_note_elem(
    self,
    *,
    tag: str = "note",
    text: str | None = "Valid Note Content",
    o_encoding: str | None = "UTF-8",
    lang: str | None = "en-US",
  ) -> T_XmlElement:
    """
    Creates a <note> element.

    extra kwargs:
    tag: The tag to use for the element (default: "note")
    text: The text content to use (default: "Valid Note Content")
    o_encoding: The o-encoding attribute to use (default: None or "UTF-8" if full is True)
    lang: The lang attribute to use (default: None or "en-US" if full is True)
    """
    elem = self.backend.make_elem(tag)
    self.backend.set_text(elem, text)
    if lang is not None:
      self.backend.set_attr(elem, f"{XML_NS}lang", lang)
    if o_encoding is not None:
      self.backend.set_attr(elem, "o-encoding", o_encoding)
    return elem

  def test_basic_usage(self, caplog: pytest.LogCaptureFixture):
    """
    Simple and most common usage of the Note deserializer.
    Tests that the Note is correctly constructed from the XML element.
    """
    elem = self.make_note_elem()
    note = self.handler._deserialize(elem)

    assert isinstance(note, Note)
    assert note.text == "Valid Note Content"
    assert note.lang == "en-US"
    assert note.o_encoding == "UTF-8"

    assert caplog.records == []

  def test_check_tag_raises(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Note deserializer raises an error when the tag is incorrect
    if the policy says so and that the error is logged using the policy's log level
    for that event.
    """
    elem = self.make_note_elem(tag="prop")
    self.policy.invalid_tag.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_tag.log_level = log_level
    with pytest.raises(InvalidTagError, match="Incorrect tag: expected note, got prop"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected note, got prop")

    assert caplog.record_tuples == [expected_log]

  def test_check_tag_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Note deserializer ignores an incorrect tag if the policy says so
    and that the error is logged using the policy's log level for that event.

    Note: This creates a Note element that doesn't reflect the original XML.
    """
    elem = self.make_note_elem(tag="prop")
    self.policy.invalid_tag.behavior = "ignore"
    self.policy.invalid_tag.log_level = log_level
    note = self.handler._deserialize(elem)
    assert isinstance(note, Note)
    assert note.text == "Valid Note Content"
    assert note.lang == "en-US"
    assert note.o_encoding == "UTF-8"

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected note, got prop")
    assert caplog.record_tuples == [expected_log]

  def test_missing_text_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Note deserializer raises an error when the text is missing
    if the policy says so and that the error is logged using the policy's log level
    for that event.
    """
    elem = self.make_note_elem(text=None)

    self.policy.missing_text.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.missing_text.log_level = log_level

    with pytest.raises(
      XmlDeserializationError, match="Element <note> does not have any text content"
    ):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Element <note> does not have any text content")
    assert caplog.record_tuples == [expected_log]

  def test_missing_text_empty(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Note deserializer falls back to an empty string when the text is missing
    if the policy says so and that the error is logged using the policy's log level
    for that event.

    Note: This creates a Note element that doesn't reflect the original XML.
    """
    elem = self.make_note_elem(text=None)

    self.policy.missing_text.behavior = "empty"
    self.policy.missing_text.log_level = log_level
    note = self.handler._deserialize(elem)

    assert note.text == ""

    expected_logs = [
      (self.logger.name, log_level, "Element <note> does not have any text content"),
      (self.logger.name, log_level, "Falling back to an empty string"),
    ]

    assert caplog.record_tuples == expected_logs

  def test_missing_text_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    """
    Tests that the Note deserializer ignores an error when the text is missing
    if the policy says so and that the error is logged using the policy's log level
    for that event.

    Note: This creates a invalid Note element that doesn't reflect the original XML.
    """
    elem = self.make_note_elem(text=None)
    self.policy.missing_text.behavior = "ignore"
    self.policy.missing_text.log_level = log_level
    note = self.handler._deserialize(elem)
    assert note.text is None

    expected_log = (self.logger.name, log_level, "Element <note> does not have any text content")
    assert caplog.record_tuples == [expected_log]
