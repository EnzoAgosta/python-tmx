from __future__ import annotations

from dataclasses import dataclass

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  P,
  R,
)
from PythonTmx.utils import (
  ensure_element_structure,
  get_factory,
  raise_serialization_errors,
)


@dataclass(slots=True)
class Note(BaseTmxElement):
  value: str
  encoding: str | None = None
  lang: str | None = None

  @classmethod
  def from_xml(cls: type[Note], element: AnyXmlElement) -> Note:
    ensure_element_structure(element, expected_tag="note")
    if not element.text:
      raise_serialization_errors(element.tag, ValueError(), missing="text")
    try:
      return cls(
        value=element.text,
        encoding=element.attrib.get("encoding", None),
        lang=element.attrib.get(
          "{http://www.w3.org/XML/1998/namespace}lang", None
        ),
      )
    except Exception as e:
      raise_serialization_errors(element.tag, e)

  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R:
    _factory = get_factory(self, factory)
    element = _factory(
      "note",
      self._make_attrib_dict(),
    )
    element.text = self.value
    return element
