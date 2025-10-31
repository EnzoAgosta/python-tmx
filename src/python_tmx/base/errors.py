class ConversionError(Exception):
  pass


class AttributeValidationError(ConversionError):
  pass


class XmlConversionError(Exception):
  pass


class UnsupportedBackendError(XmlConversionError):
  pass


class IncorrectTagError(XmlConversionError):
  pass


class IncorrectContentError(XmlConversionError):
  pass


class ArrowConversionError(ConversionError):
  pass


class MissingArrowStructError(ArrowConversionError):
  pass


class IncorrectArrowTypeError(ArrowConversionError):
  pass


class IncorrectArrowContentError(ArrowConversionError):
  pass
