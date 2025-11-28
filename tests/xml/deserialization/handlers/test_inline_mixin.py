import logging
from typing import Any, Callable

import pytest

from python_tmx.base.errors import XmlDeserializationError
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization.base import InlineContentDeserializerMixin
from python_tmx.xml.policy import DeserializationPolicy


class MockInlineHandler[T_XmlElement](InlineContentDeserializerMixin[T_XmlElement]):
  """
  A concrete implementation of the Mixin solely for testing purposes.
  It mimics the interface of a real Deserializer handler.
  """

  def __init__(self, backend: XMLBackend[T_XmlElement], policy: DeserializationPolicy, logger: logging.Logger):
    self.backend = backend
    self.policy = policy
    self.logger = logger
    self.mock_emit_callback: Callable[[T_XmlElement], Any] = lambda x: f"MOCK({self.backend.get_tag(x)})"

  def emit(self, obj: T_XmlElement) -> Any:
    return self.mock_emit_callback(obj)


class TestInlineContentDeserializerMixin[T_XmlElement]:
  handler: MockInlineHandler[T_XmlElement]
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = MockInlineHandler(self.backend, self.policy, self.logger)

  def test_pure_text(self):
    """Scenario: <seg>Hello World</seg>"""
    elem = self.backend.make_elem("seg")
    self.backend.set_text(elem, "Hello World")

    result = self.handler.deserialize_content(elem)

    assert result == ["Hello World"]

  def test_pure_inline_tags(self):
    """Scenario: <seg><ph/><bpt/></seg>"""
    elem = self.backend.make_elem("seg")
    self.backend.append(elem, self.backend.make_elem("ph"))
    self.backend.append(elem, self.backend.make_elem("bpt"))

    result = self.handler.deserialize_content(elem)

    assert result == ["MOCK(ph)", "MOCK(bpt)"]

  def test_complex_mixed_content(self):
    """
    Scenario: TMX Mixed Content
    <seg>Start <ph/> Middle <bpt/> End</seg>
    """
    seg = self.backend.make_elem("seg")
    self.backend.set_text(seg, "Start ")

    ph = self.backend.make_elem("ph")
    self.backend.set_tail(ph, " Middle ")
    self.backend.append(seg, ph)

    bpt = self.backend.make_elem("bpt")
    self.backend.set_tail(bpt, " End")
    self.backend.append(seg, bpt)

    result = self.handler.deserialize_content(seg)

    assert result == ["Start ", "MOCK(ph)", " Middle ", "MOCK(bpt)", " End"]

  def test_whitespace_preservation(self):
    """
    Critical TMX Requirement: Whitespace must be preserved exactly,
    even if it looks like indentation.
    """
    seg = self.backend.make_elem("seg")
    self.backend.set_text(seg, "\n  Content  \n")

    ph = self.backend.make_elem("ph")
    self.backend.set_tail(ph, "\n")
    self.backend.append(seg, ph)

    result = self.handler.deserialize_content(seg)

    assert result == ["\n  Content  \n", "MOCK(ph)", "\n"]

  def test_host_tag_check(self):
    """The Mixin checks if the *parent* tag allows inline content."""
    elem = self.backend.make_elem("tmx")

    with pytest.raises(XmlDeserializationError, match="tag <tmx> is not allowed in inline content"):
      self.handler.deserialize_content(elem)

    self.policy.invalid_inline_tag.behavior = "ignore"
    result = self.handler.deserialize_content(elem)
    assert result == []

  def test_child_tag_validation(self):
    """
    The Mixin validates children against the ALLOWED dictionary.
    <seg> allows 'ph', but does NOT allow 'note'.
    """
    seg = self.backend.make_elem("seg")

    self.backend.append(seg, self.backend.make_elem("ph"))
    self.backend.append(seg, self.backend.make_elem("note"))

    self.policy.invalid_child_element.behavior = "raise"

    with pytest.raises(XmlDeserializationError, match="Incorrect content element"):
      self.handler.deserialize_content(seg)

  def test_child_tag_validation_ignore(self):
    """Test ignoring invalid children."""
    seg = self.backend.make_elem("seg")
    self.backend.append(seg, self.backend.make_elem("ph"))

    self.policy.invalid_child_element.behavior = "ignore"

    result = self.handler.deserialize_content(seg)

    assert result == ["MOCK(ph)"]

  def test_emit_returns_none(self):
    """
    If the orchestrator (via emit) returns None for a valid tag
    (e.g., policy said ignore, or handler missing), it should not be added to content.
    """
    seg = self.backend.make_elem("seg")
    self.backend.set_text(seg, "A")
    ph = self.backend.make_elem("ph")
    self.backend.set_tail(ph, "B")
    self.backend.append(seg, ph)

    self.handler.mock_emit_callback = lambda x: None

    result = self.handler.deserialize_content(seg)

    assert result == ["A", "B"]
