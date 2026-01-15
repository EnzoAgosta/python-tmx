import pytest
import logging
from datetime import datetime
from enum import StrEnum
from hypomnema.base.types import Prop
from hypomnema.base.errors import AttributeDeserializationError, XmlDeserializationError
from hypomnema.xml.deserialization.base import BaseElementDeserializer
from hypomnema.xml.policy import DeserializationPolicy, PolicyValue


class ConcreteDeserializer(BaseElementDeserializer):
  """A concrete implementation for testing abstract BaseElementDeserializer."""

  def _deserialize(self, element):
    return None


class MockEnum(StrEnum):
  A = "a"
  B = "b"


class BaseDeserializerTest:
  @pytest.fixture(autouse=True)
  def setup(self, mocker, backend):
    self.mocker = mocker
    self.backend = backend
    self.policy = DeserializationPolicy()
    self.logger = logging.getLogger("test")
    self.deserializer = ConcreteDeserializer(backend, self.policy, self.logger)

    self.deserializer._set_emit(lambda x: Prop(text="mock", type="mock"))


class TestBaseDeserializerHappy(BaseDeserializerTest):
  """Happy path tests for BaseElementDeserializer."""

  def test_emit_delegates(self):
    """Test that emit calls the provided callable."""
    mock_emit = self.mocker.Mock(return_value="result")
    self.deserializer._set_emit(mock_emit)
    elem = self.backend.create_element("elem")
    assert self.deserializer.emit(elem) == "result"
    mock_emit.assert_called_once_with(elem)

  def test_handle_missing_attribute_not_required(self):
    """Test missing optional attribute does nothing."""
    elem = self.backend.create_element("elem")
    self.deserializer._handle_missing_attribute(elem, "attr", required=False)

  def test_parse_attribute_as_str_valid(self):
    elem = self.backend.create_element("elem", attributes={"attr": "val"})
    val = self.deserializer._parse_attribute_as_str(elem, "attr", required=True)
    assert val == "val"

  def test_parse_attribute_as_str_missing_optional(self):
    elem = self.backend.create_element("elem")
    val = self.deserializer._parse_attribute_as_str(elem, "attr", required=False)
    assert val is None

  def test_parse_attribute_as_int_valid(self):
    elem = self.backend.create_element("elem", attributes={"count": "42"})
    val = self.deserializer._parse_attribute_as_int(elem, "count", required=True)
    assert val == 42

  def test_parse_attribute_as_int_missing_optional(self):
    elem = self.backend.create_element("elem")
    val = self.deserializer._parse_attribute_as_int(elem, "count", required=False)
    assert val is None

  def test_parse_attribute_as_datetime_valid(self):
    dt_str = "2023-01-01T12:00:00"
    elem = self.backend.create_element("elem", attributes={"date": dt_str})
    val = self.deserializer._parse_attribute_as_datetime(elem, "date", required=True)
    assert val == datetime.fromisoformat(dt_str)

  def test_parse_attribute_as_datetime_missing_optional(self):
    elem = self.backend.create_element("elem")
    val = self.deserializer._parse_attribute_as_datetime(elem, "date", required=False)
    assert val is None

  def test_parse_attribute_as_enum_valid(self):
    elem = self.backend.create_element("elem", attributes={"type": "a"})
    val = self.deserializer._parse_attribute_as_enum(elem, "type", MockEnum, required=True)
    assert val == MockEnum.A

  def test_parse_attribute_as_enum_missing_optional(self):
    elem = self.backend.create_element("elem")
    val = self.deserializer._parse_attribute_as_enum(elem, "type", MockEnum, required=False)
    assert val is None

  def test_deserialize_content_text_only(self):
    elem = self.backend.create_element("elem")
    self.backend.set_text(elem, "Hello")
    content = self.deserializer._deserialize_content(elem, allowed=())
    assert content == ["Hello"]

  def test_deserialize_content_mixed(self):
    elem = self.backend.create_element("elem")
    self.backend.set_text(elem, "Hello")

    child = self.backend.create_element("child")

    self.backend.set_tail(child, "!")
    self.backend.append_child(elem, child)

    mock_obj = Prop(text="p", type="t")
    self.deserializer._set_emit(lambda x: mock_obj)

    content = self.deserializer._deserialize_content(elem, allowed=("child",))

    assert len(content) == 3
    assert content[0] == "Hello"
    assert content[1] == mock_obj
    assert content[2] == "!"

  def test_deserialize_content_empty_fallback_string(self):
    self.policy.empty_content = PolicyValue("empty", logging.DEBUG)
    elem = self.backend.create_element("elem")
    content = self.deserializer._deserialize_content(elem, allowed=())
    assert content == [""]


class TestBaseDeserializerError(BaseDeserializerTest):
  """Error cases for BaseElementDeserializer."""

  def test_emit_raises_if_not_set(self):
    fresh_deserializer = ConcreteDeserializer(self.backend, self.policy, self.logger)
    with pytest.raises(AssertionError, match=r"emit\(\) called before set_emit\(\)"):
      fresh_deserializer.emit("something")

  def test_handle_missing_attribute_required_raise(self):
    elem = self.backend.create_element("elem")
    with pytest.raises(AttributeDeserializationError, match="Required attribute 'attr' is None"):
      self.deserializer._handle_missing_attribute(elem, "attr", required=True)

  def test_parse_attribute_as_str_missing_required(self):
    elem = self.backend.create_element("elem")
    with pytest.raises(AttributeDeserializationError, match="Required attribute 'attr' is None"):
      self.deserializer._parse_attribute_as_str(elem, "attr", required=True)

  def test_parse_attribute_as_int_invalid(self):
    elem = self.backend.create_element("elem", attributes={"count": "abc"})
    with pytest.raises(AttributeDeserializationError, match="Cannot convert"):
      self.deserializer._parse_attribute_as_int(elem, "count", required=True)

  def test_parse_attribute_as_datetime_invalid(self):
    elem = self.backend.create_element("elem", attributes={"date": "bad-date"})
    with pytest.raises(AttributeDeserializationError, match="Cannot convert"):
      self.deserializer._parse_attribute_as_datetime(elem, "date", required=True)

  def test_parse_attribute_as_enum_invalid(self):
    elem = self.backend.create_element("elem", attributes={"type": "c"})
    with pytest.raises(AttributeDeserializationError, match="not a valid enum value"):
      self.deserializer._parse_attribute_as_enum(elem, "type", MockEnum, required=True)

  def test_deserialize_content_invalid_child(self):
    elem = self.backend.create_element("elem")
    child = self.backend.create_element("bad")
    self.backend.append_child(elem, child)

    with pytest.raises(XmlDeserializationError, match="Incorrect child element"):
      self.deserializer._deserialize_content(elem, allowed=("good",))

  def test_deserialize_content_empty_raise(self):
    elem = self.backend.create_element("elem")
    with pytest.raises(XmlDeserializationError, match="Element <elem> is empty"):
      self.deserializer._deserialize_content(elem, allowed=())
