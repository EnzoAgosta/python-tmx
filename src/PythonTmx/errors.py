from typing import Any

from PythonTmx.core import BaseTmxElement

__all__ = [
  "XmlParsingError",
  "WrongTagError",
  "SerializationError",
  "DeserializationError",
  "RequiredAttributeMissingError",
  "NotMappingLikeError",
  "ValidationError",
  "MissingDefaultFactoryError",
]


class XmlParsingError(Exception):
  tag: str
  line: int | None
  original_exception: Exception | None

  def __init__(
    self,
    tag: str,
    line: int | None = None,
    original_exception: Exception | None = None,
  ) -> None:
    self.tag = tag
    self.line = line
    self.original_exception = original_exception
    msg = f"Cannot parse Xml Element - Tag: {tag!r}"
    if line is not None:
      msg += f" - Line: {line!r}"
    if original_exception is not None:
      msg += f" - Caused by: {original_exception!r}"
    super().__init__(msg)


class WrongTagError(Exception):
  tag: str
  expected_tag: str

  def __init__(self, tag: str, expected_tag: str) -> None:
    self.tag = tag
    self.expected_tag = expected_tag
    msg = f"Wrong tag: {tag!r}. Expected: {expected_tag!r}"
    super().__init__(msg)


class SerializationError(Exception):
  tmx_element: type[BaseTmxElement]
  original_exception: Exception | None

  def __init__(
    self,
    tmx_element: type[BaseTmxElement],
    original_exception: Exception | None = None,
  ) -> None:
    self.tmx_element = tmx_element
    self.original_exception = original_exception
    msg = f"Cannot serialize Xml Element to Tmx Element - Element: {self.tmx_element!r}"
    if self.original_exception is not None:
      msg += f" - Caused by: {original_exception!r}"
    super().__init__(msg)


class DeserializationError(Exception):
  tmx_element: BaseTmxElement
  original_exception: Exception | None

  def __init__(
    self,
    tmx_element: BaseTmxElement,
    original_exception: Exception | None = None,
  ) -> None:
    self.tmx_element = tmx_element
    self.original_exception = original_exception
    msg = (
      f"Cannot deserialize Tmx Element to Xml Element - Element: {self.tmx_element!r}"
    )
    if self.original_exception is not None:
      msg += f" - Caused by: {original_exception!r}"
    super().__init__(msg)


class RequiredAttributeMissingError(Exception):
  missing_field: str
  original_exception: Exception | None

  def __init__(
    self, missing_field: str, original_exception: Exception | None = None
  ) -> None:
    self.missing_field = missing_field
    self.original_exception = original_exception
    msg = f"Unexpected required attribute missing - Missing field: {missing_field!r}"
    if original_exception is not None:
      msg += f" - Caused by: {original_exception!r}"
    super().__init__(msg)


class NotMappingLikeError(Exception):
  mapping: object
  original_exception: Exception | None

  def __init__(
    self, mapping: object, original_exception: Exception | None = None
  ) -> None:
    self.mapping = mapping
    self.original_exception = original_exception
    msg = f"{mapping!r} is not usable as Mapping"
    if original_exception is not None:
      msg += f" - Caused by: {original_exception!r}"
    super().__init__(msg)


class ValidationError(Exception):
  field: str
  expected: Any
  actual: Any
  original_exception: Exception | None

  def __init__(
    self,
    field: str,
    expected: Any,
    actual: Any,
    original_exception: Exception | None = None,
  ):
    self.field = field
    self.actual = actual
    self.expected = expected
    self.original_exception = original_exception
    msg = (
      f"Validation failed! - Field: {self.field!r} "
      + f"- Expected: {self.expected!r} -  "
      + f"Actual: {self.actual!r}"
    )
    if original_exception is not None:
      msg += f" - Caused by: {self.original_exception!r}"
    super().__init__(msg)


class MissingDefaultFactoryError(Exception):
  element: BaseTmxElement
  original_exception: Exception | None

  def __init__(
    self, element: BaseTmxElement, original_exception: Exception | None = None
  ) -> None:
    self.element = element
    self.original_exception = original_exception
    msg = f"Missing default factory for element {element!r}"
    if original_exception is not None:
      msg += f" - Caused by: {original_exception!r}"
    super().__init__(msg)
