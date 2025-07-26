from __future__ import annotations

from dataclasses import dataclass, field
from types import NoneType

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
)
from PythonTmx.errors import ValidationError
from PythonTmx.utils import (
  ensure_element_structure,
  get_factory,
  raise_serialization_errors,
)


@dataclass(slots=True)
class Note(BaseTmxElement):
  text: str = field(metadata={"expected_types": (str,)})
  encoding: str | None = field(
    default=None, metadata={"expected_types": (str, NoneType)}
  )
  lang: str | None = field(
    default=None, metadata={"expected_types": (str, NoneType)}
  )

  @classmethod
  def from_xml(cls: type[Note], element: AnyXmlElement) -> Note:
    ensure_element_structure(element, expected_tag="note")
    if not element.text:
      raise_serialization_errors(element.tag, ValueError(), missing="text")
    try:
      return cls(
        text=element.text,
        encoding=element.attrib.get("o-encoding", None),
        lang=element.attrib.get(
          "{http://www.w3.org/XML/1998/namespace}lang", None
        ),
      )
    except Exception as e:
      raise_serialization_errors(element.tag, e)

  def to_xml(self, factory: AnyElementFactory[..., R] | None = None) -> R:
    _factory = get_factory(self, factory)
    element = _factory("note", self._make_attrib_dict(exclude=("text",)))
    if not isinstance(self.text, str):  # type: ignore # we're being defensive here, ignore redundant isinstance check
      raise ValidationError(
        f"Validation failed - Expected type: str - Actual type: {type(self.text)}",
        "text",
        self.text,
        TypeError(),
      )
    element.text = self.text
    return element
