import logging
import pytest
from python_tmx.base.types import Prop
from python_tmx.base.errors import AttributeDeserializationError, InvalidTagError, XmlDeserializationError
from python_tmx.xml import XML_NS
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import PropDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestPropDeserializer[T_XmlElement]:
  handler: PropDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = PropDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_valid_elem(self, *, full: bool = False) -> T_XmlElement:
    """
    Creates a <prop> element.
    if full is True, all optional attributes are filled.
    """
    elem = self.backend.make_elem("prop")
    self.backend.set_attr(elem, "type", "x-test-type")
    self.backend.set_text(elem, "Valid Prop Content")

    if full:
      self.backend.set_attr(elem, f"{XML_NS}lang", "en-US")
      self.backend.set_attr(elem, "o-encoding", "UTF-8")

    return elem

  def test_minimal_valid(self):
    """Prop requires 'type' and text."""
    elem = self.make_valid_elem()
    prop = self.handler._deserialize(elem)

    assert isinstance(prop, Prop)
    assert prop.text == "Valid Prop Content"
    assert prop.type == "x-test-type"
    assert prop.lang is None

  def test_full_valid(self):
    elem = self.make_valid_elem(full=True)
    prop = self.handler._deserialize(elem)

    assert prop.lang == "en-US"
    assert prop.o_encoding == "UTF-8"

  def test_check_tag(self):
    elem = self.backend.make_elem("note")
    with pytest.raises(InvalidTagError, match="expected prop"):
      self.handler._deserialize(elem)

  def test_missing_required_type(self):
    """'type' is required for <prop>."""
    elem = self.make_valid_elem()
    elem = self.backend.make_elem("prop")
    self.backend.set_text(elem, "Content")

    with pytest.raises(AttributeDeserializationError, match="Missing required attribute 'type'"):
      self.handler._deserialize(elem)

  def test_missing_text_raise(self):
    """Policy: Text missing -> Raise (Default)."""
    elem = self.make_valid_elem()
    self.backend.set_text(elem, None)
    self.policy.missing_text.behavior = "raise"

    with pytest.raises(XmlDeserializationError, match="does not have any text content"):
      self.handler._deserialize(elem)

  def test_missing_text_empty(self):
    """Policy: Text missing -> Return empty string."""
    elem = self.make_valid_elem()
    self.backend.set_text(elem, None)
    self.policy.missing_text.behavior = "empty"

    prop = self.handler._deserialize(elem)
    assert prop.text == ""
