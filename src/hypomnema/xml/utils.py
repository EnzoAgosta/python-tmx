from hypomnema.base.errors import XmlSerializationError, InvalidTagError
from hypomnema.xml.policy import SerializationPolicy, DeserializationPolicy
from codecs import lookup
from collections.abc import Collection
from logging import Logger
from typing import TypeIs, Any
from encodings import normalize_encoding as python_normalize_encoding


def normalize_tag(tag: Any) -> str:
  if isinstance(tag, str):
    return tag.split("}", 1)[1] if "}" in tag else tag
  elif isinstance(tag, (bytes, bytearray)):
    return normalize_tag(tag.decode("utf-8"))
  elif hasattr(tag, "localname"):
    return tag.localname
  elif hasattr(tag, "text"):
    return normalize_tag(tag.text)
  else:
    raise TypeError(f"Unexpected tag type: {type(tag)}")


def normalize_encoding(encoding: str | None) -> str:
  if encoding is None or encoding.lower() == "unicode":
    return "utf-8"
  normalized_encoding = _normalize_encoding(encoding)
  try:
    codec = lookup(normalized_encoding)
    return codec.name
  except LookupError as e:
    raise ValueError(f"Unknown encoding: {normalized_encoding}") from e


def prep_tag_set(tags: str | Collection[str] | None) -> set[str] | None:
  if tags is None:
    return None
  if isinstance(tags, str):
    if not len(tags):
      return None
    tag_set = {normalize_tag(tags)}
  elif isinstance(tags, Collection):
    tag_set = set(normalize_tag(tag) for tag in tags)
  else:
    raise TypeError(f"Unexpected tag type: {type(tags)}")
  return tag_set or None


def assert_object_type[ExpectedType](
  obj: Any, expected_type: type[ExpectedType], *, logger: Logger, policy: SerializationPolicy
) -> TypeIs[ExpectedType]:
  if not isinstance(obj, expected_type):
    logger.log(
      policy.invalid_object_type.log_level,
      "object of type %r is not an instance of %r",
      obj.__class__.__name__,
      expected_type.__name__,
    )
    if policy.invalid_object_type.behavior == "raise":
      raise XmlSerializationError(
        f"object of type {obj.__class__.__name__!r} is not an instance of {expected_type.__name__!r}"
      )
    return False
  return True


def check_tag(tag: str, expected_tag: str, logger: Logger, policy: DeserializationPolicy) -> None:
  if not tag == expected_tag:
    logger.log(
      policy.invalid_tag.log_level, "Incorrect tag: expected %s, got %s", expected_tag, tag
    )
    if policy.invalid_tag.behavior == "raise":
      raise InvalidTagError(f"Incorrect tag: expected {expected_tag}, got {tag}")
