from datetime import UTC, datetime
import logging
from unittest.mock import Mock
import pytest

from python_tmx.base.errors import XmlDeserializationError
from python_tmx.base.types import Note, Prop, Tuv
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
    props: int = 1,
    notes: int = 1,
    seg_text: str | None = "Tuv Content",
  ) -> T_XmlElement:
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

  def test_returns_Tuv(self):
    elem = self.make_tuv_elem()
    tuv = self.handler._deserialize(elem)
    assert isinstance(tuv, Tuv)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_tuv_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "tuv")

  def test_calls_parse_attribute_correctly(self):
    mock_parse_attributes = Mock()
    mock_parse_attributes_as_int = Mock()
    mock_parse_attributes_as_dt = Mock()
    self.handler._parse_attribute = mock_parse_attributes
    self.handler._parse_attribute_as_int = mock_parse_attributes_as_int
    self.handler._parse_attribute_as_dt = mock_parse_attributes_as_dt

    elem = self.make_tuv_elem()
    self.handler._deserialize(elem)

    assert mock_parse_attributes.call_count == 8
    mock_parse_attributes.assert_any_call(elem, f"{XML_NS}lang", True)
    mock_parse_attributes.assert_any_call(elem, "o-encoding", False)
    mock_parse_attributes.assert_any_call(elem, "datatype", False)
    mock_parse_attributes.assert_any_call(elem, "creationtool", False)
    mock_parse_attributes.assert_any_call(elem, "creationtoolversion", False)
    mock_parse_attributes.assert_any_call(elem, "creationid", False)
    mock_parse_attributes.assert_any_call(elem, "changeid", False)
    mock_parse_attributes.assert_any_call(elem, "o-tmf", False)

    mock_parse_attributes_as_int.assert_called_once_with(elem, "usagecount", False)

    assert mock_parse_attributes_as_dt.call_count == 3
    mock_parse_attributes_as_dt.assert_any_call(elem, "creationdate", False)
    mock_parse_attributes_as_dt.assert_any_call(elem, "changedate", False)
    mock_parse_attributes_as_dt.assert_any_call(elem, "lastusagedate", False)

  def test_calls_emit(self):
    mock_emit = Mock()
    self.handler._set_emit(mock_emit)
    elem = self.make_tuv_elem()
    self.handler._deserialize(elem)

    assert mock_emit.call_count == 2
    for i in self.backend.iter_children(elem, ("note", "prop")):
      mock_emit.assert_any_call(i)

  def test_only_appends_prop_and_notes_if_correct_type(self):
    mock_prop = Prop(text="prop", type="x-test")
    mock_note = Note(text="note")

    def side_effect(element: T_XmlElement):
      tag = self.backend.get_tag(element)
      if tag == "prop":
        return mock_prop
      elif tag == "note":
        return mock_note
      return None

    mock_emit = Mock(side_effect=side_effect)
    self.handler._set_emit(mock_emit)
    elem = self.make_tuv_elem()

    tuv = self.handler._deserialize(elem)

    assert tuv.props == [mock_prop]
    assert tuv.notes == [mock_note]
    
    assert mock_emit.call_count == 2
    for i in self.backend.iter_children(elem, ("note", "prop")):
      mock_emit.assert_any_call(i)

  def test_calls_deserialize_content(self):
    mock_deserialize_content = Mock()
    self.handler.deserialize_content = mock_deserialize_content

    elem = self.make_tuv_elem(seg_text=None)
    seg = self.backend.make_elem("seg")
    self.backend.set_text(seg, "Seg Text")
    self.backend.append(elem, seg)

    self.handler._deserialize(elem)

    mock_deserialize_content.assert_called_once_with(seg, ("bpt", "ept", "ph", "it", "hi"))

  def test_extra_text_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "raise"
    self.policy.extra_text.log_level = log_level

    with pytest.raises(
      XmlDeserializationError,
      match="Element <tuv> has extra text content '  I should not be here  '",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <tuv> has extra text content '  I should not be here  '",
    )
    assert caplog.record_tuples == [expected_log]

  def test_extra_text_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "ignore"
    self.policy.extra_text.log_level = log_level

    self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <tuv> has extra text content '  I should not be here  '",
    )
    assert caplog.record_tuples == [expected_log]

  def test_missing_seg_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem(seg_text=None)

    self.policy.missing_seg.behavior = "raise"
    self.policy.missing_seg.log_level = log_level

    with pytest.raises(
      XmlDeserializationError, match="Element <tuv> is missing a <seg> child element"
    ):
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
    self.backend.set_text(seg1, "First")
    seg2 = self.backend.make_elem("seg")
    self.backend.set_text(seg2, "Second")
    self.backend.append(elem, seg1)
    self.backend.append(elem, seg2)

    self.policy.multiple_seg.behavior = "raise"
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

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tuv_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "raise"
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
