from __future__ import annotations

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
)
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  RequiredAttributeMissingError,
  SerializationError,
  ValidationError,
  WrongTagError,
)
from PythonTmx.utils import (
  check_element_is_usable,
  get_factory,
)

__all__ = ["Note"]


class Note(BaseTmxElement):
  """Represents a note element in a TMX file.

  A note element contains additional information or comments about translation units.
  Notes can be attached to various TMX elements to provide context, instructions,
  or other metadata that doesn't fit into the standard translation structure.
  """

  __slots__ = ("text", "encoding", "lang")
  text: str
  """The text content of the note."""
  encoding: str | None
  """Optional encoding specification for the note text."""
  lang: str | None
  """Optional language specification for the note content."""

  def __init__(
    self,
    text: str,
    encoding: str | None = None,
    lang: str | None = None,
  ) -> None:
    """Initialize a Note element.

    Args:
      text: The note content. Must be a non-empty string.
      encoding: Optional encoding specification (e.g., "UTF-8", "ISO-8859-1").
                If provided, will be serialized as the "o-encoding" attribute.
      lang: Optional language code for the note content (e.g., "en", "fr").
            If provided, will be serialized as the "xml:lang" attribute.

    Raises:
      ValueError: If text is empty or None.
    """
    self.text = text
    self.encoding = encoding
    self.lang = lang

  @classmethod
  def from_xml(cls: type[Note], element: AnyXmlElement) -> Note:
    """Create a Note instance from an XML element.

    This method parses a TMX note element and creates a corresponding Note object.
    The XML element must have the tag "note" and contain text content.

    Args:
      element: The XML element to parse. Must have tag "note" and contain text.

    Returns:
      A new Note instance with the parsed data.

    Raises:
      WrongTagError: If the element tag is not "note".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      ValueError: If the note element has no text content.
      SerializationError: If any other parsing error occurs.
    """
    try:
      check_element_is_usable(element)
      if element.tag != "note":
        raise WrongTagError(element.tag, "note")
      if element.text is None:
        raise ValueError("Note element must have text")
      return cls(
        text=element.text,
        encoding=element.attrib.get("o-encoding"),
        lang=element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang"),
      )
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
      ValueError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[..., R] | None = None) -> R:
    """Convert this Note instance to an XML element.

    Creates an XML element with tag "note" and the appropriate attributes.
    The note text becomes the element's text content.

    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.

    Returns:
      An XML element representing this Note.

    Raises:
      ValidationError: If any attribute has an invalid type.
      MissingDefaultFactoryError: If no factory is available.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("note", self._make_attrib_dict())
      if not isinstance(self.text, str):  # type: ignore
        raise ValidationError("note", str, type(self.text), None)
      element.text = self.text
      return element
    except ValidationError as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Note.

    Builds the attribute dictionary that will be used when serializing
    this Note to XML. Only includes attributes that have non-None values.

    Returns:
      A dictionary mapping attribute names to string values.

    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    attrs: dict[str, str] = {}
    if self.encoding is not None:
      if not isinstance(self.encoding, str):  # type: ignore
        raise ValidationError("encoding", str, type(self.encoding), None)
      attrs["o-encoding"] = self.encoding
    if self.lang is not None:
      if not isinstance(self.lang, str):  # type: ignore
        raise ValidationError("lang", str, type(self.lang), None)
      attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.lang
    return attrs
