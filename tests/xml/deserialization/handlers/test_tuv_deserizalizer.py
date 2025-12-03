import logging

import pytest
from pytest_mock import MockerFixture
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
  def setup_method_fixture(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker
    self.handler = TuvDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_tuv_elem(self) -> T_XmlElement:
    elem = self.backend.make_elem("tuv")
    self.backend.set_attr(elem, f"{XML_NS}lang", "en")
    self.backend.set_attr(elem, "o-encoding", "base64")
    self.backend.set_attr(elem, "datatype", "text")
    self.backend.set_attr(elem, "usagecount", "1")
    self.backend.set_attr(elem, "lastusagedate", "20230101T000000Z")
    self.backend.set_attr(elem, "creationtool", "pytest")
    self.backend.set_attr(elem, "creationtoolversion", "0.0.1")
    self.backend.set_attr(elem, "creationdate", "20230101T000000Z")
    self.backend.set_attr(elem, "creationid", "pytest")
    self.backend.set_attr(elem, "changedate", "20230201T000000Z")
    self.backend.set_attr(elem, "changeid", "pytest")
    self.backend.set_attr(elem, "o-tmf", "tmx")
    self.backend.append(elem, self.backend.make_elem("prop"))
    self.backend.append(elem, self.backend.make_elem("note"))
    seg = self.backend.make_elem("seg")
    self.backend.set_text(seg, "foo")
    self.backend.append(elem, seg)
    return elem

  def test_returns_Tuv(self):
    elem = self.make_tuv_elem()
    tuv = self.handler._deserialize(elem)
    assert isinstance(tuv, Tuv)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    tuv = self.make_tuv_elem()

    self.handler._deserialize(tuv)

    spy_check_tag.assert_called_once_with(tuv, "tuv")

  def test_calls_parse_attribute_correctly(self):
    spy_parse_attributes = self.mocker.spy(self.handler, "_parse_attribute")
    tuv = self.make_tuv_elem()
    self.handler._deserialize(tuv)

    assert spy_parse_attributes.call_count == 8
    # required attribute
    spy_parse_attributes.assert_any_call(tuv, f"{XML_NS}lang", True)
    # optional attributes
    spy_parse_attributes.assert_any_call(tuv, "o-encoding", False)
    spy_parse_attributes.assert_any_call(tuv, "datatype", False)
    spy_parse_attributes.assert_any_call(tuv, "creationtool", False)
    spy_parse_attributes.assert_any_call(tuv, "creationtoolversion", False)
    spy_parse_attributes.assert_any_call(tuv, "creationid", False)
    spy_parse_attributes.assert_any_call(tuv, "changeid", False)
    spy_parse_attributes.assert_any_call(tuv, "o-tmf", False)

  def test_calls_parse_attribute_as_dt(self):
    spy_parse_attributes_as_dt = self.mocker.spy(self.handler, "_parse_attribute_as_dt")

    tuv = self.make_tuv_elem()
    self.handler._deserialize(tuv)

    assert spy_parse_attributes_as_dt.call_count == 3
    spy_parse_attributes_as_dt.assert_any_call(tuv, "creationdate", False)
    spy_parse_attributes_as_dt.assert_any_call(tuv, "lastusagedate", False)
    spy_parse_attributes_as_dt.assert_any_call(tuv, "changedate", False)

  def test_calls_parse_attribute_as_int(self):
    spy_parse_attributes_as_int = self.mocker.spy(self.handler, "_parse_attribute_as_int")

    elem = self.make_tuv_elem()
    self.handler._deserialize(elem)

    spy_parse_attributes_as_int.assert_called_once_with(elem, "usagecount", False)

  def test_calls_emit_on_props_notes_only(self):
    spy_emit = self.mocker.spy(self.handler, "emit")
    elem = self.make_tuv_elem()
    self.handler._deserialize(elem)

    assert spy_emit.call_count == 2
    for i in self.backend.iter_children(elem, ("prop", "note")):
      spy_emit.assert_any_call(i)

  def test_appends_if_emit_does_not_return_none(self):
    self.handler._set_emit(
      lambda x: Prop(text="foo", type="bar")
      if self.backend.get_tag(x) == "prop"
      else Note(text="baz")
      if self.backend.get_tag(x) == "note"
      else None
    )
    spy_emit = self.mocker.spy(self.handler, "emit")
    elem = self.make_tuv_elem()

    tuv = self.handler._deserialize(elem)

    assert tuv.props == [Prop(text="foo", type="bar")]
    assert tuv.notes == [Note(text="baz")]

    assert spy_emit.call_count == 2
    for i in self.backend.iter_children(elem, ("prop", "note")):
      spy_emit.assert_any_call(i)

  def test_does_not_append_if_emit_returns_none(self):
    elem = self.make_tuv_elem()
    tuv = self.handler._deserialize(elem)

    assert tuv.props == []
    assert tuv.notes == []

  def test_raise_if_invalid_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "raise"

    elem = self.make_tuv_elem()
    self.backend.append(elem, self.backend.make_elem("invalid"))

    with pytest.raises(XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Invalid child element <invalid> in <tuv>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_invalid_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "ignore"

    elem = self.make_tuv_elem()
    self.backend.append(elem, self.backend.make_elem("invalid"))

    self.handler._deserialize(elem)

    log_message = "Invalid child element <invalid> in <tuv>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_if_text_is_not_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.extra_text.log_level = log_level
    self.policy.extra_text.behavior = "raise"

    elem = self.make_tuv_elem()
    self.backend.set_text(elem, "foo")

    with pytest.raises(XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Element <tuv> has extra text content 'foo'"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_text_is_not_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.extra_text.log_level = log_level
    self.policy.extra_text.behavior = "ignore"

    elem = self.make_tuv_elem()
    self.backend.set_text(elem, "foo")

    self.handler._deserialize(elem)

    log_message = "Element <tuv> has extra text content 'foo'"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_raise_if_no_seg(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.missing_seg.log_level = log_level
    self.policy.missing_seg.behavior = "raise"

    elem = self.backend.make_elem("tuv")
    self.backend.set_attr(elem, f"{XML_NS}lang", "en")

    with pytest.raises(XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Element <tuv> is missing a <seg> child element"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_no_seg(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.missing_seg.log_level = log_level
    self.policy.missing_seg.behavior = "ignore"

    elem = self.backend.make_elem("tuv")
    self.backend.set_attr(elem, f"{XML_NS}lang", "en")

    tuv = self.handler._deserialize(elem)
    assert tuv.content == []

    log_message = "Element <tuv> is missing a <seg> child element"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_raise_if_multiple_seg(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.multiple_seg.log_level = log_level
    self.policy.multiple_seg.behavior = "raise"

    elem = self.make_tuv_elem()
    self.backend.append(elem, self.backend.make_elem("seg"))

    with pytest.raises(XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Multiple <seg> elements in <tuv>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_keep_first_seg(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.multiple_seg.log_level = log_level
    self.policy.multiple_seg.behavior = "keep_first"

    elem = self.make_tuv_elem()
    seg2 = self.backend.make_elem("seg")
    self.backend.set_text(seg2, "bar")
    self.backend.append(elem, seg2)

    tuv = self.handler._deserialize(elem)

    assert tuv.content == ["foo"]

    log_message = "Multiple <seg> elements in <tuv>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_keep_last_seg(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.multiple_seg.log_level = log_level
    self.policy.multiple_seg.behavior = "keep_last"

    elem = self.make_tuv_elem()
    seg2 = self.backend.make_elem("seg")
    self.backend.set_text(seg2, "bar")
    self.backend.append(elem, seg2)

    tuv = self.handler._deserialize(elem)

    assert tuv.content == ["bar"]

    log_message = "Multiple <seg> elements in <tuv>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]
