from __future__ import annotations
from typing import Generic, Type

from python_tmx.base.errors import MissingHandlerError, XmlSerializationError
from python_tmx.base.types import BaseElement, Bpt, Ept, Header, Hi, It, Note, Ph, Prop, Sub, Tmx, Tu, Tuv
from python_tmx.xml import XmlElement
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.serialization.base import BaseElementSerializer
from python_tmx.xml.serialization.logger import SerializationLogger
from python_tmx.xml.serialization._handlers import (
  BptSerializer,
  EptSerializer,
  HeaderSerializer,
  HiSerializer,
  InlineComposer,
  ItSerializer,
  NoteSerializer,
  PhSerializer,
  PropSerializer,
  SubSerializer,
  TmxSerializer,
  TuSerializer,
  TuvSerializer,
)
from python_tmx.xml.serialization.policy import SerializationPolicy


class Serializer(Generic[XmlElement]):
  def __init__(
    self,
    backend: XMLBackend[XmlElement],
    policy: SerializationPolicy,
    *,
    logger: SerializationLogger | None = None,
    handlers: dict[Type[BaseElement], BaseElementSerializer[XmlElement]] | None = None,
    inline_composer: InlineComposer[XmlElement] | None = None,
  ):
    self.backend: XMLBackend[XmlElement] = backend
    self.policy = policy
    self.logger = logger or SerializationLogger(policy)
    self.composer: InlineComposer[XmlElement] = inline_composer or InlineComposer(
      self.backend, self.policy, self.logger, self.serialize
    )
    self.handlers: dict[Type[BaseElement], BaseElementSerializer[XmlElement]] = handlers or self._get_default_handlers()
    for handler in self.handlers.values():
      if handler._emit is None:
        handler._set_emit(self.serialize)

  def _get_default_handlers(self) -> dict[Type[BaseElement], BaseElementSerializer[XmlElement]]:
    self.logger.debug_action("Using default handlers")
    return {
      Note: NoteSerializer(self.backend, self.policy, self.logger),
      Prop: PropSerializer(self.backend, self.policy, self.logger),
      Header: HeaderSerializer(self.backend, self.policy, self.logger),
      Tmx: TmxSerializer(self.backend, self.policy, self.logger),
      Tu: TuSerializer(self.backend, self.policy, self.logger),
      Tuv: TuvSerializer(self.composer, self.backend, self.policy, self.logger),
      Bpt: BptSerializer(self.backend, self.policy, self.logger),
      Ept: EptSerializer(self.backend, self.policy, self.logger),
      It: ItSerializer(self.backend, self.policy, self.logger),
      Ph: PhSerializer(self.backend, self.policy, self.logger),
      Sub: SubSerializer(self.backend, self.policy, self.logger),
      Hi: HiSerializer(self.backend, self.policy, self.logger),
    }

  def serialize(self, obj: BaseElement) -> XmlElement | None:
    self.logger.debug_action("Serializing %s", type(obj).__name__)
    handler = self.handlers.get(type(obj))
    if handler is None:
      self.logger.log_missing_handler(type(obj).__name__)
      if self.policy.missing_handler == "default":
        handler = self._get_default_handlers().get(type(obj))
      if handler is None:
        raise MissingHandlerError(f"Missing handler for {type(obj).__name__!r}")

    elem = handler.serialize(obj)
    if elem is None:
      if self.policy.invalid_element == "ignore":
        return None
      raise XmlSerializationError(f"Handler returned None for {type(obj).__name__!r}")
    return elem
