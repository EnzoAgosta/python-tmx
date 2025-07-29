from datetime import datetime
from typing import Literal, TypeGuard, cast, overload

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
  NotMappingLikeError,
  RequiredAttributeMissingError,
)


def check_element_is_usable(element: object) -> TypeGuard[AnyXmlElement]:
  for attr in ("tag", "attrib", "text", "tail"):
    if not hasattr(element, attr):
      raise RequiredAttributeMissingError(attr)
  if not hasattr(getattr(element, "attrib"), "__getitem__"):
    raise NotMappingLikeError(
      getattr(element, "attrib"),
      RequiredAttributeMissingError("attrib.__getitem__"),
    )
  if not hasattr(getattr(element, "attrib"), "get"):
    raise NotMappingLikeError(
      getattr(element, "attrib"),
      RequiredAttributeMissingError("attrib.get"),
    )
  return True


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
    raise MissingDefaultFactoryError(element)
  # @type checkers trust me on this one
  return cast(AnyElementFactory[P, R], _factory)


@overload
def try_parse_datetime(
  value: str | datetime | None, required: Literal[True]
) -> datetime: ...
@overload
def try_parse_datetime(
  value: str | datetime | None, required: Literal[False]
) -> datetime | None: ...
def try_parse_datetime(value: str | datetime | None, required: bool) -> datetime | None:
  if isinstance(value, datetime):
    return value
  if value is None:
    if required:
      raise ValueError("Missing required datetime value")
    return None
  try:
    return datetime.fromisoformat(value)
  except Exception as e:
    if required:
      raise e
    return None
