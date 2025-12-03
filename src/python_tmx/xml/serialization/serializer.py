from collections.abc import Mapping
from logging import Logger, getLogger

from python_tmx.base.errors import MissingHandlerError
from python_tmx.base.types import (
  BaseElement,
)
from python_tmx.xml import T_XmlElement
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.policy import SerializationPolicy
from python_tmx.xml.serialization._handlers import (
  BptSerializer,
  EptSerializer,
  HeaderSerializer,
  HiSerializer,
  ItSerializer,
  NoteSerializer,
  PhSerializer,
  PropSerializer,
  SubSerializer,
  TmxSerializer,
  TuSerializer,
  TuvSerializer,
)
from python_tmx.xml.serialization.base import BaseElementSerializer


_ModuleLogger = getLogger(__name__)

__all__ = ["Serializer"]


class Serializer[T_XmlElement]:
  def __init__(
    self,
    backend: XMLBackend[T_XmlElement],
    policy: SerializationPolicy | None = None,
    logger: Logger | None = None,
    handlers: Mapping[str, BaseElementSerializer[T_XmlElement]] | None = None,
  ):
    self.backend = backend
    self.policy = policy or SerializationPolicy()
    self.logger = logger or _ModuleLogger
    if handlers is None:
      self.logger.info("Using default handlers")
      handlers = self._get_default_handlers()
    else:
      self.logger.debug("Using custom handlers")
    self.handlers = handlers

    for handler in self.handlers.values():
      if handler._emit is None:
        handler._set_emit(self.serialize)

  def _get_default_handlers(self) -> dict[str, BaseElementSerializer[T_XmlElement]]:
    return {
      "Note": NoteSerializer(self.backend, self.policy, self.logger),
      "Prop": PropSerializer(self.backend, self.policy, self.logger),
      "Header": HeaderSerializer(self.backend, self.policy, self.logger),
      "Tu": TuSerializer(self.backend, self.policy, self.logger),
      "Tuv": TuvSerializer(self.backend, self.policy, self.logger),
      "Bpt": BptSerializer(self.backend, self.policy, self.logger),
      "Ept": EptSerializer(self.backend, self.policy, self.logger),
      "It": ItSerializer(self.backend, self.policy, self.logger),
      "Ph": PhSerializer(self.backend, self.policy, self.logger),
      "Sub": SubSerializer(self.backend, self.policy, self.logger),
      "Hi": HiSerializer(self.backend, self.policy, self.logger),
      "Tmx": TmxSerializer(self.backend, self.policy, self.logger),
    }

  def serialize(self, obj: BaseElement) -> T_XmlElement | None:
    obj_type = obj.__class__.__name__
    self.logger.debug("Serializing %s", obj_type)
    handler = self.handlers.get(obj_type)
    if handler is None:
      self.logger.log(self.policy.missing_handler.log_level, "Missing handler for %s", obj_type)
      if self.policy.missing_handler.behavior == "raise":
        raise MissingHandlerError(f"Missing handler for {obj_type}") from None
      elif self.policy.missing_handler.behavior == "ignore":
        return None
      else:
        self.logger.log(self.policy.missing_handler.log_level, "Falling back to default handler for %s", obj_type)
        handler = self._get_default_handlers().get(obj_type)
        if handler is None:
          raise MissingHandlerError(f"Missing handler for {obj_type}") from None
    return handler._serialize(obj)
