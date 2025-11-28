import logging
from datetime import datetime
from typing import Any

import pytest

from python_tmx.base.errors import (
  AttributeDeserializationError,
  InvalidTagError,
  XmlDeserializationError,
)
from python_tmx.base.types import Header, Note, Prop, Segtype
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import HeaderDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestHeaderDeserializer[T_XmlElement]:
  handler: HeaderDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = HeaderDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)

    self.handler._set_emit(lambda x: None)

  def make_valid_elem(self, *, full: bool = False, notes: bool = False, props: bool = False) -> T_XmlElement:
    """
    Helper to create a valid header element.
    If full is True, all optional attributes are filled.
    If notes is True, a note is added to the header.
    If props is True, a prop is added to the header.
    """
    elem = self.backend.make_elem("header")
    self.backend.set_attr(elem, "creationtool", "pytest")
    self.backend.set_attr(elem, "creationtoolversion", "v1")
    self.backend.set_attr(elem, "segtype", "sentence")
    self.backend.set_attr(elem, "o-tmf", "TestTMF")
    self.backend.set_attr(elem, "adminlang", "en-US")
    self.backend.set_attr(elem, "srclang", "en-US")
    self.backend.set_attr(elem, "datatype", "plaintext")
    if full:
      self.backend.set_attr(elem, "o-encoding", "UTF-8")
      self.backend.set_attr(elem, "creationid", "User1")
      self.backend.set_attr(elem, "changeid", "User2")
      self.backend.set_attr(elem, "creationdate", "20250101T120000Z")
      self.backend.set_attr(elem, "changedate", "20250201T143000Z")
    if notes:
      self.backend.append(elem, self.backend.make_elem("note"))
    if props:
      self.backend.append(elem, self.backend.make_elem("prop"))
    return elem

  def test_minimal_valid(self):
    """Verifies that a header with only required attributes parses correctly."""
    elem = self.make_valid_elem()
    header = self.handler._deserialize(elem)

    assert header.creationtool == "pytest"
    assert header.segtype == Segtype.SENTENCE
    assert header.creationdate is None
    assert header.props == []

  def test_full_valid(self):
    """Verifies that all optional attributes and dates are parsed correctly."""
    elem = self.make_valid_elem(full=True)
    header = self.handler._deserialize(elem)

    assert header.o_encoding == "UTF-8"
    assert header.creationid == "User1"
    assert header.changeid == "User2"
    assert header.creationdate == datetime(2025, 1, 1, 12, 0, 0)
    assert header.changedate == datetime(2025, 2, 1, 14, 30, 0)

  def test_valid_tag_check(self):
    """Verifies the base class _check_tag logic."""
    elem = self.backend.make_elem("tmx")  # Wrong tag
    with pytest.raises(InvalidTagError, match="expected header, got tmx"):
      self.handler._deserialize(elem)

  def test_segtype_parsing_error(self):
    """Verifies enum conversion for segtype."""
    elem = self.make_valid_elem()

    self.backend.set_attr(elem, "segtype", "invalid_enum_value")
    with pytest.raises(AttributeDeserializationError, match="Invalid enum value"):
      self.handler._deserialize(elem)

  def test_date_parsing_iso_fallback(self, caplog:pytest.LogCaptureFixture):
    """
    Verifies that we accept ISO formatted dates (common in wild TMX)
    even if they don't match the strict TMX spec, but log an INFO message.
    """
    elem = self.make_valid_elem()
    self.backend.set_attr(elem, "creationdate", "2025-01-01T12:00:00")

    with caplog.at_level(logging.INFO, logger="python_tmx.test"):
      header = self.handler._deserialize(elem)

    assert header.creationdate == datetime(2025, 1, 1, 12, 0, 0)
    assert any("Falling back to iso format" in r.message for r in caplog.records)

  def test_date_parsing_failure(self):
    """Verifies that completely malformed dates raise an error."""
    elem = self.make_valid_elem()
    self.backend.set_attr(elem, "creationdate", "not-a-date-string")

    with pytest.raises(AttributeDeserializationError, match="Invalid datetime value"):
      self.handler._deserialize(elem)

  def test_children_processing_mocked(self):
    """
    Verifies that props and notes are correctly identified, emitted,
    and added to the correct lists.
    """
    elem = self.make_valid_elem(notes=True, props=True)

    mock_prop = Prop(text="P", type="t")
    mock_note = Note(text="N")

    def mock_emit(child_elem) -> Any:
      tag = self.backend.get_tag(child_elem)
      if tag == "prop":
        return mock_prop
      if tag == "note":
        return mock_note
      return None

    self.handler._set_emit(mock_emit)

    header = self.handler._deserialize(elem)

    assert len(header.props) == 1
    assert header.props[0] == mock_prop
    assert len(header.notes) == 1
    assert header.notes[0] == mock_note

  def test_missing_required_attribute_raise(self):
    """Policy: Missing Required Attr -> Raise."""
    elem_bad = self.backend.make_elem("header")

    with pytest.raises(AttributeDeserializationError, match="Missing required attribute"):
      self.handler._deserialize(elem_bad)

  def test_extra_text_content_raise(self):
    """Policy: Text content in header -> Raise."""
    elem = self.make_valid_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    with pytest.raises(XmlDeserializationError, match="extra text content"):
      self.handler._deserialize(elem)

  def test_extra_text_content_ignore(self):
    """Policy: Text content in header -> Ignore."""
    elem = self.make_valid_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "ignore"

    header = self.handler._deserialize(elem)
    assert isinstance(header, Header)

  def test_invalid_child_raise(self):
    """Policy: Invalid child element -> Raise."""
    elem = self.make_valid_elem()
    self.backend.append(elem, self.backend.make_elem("tu"))

    self.policy.invalid_child_element.behavior = "raise"

    with pytest.raises(XmlDeserializationError, match="Invalid child element <tu>"):
      self.handler._deserialize(elem)

  def test_invalid_child_ignore(self):
    """Policy: Invalid child element -> Ignore."""
    elem = self.make_valid_elem()
    self.backend.append(elem, self.backend.make_elem("tu"))

    self.policy.invalid_child_element.behavior = "ignore"

    header = self.handler._deserialize(elem)
    assert header.props == []
    assert header.notes == []
