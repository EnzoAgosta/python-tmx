from typing import Literal
from pytest_mock import MockerFixture
from hypomnema.xml.policy import SerializationPolicy, PolicyValue
import logging
import pytest
from hypomnema.xml.serialization.base import (
  BaseElementSerializer,
  InlineContentSerializerMixin,
  ChildrenSerializerMixin,
)
import hypomnema as hm
from datetime import datetime, UTC


class FakeBaseElementSerializer(
  BaseElementSerializer, InlineContentSerializerMixin, ChildrenSerializerMixin
):
  """
  "Concrete" implementation of BaseElementSerializer for testing purposes.
  Does not implement any serialization logic.
  """

  def _serialize(self, obj):
    raise NotImplementedError


class TestBaseElementSerializer:
  @pytest.fixture(autouse=True)
  def setup(self, backend: hm.XmlBackend, test_logger: logging.Logger, mocker: MockerFixture):
    policy = SerializationPolicy()
    self.serializer = FakeBaseElementSerializer(backend=backend, logger=test_logger, policy=policy)
    self.mocker = mocker

  def test_init(self):
    assert self.serializer.backend is not None
    assert self.serializer.logger is not None
    assert self.serializer.policy is not None
    assert self.serializer._emit is None

  def test_set_emit(self):
    def fake_emit(x):
      raise NotImplementedError

    self.serializer._set_emit(fake_emit)

    assert self.serializer._emit is fake_emit

  def test_emit_raises_if_not_set(self):
    with pytest.raises(AssertionError, match=r"emit\(\) called before set_emit\(\) was called"):
      self.serializer.emit(None)  # type: ignore

  def test_emit_returns_emit_return_value(self):
    def fake_emit(x):
      return x + 1

    self.serializer._set_emit(fake_emit)

    assert self.serializer.emit(1) == 2  # type: ignore

  def test_handle_missing_attribute_raises(self, caplog: pytest.LogCaptureFixture, log_level: int):
    element = self.serializer.backend.make_elem("elem")
    log_message = "Required attribute 'attr' is missing on element <elem>"
    self.serializer.policy.required_attribute_missing.log_level = log_level

    with pytest.raises(hm.AttributeSerializationError, match=log_message):
      self.serializer._handle_missing_attribute(element, "attr", True)
    assert caplog.record_tuples == [(self.serializer.logger.name, log_level, log_message)]

  def test_handle_missing_attribute_ignores(self, caplog: pytest.LogCaptureFixture, log_level: int):
    element = self.serializer.backend.make_elem("elem")
    self.serializer.policy.required_attribute_missing.behavior = "ignore"
    log_message = "Required attribute 'attr' is missing on element <elem>"
    self.serializer.policy.required_attribute_missing.log_level = log_level
    self.serializer._handle_missing_attribute(element, "attr", True)

    assert caplog.record_tuples == [(self.serializer.logger.name, log_level, log_message)]

  def test_set_datetime_attribute_formats_as_iso8601(self):
    element = self.serializer.backend.make_elem("elem")
    self.serializer._set_datetime_attribute(
      element, datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC), "attr", True
    )

    assert self.serializer.backend.get_attr(element, "attr") == "2025-01-01T12:00:00+00:00"

  def test_set_datetime_attribute_uses_backend(self):
    element = self.serializer.backend.make_elem("elem")
    backend_set_attr_mock = self.mocker.Mock()
    self.serializer.backend.set_attr = backend_set_attr_mock
    self.serializer._set_datetime_attribute(
      element, datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC), "attr", True
    )

    backend_set_attr_mock.assert_called_once_with(element, "attr", "2025-01-01T12:00:00+00:00")

  def test_set_datetime_attribute_calls_required_attribute_missing(self):
    element = self.serializer.backend.make_elem("elem")
    required_mock = self.mocker.Mock()
    self.serializer._handle_missing_attribute = required_mock
    self.serializer._set_datetime_attribute(element, None, "attr", True)

    assert required_mock.call_count == 1
    required_mock.assert_called_once_with(element, "attr", True)

  @pytest.mark.parametrize("behavior", ["ignore", "raise"])
  def test_set_datetime_attribute_bad_type(
    self, behavior: Literal["ignore", "raise"], caplog: pytest.LogCaptureFixture, log_level: int
  ) -> None:
    elem = self.serializer.backend.make_elem("elem")
    self.serializer.policy.invalid_attribute_type = PolicyValue(behavior, log_level)

    error_message = "Attribute 'attr' is not a datetime object"

    if behavior == "raise":
      with pytest.raises(hm.AttributeSerializationError, match=error_message):
        self.serializer._set_datetime_attribute(elem, "not a dt", "attr", True)  # type: ignore
    else:
      self.serializer._set_datetime_attribute(elem, "not a dt", "attr", True)  # type: ignore
      assert self.serializer.backend.get_attr(elem, "attr") is None

    assert caplog.record_tuples == [(self.serializer.logger.name, log_level, error_message)]

  def test_set_int_attribute_formats_as_string(self):
    element = self.serializer.backend.make_elem("elem")
    self.serializer._set_int_attribute(element, 1, "attr", True)

    assert self.serializer.backend.get_attr(element, "attr") == "1"

  def test_set_int_attribute_uses_backend(self):
    element = self.serializer.backend.make_elem("elem")
    backend_set_attr_mock = self.mocker.Mock()
    self.serializer.backend.set_attr = backend_set_attr_mock
    self.serializer._set_int_attribute(element, 1, "attr", True)

    backend_set_attr_mock.assert_called_once_with(element, "attr", "1")

  def test_set_int_attribute_calls_required_attribute_missing(self):
    element = self.serializer.backend.make_elem("elem")
    required_mock = self.mocker.Mock()
    self.serializer._handle_missing_attribute = required_mock
    self.serializer._set_int_attribute(element, None, "attr", True)

    assert required_mock.call_count == 1
    required_mock.assert_called_once_with(element, "attr", True)

  @pytest.mark.parametrize("behavior", ["ignore", "raise"])
  def test_set_int_attribute_bad_type(
    self, behavior: Literal["ignore", "raise"], caplog: pytest.LogCaptureFixture, log_level: int
  ) -> None:
    elem = self.serializer.backend.make_elem("elem")
    self.serializer.policy.invalid_attribute_type = PolicyValue(behavior, log_level)

    error_message = "Attribute 'attr' is not an int"

    if behavior == "raise":
      with pytest.raises(hm.AttributeSerializationError, match=error_message):
        self.serializer._set_int_attribute(elem, "not an int", "attr", True)  # type: ignore
    else:
      self.serializer._set_int_attribute(elem, "not an int", "attr", True)  # type: ignore
      assert self.serializer.backend.get_attr(elem, "attr") is None

    assert caplog.record_tuples == [(self.serializer.logger.name, log_level, error_message)]

  def test_set_enum_attribute_formats_as_string(self):
    element = self.serializer.backend.make_elem("elem")
    self.serializer._set_enum_attribute(element, hm.Segtype.BLOCK, "attr", hm.Segtype, True)

    assert self.serializer.backend.get_attr(element, "attr") == "block"

  def test_set_enum_attribute_uses_backend(self):
    element = self.serializer.backend.make_elem("elem")
    backend_set_attr_mock = self.mocker.Mock()
    self.serializer.backend.set_attr = backend_set_attr_mock
    self.serializer._set_enum_attribute(element, hm.Segtype.BLOCK, "attr", hm.Segtype, True)

    backend_set_attr_mock.assert_called_once_with(element, "attr", "block")

  def test_set_enum_attribute_calls_required_attribute_missing(self):
    element = self.serializer.backend.make_elem("elem")
    required_mock = self.mocker.Mock()
    self.serializer._handle_missing_attribute = required_mock
    self.serializer._set_enum_attribute(element, None, "attr", hm.Segtype, True)

    required_mock.assert_called_once_with(element, "attr", True)

  @pytest.mark.parametrize("behavior", ["ignore", "raise"])
  def test_set_enum_attribute_bad_type(
    self, behavior: Literal["ignore", "raise"], caplog: pytest.LogCaptureFixture, log_level: int
  ) -> None:
    elem = self.serializer.backend.make_elem("elem")
    self.serializer.policy.invalid_attribute_type = PolicyValue(behavior, log_level)

    error_message = "Attribute 'attr' is not a member of <enum 'Segtype'>"

    if behavior == "raise":
      with pytest.raises(hm.AttributeSerializationError, match=error_message):
        self.serializer._set_enum_attribute(elem, "not an Enum", "attr", hm.Segtype, True)  # type: ignore
    else:
      self.serializer._set_enum_attribute(elem, "not an Enum", "attr", hm.Segtype, True)  # type: ignore
      assert self.serializer.backend.get_attr(elem, "attr") is None

    assert caplog.record_tuples == [(self.serializer.logger.name, log_level, error_message)]

  def test_set_str_attribute_formats_as_string(self):
    element = self.serializer.backend.make_elem("elem")
    self.serializer._set_str_attribute(element, "value", "attr", True)

    assert self.serializer.backend.get_attr(element, "attr") == "value"

  def test_set_str_attribute_uses_backend(self):
    element = self.serializer.backend.make_elem("elem")
    backend_set_attr_mock = self.mocker.Mock()
    self.serializer.backend.set_attr = backend_set_attr_mock
    self.serializer._set_str_attribute(element, "value", "attr", True)

    backend_set_attr_mock.assert_called_once_with(element, "attr", "value")

  def test_set_str_attribute_calls_required_attribute_missing(self):
    element = self.serializer.backend.make_elem("elem")
    required_mock = self.mocker.Mock()
    self.serializer._handle_missing_attribute = required_mock
    self.serializer._set_str_attribute(element, None, "attr", True)

    assert required_mock.call_count == 1
    required_mock.assert_called_once_with(element, "attr", True)


class TestInlineContentSerializerMixin:
  @pytest.fixture(autouse=True)
  def setup(self, backend: hm.XmlBackend, test_logger: logging.Logger, mocker: MockerFixture):
    policy = SerializationPolicy()
    self.serializer = FakeBaseElementSerializer(backend=backend, logger=test_logger, policy=policy)
    self.mocker = mocker

  @pytest.mark.parametrize("behavior", ["ignore", "raise"])
  def test_set_str_attribute_bad_type(
    self, behavior: Literal["ignore", "raise"], caplog: pytest.LogCaptureFixture, log_level: int
  ) -> None:
    elem = self.serializer.backend.make_elem("elem")
    self.serializer.policy.invalid_attribute_type = PolicyValue(behavior, log_level)

    error_message = "Attribute 'attr' is not a string"

    if behavior == "raise":
      with pytest.raises(hm.AttributeSerializationError, match=error_message):
        self.serializer._set_str_attribute(elem, 1, "attr", True)  # type: ignore
    else:
      self.serializer._set_str_attribute(elem, 1, "attr", True)  # type: ignore
      assert self.serializer.backend.get_attr(elem, "attr") is None

    assert caplog.record_tuples == [(self.serializer.logger.name, log_level, error_message)]

  def test_serialize_content_into_serializes_mixed_content_in_order(self):
    element = self.serializer.backend.make_elem("elem")
    mock_obj = self.mocker.Mock()
    mock_child = self.mocker.Mock(spec=hm.Bpt)

    def fake_emit(x):
      if x is mock_child:
        e = self.serializer.backend.make_elem("child")
        self.serializer.backend.set_text(e, "child text")
        return e
      raise NotImplementedError

    mock_obj.content = ["first", mock_child, "second"]

    self.serializer._set_emit(fake_emit)

    self.serializer._serialize_content_into(
      mock_obj, element, (hm.Bpt, hm.Ept, hm.Ph, hm.It, hm.Hi)
    )

    assert self.serializer.backend.get_text(element) == "first"
    child = next(self.serializer.backend.iter_children(element))
    assert self.serializer.backend.get_tag(child) == "child"
    assert self.serializer.backend.get_text(child) == "child text"
    assert self.serializer.backend.get_tail(child) == "second"

  def test_serialize_content_into_raises_if_invalid_child(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    element = self.serializer.backend.make_elem("elem")
    mock_obj = self.mocker.Mock()
    mock_obj.content = [1]
    log_message = "Incorrect child element in Mock: expected one of Bpt, Ept, Ph, It, Hi, got 'int'"

    self.serializer.policy.invalid_content_type.log_level = log_level

    with pytest.raises(hm.XmlSerializationError, match=log_message):
      self.serializer._serialize_content_into(
        mock_obj, element, (hm.Bpt, hm.Ept, hm.Ph, hm.It, hm.Hi)
      )

    expected_log = (self.serializer.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_serialize_content_into_ignores_if_invalid_child(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    element = self.serializer.backend.make_elem("elem")
    mock_obj = self.mocker.Mock()
    mock_obj.content = ["first", 1, "second"]
    log_message = "Incorrect child element in Mock: expected one of Bpt, Ept, Ph, It, Hi, got 'int'"

    self.serializer.policy.invalid_content_type.behavior = "ignore"
    self.serializer.policy.invalid_content_type.log_level = log_level

    self.serializer._serialize_content_into(
      mock_obj, element, (hm.Bpt, hm.Ept, hm.Ph, hm.It, hm.Hi)
    )

    expected_log = (self.serializer.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]
    assert self.serializer.backend.get_text(element) == "firstsecond"

  def test_serialize_content_into_does_not_append_if_emit_returns_none(self):
    element = self.serializer.backend.make_elem("elem")

    self.serializer._set_emit(lambda x: None)
    mock_obj = self.mocker.Mock()
    mock_obj.content = ["first", self.mocker.Mock(spec=hm.Bpt), "second"]

    self.serializer._serialize_content_into(
      mock_obj, element, (hm.Bpt, hm.Ept, hm.Ph, hm.It, hm.Hi)
    )

    assert self.serializer.backend.get_text(element) == "firstsecond"


class TestChildrenSerializerMixin:
  @pytest.fixture(autouse=True)
  def setup(self, backend: hm.XmlBackend, test_logger: logging.Logger, mocker: MockerFixture):
    policy = SerializationPolicy()
    self.serializer = FakeBaseElementSerializer(backend=backend, logger=test_logger, policy=policy)
    self.mocker = mocker

  def test_serialize_children_serializes_children(self):
    element = self.serializer.backend.make_elem("elem")
    mock_child = self.mocker.Mock(spec=hm.Bpt)

    def fake_emit(x):
      if x is mock_child:
        e = self.serializer.backend.make_elem("child")
        self.serializer.backend.set_text(e, "child text")
        return e
      raise NotImplementedError

    self.serializer._set_emit(fake_emit)

    self.serializer._serialize_children([mock_child], element, hm.Bpt)

    assert len(list(self.serializer.backend.iter_children(element))) == 1
    child = next(self.serializer.backend.iter_children(element))
    assert self.serializer.backend.get_tag(child) == "child"
    assert self.serializer.backend.get_text(child) == "child text"

  def test_serialize_children_raises_if_invalid_child(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    element = self.serializer.backend.make_elem("elem")
    log_message = "Invalid child element 'int' when serializing <elem>"

    self.serializer.policy.invalid_child_element.log_level = log_level

    with pytest.raises(hm.XmlSerializationError, match=log_message):
      self.serializer._serialize_children([1], element, hm.Bpt)  # type: ignore

    expected_log = (self.serializer.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_serialize_children_ignores_if_invalid_child(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    element = self.serializer.backend.make_elem("elem")
    log_message = "Invalid child element 'int' when serializing <elem>"

    self.serializer.policy.invalid_child_element.behavior = "ignore"
    self.serializer.policy.invalid_child_element.log_level = log_level

    self.serializer._serialize_children([1], element, hm.Bpt)  # type: ignore

    expected_log = (self.serializer.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_serialize_children_does_not_append_if_emit_returns_none(self):
    element = self.serializer.backend.make_elem("elem")

    self.serializer._set_emit(lambda x: None)
    mock_child = self.mocker.Mock(spec=hm.Bpt)

    self.serializer._serialize_children([mock_child], element, hm.Bpt)

    assert len(list(self.serializer.backend.iter_children(element))) == 0
