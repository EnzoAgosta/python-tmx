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


class Ude(BaseTmxElement, WithChildren[Map]):
  __slots__ = ("name", "base", "_children")
  _children: list[Map]
  name: str
  base: str | None

  def __init__(
    self, name: str, base: str | None = None, maps: list[Map] | None = None
  ) -> None:
    self.name = name
    self.base = base
    self._children = maps if maps is not None else []

  @property
  def maps(self) -> list[Map]:
    return self._children

  @classmethod
  def from_xml(cls: type[Ude], element: AnyXmlElement) -> Ude:
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
    _factory = get_factory(self, factory)
    try:
      element = _factory("ude", self._make_attrib_dict())
      for map in self.maps:
        if not isinstance(map, Map):  # type: ignore
          raise TypeError(
            f"All children of ude element must be of type Map, got {type(map)}"
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
    if not isinstance(self.name, str):  # type: ignore
      raise ValidationError("name", str, type(self.name), None)
    attrs: dict[str, str] = {"name": self.name}
    if self.base is not None:
      if not isinstance(self.base, str):  # type: ignore
        raise ValidationError("base", str, type(self.base), None)
      attrs["base"] = self.base
    return attrs
