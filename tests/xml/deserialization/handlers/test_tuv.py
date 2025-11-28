from datetime import UTC, datetime
import logging
from unittest.mock import Mock
import pytest

from python_tmx.base.errors import AttributeDeserializationError, XmlDeserializationError
from python_tmx.base.types import Bpt, Ept, Note, Tuv, Prop
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

  def make_tuv_elem(
    self,
    *,
    tag: str = "tuv",
    lang: str | None = "en-US",
    o_encoding: str | None = "UTF-8",
    datatype: str | None = "plaintext",
    usagecount: int | None = 1,
    lastusagedate: datetime | None = datetime(2023, 3, 1, 0, 0, 0, tzinfo=UTC),
    creationtool: str | None = "pytest",
    creationtoolversion: str | None = "v1",
    creationdate: datetime | None = datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC),
    creationid: str | None = "User1",
    changedate: datetime | None = datetime(2023, 2, 1, 0, 0, 0, tzinfo=UTC),
    changeid: str | None = "User2",
    o_tmf: str | None = "TestTMF",
    props: int = 0,
    notes: int = 0,
    seg_text: str | None = "Tuv Content",
  ) -> T_XmlElement:
    """
    Creates a <tuv> element

    extra kwargs:
    tag: The tag to use for the element (default: "tuv")
    lang: The lang attribute to use (default: "en-US")
    o_encoding: The o-encoding attribute to use (default: "UTF-8")
    datatype: The datatype attribute to use (default: "plaintext")
    usagecount: The usagecount attribute to use (default: 1)
    lastusagedate: The lastusagedate attribute to use (default: 2023-03-01T00:00:00Z)
    creationtool: The creationtool attribute to use (default: "pytest")
    creationtoolversion: The creationtoolversion attribute to use (default: "v1")
    creationdate: The creationdate attribute to use (default: 2023-01-01T00:00:00Z)
    creationid: The creationid attribute to use (default: "User1")
    changedate: The changedate attribute to use (default: 2023-02-01T00:00:00Z)
    changeid: The changeid attribute to use (default: "User2")
    o_tmf: The o-tmf attribute to use (default: "TestTMF")
    props: The number of props to add to the tuv (default: 0)
    notes: The number of notes to add to the tuv (default: 0)
    seg_text: The text content of the <seg> element (default: "Tuv Content")
    """
    elem = self.backend.make_elem(tag)
    if lang is not None:
      self.backend.set_attr(elem, f"{XML_NS}lang", lang)
    if o_encoding is not None:
      self.backend.set_attr(elem, "o-encoding", o_encoding)
    if datatype is not None:
      self.backend.set_attr(elem, "datatype", datatype)
    if usagecount is not None:
      self.backend.set_attr(elem, "usagecount", str(usagecount))
    if lastusagedate is not None:
      self.backend.set_attr(elem, "lastusagedate", lastusagedate.isoformat())
    if creationtool is not None:
      self.backend.set_attr(elem, "creationtool", creationtool)
    if creationtoolversion is not None:
      self.backend.set_attr(elem, "creationtoolversion", creationtoolversion)
    if creationdate is not None:
      self.backend.set_attr(elem, "creationdate", creationdate.isoformat())
    if creationid is not None:
      self.backend.set_attr(elem, "creationid", creationid)
    if changedate is not None:
      self.backend.set_attr(elem, "changedate", changedate.isoformat())
    if changeid is not None:
      self.backend.set_attr(elem, "changeid", changeid)
    if o_tmf is not None:
      self.backend.set_attr(elem, "o-tmf", o_tmf)
    if props is not None:
      for _ in range(props):
        self.backend.append(elem, self.backend.make_elem("prop"))
    if notes is not None:
      for _ in range(notes):
        self.backend.append(elem, self.backend.make_elem("note"))
    if seg_text is not None:
      seg_elem = self.backend.make_elem("seg")
      self.backend.set_text(seg_elem, seg_text)
      self.backend.append(elem, seg_elem)
    return elem

  def test_basic_seg_content(self, caplog: pytest.LogCaptureFixture):
    mock_prop_obj = Prop(text="P", type="T")
    mock_note_obj = Note(text="N")

    def side_effect(child_id):
      tag = self.backend.get_tag(child_id)
      if tag == "prop":
        return mock_prop_obj
      if tag == "note":
        return mock_note_obj
      if tag == "seg":
        return "Tuv Content"
      return None

    mock_emit = Mock(side_effect=side_effect)
    self.handler._set_emit(mock_emit)

    elem = self.make_tuv_elem(props=1, notes=1)
    tuv = self.handler._deserialize(elem)

    assert isinstance(tuv, Tuv)
    assert tuv.lang == "en-US"
    assert tuv.o_encoding == "UTF-8"
    assert tuv.datatype == "plaintext"
    assert tuv.usagecount == 1
    assert tuv.lastusagedate == datetime(2023, 3, 1, 0, 0, 0, tzinfo=UTC)
    assert tuv.creationtool == "pytest"
    assert tuv.creationtoolversion == "v1"
    assert tuv.creationdate == datetime(2023, 1, 1, 0, 0, 0, tzinfo=UTC)
    assert tuv.creationid == "User1"
    assert tuv.changedate == datetime(2023, 2, 1, 0, 0, 0, tzinfo=UTC)
    assert tuv.changeid == "User2"
    assert tuv.o_tmf == "TestTMF"
    assert tuv.props == [mock_prop_obj]
    assert tuv.notes == [mock_note_obj]
    assert tuv.content == ["Tuv Content"]

    assert mock_emit.call_count == 2
    for i in self.backend.iter_children(elem, ("note", "prop")):
      mock_emit.assert_any_call(i)
    assert caplog.records == []

  def test_mixed_seg_content(self, caplog: pytest.LogCaptureFixture):
    mock_bpt = Bpt(i=1, x=1, type="T", content=["Bpt Content"])
    mock_ept = Ept(i=2, content=["Ept Content"])

    def side_effect(child_id):
      tag = self.backend.get_tag(child_id)
      if tag == "bpt":
        return mock_bpt
      if tag == "ept":
        return mock_ept
      return None

    mock_emit = Mock(side_effect=side_effect)
    self.handler._set_emit(mock_emit)

    elem = self.make_tuv_elem(seg_text=None)

    seg = self.backend.make_elem("seg")
    self.backend.set_text(seg, "Seg Text ")
    bpt = self.backend.make_elem("bpt")
    self.backend.set_tail(bpt, "Bpt Tail ")
    self.backend.append(seg, bpt)
    ept = self.backend.make_elem("ept")
    self.backend.set_tail(ept, "Ept Tail ")
    self.backend.append(seg, ept)

    self.backend.append(elem, seg)

    tuv = self.handler._deserialize(elem)

    assert isinstance(tuv, Tuv)
    assert tuv.content == ["Seg Text ", mock_bpt, "Bpt Tail ", mock_ept, "Ept Tail "]

    assert mock_emit.call_count == 2
    for i in self.backend.iter_children(elem, ("bpt", "ept")):
      mock_emit.assert_any_call(i)
    assert caplog.records == []

  def test_missing_seg_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem(seg_text=None)
    self.policy.missing_seg.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.missing_seg.log_level = log_level
    with pytest.raises(XmlDeserializationError, match="Element <tuv> is missing a <seg> child element"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Element <tuv> is missing a <seg> child element")
    assert caplog.record_tuples == [expected_log]

  def test_missing_seg_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem(seg_text=None)
    self.policy.missing_seg.behavior = "ignore"
    self.policy.missing_seg.log_level = log_level

    tuv = self.handler._deserialize(elem)
    assert isinstance(tuv, Tuv)
    assert tuv.content == []
    expected_log = (self.logger.name, log_level, "Element <tuv> is missing a <seg> child element")
    assert caplog.record_tuples == [expected_log]

  def test_multiple_seg_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem(seg_text=None)
    seg1 = self.backend.make_elem("seg")
    seg2 = self.backend.make_elem("seg")
    self.backend.append(elem, seg1)
    self.backend.append(elem, seg2)

    self.policy.multiple_seg.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.multiple_seg.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Multiple <seg> elements in <tuv>"):
      self.handler._deserialize(elem)
    expected_log = (self.logger.name, log_level, "Multiple <seg> elements in <tuv>")
    assert caplog.record_tuples == [expected_log]

  def test_multiple_seg_keep_first(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem(seg_text=None)
    seg1 = self.backend.make_elem("seg")
    self.backend.set_text(seg1, "First")
    seg2 = self.backend.make_elem("seg")
    self.backend.set_text(seg2, "Second")
    self.backend.append(elem, seg1)
    self.backend.append(elem, seg2)

    self.policy.multiple_seg.behavior = "keep_first"
    self.policy.multiple_seg.log_level = log_level
    tuv = self.handler._deserialize(elem)

    assert isinstance(tuv, Tuv)
    assert tuv.content == ["First"]
    expected_log = (self.logger.name, log_level, "Multiple <seg> elements in <tuv>")
    assert caplog.record_tuples == [expected_log]

  def test_multiple_seg_keep_last(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem(seg_text=None)
    seg1 = self.backend.make_elem("seg")
    self.backend.set_text(seg1, "First")
    seg2 = self.backend.make_elem("seg")
    self.backend.set_text(seg2, "Second")
    self.backend.append(elem, seg1)
    self.backend.append(elem, seg2)

    self.policy.multiple_seg.behavior = "keep_last"
    self.policy.multiple_seg.log_level = log_level
    tuv = self.handler._deserialize(elem)

    assert isinstance(tuv, Tuv)
    assert tuv.content == ["Second"]
    expected_log = (self.logger.name, log_level, "Multiple <seg> elements in <tuv>")
    assert caplog.record_tuples == [expected_log]

  def test_empty_seg_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem(seg_text=None)
    seg = self.backend.make_elem("seg")
    self.backend.append(elem, seg)
    self.policy.empty_seg.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.empty_seg.log_level = log_level
    with pytest.raises(XmlDeserializationError, match="Element <tuv> has an empty <seg> child element"):
      self.handler._deserialize(elem)
    expected_log = (self.logger.name, log_level, "Element <tuv> has an empty <seg> child element")
    assert caplog.record_tuples == [expected_log]

  def test_empty_seg_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem(seg_text=None)
    seg = self.backend.make_elem("seg")
    self.backend.append(elem, seg)
    self.policy.empty_seg.behavior = "ignore"
    self.policy.empty_seg.log_level = log_level
    tuv = self.handler._deserialize(elem)
    assert isinstance(tuv, Tuv)
    assert tuv.content == []
    expected_log = (self.logger.name, log_level, "Element <tuv> has an empty <seg> child element")
    assert caplog.record_tuples == [expected_log]

  def test_missing_required_attribute_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem(lang=None)
    self.policy.required_attribute_missing.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.required_attribute_missing.log_level = log_level
    with pytest.raises(AttributeDeserializationError, match=f"Missing required attribute '{XML_NS}lang'"):
      self.handler._deserialize(elem)
    expected_log = (self.logger.name, log_level, f"Missing required attribute '{XML_NS}lang' on element <tuv>")
    assert caplog.record_tuples == [expected_log]

  def test_missing_required_attribute_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem(lang=None)
    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level
    tuv = self.handler._deserialize(elem)
    assert isinstance(tuv, Tuv)
    assert tuv.lang is None
    expected_log = (self.logger.name, log_level, f"Missing required attribute '{XML_NS}lang' on element <tuv>")
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))
    self.policy.invalid_child_element.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.invalid_child_element.log_level = log_level
    with pytest.raises(XmlDeserializationError, match="Invalid child element <wrong> in <tuv>"):
      self.handler._deserialize(elem)
    expected_log = (self.logger.name, log_level, "Invalid child element <wrong> in <tuv>")
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))
    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level
    tuv = self.handler._deserialize(elem)
    assert isinstance(tuv, Tuv)
    assert tuv.content == ["Tuv Content"]
    expected_log = (self.logger.name, log_level, "Invalid child element <wrong> in <tuv>")
    assert caplog.record_tuples == [expected_log]
