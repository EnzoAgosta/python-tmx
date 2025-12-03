from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from logging import Logger
from typing import Protocol, TypeGuard, TypeVar

from python_tmx.base.errors import AttributeSerializationError, XmlSerializationError
from python_tmx.base.types import BaseElement, BaseInlineElement, Tuv
from python_tmx.xml import T_XmlElement
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization.base import T_Enum
from python_tmx.xml.policy import SerializationPolicy

T_Expected = TypeVar("T_Expected", bound=BaseElement)


class SerializerHost(Protocol[T_XmlElement]):
  """
  Protocol defining the contract for the orchestrator driving the serialization process.

  This allows handlers and mixins to callback into the main recursion loop (via `emit`)
  without creating circular import dependencies.
  """

  backend: XMLBackend[T_XmlElement]
  policy: SerializationPolicy
  logger: Logger

  def emit(self, obj: BaseElement) -> T_XmlElement | None:
    """
    Dispatches a child Python object to its appropriate handler for serialization.

    Args:
        obj (BaseElement): The Python object to serialize.

    Returns:
        T_XmlElement | None: The resulting XML element, or None if skipped based on policy.
    """
    ...


class BaseElementSerializer[T_XmlElement](ABC):
  """
  Abstract base class for all TMX element serializers.

  Provides utilities for type checking, attribute setting (with type conversion),
  and policy enforcement regarding missing or invalid data.

  Attributes:
      backend (XMLBackend): The abstraction layer for building XML nodes.
      policy (SerializationPolicy): Configuration controlling validation strictness.
      logger (Logger): Channel for debug/warning/error logs.
  """

  def __init__(
    self,
    backend: XMLBackend,
    policy: SerializationPolicy,
    logger: Logger,
  ):
    self.backend: XMLBackend[T_XmlElement] = backend
    self.policy = policy
    self.logger = logger
    self._emit: Callable[[BaseElement], T_XmlElement | None] | None = None

  def _set_emit(self, emit: Callable[[BaseElement], T_XmlElement | None]) -> None:
    """
    Injects the orchestrator's callback function.

    Must be called before `emit()` is used.

    Args:
        emit (Callable): The main dispatch function (usually `Serializer.serialize`).
    """
    self._emit = emit

  def emit(self, obj: BaseElement) -> T_XmlElement | None:
    """
    Delegates serialization of a child object to the orchestrator.

    Args:
        obj (BaseElement): The child object.

    Returns:
        T_XmlElement | None: The serialized element.

    Raises:
        AssertionError: If `_set_emit` has not been called yet.
    """
    assert self._emit is not None, "emit() called before set_emit() was called"
    return self._emit(obj)

  @abstractmethod
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    """
    Converts a Python TMX object into an XML element.

    Args:
        obj (BaseElement): The specific object to serialize (e.g., Header).

    Returns:
        T_XmlElement | None: The constructed XML node.
    """
    ...

  def _check_obj_type(
    self, obj: BaseElement, expected_type: type[T_Expected]
  ) -> TypeGuard[T_Expected]:
    """
    Validates that the object passed to the handler matches the expected type.

    Policy Impact (`policy.invalid_object_type`):
        - `raise`: Raises `XmlSerializationError` on mismatch.
        - `ignore`: Returns `False`, allowing the caller to abort gracefully.

    Args:
        obj (BaseElement): The object instance.
        expected_type (type): The expected class (e.g., `Header`).

    Returns:
        bool: True if the type matches, False if mismatch (and policy allowed ignore).

    Raises:
        XmlSerializationError: If types mismatch and policy is 'raise'.
    """
    if not isinstance(obj, expected_type):
      self.logger.log(
        self.policy.invalid_object_type.log_level,
        "Cannot serialize object of type %r to xml element using %r",
        type(obj).__name__,
        type(self).__name__,
      )
      if self.policy.invalid_object_type.behavior == "raise":
        raise XmlSerializationError(
          f"Cannot serialize object of type {type(obj).__name__!r} to xml element using {type(self).__name__!r}"
        )
      return False
    return True

  def _set_dt_attribute(
    self,
    target: T_XmlElement,
    value: datetime | None,
    attribute: str,
    required: bool,
  ) -> None:
    """
    Serializes a `datetime` object to an ISO 8601 string attribute.

    Policy Impact:
        - `required_attribute_missing`: Checks if `required=True` but value is None.
        - `invalid_attribute_type`: Checks if value is actually a `datetime` instance.

    Args:
        target (T_XmlElement): The XML element to modify.
        value (datetime | None): The value to set.
        attribute (str): The XML attribute name.
        required (bool): Whether this attribute is mandatory in TMX.

    Raises:
        AttributeSerializationError: If validation fails and policy is 'raise'.
    """
    if value is None:
      if required:
        self.logger.log(
          self.policy.required_attribute_missing.log_level,
          "Required attribute %r is None",
          attribute,
        )
        if self.policy.required_attribute_missing.behavior == "raise":
          raise AttributeSerializationError(f"Required attribute {attribute!r} is None")
      return
    if not isinstance(value, datetime):
      self.logger.log(
        self.policy.invalid_attribute_type.log_level,
        "Attribute %r is not a datetime object",
        attribute,
      )
      if self.policy.invalid_attribute_type.behavior == "raise":
        raise AttributeSerializationError(f"Attribute {attribute!r} is not a datetime object")
      return
    self.backend.set_attr(target, attribute, value.isoformat())

  def _set_int_attribute(
    self,
    target: T_XmlElement,
    value: int | None,
    attribute: str,
    required: bool,
  ) -> None:
    """
    Serializes an integer value to a string attribute.

    Policy Impact:
        - `required_attribute_missing`: Checks for None on required fields.
        - `invalid_attribute_type`: Checks if value is an `int`.

    Args:
        target (T_XmlElement): The XML element.
        value (int | None): The integer value.
        attribute (str): XML attribute name.
        required (bool): Mandatory flag.
    """
    if value is None:
      if required:
        self.logger.log(
          self.policy.required_attribute_missing.log_level,
          "Required attribute %r is None",
          attribute,
        )
        if self.policy.required_attribute_missing.behavior == "raise":
          raise AttributeSerializationError(f"Required attribute {attribute!r} is None")
      return
    if not isinstance(value, int):
      self.logger.log(
        self.policy.invalid_attribute_type.log_level, "Attribute %r is not an int", attribute
      )
      if self.policy.invalid_attribute_type.behavior == "raise":
        raise AttributeSerializationError(f"Attribute {attribute!r} is not an int")
      return
    self.backend.set_attr(target, attribute, str(value))

  def _set_enum_attribute(
    self,
    target: T_XmlElement,
    value: T_Enum | None,
    attribute: str,
    enum_type: type[T_Enum],
    required: bool,
  ) -> None:
    """
    Serializes an Enum member to its string value.

    Policy Impact:
        - `required_attribute_missing`: Checks for None.
        - `invalid_attribute_type`: Checks if value is an instance of `enum_type`.

    Args:
        target (T_XmlElement): The XML element.
        value (T_Enum | None): The enum member.
        attribute (str): XML attribute name.
        enum_type (type[T_Enum]): The expected Enum class.
        required (bool): Mandatory flag.
    """
    if value is None:
      if required:
        self.logger.log(
          self.policy.required_attribute_missing.log_level,
          "Required attribute %r is None",
          attribute,
        )
        if self.policy.required_attribute_missing.behavior == "raise":
          raise AttributeSerializationError(f"Required attribute {attribute!r} is None")
      return
    if not isinstance(value, enum_type):
      self.logger.log(
        self.policy.invalid_attribute_type.log_level,
        "Attribute %r is not a %s",
        attribute,
        enum_type,
      )
      if self.policy.invalid_attribute_type.behavior == "raise":
        raise AttributeSerializationError(f"Attribute {attribute!r} is not a {enum_type}")
      return
    self.backend.set_attr(target, attribute, value.value)

  def _set_attribute(
    self,
    target: T_XmlElement,
    value: str | None,
    attribute: str,
    required: bool,
  ) -> None:
    """
    Sets a string attribute.

    Policy Impact:
        - `required_attribute_missing`: Checks for None.
        - `invalid_attribute_type`: Checks if value is a string.

    Args:
        target (T_XmlElement): The XML element.
        value (str | None): The string value.
        attribute (str): XML attribute name.
        required (bool): Mandatory flag.
    """
    if value is None:
      if required:
        self.logger.log(
          self.policy.required_attribute_missing.log_level,
          "Required attribute %r is None",
          attribute,
        )
        if self.policy.required_attribute_missing.behavior == "raise":
          raise AttributeSerializationError(f"Required attribute {attribute!r} is None")
      return
    if not isinstance(value, str):
      self.logger.log(
        self.policy.invalid_attribute_type.log_level,
        "Attribute %r is not a string",
        attribute,
      )
      if self.policy.invalid_attribute_type.behavior == "raise":
        raise AttributeSerializationError(f"Attribute {attribute!r} is not a string")
      return
    self.backend.set_attr(target, attribute, value)


class InlineContentSerializerMixin[T_XmlElement](SerializerHost[T_XmlElement]):
  """
  Mixin for Serializers that need to produce mixed content (text + tags).

  Used by handlers like `TuvSerializer`, `BptSerializer`, etc. to serialize
  a list of strings and objects into a parent XML element, properly managing
  text nodes and tail text.
  """

  __slots__ = tuple()

  def serialize_content(
    self,
    source: BaseInlineElement | Tuv,
    target: T_XmlElement,
    allowed: tuple[type[BaseInlineElement], ...],
  ) -> None:
    """
    Iterates over a content list and appends text/elements to the target.

    This handles the logic of appending text to the parent's `.text` (if it's the first child)
    or the previous sibling's `.tail` (if it's subsequent text).

    Policy Impact:
        - `policy.invalid_content_type`: Checks if an item in the list is an allowed type.

    Args:
        source (BaseInlineElement | Tuv): The object containing the `.content` list.
        target (T_XmlElement): The parent XML element to populate.
        allowed (tuple[type]): A whitelist of allowed Python classes for child elements.

    Raises:
        XmlSerializationError: If an invalid object type is found in content and policy is 'raise'.
    """
    last_child: T_XmlElement | None = None
    for item in source.content:
      if isinstance(item, str):
        if last_child is None:
          text = self.backend.get_text(target)
          if text is None:
            text = ""
          self.backend.set_text(target, text + item)
        else:
          tail = self.backend.get_tail(last_child)
          if tail is None:
            tail = ""
          self.backend.set_tail(last_child, tail + item)
      elif isinstance(item, allowed):
        child_elem = self.emit(item)
        if child_elem is not None:
          self.backend.append(target, child_elem)
          last_child = child_elem
      else:
        self.logger.log(
          self.policy.invalid_content_type.log_level,
          "Incorrect child element in %s: expected one of %s, got %s",
          type(source).__name__,
          ", ".join(x.__name__ for x in allowed),
          type(item).__name__,
        )
        if self.policy.invalid_content_type.behavior == "raise":
          raise XmlSerializationError(
            f"Incorrect child element in {type(source).__name__}: expected one of {', '.join(x.__name__ for x in allowed)}, got {type(item).__name__}"
          )
        continue
