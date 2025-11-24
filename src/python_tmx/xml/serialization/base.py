from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import Any, Generic, final
from python_tmx.base.errors import AttributeValidationError, InvalidContentError
from python_tmx.base.types import Assoc, BaseElement, Pos, Segtype
from python_tmx.xml import XmlElement
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.serialization.logger import SerializationLogger
from python_tmx.xml.serialization.policy import SerializationPolicy


class BaseSerializer(Generic[XmlElement], ABC):
  def __init__(
    self,
    backend: XMLBackend[XmlElement],
    policy: SerializationPolicy,
    logger: SerializationLogger,
    /,
  ):
    self.backend: XMLBackend[XmlElement] = backend
    self.policy = policy
    self.logger = logger
    self._emit: Callable[[BaseElement], XmlElement | None] | None = None

  def _set_emit(self, emit: Callable[[BaseElement], XmlElement | None]) -> None:
    self._emit = emit

  def emit(self, obj: BaseElement) -> XmlElement | None:
    assert self._emit is not None, "emit() called before set_emit() was called"
    return self._emit(obj)

  @abstractmethod
  def serialize(self, obj: BaseElement) -> XmlElement | None: ...

  @final
  def _set_attribute(
    self, element: Any, attr_name: str, attr_value: Any, expected_type: type | tuple[type, ...], optional: bool
  ) -> None:
    self.logger.debug_action(f"Setting attribute {attr_name!r}={attr_value!r} on element <{element.tag}>")
    if attr_value is None:
      if not optional:
        self.logger.log_missing_attr(attr_name)
        if self.policy.required_attribute_missing == "raise":
          raise AttributeValidationError(f"Missing value for required attribute {attr_name!r}")
      return
    if not isinstance(attr_value, expected_type):
      self.logger.log_invalid_attribute_type(attr_name, repr(expected_type), attr_value)
      if self.policy.invalid_attribute_type == "raise":
        raise AttributeValidationError(
          f"Invalid value type for attribute {attr_name!r}: expected {expected_type!r}, got {attr_value!r}"
        )
      if self.policy.invalid_attribute_type == "ignore":
        return
      if self.policy.invalid_attribute_type == "coerce":
        self.logger.debug_action(f"Coercing attribute {attr_value!r} to a string")
        attr_value = str(attr_value)
    match attr_value:
      case Pos() | Segtype() | Assoc():
        self.backend.set_attr(element, attr_name, attr_value.value)
      case str():
        self.backend.set_attr(element, attr_name, attr_value)
      case int():
        self.backend.set_attr(element, attr_name, str(attr_value))
      case datetime():
        self.backend.set_attr(element, attr_name, attr_value.strftime("%Y%m%dT%H%M%SZ"))
      case _:
        raise AssertionError("unreachable: unexpected attr_value branch")

  @final
  def _set_text(self, element: Any, value: str) -> None:
    tag = getattr(element, "tag", type(element).__name__)
    self.logger.debug_action("Setting text %r on element <%s>", value, tag)
    if isinstance(value, str):
      self.backend.set_text(element, value)
      return
    self.logger.log_invalid_attribute_type("text", "str", value)
    match self.policy.invalid_content:
      case "raise":
        raise InvalidContentError(f"Invalid value for 'text': expected 'str', got {type(value).__name__!r}")
      case "coerce":
        self.logger.debug_action("Coercing text %r to string", value)
        self.backend.set_text(element, str(value))
        return
      case "empty":
        self.backend.set_text(element, "")
        return
      case  _:
        return
