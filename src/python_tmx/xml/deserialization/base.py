from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger
from typing import Callable, LiteralString, Protocol, TypeVar

from python_tmx.base.errors import (
  AttributeDeserializationError,
  InvalidTagError,
  XmlDeserializationError,
)
from python_tmx.base.types import Assoc, BaseElement, BaseInlineElement, Pos, Segtype
from python_tmx.xml import T_XmlElement
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.policy import DeserializationPolicy

T_Enum = TypeVar("T_Enum", Pos, Segtype, Assoc)

__all__ = ["BaseElementDeserializer", "DeserializerHost", "InlineContentDeserializerMixin"]


class DeserializerHost(Protocol[T_XmlElement]):
  backend: XMLBackend[T_XmlElement]
  policy: DeserializationPolicy
  logger: Logger

  def emit(self, obj: T_XmlElement) -> BaseElement | None: ...


class BaseElementDeserializer[T_XmlElement](ABC):
  def __init__(
    self,
    backend: XMLBackend,
    policy: DeserializationPolicy,
    logger: Logger,
  ):
    self.backend: XMLBackend[T_XmlElement] = backend
    self.policy = policy
    self.logger = logger
    self._emit = None

  def _set_emit(self, emit: Callable[[T_XmlElement], BaseElement | None]) -> None:
    self._emit = emit

  def emit(self, obj: T_XmlElement) -> BaseElement | None:
    assert self._emit is not None, "emit() called before set_emit() was called"
    return self._emit(obj)

  @abstractmethod
  def _deserialize(self, element: T_XmlElement) -> BaseElement | None: ...

  def _check_tag(self, element: T_XmlElement, expected_tag: LiteralString) -> None:
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
  __slots__ = tuple()

  def deserialize_content(
    self, source: T_XmlElement, allowed: tuple[str, ...]
  ) -> list[BaseInlineElement | str]:
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
