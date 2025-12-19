from hypomnema.base.errors import XmlSerializationError, InvalidTagError
from hypomnema.xml.policy import SerializationPolicy, DeserializationPolicy
from codecs import lookup
from collections.abc import Collection
from logging import Logger
from typing import TypeIs, Any
from encodings import normalize_encoding as python_normalize_encoding


def normalize_tag(tag: Any) -> str:
  """
  Extract the local name from an XML tag, removing namespaces or extracting from objects.

  Parameters
  ----------
  tag : Any
      The tag to normalize. Can be a string (Clark notation or plain), bytes,
      a lxml or Standard Library QName object, or an object with either a
      `localname` or `text` attribute.

  Returns
  -------
  str
      The local name of the tag.

  Raises
  ------
  TypeError
      If the tag type is not supported.
  """
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
  """
  Validate and normalize an encoding name to its standard codec name.

  Parameters
  ----------
  encoding : str | None
      The encoding string to normalize. If None or "unicode", defaults to "utf-8".

  Returns
  -------
  str
      The canonical codec name.

  Raises
  ------
  ValueError
      If the encoding is not recognized by the Python codec registry.
  """
  if encoding is None or encoding.lower() == "unicode":
    return "utf-8"
  normalized_encoding = python_normalize_encoding(encoding)
  try:
    codec = lookup(normalized_encoding)
    return codec.name
  except LookupError as e:
    raise ValueError(f"Unknown encoding: {normalized_encoding}") from e


def prep_tag_set[TagName: str | bytes](
  tags: TagName | Collection[TagName] | None,
) -> set[str] | None:
  """
  Normalize a single tag or a collection of tags into a unique set.

  Parameters
  ----------
  tags : str | Collection[str] | None
      Input tag or tags to process.

  Returns
  -------
  set[str] | None
      A set of normalized local names, or None if the input was None or empty.

  Raises
  ------
  TypeError
      If the input type is not a string, collection, or None.
  """
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
  """
  Verify that an object matches the expected type according to the serialization policy.

  Parameters
  ----------
  obj : Any
      The object instance to verify.
  expected_type : type[ExpectedType]
      The type class that the object is expected to be an instance of.
  logger : Logger
      The logger instance used to report policy violations.
  policy : SerializationPolicy
      The policy determining the logging level and whether to raise an exception.

  Returns
  -------
  TypeIs[ExpectedType]
      True if the object is an instance of expected_type, False otherwise.

  Raises
  ------
  XmlSerializationError
      If the object type is incorrect and policy.invalid_object_type.behavior is "raise".
  """
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
  """
  Validate that an XML element's tag matches the expected TMX element name.

  Parameters
  ----------
  element : BackendElementType
      The XML element to validate.
  expected_tag : str
      The tag name expected by the caller (e.g., "tu", "tuv").
  backend : XMLBackend[BackendElementType]
      The XML library wrapper used to extract the tag name.
  logger : Logger
      The logger instance used to report tag mismatches.
  policy : DeserializationPolicy
      The policy determining the logging level and whether to raise an exception.

  Raises
  ------
  InvalidTagError
      If the element's tag does not match `expected_tag` and
      `policy.invalid_tag.behavior` is "raise".
  """
  if not tag == expected_tag:
    logger.log(
      policy.invalid_tag.log_level, "Incorrect tag: expected %s, got %s", expected_tag, tag
    )
    if policy.invalid_tag.behavior == "raise":
      raise InvalidTagError(f"Incorrect tag: expected {expected_tag}, got {tag}")
