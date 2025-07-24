from os import PathLike
from pathlib import Path
from typing import Any, Never

from PythonTmx.core import AnyXmlElement
from PythonTmx.errors import (
  MalFormedElementError,
  ParsingError,
  SerializationError,
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
        f"tag: {tag!r} - Expected type: {extra.get('expected', 'Unknown')!r}\nactual type: {extra.get('actual', 'Unknown')!r} - Unexpected data type encountered.",
        tag,
        error,
        **extra,
      ) from error
    case _:
      raise SerializationError(
        f"taf: {tag!r} - Unknown error: {error}",
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


def ensure_element_structure(element: object, expected_tag: str) -> None:
  """
  Ensures that the provided element has the expected structure for TMX elements.

  Args:
    element: The element to check.

  Raises:
    SerializationError: If the element does not have any of the expected attributes.
  """
  # Check attribute/method existence
  if not hasattr(element, "tag"):
    raise MalFormedElementError(
      f"Element {element} does not have a tag attribute",
      "tag",
    )
  if not hasattr(element, "attrib"):
    raise MalFormedElementError(
      f"Element {element} does not have an attrib attribute",
      "attrib",
    )
  if not hasattr(element, "text"):
    raise MalFormedElementError(
      f"Element {element} does not have a text attribute",
      "text",
    )
  if not hasattr(element, "tail"):
    raise MalFormedElementError(
      f"Element {element} does not have a tail attribute",
      "tail",
    )
  if not hasattr(element, "__iter__"):
    raise MalFormedElementError(
      f"Element {element} does not have an __iter__ method",
      "__iter__",
    )
  if not hasattr(element, "__len__"):
    raise MalFormedElementError(
      f"Element {element} does not have a __len__ method",
      "__len__",
    )
  # ensure attrib is usable as a read-only mapping
  if not hasattr(getattr(element, "attrib"), "__getitem__"):
    raise MalFormedElementError(
      f"Element {element} attrib attribute does not have a __getitem__ method, cannot use it as a mapping-like object",
      "attrib",
    )
  # ensure attrib is usable as a read-only mapping
  if not hasattr(getattr(element, "attrib"), "get"):
    raise MalFormedElementError(
      f"Element {element} attrib attribute does not have a get method, cannot use it as a mapping-like object",
      "attrib",
    )
  # check expected tag
  tag = getattr(element, "tag")
  if str(tag) != expected_tag:
    raise MalFormedElementError(
      f"Element {element} has a tag attribute with unexpected value {str(tag)}, expected {expected_tag}",
      "tag",
    )


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
