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


class ArrowConversionError(XmlSerializationError):
  pass


class MissingArrowStructError(ArrowConversionError):
  pass


class IncorrectArrowTypeError(ArrowConversionError):
  pass


class IncorrectArrowContentError(ArrowConversionError):
  pass


class MissingHandlerError(XmlSerializationError):
  pass
