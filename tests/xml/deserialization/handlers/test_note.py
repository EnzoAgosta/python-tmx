import logging
import pytest
from python_tmx.base.types import Note
from python_tmx.base.errors import AttributeDeserializationError, InvalidTagError, XmlDeserializationError
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

  def make_valid_elem(self, *, full: bool = False) -> T_XmlElement:
    """
    Creates a <note> element.
    If full is True, all optional attributes are filled.
    If text is not None, it is set as the note content (default: "Valid Note Content").
    """
    elem = self.backend.make_elem("note")
    self.backend.set_attr(elem, f"{XML_NS}lang", "en-US")
    self.backend.set_text(elem, "Valid Note Content")
    if full:
      self.backend.set_attr(elem, "o-encoding", "UTF-8")
    return elem

  def test_minimal_valid(self):
    elem = self.make_valid_elem()
    note = self.handler._deserialize(elem)

    assert isinstance(note, Note)
    assert note.text == "Valid Note Content"
    assert note.lang == "en-US"
    assert note.o_encoding is None

  def test_full_valid(self):
    elem = self.make_valid_elem(full=True)
    note = self.handler._deserialize(elem)

    assert note.o_encoding == "UTF-8"

  def test_check_tag(self):
    elem = self.backend.make_elem("prop")

    with pytest.raises(InvalidTagError, match="expected note"):
      self.handler._deserialize(elem)

  def test_missing_required_lang(self):
    """xml:lang is required for <note>."""
    elem = self.backend.make_elem("note")
    self.backend.set_text(elem, "Content")

    with pytest.raises(AttributeDeserializationError, match="Missing required attribute"):
      self.handler._deserialize(elem)

  def test_missing_text_raise(self):
    """Policy: Text missing -> Raise (Default)."""
    elem = self.make_valid_elem()
    self.backend.set_text(elem, None)

    with pytest.raises(XmlDeserializationError, match="does not have any text content"):
      self.handler._deserialize(elem)

  def test_missing_text_empty(self):
    """Policy: Text missing -> Return empty string."""
    elem = self.make_valid_elem()
    self.backend.set_text(elem, None)

    self.policy.missing_text.behavior = "empty"

    note = self.handler._deserialize(elem)
    assert note.text == ""

  def test_missing_text_ignore(self):
    """Policy: Text missing -> Return None (if typing allows) or backend default."""
    elem = self.make_valid_elem()
    self.backend.set_text(elem, None)

    self.policy.missing_text.behavior = "ignore"

    note = self.handler._deserialize(elem)

    assert note.text is None
