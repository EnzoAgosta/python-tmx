import logging

import pytest
from pytest_mock import MockerFixture
from python_tmx.base.errors import XmlDeserializationError
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
  def setup_method_fixture(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker
    self.handler = HeaderDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_header_elem(self) -> T_XmlElement:
    elem = self.backend.make_elem("header")
    self.backend.set_attr(elem, "creationtool", "pytest")
    self.backend.set_attr(elem, "creationtoolversion", "0.0.1")
    self.backend.set_attr(elem, "segtype", "block")
    self.backend.set_attr(elem, "o-tmf", "tmx")
    self.backend.set_attr(elem, "adminlang", "en")
    self.backend.set_attr(elem, "srclang", "en")
    self.backend.set_attr(elem, "datatype", "text")
    self.backend.set_attr(elem, "o-encoding", "base64")
    self.backend.set_attr(elem, "creationdate", "20230101T000000Z")
    self.backend.set_attr(elem, "creationid", "pytest")
    self.backend.set_attr(elem, "changedate", "20230201T000000Z")
    self.backend.set_attr(elem, "changeid", "pytest")
    self.backend.append(elem, self.backend.make_elem("prop"))
    self.backend.append(elem, self.backend.make_elem("note"))
    return elem

  def test_returns_Header(self):
    elem = self.make_header_elem()
    header = self.handler._deserialize(elem)
    assert isinstance(header, Header)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    header = self.make_header_elem()

    self.handler._deserialize(header)

    spy_check_tag.assert_called_once_with(header, "header")

  def test_calls_parse_attribute_correctly(self):
    spy_parse_attributes = self.mocker.spy(self.handler, "_parse_attribute")
    header = self.make_header_elem()
    self.handler._deserialize(header)

    assert spy_parse_attributes.call_count == 9
    # required attribute
    spy_parse_attributes.assert_any_call(header, "creationtool", True)
    spy_parse_attributes.assert_any_call(header, "creationtoolversion", True)
    spy_parse_attributes.assert_any_call(header, "o-tmf", True)
    spy_parse_attributes.assert_any_call(header, "adminlang", True)
    spy_parse_attributes.assert_any_call(header, "srclang", True)
    spy_parse_attributes.assert_any_call(header, "datatype", True)

    # optional attributes
    spy_parse_attributes.assert_any_call(header, "o-encoding", False)
    spy_parse_attributes.assert_any_call(header, "creationid", False)
    spy_parse_attributes.assert_any_call(header, "changeid", False)

  def test_calls_parse_attribute_as_dt(self):
    spy_parse_attributes_as_dt = self.mocker.spy(self.handler, "_parse_attribute_as_dt")

    header = self.make_header_elem()
    self.handler._deserialize(header)

    assert spy_parse_attributes_as_dt.call_count == 2
    spy_parse_attributes_as_dt.assert_any_call(header, "creationdate", False)
    spy_parse_attributes_as_dt.assert_any_call(header, "changedate", False)

  def test_calls_parse_attribute_as_enum(self):
    spy_parse_attributes_as_enum = self.mocker.spy(self.handler, "_parse_attribute_as_enum")

    header = self.make_header_elem()
    self.handler._deserialize(header)

    spy_parse_attributes_as_enum.assert_called_with(header, "segtype", Segtype, True)

  def test_calls_emit_on_props_and_notes(self):
    spy_emit = self.mocker.spy(self.handler, "emit")
    header = self.make_header_elem()
    self.handler._deserialize(header)

    assert spy_emit.call_count == 2
    for i in self.backend.iter_children(header):
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
    header = self.make_header_elem()

    elem = self.backend.make_elem("prop")

    header = self.handler._deserialize(header)

    assert header.props == [Prop(text="foo", type="bar")]
    assert header.notes == [Note(text="baz")]

    assert spy_emit.call_count == 2
    for i in self.backend.iter_children(elem):
      spy_emit.assert_any_call(i)

  def test_does_not_append_if_emit_returns_none(self):
    elem = self.make_header_elem()
    header = self.handler._deserialize(elem)

    assert header.props == []
    assert header.notes == []

  def test_raise_if_invalid_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "raise"

    elem = self.make_header_elem()
    self.backend.append(elem, self.backend.make_elem("invalid"))

    with pytest.raises(XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Invalid child element <invalid> in <header>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_invalid_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "ignore"

    elem = self.make_header_elem()
    self.backend.append(elem, self.backend.make_elem("invalid"))

    self.handler._deserialize(elem)

    log_message = "Invalid child element <invalid> in <header>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_if_text_is_not_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.extra_text.log_level = log_level
    self.policy.extra_text.behavior = "raise"

    elem = self.make_header_elem()
    self.backend.set_text(elem, "foo")

    with pytest.raises(XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Element <header> has extra text content 'foo'"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_text_is_not_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.extra_text.log_level = log_level
    self.policy.extra_text.behavior = "ignore"

    elem = self.make_header_elem()
    self.backend.set_text(elem, "foo")

    self.handler._deserialize(elem)

    log_message = "Element <header> has extra text content 'foo'"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]
