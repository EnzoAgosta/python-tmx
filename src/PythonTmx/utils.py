from datetime import datetime
from enum import StrEnum
from os import PathLike
from pathlib import Path
from typing import Any, Literal, Never, TypeVar, cast, overload

from PythonTmx.core import (
  DEFAULT_XML_FACTORY,
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  P,
  R,
)
from PythonTmx.errors import (
  MissingDefaultFactoryError,
  ParsingError,
  SerializationError,
  UnusableElementError,
)


def ensure_file(path: PathLike[str] | Path | str) -> Path:
  path = Path(path).resolve()
  if not path.exists():
    raise FileNotFoundError(f"file {path} doesn't exist")
  if not path.is_file():
    raise IsADirectoryError(f"file {path} is not a file")
  return path


def raise_serialization_errors(
  tag: str,
  error: Exception,
  **extra: Any,
) -> Never:
  """
  Centralized handler for mapping errors during element serialization to a `SerializationError`.

  Args:
    tag: The XML tag being parsed.
    line: The line number in the XML file.
    error: The exception to handle.
    **extra: Optional extra context for error reporting (e.g., missing attribute, value, expected/actual types).

  Raises:
      SerializationError: Always, with a descriptive message and context and raised from the original exception.
  """
  match error:
    case KeyError():
      raise SerializationError(
        f"tag: {tag!r} - missing attribute: {extra.get('missing', 'Unknown')!r} - Unexpected required attribute missing",
        tag,
        error,
        **extra,
      ) from error
    case ValueError():
      raise SerializationError(
        f"tag: {tag!r} - Incorrect value: {extra.get('value', 'Unknown')!r} - Unexpected or missing value encountered.",
        tag,
        error,
        **extra,
      ) from error
    case TypeError():
      raise SerializationError(
        f"tag: {tag!r} - Expected type: {extra.get('expected', 'Unknown')!r} - actual type: {extra.get('actual', 'Unknown')!r} - Unexpected data type encountered.",
        tag,
        error,
        **extra,
      ) from error
    case _:
      raise SerializationError(
        f"tag: {tag!r} - Unknown error: {error}",
        tag,
        error,
        **extra,
      ) from error


def raise_parsing_errors(
  tag: str,
  line: str,
  error: Exception,
  **extra: Any,
) -> Never:
  """
  Centralized handler for mapping errors during element parsing to a `ParsingError`.

  Args:
    tag: The XML tag being parsed.
    line: The line number in the XML file.
    error: The exception to handle.
    **extra: Optional extra context for error reporting (e.g., missing attribute, value, expected/actual types).

  Raises:
      ParsingError: Always, with a descriptive message and context and raised from the original exception.
  """
  match error:
    case SerializationError():
      raise ParsingError(
        f"Tag: {tag!r} - Line: {line!r} - Could not serialize element after parsing",
        tag,
        line,
        error,
        **extra,
      ) from error
    case _:
      raise ParsingError(
        f"Tag: {tag!r} - Line: {line!r} - Unknown error: {error}",
        tag,
        line,
        error,
        **extra,
      )


def _check_attrs_and_methods(element: object) -> None:
  if not hasattr(element, "tag"):
    raise UnusableElementError(
      f"Element {element} does not have a tag attribute",
      missing_field="tag",
    )
  if not hasattr(element, "attrib"):
    raise UnusableElementError(
      f"Element {element} does not have an attrib attribute",
      missing_field="attrib",
    )
  if not hasattr(element, "text"):
    raise UnusableElementError(
      f"Element {element} does not have a text attribute",
      missing_field="text",
    )
  if not hasattr(element, "tail"):
    raise UnusableElementError(
      f"Element {element} does not have a tail attribute",
      missing_field="tail",
    )
  if not hasattr(element, "append"):
    raise UnusableElementError(
      f"Element {element} does not have an append method",
      missing_field="append",
    )
  try:
    iter(element)  # type: ignore # we're intentionally not being safe here
  except TypeError as e:
    raise UnusableElementError(
      f"Element {element} is not iterable",
    ) from e


def _check_attrib_is_mapping_like(element: object) -> None:
  if not hasattr(getattr(element, "attrib"), "__getitem__"):
    raise UnusableElementError(
      f"Element {element} attrib attribute does not have a __getitem__ method, cannot use it as a mapping-like object",
      missing_field="attrib",
    )
  if not hasattr(getattr(element, "attrib"), "get"):
    raise UnusableElementError(
      f"Element {element} attrib attribute does not have a get method, cannot use it as a mapping-like object",
      missing_field="attrib",
    )


def _check_tag_is_expected(element: object, expected_tag: str) -> None:
  tag: str = getattr(element, "tag")
  if str(tag) != expected_tag:
    raise UnusableElementError(
      f"Element {element} has a tag attribute with unexpected value {str(tag)}, expected {expected_tag}",
    )


def ensure_element_structure(element: object, expected_tag: str) -> None:
  """
  Ensures that the provided element has the expected structure for TMX elements.

  Args:
    element: The element to check.

  Raises:
    UnusableElementError: If the element does not have any of the expected attributes.
  """
  _check_attrs_and_methods(element)
  _check_attrib_is_mapping_like(element)
  _check_tag_is_expected(element, expected_tag)


def ensure_required_attributes_are_present(
  element: AnyXmlElement, required_attributes: tuple[str, ...]
) -> None:
  """
  Ensures that the provided element has all the required attributes.

  Args:
    element: The element to check.
    required_attributes: The required attributes to check.

  Raises:
    SerializationError: If the element does not have all of the required attributes.
  """
  for attr in required_attributes:
    try:
      element.attrib[attr]
    except KeyError as e:
      raise SerializationError(
        f"Tag {element.tag!r} - Missing required attribute {attr!r}",
        element.tag,
        e,
      )


def get_factory(
  element: BaseTmxElement,
  factory: AnyElementFactory[P, R] | None,
) -> AnyElementFactory[P, R]:
  _factory = (
    factory
    if factory is not None
    else element.xml_factory
    if element.xml_factory is not None
    else DEFAULT_XML_FACTORY
  )
  if _factory is None:
    raise MissingDefaultFactoryError(
      "No default factory set at any level. Cannot deserialize."
    )
  # @Pyright trust me on this one
  return cast(AnyElementFactory[P, R], _factory)


@overload
def try_parse_datetime(
  value: str | None, required: Literal[True] = True
) -> datetime | str: ...
@overload
def try_parse_datetime(
  value: str | None, required: Literal[False] = False
) -> datetime | str | None: ...
def try_parse_datetime(
  value: str | None, required: bool = False
) -> datetime | str | None:
  if value is None:
    return None
  try:
    return datetime.fromisoformat(value)
  except ValueError:
    return value
  except TypeError as e:
    raise e


ET = TypeVar("ET", bound=StrEnum)


@overload
def try_parse_enum(
  value: str | None, enum: type[ET], required: Literal[True] = True
) -> ET | str: ...
@overload
def try_parse_enum(
  value: str | None, enum: type[ET], required: Literal[False] = False
) -> ET | str: ...
def try_parse_enum(
  value: str | None, enum: type[ET], required: bool = False
) -> ET | str | None:
  if value is None:
    return None
  if not isinstance(value, str):  # type: ignore # defensive check
    raise TypeError(f"value must be a string, got {type(value)}")
  try:
    return enum(value)
  except ValueError:
    return value
