from typing import Literal
import pytest
from pytest_mock import MockerFixture
from hypomnema.xml.policy import DeserializationPolicy, PolicyValue
import logging
from hypomnema.xml.deserialization.base import (
  BaseElementDeserializer,
  InlineContentDeserializerMixin,
)
from datetime import datetime, UTC
import hypomnema as hm


class FakeDeserializer(
  BaseElementDeserializer[str, hm.BaseElement], InlineContentDeserializerMixin[str]
):
  def _deserialize(self, element: str) -> hm.BaseElement | None:
    raise NotImplementedError


class TestBaseElementDeserializer:
  backend: hm.XmlBackend[str]
  logger: logging.Logger
  policy: DeserializationPolicy
  mocker: MockerFixture

  @pytest.fixture(autouse=True)
  def _setup(
    self, backend: hm.XmlBackend[str], test_logger: logging.Logger, mocker: MockerFixture
  ) -> None:
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker

  def test_emit_not_set_raises(self) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    with pytest.raises(AssertionError, match=r"emit\(\) called before set_emit"):
      des.emit("dummy")

  def test_emit_dispatches(self) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    fake_emit = self.mocker.Mock(return_value=hm.Note(text="ok"))
    des._set_emit(fake_emit)
    out = des.emit("dummy")
    assert out is fake_emit.return_value
    fake_emit.assert_called_once_with("dummy")

  @pytest.mark.parametrize(
    "behaviour", ["raise", "ignore"], ids=["behaviour=raise", "behaviour=ignore"]
  )
  def test_handle_missing_attribute_policy(
    self, behaviour: Literal["raise", "ignore"], log_level: int, caplog: pytest.LogCaptureFixture
  ) -> None:
    self.policy.required_attribute_missing = PolicyValue(behaviour, log_level)
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    msg = "Required attribute 'attr' is None"

    if behaviour == "raise":
      with pytest.raises(hm.AttributeDeserializationError, match=msg):
        des._handle_missing_attribute(elem, "attr", required=True)
    else:
      des._handle_missing_attribute(elem, "attr", required=True)

    assert caplog.record_tuples == [(self.logger.name, log_level, msg)]

  def test_handle_missing_attribute_not_required(self, caplog: pytest.LogCaptureFixture) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    des._handle_missing_attribute(elem, "attr", required=False)
    assert not caplog.record_tuples

  @pytest.mark.parametrize(
    "behaviour", ["raise", "ignore"], ids=["behaviour=raise", "behaviour=ignore"]
  )
  def test_parse_attribute_as_datetime_policy(
    self, behaviour: Literal["raise", "ignore"], log_level: int, caplog: pytest.LogCaptureFixture
  ) -> None:
    self.policy.invalid_attribute_value = PolicyValue(behaviour, log_level)
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    self.backend.set_attr(elem, "ts", "bad-iso")

    msg = "Cannot convert 'bad-iso' to a datetime object for attribute ts"
    if behaviour == "raise":
      with pytest.raises(hm.AttributeDeserializationError, match=msg):
        des._parse_attribute_as_datetime(elem, "ts", required=False)
    else:
      out = des._parse_attribute_as_datetime(elem, "ts", required=False)
      assert out is None

    assert caplog.record_tuples == [(self.logger.name, log_level, msg)]

  def test_parse_attribute_as_datetime_ok(self) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    now = datetime.now(UTC).replace(microsecond=0)
    self.backend.set_attr(elem, "ts", now.isoformat())

    out = des._parse_attribute_as_datetime(elem, "ts", required=False)
    assert out == now

  def test_parse_attribute_as_datetime_missing_calls_handle_missing(self) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    des._handle_missing_attribute = self.mocker.Mock()
    out = des._parse_attribute_as_datetime(elem, "ts", required=False)
    assert out is None
    des._handle_missing_attribute.assert_called_once_with(elem, "ts", False)

  @pytest.mark.parametrize(
    "behaviour", ["raise", "ignore"], ids=["behaviour=raise", "behaviour=ignore"]
  )
  def test_parse_attribute_as_int_policy(
    self, behaviour: Literal["raise", "ignore"], log_level: int, caplog: pytest.LogCaptureFixture
  ) -> None:
    self.policy.invalid_attribute_value = PolicyValue(behaviour, log_level)
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    self.backend.set_attr(elem, "count", "abc")

    msg = "Cannot convert 'abc' to an int for attribute count"
    if behaviour == "raise":
      with pytest.raises(hm.AttributeDeserializationError, match=msg):
        des._parse_attribute_as_int(elem, "count", required=False)
    else:
      out = des._parse_attribute_as_int(elem, "count", required=False)
      assert out is None

    assert caplog.record_tuples == [(self.logger.name, log_level, msg)]

  def test_parse_attribute_as_int_ok(self) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    self.backend.set_attr(elem, "count", "42")

    out = des._parse_attribute_as_int(elem, "count", required=False)
    assert out == 42

  def test_parse_attribute_as_int_missing_calls_handle_missing(self) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    des._handle_missing_attribute = self.mocker.Mock()
    out = des._parse_attribute_as_int(elem, "count", required=False)
    assert out is None
    des._handle_missing_attribute.assert_called_once_with(elem, "count", False)

  @pytest.mark.parametrize(
    "behaviour", ["raise", "ignore"], ids=["behaviour=raise", "behaviour=ignore"]
  )
  def test_parse_attribute_as_enum_policy(
    self, behaviour: Literal["raise", "ignore"], log_level: int, caplog: pytest.LogCaptureFixture
  ) -> None:
    self.policy.invalid_attribute_value = PolicyValue(behaviour, log_level)
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    self.backend.set_attr(elem, "kind", "baz")

    msg = "Value 'baz' is not a valid enum value for attribute kind"
    if behaviour == "raise":
      with pytest.raises(hm.AttributeDeserializationError, match=msg):
        des._parse_attribute_as_enum(elem, "kind", hm.Pos, required=False)
    else:
      out = des._parse_attribute_as_enum(elem, "kind", hm.Pos, required=False)
      assert out is None

    assert caplog.record_tuples == [(self.logger.name, log_level, msg)]

  def test_parse_attribute_as_enum_ok(self) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    self.backend.set_attr(elem, "kind", "begin")

    out = des._parse_attribute_as_enum(elem, "kind", hm.Pos, required=False)
    assert out is hm.Pos.BEGIN

  def test_parse_attribute_as_enum_missing_calls_handle_missing(self) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    des._handle_missing_attribute = self.mocker.Mock()
    out = des._parse_attribute_as_enum(elem, "kind", hm.Pos, required=False)
    assert out is None
    des._handle_missing_attribute.assert_called_once_with(elem, "kind", False)

  def test_parse_attribute_as_str_missing_calls_handle_missing(self) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    des._handle_missing_attribute = self.mocker.Mock()
    out = des._parse_attribute_as_str(elem, "text", required=False)
    assert out is None
    des._handle_missing_attribute.assert_called_once_with(elem, "text", False)

  def test_parse_attribute_as_str_ok(self) -> None:
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    elem = self.backend.make_elem("tu")
    self.backend.set_attr(elem, "text", "hello")

    out = des._parse_attribute_as_str(elem, "text", required=False)
    assert out == "hello"


class TestInlineContentDeserializerMixin:
  backend: hm.XmlBackend[str]
  logger: logging.Logger
  policy: DeserializationPolicy
  mocker: MockerFixture

  @pytest.fixture(autouse=True)
  def _setup(
    self, backend: hm.XmlBackend[str], test_logger: logging.Logger, mocker: MockerFixture
  ) -> None:
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker

  def test_deserialize_content_text_only(self) -> None:
    parent = self.backend.make_elem("source")
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    self.backend.set_text(parent, "text")
    out = des._deserialize_content(parent, allowed=())
    assert out == ["text"]

  def test_deserialize_content_with_children(self) -> None:
    parent = self.backend.make_elem("source")
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    des.emit = self.mocker.Mock(return_value=hm.Bpt(i=1))
    self.backend.set_text(parent, "pre")
    child = self.backend.make_elem("bpt")
    self.backend.append(parent, child)
    self.backend.set_tail(child, "post")

    out = des._deserialize_content(parent, allowed=("bpt",))

    assert out == ["pre", des.emit.return_value, "post"]

  @pytest.mark.parametrize(
    "behaviour", ["raise", "ignore"], ids=["behaviour=raise", "behaviour=ignore"]
  )
  def test_deserialize_content_invalid_child_policy(
    self, behaviour: Literal["raise", "ignore"], log_level: int, caplog: pytest.LogCaptureFixture
  ) -> None:
    self.policy.invalid_child_element = PolicyValue(behaviour, log_level)
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    parent = self.backend.make_elem("source")
    bad = self.backend.make_elem("bad")
    self.backend.append(parent, bad)

    msg = "Incorrect child element in source: expected one of bpt, got bad"
    with pytest.raises(hm.XmlDeserializationError):
      out = des._deserialize_content(parent, allowed=("bpt",))
      assert out == []  # only runs if the exception is not raised, ie. if policy is "ignore"

    assert (self.logger.name, log_level, msg) in caplog.record_tuples

  @pytest.mark.parametrize(
    "behaviour",
    ["raise", "ignore", "empty"],
    ids=["behaviour=raise", "behaviour=ignore", "behaviour=empty"],
  )
  def test_deserialize_content_empty_policy(
    self,
    behaviour: Literal["raise", "ignore", "empty"],
    log_level: int,
    caplog: pytest.LogCaptureFixture,
  ) -> None:
    self.policy.empty_content = PolicyValue(behaviour, log_level)
    des = FakeDeserializer(self.backend, self.policy, self.logger)
    parent = self.backend.make_elem("source")

    msg = "Element <source> is empty"
    if behaviour == "raise":
      with pytest.raises(hm.XmlDeserializationError, match=msg):
        des._deserialize_content(parent, allowed=())
    elif behaviour == "empty":
      out = des._deserialize_content(parent, allowed=())
      assert out == [""]
    else:
      out = des._deserialize_content(parent, allowed=())
      assert out == []

    assert (self.logger.name, log_level, msg) in caplog.record_tuples
