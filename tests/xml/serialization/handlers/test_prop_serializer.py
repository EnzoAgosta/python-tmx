import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.errors import XmlSerializationError
from python_tmx.base.types import Prop
from python_tmx.xml import XML_NS
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.policy import SerializationPolicy
from python_tmx.xml.serialization._handlers import PropSerializer


class TestPropSerializer[T_XmlElement]:
  handler: PropSerializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = SerializationPolicy()

    self.handler = PropSerializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_prop_object(
    self,
    *,
    text: str | None = "Valid Prop Content",
    o_encoding: str | None = "UTF-8",
    lang: str | None = "en-US",
    _type: str | None = "x-test",
  ) -> Prop:
    return Prop(text=text, lang=lang, o_encoding=o_encoding, type=_type)  # type: ignore[arg-type]

  def test_calls_backend_make_elem(self):
    original = self.backend.make_elem
    mock_make_elem = Mock(side_effect=lambda x: original(x))
    self.backend.make_elem = mock_make_elem

    prop = self.make_prop_object()
    self.handler._serialize(prop)

    mock_make_elem.assert_called_once_with("prop")

  def test_calls_backend_set_text(self):
    original = self.backend.set_text
    mock_set_text = Mock(side_effect=lambda element, text: original(element, text))
    self.backend.set_text = mock_set_text

    prop = self.make_prop_object()
    elem = self.handler._serialize(prop)

    mock_set_text.assert_called_once_with(elem, prop.text)

  def test_calls_set_attribute(self):
    mock_set_attribute = Mock()
    self.handler._set_attribute = mock_set_attribute

    prop = self.make_prop_object()
    elem = self.handler._serialize(prop)

    assert mock_set_attribute.call_count == 3
    mock_set_attribute.assert_any_call(elem, prop.type, "type", True)
    mock_set_attribute.assert_any_call(elem, prop.lang, f"{XML_NS}lang", False)
    mock_set_attribute.assert_any_call(elem, prop.o_encoding, "o-encoding", False)


  def test_raises_if_invalid_object_type(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_object_type.behavior = "raise"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'PropSerializer'"

    with pytest.raises(XmlSerializationError, match=log_message):
      self.handler._serialize(1)  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_ignores_if_invalid_object_type(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'PropSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]