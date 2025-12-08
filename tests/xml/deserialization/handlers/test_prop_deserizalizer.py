import logging

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestPropDeserializer[T]:
  handler: hm.PropDeserializer
  backend: hm.XMLBackend[T]
  logger: logging.Logger
  policy: hm.DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: hm.XMLBackend[T], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = hm.DeserializationPolicy()
    self.mocker = mocker
    self.handler = hm.PropDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_prop_elem(self) -> T:
    elem = self.backend.make_elem("prop")
    self.backend.set_text(elem, "Valid Prop Content")
    self.backend.set_attr(elem, "type", "prop_type")
    self.backend.set_attr(elem, f"{hm.XML_NS}lang", "en")
    self.backend.set_attr(elem, "o-encoding", "base64")
    return elem

  def test_returns_Prop(self):
    elem = self.make_prop_elem()
    prop = self.handler._deserialize(elem)
    assert isinstance(prop, hm.Prop)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    prop = self.make_prop_elem()

    self.handler._deserialize(prop)

    spy_check_tag.assert_called_once_with(prop, "prop")

  def test_calls_parse_attribute_correctly(self):
    spy_parse_attributes = self.mocker.spy(self.handler, "_parse_attribute")
    prop = self.make_prop_elem()
    self.handler._deserialize(prop)

    assert spy_parse_attributes.call_count == 3
    # required attribute
    spy_parse_attributes.assert_any_call(prop, "type", True)
    # optional attributes
    spy_parse_attributes.assert_any_call(prop, "o-encoding", False)
    spy_parse_attributes.assert_any_call(prop, f"{hm.XML_NS}lang", False)

  def test_calls_parse_backend_get_text(self):
    spy_get_text = self.mocker.spy(self.backend, "get_text")

    prop = self.make_prop_elem()
    self.handler._deserialize(prop)

    assert spy_get_text.call_count == 1
    spy_get_text.assert_called_with(prop)

  def test_raises_if_text_is_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.empty_content.log_level = log_level
    self.policy.empty_content.behavior = "raise"

    elem = self.make_prop_elem()
    self.backend.set_text(elem, None)

    with pytest.raises(hm.XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Element <prop> does not have any text content"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignores_if_text_is_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.empty_content.log_level = log_level
    self.policy.empty_content.behavior = "ignore"

    elem = self.make_prop_elem()
    self.backend.set_text(elem, None)

    self.handler._deserialize(elem)

    log_message = "Element <prop> does not have any text content"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_fallbacks_to_empty_string_if_text_is_none(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.empty_content.log_level = log_level
    self.policy.empty_content.behavior = "empty"

    elem = self.make_prop_elem()
    self.backend.set_text(elem, None)

    prop = self.handler._deserialize(elem)
    assert prop.text == ""

    empty_log_message = "Element <prop> does not have any text content"
    empty_fallback_log_message = "Falling back to an empty string"
    expected_empty_log = (self.logger.name, log_level, empty_log_message)
    expected_empty_fallback_log = (self.logger.name, log_level, empty_fallback_log_message)

    assert caplog.record_tuples == [expected_empty_log, expected_empty_fallback_log]

  def test_raise_if_any_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "raise"

    elem = self.make_prop_elem()
    self.backend.append(elem, self.backend.make_elem("sub"))

    with pytest.raises(hm.XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Invalid child element <sub> in <prop>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_any_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "ignore"

    elem = self.make_prop_elem()
    self.backend.append(elem, self.backend.make_elem("sub"))

    self.handler._deserialize(elem)

    log_message = "Invalid child element <sub> in <prop>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]
