from logging import Logger, getLogger
from python_tmx.base.errors import MissingHandlerError
from python_tmx.base.types import BaseElement
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import (
  BptDeserializer,
  EptDeserializer,
  HeaderDeserializer,
  HiDeserializer,
  ItDeserializer,
  NoteDeserializer,
  PhDeserializer,
  PropDeserializer,
  SubDeserializer,
  TmxDeserializer,
  TuDeserializer,
  TuvDeserializer,
)
from python_tmx.xml.deserialization.base import BaseElementDeserializer
from python_tmx.xml.policy import DeserializationPolicy

_ModuleLogger = getLogger(__name__)

__all__ = ["Deserializer"]


class Deserializer[T_XmlElement]:
  def __init__(
    self,
    backend: XMLBackend,
    policy: DeserializationPolicy | None = None,
    logger: Logger | None = None,
    handlers: dict[str, BaseElementDeserializer[T_XmlElement]] | None = None,
  ):
    self.backend = backend
    self.policy = policy or DeserializationPolicy()
    self.logger = logger or _ModuleLogger
    self.handlers = handlers or self._get_default_handlers()

    for handler in self.handlers.values():
      if handler._emit is None:
        handler._set_emit(self.deserialize)

  def _get_default_handlers(self) -> dict[str, BaseElementDeserializer[T_XmlElement]]:
    self.logger.info("using default handlers")
    return {
      "note": NoteDeserializer(self.backend, self.policy, self.logger),
      "prop": PropDeserializer(self.backend, self.policy, self.logger),
      "header": HeaderDeserializer(self.backend, self.policy, self.logger),
      "tu": TuDeserializer(self.backend, self.policy, self.logger),
      "tuv": TuvDeserializer(self.backend, self.policy, self.logger),
      "bpt": BptDeserializer(self.backend, self.policy, self.logger),
      "ept": EptDeserializer(self.backend, self.policy, self.logger),
      "it": ItDeserializer(self.backend, self.policy, self.logger),
      "ph": PhDeserializer(self.backend, self.policy, self.logger),
      "sub": SubDeserializer(self.backend, self.policy, self.logger),
      "hi": HiDeserializer(self.backend, self.policy, self.logger),
      "tmx": TmxDeserializer(self.backend, self.policy, self.logger),
    }

  def deserialize(self, element: T_XmlElement) -> BaseElement | None:
    tag = self.backend.get_tag(element)
    self.logger.debug("Deserializing <%s>", tag)
    handler = self.handlers.get(tag)
    if handler is None:
      self.logger.log(self.policy.missing_handler.log_level, "Missing handler for <%s>", tag)
      if self.policy.missing_handler.behavior == "raise":
        raise MissingHandlerError(f"Missing handler for <{tag}>") from None
      elif self.policy.missing_handler.behavior == "ignore":
        return None
      else:
        handler = self._get_default_handlers().get(tag)
        if handler is None:
          raise MissingHandlerError(f"Missing handler for <{tag}>") from None
    return handler._deserialize(element)
