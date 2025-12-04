__all__ = [
  "XmlSerializationError",
  "XmlDeserializationError",
  "AttributeSerializationError",
  "AttributeDeserializationError",
  "InvalidTagError",
  "InvalidContentError",
  "MissingHandlerError",
]


class XmlSerializationError(Exception):
  pass


class XmlDeserializationError(Exception):
  pass


class AttributeSerializationError(XmlSerializationError):
  pass


class AttributeDeserializationError(XmlDeserializationError):
  pass


class InvalidTagError(XmlDeserializationError):
  pass


class InvalidContentError(Exception):
  pass


class MissingHandlerError(XmlSerializationError):
  pass
