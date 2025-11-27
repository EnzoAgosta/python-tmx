from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger, getLogger
from typing import Callable, Final, Protocol, TypeVar, cast

from python_tmx.base.errors import AttributeSerializationError, XmlSerializationError
from python_tmx.base.types import BaseElement, BaseInlineElement, Bpt, Ept, Hi, It, Ph, Sub, Tuv
from python_tmx.xml import T_XmlElement
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization.base import T_Enum
from python_tmx.xml.policy import SerializationPolicy

__all__ = ["SerializerHost", "BaseElementSerializer", "InlineContentSerializerMixin"]

_ModuleLogger = getLogger(__name__)
T_BaseElement = TypeVar("T_BaseElement", bound=BaseElement)


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
    logger: Logger = _ModuleLogger,
  ):
    self.backend: XMLBackend[T_XmlElement] = backend
    self.policy = policy
    self.logger = logger
    self._emit: Callable[[BaseElement], T_XmlElement | None] | None = None

  def _set_emit(self, emit: Callable[[BaseElement], T_XmlElement | None]) -> None:
    self._emit = emit

  def emit(self, obj: BaseElement) -> T_XmlElement | None:
    assert self._emit is not None, "emit() called before set_emit() was called"
    return self._emit(obj)

  @abstractmethod
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None: ...

  def _check_obj_type(self, obj: BaseElement, expected_type: type[T_BaseElement]) -> T_BaseElement:
    if not isinstance(obj, expected_type):
      self.logger.log(
        self.policy.invalid_object_type.log_level,
        "Invalid element type: expected %s, got %s",
        expected_type.__class__.__name__,
        type(obj).__name__,
      )
      if self.policy.invalid_object_type.behavior == "raise":
        raise XmlSerializationError(f"Invalid element type: expected {expected_type}, got {type(obj).__name__!r}")
    return cast(T_BaseElement, obj)

  def _set_int_attribute(self, element: T_XmlElement, name: str, value: int | None, required: bool) -> None:
    if value is None:
      if required:
        self.logger.log(
          self.policy.missing_required_attribute.log_level,
          "Missing required attribute %r on element <%s>",
          name,
          self.backend.get_tag(element),
        )
        if self.policy.missing_required_attribute.behavior == "raise":
          raise AttributeSerializationError(f"Missing required attribute {name!r} for element <{self.backend.get_tag(element)}>")
      return
    if not isinstance(value, int):
      self.logger.log(
        self.policy.invalid_attribute_type.log_level,
        "Invalid attribute type %r for attribute %s: expected int",
        value,
        name,
      )
      if self.policy.invalid_attribute_type.behavior == "raise":
        raise AttributeSerializationError(f"Invalid attribute type {value!r} for attribute {name!r}")
      return
    else:
      self.backend.set_attr(element, name, str(value))

  def _set_enum_attribute(
    self, element: T_XmlElement, name: str, value: T_Enum | None, enum_type: type[T_Enum], required: bool
  ) -> None:
    if value is None:
      if required:
        self.logger.log(
          self.policy.missing_required_attribute.log_level,
          "Missing required attribute %r on element <%s>",
          name,
          self.backend.get_tag(element),
        )
        if self.policy.missing_required_attribute.behavior == "raise":
          raise AttributeSerializationError(f"Missing required attribute {name!r} for element <{self.backend.get_tag(element)}>")
      return
    if not isinstance(value, enum_type):
      self.logger.log(
        self.policy.invalid_attribute_type.log_level,
        "Invalid attribute type %r for attribute %s: expected %s",
        value,
        name,
        enum_type.__name__,
      )
      if self.policy.invalid_attribute_type.behavior == "raise":
        raise AttributeSerializationError(f"Invalid attribute type {value!r} for attribute {name!r}")
      return
    else:
      self.backend.set_attr(element, name, str(value.value))

  def _set_dt_attribute(self, element: T_XmlElement, name: str, value: datetime | None, required: bool) -> None:
    if value is None:
      if required:
        self.logger.log(
          self.policy.missing_required_attribute.log_level,
          "Missing required attribute %r on element <%s>",
          name,
          self.backend.get_tag(element),
        )
        if self.policy.missing_required_attribute.behavior == "raise":
          raise AttributeSerializationError(f"Missing required attribute {name!r} for element <{self.backend.get_tag(element)}>")
      return
    if not isinstance(value, datetime):
      self.logger.log(
        self.policy.invalid_attribute_type.log_level,
        "Invalid attribute type %r for attribute %s: expected datetime",
        value,
        name,
      )
      if self.policy.invalid_attribute_type.behavior == "raise":
        raise AttributeSerializationError(f"Invalid attribute type {value!r} for attribute {name!r}")
      return
    else:
      self.backend.set_attr(element, name, value.strftime("%Y%m%dT%H%M%SZ"))

  def _set_attribute(self, element: T_XmlElement, name: str, value: str | None, required: bool) -> None:
    if value is None:
      if required:
        self.logger.log(
          self.policy.missing_required_attribute.log_level,
          "Missing required attribute %r on element <%s>",
          name,
          self.backend.get_tag(element),
        )
        if self.policy.missing_required_attribute.behavior == "raise":
          raise AttributeSerializationError(f"Missing required attribute {name!r} for element <{self.backend.get_tag(element)}>")
      return
    if not isinstance(value, str):
      self.logger.log(
        self.policy.invalid_attribute_type.log_level,
        "Invalid attribute type %r for attribute %s: expected str",
        value,
        name,
      )
      if self.policy.invalid_attribute_type.behavior == "raise":
        raise AttributeSerializationError(f"Invalid attribute type {value!r} for attribute {name!r}")
      return
    else:
      self.backend.set_attr(element, name, value)


class InlineContentSerializerMixin[T_XmlElement](SerializerHost[T_XmlElement]):
  __slots__ = tuple()
  ALLOWED: Final[dict[str, tuple[type, ...]]] = {
    "bpt": (Sub,),
    "ept": (Sub,),
    "it": (Sub,),
    "ph": (Sub,),
    "sub": (Bpt, Ept, Ph, It, Hi),
    "hi": (Bpt, Ept, Ph, It, Hi),
    "seg": (Bpt, Ept, Ph, It, Hi),
  }

  def serialize_content_into(self, source: BaseInlineElement | Tuv, target: T_XmlElement) -> None:
    tag = self.backend.get_tag(target)
    allowed = self.ALLOWED.get(tag)
    last_child: T_XmlElement | None = None
    if allowed is None:
      self.logger.log(self.policy.invalid_inline_tag.log_level, "tag <%s> is does not allow inline content", tag)
      if self.policy.invalid_inline_tag.behavior == "raise":
        raise XmlSerializationError(f"tag <{tag}> is does not allow inline content")
      return
    for item in source.content:
      if isinstance(item, str):
        if last_child is None:
          current_text = self.backend.get_text(target) or ""
          self.backend.set_text(target, current_text + item)
        else:
          current_tail = self.backend.get_tail(last_child) or ""
          self.backend.set_tail(last_child, current_tail + item)
      elif not isinstance(item, allowed):
        self.logger.log(
          self.policy.invalid_inline_content.log_level,
          "Incorrect content element: expected %s, got %s",
          allowed,
          type(item).__name__,
        )
        if self.policy.invalid_inline_content.behavior == "raise":
          raise XmlSerializationError(f"Incorrect content element: expected {allowed}, got {type(item).__name__!r}")
        continue
      else:
        child_element = self.emit(item)
        if child_element is not None:
          self.backend.append(target, child_element)
          last_child = child_element
