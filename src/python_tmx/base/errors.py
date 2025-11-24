class XmlSerializationError(Exception):
  pass


class AttributeValidationError(Exception):
  pass


class UnsupportedBackendError(Exception):
  pass


class IncorrectTagError(Exception):
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
