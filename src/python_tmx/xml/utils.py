from __future__ import annotations
from datetime import datetime
import logging
from typing import Any, cast
import xml.etree.ElementTree as ET
import lxml.etree as LET

from python_tmx.base.errors import (
  AttributeValidationError,
  IncorrectTagError,
  UnsupportedBackendError,
)
from python_tmx.base.types import Assoc, Pos, Segtype
from python_tmx.xml import XmlElement


logger = logging.getLogger(__name__)


def _log_incorrect_attribute_warning() -> None:
  logger.debug("Treating value as if it were None and optional.")
  logger.debug("This is not recommended and can lead to the creation of invalid TMX files.")
  logger.debug("Use strict=True to raise an error.")


def set_attribute(
  elem: XmlElement,
  name: str,
  value: str | int | datetime | Pos | Assoc | Segtype | None,
  optional: bool,
  expected: type | tuple[type, ...],
  strict: bool = True,
) -> None:
  err_msg = f"Attribute {name!r} is required but value is None"
  if value is None:
    if not optional:
      if strict:
        raise AttributeValidationError(err_msg)
      logger.warning(err_msg)
      _log_incorrect_attribute_warning()
    return

  err_msg = f"Attribute {name!r} expected {expected}, got {type(value)}"
  if not isinstance(value, expected):
    if strict:
      raise AttributeValidationError(err_msg)
    logger.warning(err_msg)
    _log_incorrect_attribute_warning()
    return
  err_msg = (
    f"Unexpected type: {type(value)}, expected one of str, int, datetime, Pos, Segtype, Assoc. Got: {type(value)}"
  )
  match value:
    case Pos() | Segtype() | Assoc():
      elem.set(name, value.value)
    case str():
      elem.set(name, value)
    case int():
      elem.set(name, str(value))
    case datetime():
      elem.set(name, value.strftime("%Y%m%dT%H%M%SZ"))
    case _:
      if strict:
        raise AttributeValidationError(err_msg)
      logger.warning(err_msg)
      _log_incorrect_attribute_warning()


def set_text(elem: XmlElement, value: Any, *, strict: bool = True) -> None:
  if not isinstance(value, str):
    msg = f"Element text expected 'str', got {type(value).__name__}"
    if strict:
      raise AttributeValidationError(msg)
    logger.warning(msg)
    logger.debug("Treating value as if it were an empty string.")
    logger.debug("This is not recommended and can lead to the creation of invalid TMX files.")
    logger.debug("Use strict=True to raise an error.")
    elem.text = ""
    return
  elem.text = value


def normalize_tag(tag: str | bytes | bytearray | ET.QName | LET.QName) -> str:
  match tag:
    case str():
      return tag.split("}", 1)[1] if "}" in tag else tag
    case bytes() | bytearray():
      return normalize_tag(tag.decode("utf-8"))
    case ET.QName():
      return normalize_tag(tag.text)
    case LET.QName():
      return tag.localname
    case _:
      raise TypeError(f"Unexpected tag type: {type(tag)}")


def check_tag(tag: Any, expected: str, strict: bool) -> None:
  try:
    tag_name = normalize_tag(tag)
  except TypeError as e:
    raise IncorrectTagError(f"Could not normalize tag {tag!r}") from e
  if tag_name == expected:
    return
  if strict:
    raise IncorrectTagError(f"Unexpected tag <{tag_name}>, expected <{expected}>")
  logger.warning(f"Unexpected tag <{tag_name}>, expected <{expected}>")
  logger.debug(f"Treating as if it were <{expected}> and trying to convert it to a dataclass nonetheless.")
  logger.debug("This is not recommended and can lead to unexpected behavior.")
  logger.debug("Use strict=True to raise an error.")


def get_backend(value: type[XmlElement] | None) -> type[XmlElement]:
  if value is None:
    return cast(type[XmlElement], LET.Element)
  elif value is ET.Element:
    return cast(type[XmlElement], ET.Element)
  elif value is LET.Element:
    return cast(type[XmlElement], LET.Element)
  else:
    raise UnsupportedBackendError(
      f"Unsupported XML backend: {value!r}. Only xml.etree.ElementTree.Element and lxml.etree.Element are supported."
    )