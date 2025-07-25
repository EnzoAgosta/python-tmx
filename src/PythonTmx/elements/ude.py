from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass, field

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
)
from PythonTmx.elements.map import Map
from PythonTmx.errors import SerializationError
from PythonTmx.utils import (
  ensure_element_structure,
  ensure_required_attributes_are_present,
  get_factory,
  raise_serialization_errors,
)


@dataclass(slots=True)
class Ude(BaseTmxElement):
  name: str
  base: str | None = None
  _children: list[Map] = field(default_factory=list)

  @property
  def maps(self) -> list[Map]:
    return self._children

  def __iter__(self) -> Generator[Map, None, None]:
    yield from self._children

  def __len__(self) -> int:
    return len(self._children)

  @classmethod
  def from_xml(cls: type[Ude], element: AnyXmlElement) -> Ude:
    ensure_element_structure(element, expected_tag="ude")
    if element.text:
      raise SerializationError(
        f"Unexpected text in ude element: {element.text!r}",
        "ude",
        Exception(),
      )
    ensure_required_attributes_are_present(element, ("name",))
    try:
      return cls(
        name=element.attrib["name"],
        base=element.attrib.get("base", None),
        _children=[Map.from_xml(map) for map in element],
      )
    except Exception as e:
      raise_serialization_errors(element.tag, e)

  def to_xml(self, factory: AnyElementFactory[..., R] | None = None) -> R:
    _factory = get_factory(self, factory)
    element = _factory("ude", self._make_attrib_dict(("_children",)))
    for map in self._children:
      element.append(map.to_xml())
    return element
