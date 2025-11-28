import logging

import pytest

from python_tmx.base.errors import (
  XmlDeserializationError,
)
from python_tmx.base.types import Note, Prop, Ph
from python_tmx.xml import XML_NS
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import TuvDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestTuvDeserializer[T_XmlElement]:
  handler: TuvDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = TuvDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)

    self.handler._set_emit(lambda x: None)

  def make_valid_elem(self, *, full: bool = False, content: str = "Text") -> T_XmlElement:
    """
    Creates a <tuv> element.
    If full is True, all optional attributes are filled.
    If content is given, it is set as the tuv content (default: "Text").
    """
    tuv = self.backend.make_elem("tuv")
    self.backend.set_attr(tuv, f"{XML_NS}lang", "en-US")
    if full:
      self.backend.set_attr(tuv, "o-encoding", "UTF-8")
      self.backend.set_attr(tuv, "datatype", "plaintext")
      self.backend.set_attr(tuv, "usagecount", "1")
      self.backend.set_attr(tuv, "lastusagedate", "20250103T000000Z")
      self.backend.set_attr(tuv, "creationtool", "tool")
      self.backend.set_attr(tuv, "creationtoolversion", "1.0")
      self.backend.set_attr(tuv, "creationdate", "20250101T000000Z")
      self.backend.set_attr(tuv, "creationid", "User")
      self.backend.set_attr(tuv, "changedate", "20250102T000000Z")
      self.backend.set_attr(tuv, "changeid", "User2")
      self.backend.set_attr(tuv, "o_tmf", "tmx")
    seg = self.backend.make_elem("seg")
    self.backend.set_text(seg, content)
    self.backend.append(tuv, seg)
    return tuv

  def test_minimal_valid(self):
    """Verifies parsing of a standard TUV with text content."""
    elem = self.make_valid_elem(content="Hello World")
    tuv = self.handler._deserialize(elem)

    assert tuv.lang == "en-US"
    assert tuv.content == ["Hello World"]
    assert tuv.props == []
    assert tuv.notes == []

  def test_mixed_inline_content(self):
    """
    Verifies that the TUV handler correctly delegates the <seg> content
    to its internal Mixin logic.
    """
    tuv_elem = self.backend.make_elem("tuv")
    self.backend.set_attr(tuv_elem, f"{XML_NS}lang", "en")

    seg_elem = self.backend.make_elem("seg")
    self.backend.set_text(seg_elem, "Prefix ")

    ph_elem = self.backend.make_elem("ph")
    self.backend.set_tail(ph_elem, " Suffix")
    self.backend.append(seg_elem, ph_elem)

    self.backend.append(tuv_elem, seg_elem)

    content = []
    mock_ph = Ph(x=1, content=content)

    def mock_emit(obj):
      if self.backend.get_tag(obj) == "ph":
        return mock_ph
      return None

    self.handler._set_emit(mock_emit)

    tuv = self.handler._deserialize(tuv_elem)

    assert tuv.content == ["Prefix ", mock_ph, " Suffix"]

  def test_structural_children(self):
    """Verifies Prop and Note siblings are collected alongside the seg."""
    elem = self.make_valid_elem()

    self.backend.append(elem, self.backend.make_elem("prop"))
    self.backend.append(elem, self.backend.make_elem("note"))

    def mock_emit(obj):
      tag = self.backend.get_tag(obj)
      if tag == "prop":
        return Prop(text="p", type="t")
      if tag == "note":
        return Note(text="n")
      return None

    self.handler._set_emit(mock_emit)

    tuv = self.handler._deserialize(elem)

    assert len(tuv.props) == 1
    assert len(tuv.notes) == 1

  def test_missing_seg_raise(self):
    """Policy: No <seg> found -> Raise."""
    elem = self.backend.make_elem("tuv")
    self.backend.set_attr(elem, f"{XML_NS}lang", "en")

    with pytest.raises(XmlDeserializationError, match="Element <tuv> is missing a <seg> child element"):
      self.handler._deserialize(elem)

  def test_missing_seg_ignore(self):
    """Policy: No <seg> found -> Return empty list."""
    elem = self.backend.make_elem("tuv")
    self.backend.set_attr(elem, f"{XML_NS}lang", "en")

    self.policy.missing_seg.behavior = "ignore"

    tuv = self.handler._deserialize(elem)
    assert tuv.content == []

  def test_multiple_seg_raise(self):
    """Policy: Multiple <seg> elements -> Raise."""
    elem = self.backend.make_elem("tuv")
    self.backend.set_attr(elem, f"{XML_NS}lang", "en")

    seg1 = self.backend.make_elem("seg")
    self.backend.set_text(seg1, "First")
    self.backend.append(elem, seg1)

    seg2 = self.backend.make_elem("seg")
    self.backend.set_text(seg2, "Second")
    self.backend.append(elem, seg2)

    with pytest.raises(XmlDeserializationError, match="multiple <seg> elements in <tuv>"):
      self.handler._deserialize(elem)

  def test_multiple_seg_keep_first(self):
    """Policy: Multiple <seg> -> Keep First, ignore rest."""
    elem = self.backend.make_elem("tuv")
    self.backend.set_attr(elem, f"{XML_NS}lang", "en")

    seg1 = self.backend.make_elem("seg")
    self.backend.set_text(seg1, "First")
    self.backend.append(elem, seg1)

    seg2 = self.backend.make_elem("seg")
    self.backend.set_text(seg2, "Second")
    self.backend.append(elem, seg2)

    self.policy.multiple_seg.behavior = "keep_first"

    tuv = self.handler._deserialize(elem)
    assert tuv.content == ["First"]

  def test_multiple_seg_keep_last(self):
    """Policy: Multiple <seg> -> Keep First, ignore rest."""
    elem = self.backend.make_elem("tuv")
    self.backend.set_attr(elem, f"{XML_NS}lang", "en")

    seg1 = self.backend.make_elem("seg")
    self.backend.set_text(seg1, "First")
    self.backend.append(elem, seg1)

    seg2 = self.backend.make_elem("seg")
    self.backend.set_text(seg2, "Second")
    self.backend.append(elem, seg2)

    seg3 = self.backend.make_elem("seg")
    self.backend.set_text(seg3, "Third")
    self.backend.append(elem, seg3)

    self.policy.multiple_seg.behavior = "keep_last"

    tuv = self.handler._deserialize(elem)
    assert tuv.content == ["Third"]

  def test_extra_text_in_tuv(self):
    """
    <tuv>Garbage<seg>...</seg></tuv>
    Text inside TUV (but outside SEG) is invalid.
    """
    elem = self.make_valid_elem()
    self.backend.set_text(elem, "Garbage")

    self.policy.extra_text.behavior = "raise"

    with pytest.raises(XmlDeserializationError, match="extra text content"):
      self.handler._deserialize(elem)
