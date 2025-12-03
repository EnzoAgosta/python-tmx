import logging

import pytest
from pytest_mock import MockerFixture
from python_tmx.base.errors import XmlDeserializationError
from python_tmx.base.types import Tu, Note, Prop, Tuv
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import TuDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestTuDeserializer[T_XmlElement]:
  handler: TuDeserializer
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
    self.handler = TuDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_tu_elem(self) -> T_XmlElement:
    elem = self.backend.make_elem("tu")
    self.backend.set_attr(elem, "tuid", "1")
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
    self.backend.set_attr(elem, "srclang", "en")
    self.backend.append(elem, self.backend.make_elem("prop"))
    self.backend.append(elem, self.backend.make_elem("note"))
    self.backend.append(elem, self.backend.make_elem("tuv"))
    return elem

  def test_returns_Tu(self):
    elem = self.make_tu_elem()
    tu = self.handler._deserialize(elem)
    assert isinstance(tu, Tu)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    tu = self.make_tu_elem()

    self.handler._deserialize(tu)

    spy_check_tag.assert_called_once_with(tu, "tu")

  def test_calls_parse_attribute_correctly(self):
    spy_parse_attributes = self.mocker.spy(self.handler, "_parse_attribute")
    tu = self.make_tu_elem()
    self.handler._deserialize(tu)

    assert spy_parse_attributes.call_count == 9
    # optional attributes
    spy_parse_attributes.assert_any_call(tu, "tuid", False)
    spy_parse_attributes.assert_any_call(tu, "o-encoding", False)
    spy_parse_attributes.assert_any_call(tu, "datatype", False)
    spy_parse_attributes.assert_any_call(tu, "creationtool", False)
    spy_parse_attributes.assert_any_call(tu, "creationtoolversion", False)
    spy_parse_attributes.assert_any_call(tu, "creationid", False)
    spy_parse_attributes.assert_any_call(tu, "changeid", False)
    spy_parse_attributes.assert_any_call(tu, "o-tmf", False)
    spy_parse_attributes.assert_any_call(tu, "srclang", False)

  def test_calls_parse_attribute_as_dt(self):
    spy_parse_attributes_as_dt = self.mocker.spy(self.handler, "_parse_attribute_as_dt")

    tu = self.make_tu_elem()
    self.handler._deserialize(tu)

    assert spy_parse_attributes_as_dt.call_count == 3
    spy_parse_attributes_as_dt.assert_any_call(tu, "creationdate", False)
    spy_parse_attributes_as_dt.assert_any_call(tu, "lastusagedate", False)
    spy_parse_attributes_as_dt.assert_any_call(tu, "changedate", False)

  def test_calls_parse_attribute_as_int(self):
    spy_parse_attributes_as_int = self.mocker.spy(self.handler, "_parse_attribute_as_int")

    elem = self.make_tu_elem()
    self.handler._deserialize(elem)

    spy_parse_attributes_as_int.assert_called_once_with(elem, "usagecount", False)

  def test_calls_emit_on_props_notes_tuv(self):
    spy_emit = self.mocker.spy(self.handler, "emit")
    tu = self.make_tu_elem()
    self.handler._deserialize(tu)

    assert spy_emit.call_count == 3
    for i in self.backend.iter_children(tu):
      spy_emit.assert_any_call(i)

  def test_appends_if_emit_does_not_return_none(self):
    self.handler._set_emit(
      lambda x: Prop(text="foo", type="bar")
      if self.backend.get_tag(x) == "prop"
      else Note(text="baz")
      if self.backend.get_tag(x) == "note"
      else Tuv(lang="en")
      if self.backend.get_tag(x) == "tuv"
      else None
    )
    spy_emit = self.mocker.spy(self.handler, "emit")
    elem = self.make_tu_elem()

    tu = self.handler._deserialize(elem)

    assert tu.props == [Prop(text="foo", type="bar")]
    assert tu.notes == [Note(text="baz")]
    assert tu.variants == [Tuv(lang="en")]

    assert spy_emit.call_count == 3
    for i in self.backend.iter_children(elem):
      spy_emit.assert_any_call(i)

  def test_does_not_append_if_emit_returns_none(self):
    elem = self.make_tu_elem()
    tu = self.handler._deserialize(elem)

    assert tu.props == []
    assert tu.notes == []
    assert tu.variants == []

  def test_raise_if_invalid_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "raise"

    elem = self.make_tu_elem()
    self.backend.append(elem, self.backend.make_elem("invalid"))

    with pytest.raises(XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Invalid child element <invalid> in <tu>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_invalid_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "ignore"

    elem = self.make_tu_elem()
    self.backend.append(elem, self.backend.make_elem("invalid"))

    self.handler._deserialize(elem)

    log_message = "Invalid child element <invalid> in <tu>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_if_text_is_not_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.extra_text.log_level = log_level
    self.policy.extra_text.behavior = "raise"

    elem = self.make_tu_elem()
    self.backend.set_text(elem, "foo")

    with pytest.raises(XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Element <tu> has extra text content 'foo'"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_text_is_not_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.extra_text.log_level = log_level
    self.policy.extra_text.behavior = "ignore"

    elem = self.make_tu_elem()
    self.backend.set_text(elem, "foo")

    self.handler._deserialize(elem)

    log_message = "Element <tu> has extra text content 'foo'"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]
