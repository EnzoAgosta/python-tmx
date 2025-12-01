from logging import Logger, getLogger

from python_tmx.base.errors import MissingHandlerError
from python_tmx.base.types import (
  BaseElement,
  Bpt,
  Ept,
  Header,
  Hi,
  It,
  Note,
  Ph,
  Prop,
  Sub,
  Tmx,
  Tu,
  Tuv,
)
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
    backend: XMLBackend,
    policy: SerializationPolicy | None = None,
    logger: Logger | None = None,
    handlers: dict[type[BaseElement], BaseElementSerializer[T_XmlElement]] | None = None,
  ):
    self.backend = backend
    self.policy = policy or SerializationPolicy()
    self.logger = logger or _ModuleLogger
    self.handlers = handlers or self._get_default_handlers()

    for handler in self.handlers.values():
      if handler._emit is None:
        handler._set_emit(self.serialize)

  def _get_default_handlers(self) -> dict[type[BaseElement], BaseElementSerializer[T_XmlElement]]:
    self.logger.info("using default handlers")
    return {
      Note: NoteSerializer(self.backend, self.policy, self.logger),
      Prop: PropSerializer(self.backend, self.policy, self.logger),
      Header: HeaderSerializer(self.backend, self.policy, self.logger),
      Tu: TuSerializer(self.backend, self.policy, self.logger),
      Tuv: TuvSerializer(self.backend, self.policy, self.logger),
      Bpt: BptSerializer(self.backend, self.policy, self.logger),
      Ept: EptSerializer(self.backend, self.policy, self.logger),
      It: ItSerializer(self.backend, self.policy, self.logger),
      Ph: PhSerializer(self.backend, self.policy, self.logger),
      Sub: SubSerializer(self.backend, self.policy, self.logger),
      Hi: HiSerializer(self.backend, self.policy, self.logger),
      Tmx: TmxSerializer(self.backend, self.policy, self.logger),
    }

  def serialize(self, element: BaseElement) -> T_XmlElement | None:
    self.logger.debug("Serializing object %s", type(element).__name__)
    handler = self.handlers.get(type(element))
    if handler is None:
      self.logger.log(
        self.policy.missing_handler.log_level, "Missing handler for %s", type(element).__name__
      )
      if self.policy.missing_handler.behavior == "raise":
        raise MissingHandlerError(f"No serializer found for type {type(element).__name__}")
      elif self.policy.missing_handler.behavior == "ignore":
        return None
      else:
        handler = self._get_default_handlers().get(type(element))
        if handler is None:
          raise MissingHandlerError(f"No serializer found for type {type(element).__name__}")
    return handler._serialize(element)
