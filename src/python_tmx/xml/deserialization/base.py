from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger
from typing import Callable, LiteralString, Protocol

from python_tmx.base.errors import (
  AttributeDeserializationError,
  InvalidTagError,
  XmlDeserializationError,
)
from python_tmx.base.types import BaseElement, BaseInlineElement
from python_tmx.xml import T_Enum, T_XmlElement
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.policy import DeserializationPolicy

__all__ = ["BaseElementDeserializer", "DeserializerHost", "InlineContentDeserializerMixin"]


class DeserializerHost(Protocol[T_XmlElement]):
  """
  Protocol defining the contract for the orchestrator driving the deserialization process.

  This is primarily used by the `InlineContentDeserializerMixin` to callback into
  the main recursion loop (via `emit`) without creating a circular import dependency
  on the concrete `Deserializer` class.
  """

  backend: XMLBackend[T_XmlElement]
  policy: DeserializationPolicy
  logger: Logger

  def emit(self, obj: T_XmlElement) -> BaseElement | None:
    """
    Dispatches a child XML element to its appropriate handler.

    Args:
        obj (T_XmlElement): The XML element to deserialize.

    Returns:
        BaseElement | None: The deserialized Python object, or None if the
        handler was missing/ignored based on policy.
    """
    ...


class BaseElementDeserializer[T_XmlElement](ABC):
  """
  Abstract base class for all TMX element deserializers.

  Provides common utilities for parsing attributes, enforcing tag names, and
  interacting with the `DeserializationPolicy`.

  Attributes:
      backend (XMLBackend): The abstraction layer for the underlying XML library (lxml/etree).
      policy (DeserializationPolicy): Configuration controlling error handling behavior.
      logger (Logger): Logger instance for recording debug/warning/error events.
  """

  def __init__(
    self,
    backend: XMLBackend,
    policy: DeserializationPolicy,
    logger: Logger,
  ):
    self.backend: XMLBackend[T_XmlElement] = backend
    self.policy = policy
    self.logger = logger
    self._emit: Callable[[T_XmlElement], BaseElement | None] | None = None

  def _set_emit(self, emit: Callable[[T_XmlElement], BaseElement | None]) -> None:
    """
    Injects the orchestrator's callback function.

    This must be called before `emit()` or `_deserialize()` is used.

    Args:
        emit (Callable): The main dispatch function (usually `Deserializer.deserialize`).
    """
    self._emit = emit

  def emit(self, obj: T_XmlElement) -> BaseElement | None:
    """
    Delegates deserialization of a child element to the orchestrator.

    Args:
        obj (T_XmlElement): The child XML element.

    Returns:
        BaseElement | None: The resulting object.

    Raises:
        AssertionError: If `_set_emit` has not been called yet.
    """
    assert self._emit is not None, "emit() called before set_emit() was called"
    return self._emit(obj)

  @abstractmethod
  def _deserialize(self, element: T_XmlElement) -> BaseElement | None:
    """
    Parses the given XML element into a TMX data object.

    Args:
        element (T_XmlElement): The specific XML node to parse (e.g., <header>).

    Returns:
        BaseElement | None: The fully populated TMX object.
    """
    ...

  def _check_tag(self, element: T_XmlElement, expected_tag: LiteralString) -> None:
    """
    Validates that the XML element's tag matches the handler's expectation.

    Policy Impact (`policy.invalid_tag`):
        - `raise`: Raises `InvalidTagError` if tags mismatch.
        - `ignore`: Logs the mismatch at the configured level and proceeds.

    Args:
        element (T_XmlElement): The element being inspected.
        expected_tag (LiteralString): The required tag name (e.g., "header").

    Raises:
        InvalidTagError: If validation fails and policy is 'raise'.
    """
    tag = self.backend.get_tag(element)
    if not tag == expected_tag:
      self.logger.log(
        self.policy.invalid_tag.log_level, "Incorrect tag: expected %s, got %s", expected_tag, tag
      )
      if self.policy.invalid_tag.behavior == "raise":
        raise InvalidTagError(f"Incorrect tag: expected {expected_tag}, got {tag}")

  def _parse_attribute_as_dt(
    self, element: T_XmlElement, attribute: str, required: bool
  ) -> datetime | None:
    """
    Parses a string attribute into a `datetime` object.

    Uses `datetime.fromisoformat()` for broad compatibility.

    Policy Impact:
        - `policy.required_attribute_missing`: Controls behavior if `required=True`
          but the attribute is absent.
        - `policy.invalid_attribute_value`: Controls behavior if the string cannot
          be parsed as a date.

    Args:
        element (T_XmlElement): The XML element.
        attribute (str): The attribute name to retrieve.
        required (bool): Whether the attribute is mandatory in TMX 1.4b.

    Returns:
        datetime | None: The parsed datetime, or None if missing/failed (and policy allowed it).

    Raises:
        AttributeDeserializationError: If a required attribute is missing or invalid,
        and the policy is set to 'raise'.
    """
    value = self.backend.get_attr(element, attribute)
    tag = self.backend.get_tag(element)
    if value is None:
      if required:
        self.logger.log(
          self.policy.required_attribute_missing.log_level,
          "Missing required attribute %r on element <%s>",
          attribute,
          tag,
        )
        if self.policy.required_attribute_missing.behavior == "raise":
          raise AttributeDeserializationError(
            f"Missing required attribute {attribute!r} on element <{tag}>"
          )
      return None
    try:
      return datetime.fromisoformat(value)
    except ValueError as e:
      self.logger.log(
        self.policy.invalid_attribute_value.log_level,
        "Cannot convert %r to a datetime object for attribute %s",
        value,
        attribute,
      )
      if self.policy.invalid_attribute_value.behavior == "raise":
        raise AttributeDeserializationError(
          f"Cannot convert {value!r} to a datetime object for attribute {attribute}"
        ) from e
      return None

  def _parse_attribute_as_int(
    self, element: T_XmlElement, attribute: str, required: bool
  ) -> int | None:
    """
    Parses a string attribute into an `int`.

    Policy Impact:
        - `policy.required_attribute_missing`: Controls missing required attributes.
        - `policy.invalid_attribute_value`: Controls `ValueError` during conversion.

    Args:
        element (T_XmlElement): The XML element.
        attribute (str): The attribute name.
        required (bool): Whether the attribute is mandatory.

    Returns:
        int | None: The integer value, or None.

    Raises:
        AttributeDeserializationError: If validation fails and policy is 'raise'.
    """
    value = self.backend.get_attr(element, attribute)
    tag = self.backend.get_tag(element)
    if value is None:
      if required:
        self.logger.log(
          self.policy.required_attribute_missing.log_level,
          "Missing required attribute %r on element <%s>",
          attribute,
          tag,
        )
        if self.policy.required_attribute_missing.behavior == "raise":
          raise AttributeDeserializationError(
            f"Missing required attribute {attribute!r} on element <{tag}>"
          )
      return None
    try:
      return int(value)
    except ValueError as e:
      self.logger.log(
        self.policy.invalid_attribute_value.log_level,
        "Cannot convert %r to an int for attribute %s",
        value,
        attribute,
      )
      if self.policy.invalid_attribute_value.behavior == "raise":
        raise AttributeDeserializationError(
          f"Cannot convert {value!r} to an int for attribute {attribute}"
        ) from e
      return None

  def _parse_attribute_as_enum(
    self,
    element: T_XmlElement,
    attribute: str,
    enum_type: type[T_Enum],
    required: bool,
  ) -> T_Enum | None:
    """
    Parses a string attribute into a specific `Enum` type.

    Policy Impact:
        - `policy.required_attribute_missing`: Controls missing required attributes.
        - `policy.invalid_attribute_value`: Controls `ValueError` during enum instantiation.

    Args:
        element (T_XmlElement): The XML element.
        attribute (str): The attribute name.
        enum_type (type[T_Enum]): The Enum class to instantiate (e.g., `Segtype`).
        required (bool): Whether the attribute is mandatory.

    Returns:
        T_Enum | None: The enum member, or None.

    Raises:
        AttributeDeserializationError: If validation fails and policy is 'raise'.
    """
    value = self.backend.get_attr(element, attribute)
    tag = self.backend.get_tag(element)
    if value is None:
      if required:
        self.logger.log(
          self.policy.required_attribute_missing.log_level,
          "Missing required attribute %r on element <%s>",
          attribute,
          tag,
        )
        if self.policy.required_attribute_missing.behavior == "raise":
          raise AttributeDeserializationError(
            f"Missing required attribute {attribute!r} on element <{tag}>"
          )
      return None
    try:
      return enum_type(value)
    except ValueError as e:
      self.logger.log(
        self.policy.invalid_attribute_value.log_level,
        "Value %r is not a valid enum value for attribute %s",
        value,
        attribute,
      )
      if self.policy.invalid_attribute_value.behavior == "raise":
        raise AttributeDeserializationError(
          f"Value {value!r} is not a valid enum value for attribute {attribute}"
        ) from e
      return None

  def _parse_attribute(
    self,
    element: T_XmlElement,
    attribute: str,
    required: bool,
  ) -> str | None:
    """
    Retrieves a string attribute.

    Policy Impact:
        - `policy.required_attribute_missing`: Controls behavior if `required=True`
          but the attribute is absent.

    Args:
        element (T_XmlElement): The XML element.
        attribute (str): The attribute name.
        required (bool): Whether the attribute is mandatory.

    Returns:
        str | None: The string value, or None.

    Raises:
        AttributeDeserializationError: If missing and policy is 'raise'.
    """
    value = self.backend.get_attr(element, attribute)
    tag = self.backend.get_tag(element)
    if value is None:
      if required:
        self.logger.log(
          self.policy.required_attribute_missing.log_level,
          "Missing required attribute %r on element <%s>",
          attribute,
          tag,
        )
        if self.policy.required_attribute_missing.behavior == "raise":
          raise AttributeDeserializationError(
            f"Missing required attribute {attribute!r} on element <{tag}>"
          )
    return value


class InlineContentDeserializerMixin[T_XmlElement](DeserializerHost[T_XmlElement]):
  """
  Mixin for Deserializers that process mixed inline content (text + tags).

  Used by handlers like `TuvDeserializer`, `BptDeserializer`, etc., to process
  content that contains strings interspersed with other TMX elements (e.g.,
  "Hello <bpt>...</bpt> world").
  """

  __slots__ = tuple()

  def deserialize_content(
    self, source: T_XmlElement, allowed: tuple[str, ...]
  ) -> list[BaseInlineElement | str]:
    """
    Iterates over children and text nodes to build a flat list of content.

    This method respects XML 'tails' (text occurring after a closing tag) to
    preserve full fidelity of the segment content.

    Policy Impact:
        - `policy.invalid_child_element`: Checks if a child's tag is in the `allowed` list.
        - `policy.empty_content`: Checks if the resulting list is empty.

    Args:
        source (T_XmlElement): The parent element (e.g., <seg>, <bpt>).
        allowed (tuple[str, ...]): A whitelist of allowed child tag names.

    Returns:
        list[BaseInlineElement | str]: The ordered content list.

    Raises:
        XmlDeserializationError: If policy violation triggers a raise.
    """
    source_tag = self.backend.get_tag(source)
    result = []
    if (text := self.backend.get_text(source)) is not None:
      result.append(text)
    for child in self.backend.iter_children(source):
      child_tag = self.backend.get_tag(child)
      if child_tag not in allowed:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Incorrect child element in %s: expected one of %s, got %s",
          source_tag,
          ", ".join(allowed),
          child_tag,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlDeserializationError(
            f"Incorrect child element in {source_tag}: expected one of {', '.join(allowed)}, got {child_tag}"
          )
        continue
      child_obj = self.emit(child)
      if child_obj is not None:
        result.append(child_obj)
      if (tail := self.backend.get_tail(child)) is not None:
        result.append(tail)
    if result == []:
      self.logger.log(self.policy.empty_content.log_level, "Element <%s> is empty", source_tag)
      if self.policy.empty_content.behavior == "raise":
        raise XmlDeserializationError(f"Element <{source_tag}> is empty")
      if self.policy.empty_content.behavior == "empty":
        self.logger.log(self.policy.empty_content.log_level, "Falling back to an empty string")
        result.append("")
    return result
