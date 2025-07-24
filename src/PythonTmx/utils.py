from os import PathLike
from pathlib import Path
from typing import Any, Never

from PythonTmx.errors import ParsingError, SerializationError


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
        f"Unexpected required attribute missing.\ntag: {tag}\nmissing attribute: {extra.get('missing', 'Unknown')}",
        tag,
        error,
        **extra,
      ) from error
    case ValueError():
      raise SerializationError(
        f"Unexpected or missing value encountered.\ntag: {tag}\nIncorrect value: {extra.get('value', 'Unknown')}",
        tag,
        error,
        **extra,
      ) from error
    case TypeError():
      raise SerializationError(
        f"Unexpected data type encountered.\ntag: {tag}\nexpected type: {extra.get('expected', 'Unknown')}\nactual type: {extra.get('actual', 'Unknown')}",
        tag,
        error,
        **extra,
      ) from error
    case _:
      raise SerializationError(
        f"Unknown error:\ntag: {tag}",
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
        f"Error at line {line} parsing <{tag}>:",
        tag,
        line,
        error,
        **extra,
      ) from error
    case _:
      raise ParsingError(
        f"Unknown error at line {line} parsing <{tag}>:",
        tag,
        line,
        error,
        **extra,
      )
