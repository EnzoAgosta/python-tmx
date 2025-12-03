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
  backend: XMLBackend[T_XmlElement]
  policy: SerializationPolicy
  logger: Logger

  def emit(self, obj: BaseElement) -> T_XmlElement | None: ...


class BaseElementSerializer[T_XmlElement](ABC):
  def __init__(
    self,
    backend: XMLBackend,
    policy: SerializationPolicy,
    logger: Logger,
  ):
    self.backend: XMLBackend[T_XmlElement] = backend
    self.policy = policy
    self.logger = logger
    self._emit = None

  def _set_emit(self, emit: Callable[[BaseElement], T_XmlElement | None]) -> None:
    self._emit = emit

  def emit(self, obj: BaseElement) -> T_XmlElement | None:
    assert self._emit is not None, "emit() called before set_emit() was called"
    return self._emit(obj)

  @abstractmethod
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None: ...

  def _check_obj_type(
    self, obj: BaseElement, expected_type: type[T_Expected]
  ) -> TypeGuard[T_Expected]:
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
  __slots__ = tuple()

  def serialize_content(
    self,
    source: BaseInlineElement | Tuv,
    target: T_XmlElement,
    allowed: tuple[type[BaseInlineElement], ...],
  ) -> None:
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
