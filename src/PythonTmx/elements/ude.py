from __future__ import annotations

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
  WithChildren,
)
from PythonTmx.elements.map import Map
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

__all__ = ["Ude"]


class Ude(BaseTmxElement, WithChildren[Map]):
  """Represents a user-defined entity (ude) element in a TMX file.

  A user-defined entity element contains custom character mapping rules that
  define how specific characters or character sequences should be handled
  during translation processing. Ude elements group related map elements
  together under a common name and optional base reference.

  User-defined entities are useful for handling domain-specific characters,
  proprietary symbols, or custom encoding requirements that aren't covered
  by standard TMX character handling.
  """

  __slots__ = ("name", "base", "_children")
  _children: list[Map]
  name: str
  """The name identifier for this user-defined entity."""
  base: str | None
  """Optional base entity reference for inheritance or extension."""

  def __init__(
    self, name: str, base: str | None = None, maps: list[Map] | None = None
  ) -> None:
    """Initialize a Ude element.

    Args:
      name: The name identifier for this user-defined entity. This name
            is used to reference the entity in TMX processing.
      base: Optional base entity reference. If provided, this ude inherits
            or extends from another entity definition.
      maps: Optional list of Map elements that define the character mappings
            for this entity. If None, starts with an empty list.
    """
    self.name = name
    self.base = base
    self._children = maps if maps is not None else []

  @property
  def maps(self) -> list[Map]:
    """Get the list of Map elements in this user-defined entity.

    Returns:
      A list of Map elements that define the character mappings for this entity.
    """
    return self._children

  @classmethod
  def from_xml(cls: type[Ude], element: AnyXmlElement) -> Ude:
    """Create a Ude instance from an XML element.

    This method parses a TMX user-defined entity element and creates a
    corresponding Ude object. The XML element must have the tag "ude" and
    cannot contain text content.

    Args:
      element: The XML element to parse. Must have tag "ude" and no text content.

    Returns:
      A new Ude instance with the parsed data.

    Raises:
      WrongTagError: If the element tag is not "ude".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      ValueError: If the ude element has text content.
      SerializationError: If any other parsing error occurs.
    """
    try:
      check_element_is_usable(element)
      if element.tag != "ude":
        raise WrongTagError(element.tag, "ude")
      if element.text is not None:
        raise ValueError("Ude element cannot have text")
      return cls(
        name=element.attrib["name"],
        base=element.attrib.get("base", None),
        maps=[Map.from_xml(map) for map in element],
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
    """Convert this Ude instance to an XML element.

    Creates an XML element with tag "ude" and the appropriate attributes.
    All child Map elements are serialized and appended to the ude element.

    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.

    Returns:
      An XML element representing this Ude.

    Raises:
      TypeError: If any child element is not a Map instance.
      ValueError: If a map has a code attribute but base is None.
      ValidationError: If any attribute has an invalid type.
      MissingDefaultFactoryError: If no factory is available.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("ude", self._make_attrib_dict())
      for map in self.maps:
        if not isinstance(map, Map):  # type: ignore
          raise TypeError(
            f"All children of ude element must be of type Map, got {type(map)!r}"
          )
        if map.code is not None:
          if self.base is None:
            raise ValueError(
              "Cannot export a ude element if at least one of its map elements has a code attribute"
            )
        element.append(map.to_xml(factory=factory))
    except (TypeError, ValueError, ValidationError) as e:
      raise DeserializationError(self, e) from e
    return element

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Ude.

    Builds the attribute dictionary that will be used when serializing
    this Ude to XML. Only includes attributes that have non-None values.

    Returns:
      A dictionary mapping attribute names to string values.

    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    if not isinstance(self.name, str):  # type: ignore
      raise ValidationError("name", str, type(self.name), None)
    attrs: dict[str, str] = {"name": self.name}
    if self.base is not None:
      if not isinstance(self.base, str):  # type: ignore
        raise ValidationError("base", str, type(self.base), None)
      attrs["base"] = self.base
    return attrs
