from datetime import UTC, datetime
import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.errors import XmlDeserializationError
from python_tmx.base.types import Note, Prop, Segtype, Tu, Tuv
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import TuDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestTuDeserializer[T_XmlElement]:
  handler: TuDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = TuDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_tu_elem(
    self,
    *,
    tag: str = "tu",
    tuid: str | None = "tu001",
    o_encoding: str | None = "UTF-8",
    datatype: str | None = "plaintext",
    usagecount: int | None = 1,
    lastusagedate: datetime | None = datetime(2025, 3, 1, 0, 0, 0, tzinfo=UTC),
    creationtool: str | None = "pytest",
    creationtoolversion: str | None = "v1",
    creationdate: datetime | None = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC),
    creationid: str | None = "User1",
    changedate: datetime | None = datetime(2025, 2, 1, 0, 0, 0, tzinfo=UTC),
    segtype: Segtype | None = Segtype.SENTENCE,
    changeid: str | None = "User2",
    o_tmf: str | None = "TestTMF",
    srclang: str | None = "en-US",
    props: int = 1,
    notes: int = 1,
    variants: int = 2,
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)

    if tuid is not None:
      self.backend.set_attr(elem, "tuid", tuid)
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
    if segtype is not None:
      self.backend.set_attr(elem, "segtype", segtype.value)
    if changeid is not None:
      self.backend.set_attr(elem, "changeid", changeid)
    if o_tmf is not None:
      self.backend.set_attr(elem, "o-tmf", o_tmf)
    if srclang is not None:
      self.backend.set_attr(elem, "srclang", srclang)

    for _ in range(props):
      self.backend.append(elem, self.backend.make_elem("prop"))
    for _ in range(notes):
      self.backend.append(elem, self.backend.make_elem("note"))
    for _ in range(variants):
      self.backend.append(elem, self.backend.make_elem("tuv"))

    return elem

  def test_returns_Tu(self):
    elem = self.make_tu_elem()
    tu = self.handler._deserialize(elem)
    assert isinstance(tu, Tu)

  def test_calls_check_tag(self):
    mock_check_tag = Mock()
    self.handler._check_tag = mock_check_tag
    elem = self.make_tu_elem()
    self.handler._deserialize(elem)

    mock_check_tag.assert_called_once_with(elem, "tu")

  def test_calls_parse_attribute_correctly(self):
    mock_parse_attributes = Mock()
    mock_parse_attributes_as_enum = Mock()
    mock_parse_attributes_as_dt = Mock()
    mock_parse_attributes_as_int = Mock()
    self.handler._parse_attribute = mock_parse_attributes
    self.handler._parse_attribute_as_enum = mock_parse_attributes_as_enum
    self.handler._parse_attribute_as_dt = mock_parse_attributes_as_dt
    self.handler._parse_attribute_as_int = mock_parse_attributes_as_int

    elem = self.make_tu_elem()
    self.handler._deserialize(elem)

    assert mock_parse_attributes.call_count == 9
    mock_parse_attributes.assert_any_call(elem, "tuid", False)
    mock_parse_attributes.assert_any_call(elem, "o-encoding", False)
    mock_parse_attributes.assert_any_call(elem, "datatype", False)
    mock_parse_attributes.assert_any_call(elem, "creationtool", False)
    mock_parse_attributes.assert_any_call(elem, "creationtoolversion", False)
    mock_parse_attributes.assert_any_call(elem, "creationid", False)
    mock_parse_attributes.assert_any_call(elem, "changeid", False)
    mock_parse_attributes.assert_any_call(elem, "o-tmf", False)
    mock_parse_attributes.assert_any_call(elem, "srclang", False)

    mock_parse_attributes_as_enum.assert_called_once_with(elem, "segtype", Segtype, False)

    assert mock_parse_attributes_as_dt.call_count == 3
    mock_parse_attributes_as_dt.assert_any_call(elem, "creationdate", False)
    mock_parse_attributes_as_dt.assert_any_call(elem, "changedate", False)
    mock_parse_attributes_as_dt.assert_any_call(elem, "lastusagedate", False)

    mock_parse_attributes_as_int.assert_called_once_with(elem, "usagecount", False)

  def test_calls_emit(self):
    mock_emit = Mock()
    self.handler._set_emit(mock_emit)

    elem = self.make_tu_elem()
    self.handler._deserialize(elem)

    assert mock_emit.call_count == 4
    for i in self.backend.iter_children(elem):
      mock_emit.assert_any_call(i)

  def test_only_appends_prop_notes_and_tuvs_if_correct_type(self):
    mock_prop = Prop(text="prop", type="x-test")
    mock_note = Note(text="note", lang="en-US")
    mock_tuv = Tuv(lang="en-US")

    def side_effect(element: T_XmlElement):
      tag = self.backend.get_tag(element)
      if tag == "prop":
        return mock_prop
      elif tag == "note":
        return mock_note
      elif tag == "tuv":
        return mock_tuv
      return None
    
    mock_emit = Mock(side_effect=side_effect)
    self.handler._set_emit(mock_emit)
    elem = self.make_tu_elem()

    tu = self.handler._deserialize(elem)

    assert tu.props == [mock_prop]
    assert tu.notes == [mock_note]
    assert tu.variants == [mock_tuv, mock_tuv]

    assert mock_emit.call_count == 4
    for i in self.backend.iter_children(elem):
      mock_emit.assert_any_call(i)

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tu_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Invalid child element <wrong> in <tu>"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Invalid child element <wrong> in <tu>")
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tu_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Invalid child element <wrong> in <tu>")
    assert caplog.record_tuples == [expected_log]

  def test_extra_text_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tu_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "raise"
    self.policy.extra_text.log_level = log_level

    with pytest.raises(
      XmlDeserializationError,
      match="Element <tu> has extra text content '  I should not be here  '",
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <tu> has extra text content '  I should not be here  '",
    )
    assert caplog.record_tuples == [expected_log]

  def test_extra_text_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tu_elem()
    self.backend.set_text(elem, "  I should not be here  ")

    self.policy.extra_text.behavior = "ignore"
    self.policy.extra_text.log_level = log_level

    self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <tu> has extra text content '  I should not be here  '",
    )
    assert caplog.record_tuples == [expected_log]
