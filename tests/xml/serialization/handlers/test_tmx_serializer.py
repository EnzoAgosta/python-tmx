import logging

import pytest
from pytest_mock import MockerFixture
from python_tmx.base.errors import XmlSerializationError
from python_tmx.base.types import BaseElement, Header, Segtype, Tmx, Tu
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.policy import SerializationPolicy
from python_tmx.xml.serialization._handlers import TmxSerializer

singleton = object()


class TestTmxSerializer[T_XmlElement]:
  handler: TmxSerializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = SerializationPolicy()
    self.mocker = mocker
    self.handler = TmxSerializer(backend=self.backend, policy=self.policy, logger=self.logger)

    def test_emit(obj: BaseElement) -> T_XmlElement | None:
      if isinstance(obj, Header):
        return self.backend.make_elem("header")
      elif isinstance(obj, Tu):
        return self.backend.make_elem("tu")
      elif obj is singleton:
        return None
      raise TypeError(f"Invalid object type {type(obj)}")

    self.handler._set_emit(test_emit)

  def make_tu_object(self) -> Tmx:
    return Tmx(
      version="1.4",
      header=Header(
        creationtool="pytest",
        creationtoolversion="v1",
        segtype=Segtype.SENTENCE,
        o_tmf="TestTMF",
        adminlang="en-US",
        srclang="en-US",
        datatype="plaintext",
      ),
      body=[Tu(tuid="tu001")],
    )

  def test_calls_backend_make_elem(self):
    spy_make_elem = self.mocker.spy(self.backend, "make_elem")
    self.handler._set_emit(lambda x: None)
    tmx = self.make_tu_object()

    self.handler._serialize(tmx)

    assert spy_make_elem.call_count == 2
    spy_make_elem.assert_any_call("tmx")
    spy_make_elem.assert_any_call("body")

  def test_calls_set_attribute(self):
    spy_set_attribute = self.mocker.spy(self.handler, "_set_attribute")

    tmx = self.make_tu_object()

    elem = self.handler._serialize(tmx)

    assert elem is not None
    spy_set_attribute.assert_called_once_with(elem, tmx.version, "version", True)

  def test_returns_None_if_not_Tmx_if_policy_is_ignore(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'TmxSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_calls_emit(self):
    spy_emit = self.mocker.spy(self.handler, "emit")
    tmx = self.make_tu_object()

    elem = self.handler._serialize(tmx)

    assert elem is not None
    assert spy_emit.call_count == 2
    spy_emit.assert_any_call(tmx.header)
    spy_emit.assert_any_call(tmx.body[0])

  def test_calls_backend_to_append_children_elements(self):
    spy_append = self.mocker.spy(self.backend, "append")

    tmx = self.make_tu_object()

    elem = self.handler._serialize(tmx)

    assert elem is not None
    assert spy_append.call_count == 3
    for i in self.backend.iter_children(elem):
      if self.backend.get_tag(i) == "header":
        spy_append.assert_any_call(elem, i)
      elif self.backend.get_tag(i) == "body":
        spy_append.assert_any_call(elem, i)
        for j in self.backend.iter_children(i):
          spy_append.assert_any_call(i, j)
      else:
        raise ValueError(f"Invalid tag {self.backend.get_tag(i)}")

  def test_raises_if_invalid_header(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    tmx = self.make_tu_object()
    tmx.header = 1  # type: ignore[assignment]

    log_message = "Tmx.header is not a Header object. Expected Header, got 'int'"

    with pytest.raises(XmlSerializationError, match=log_message):
      self.handler._serialize(tmx)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_ignores_if_invalid_header(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    tmx = self.make_tu_object()
    tmx.header = singleton  # type: ignore[assignment]

    log_message = "Tmx.header is not a Header object. Expected Header, got 'object'"

    self.handler._serialize(tmx)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_raises_if_invalid_child_in_body(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    log_message = "Invalid child element 'int' in Tmx.body"
    tmx = self.make_tu_object()
    tmx.body = [1]  # type: ignore[list-item]

    with pytest.raises(XmlSerializationError, match=log_message):
      self.handler._serialize(tmx)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_ignores_if_invalid_child_in_body(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    tmx = self.make_tu_object()
    tmx.body = [singleton]  # type: ignore[list-item]

    self.handler._serialize(tmx)

    log_message = "Invalid child element 'object' in Tmx.body"

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]
