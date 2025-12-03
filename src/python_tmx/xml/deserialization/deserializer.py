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
  """
  The main orchestrator for converting XML TMX documents into Python objects.

  This class acts as a facade and dispatcher. It does not parse XML logic itself;
  instead, it inspects the tag of the incoming element and delegates processing
  to a registered `BaseElementDeserializer` handler.

  Attributes:
      backend (XMLBackend): The adapter interface for the underlying XML parser.
      policy (DeserializationPolicy): Configuration controlling strictness and error recovery.
      logger (Logger): The logging channel.
      handlers (dict): A map of tag names (str) to handler instances.
  """

  def __init__(
    self,
    backend: XMLBackend,
    policy: DeserializationPolicy | None = None,
    logger: Logger | None = None,
    handlers: dict[str, BaseElementDeserializer[T_XmlElement]] | None = None,
  ):
    """
    Initializes the Deserializer.

    Args:
        backend (XMLBackend): The backend instance (e.g., LxmlBackend).
        policy (DeserializationPolicy | None): Custom policy options. Defaults to a standard policy.
        logger (Logger | None): Custom logger. Defaults to module logger.
        handlers (dict | None): Custom handler map. If None, default handlers for
            TMX 1.4b (tu, tuv, header, etc.) are loaded.
    """
    self.backend = backend
    self.policy = policy or DeserializationPolicy()
    self.logger = logger or _ModuleLogger
    if handlers is None:
      self.logger.info("Using default handlers")
      handlers = self._get_default_handlers()
    else:
      self.logger.debug("Using custom handlers")
    self.handlers = handlers

    for handler in self.handlers.values():
      if handler._emit is None:
        handler._set_emit(self.deserialize)

  def _get_default_handlers(self) -> dict[str, BaseElementDeserializer[T_XmlElement]]:
    """Returns the standard set of handlers for TMX 1.4b compliance."""
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
    """
    Orchestrates the deserialization of an XML element.

    This method identifies the element's tag and delegates to the appropriate handler.

    Policy Impact (`policy.missing_handler`):
        - `raise`: Raises `MissingHandlerError` if no handler exists for the tag.
        - `ignore`: Returns `None`.
        - `default`: Attempts to fallback to standard TMX handlers if a custom handler dict is incomplete.

    Args:
        element (T_XmlElement): The root or child element to deserialize.

    Returns:
        BaseElement | None: The resulting Python object, or None if skipped/ignored.

    Raises:
        MissingHandlerError: If an unknown tag is encountered and policy is 'raise'.
    """
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
        self.logger.log(
          self.policy.missing_handler.log_level,
          "Falling back to default handler for <%s>",
          tag,
        )
        handler = self._get_default_handlers().get(tag)
        if handler is None:
          raise MissingHandlerError(f"Missing handler for <{tag}>") from None
    return handler._deserialize(element)
