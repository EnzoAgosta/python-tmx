import pytest
import logging
from hypomnema.xml.deserialization.deserializer import Deserializer
from hypomnema.xml.policy import DeserializationPolicy, PolicyValue
from hypomnema.base.errors import MissingHandlerError
from hypomnema.base.types import Prop


class BaseDeserializerTest:
  @pytest.fixture(autouse=True)
  def setup(self, mocker, backend):
    self.mocker = mocker
    self.backend = backend
    self.deserializer = Deserializer(backend, policy=DeserializationPolicy())


class TestDeserializerHappy(BaseDeserializerTest):
  def test_deserialize_dispatch(self):
    """Test that deserialize dispatches to the correct handler."""

    elem = self.backend.create_element("prop", attributes={"type": "t"})
    self.backend.set_text(elem, "val")

    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Prop)
    assert obj.text == "val"

  def test_deserialize_unknown_tag_ignore(self):
    self.deserializer.policy.missing_handler = PolicyValue("ignore", logging.DEBUG)
    elem = self.backend.create_element("unknown")
    result = self.deserializer.deserialize(elem)
    assert result is None

  def test_deserialize_unknown_tag_default_fallback_success(self):
    deserializer = Deserializer(self.backend, handlers={})
    deserializer.policy.missing_handler = PolicyValue("default", logging.DEBUG)

    elem = self.backend.create_element("prop", attributes={"type": "t"})
    self.backend.set_text(elem, "val")

    obj = deserializer.deserialize(elem)
    assert isinstance(obj, Prop)

  def test_custom_handler(self):
    mock_handler = self.mocker.Mock()
    mock_handler._emit = None
    mock_handler._set_emit = self.mocker.Mock()
    mock_handler._deserialize.return_value = "mock_obj"

    handlers = {"custom": mock_handler}
    deserializer = Deserializer(self.backend, handlers=handlers)

    elem = self.backend.create_element("custom")
    result = deserializer.deserialize(elem)

    assert result == "mock_obj"
    mock_handler._deserialize.assert_called_once_with(elem)


class TestDeserializerError(BaseDeserializerTest):
  def test_deserialize_unknown_tag_raise(self):
    elem = self.backend.create_element("unknown")
    with pytest.raises(MissingHandlerError, match="Missing handler"):
      self.deserializer.deserialize(elem)

  def test_deserialize_unknown_tag_default_fallback_fail(self):
    self.deserializer.policy.missing_handler = PolicyValue("default", logging.DEBUG)
    elem = self.backend.create_element("truly_unknown")
    with pytest.raises(MissingHandlerError, match="Missing handler"):
      self.deserializer.deserialize(elem)
