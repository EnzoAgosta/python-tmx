from __future__ import annotations

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
  WithChildren,
)
from PythonTmx.elements.header import Header
from PythonTmx.elements.tu import Tu
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

__all__ = ["Tmx"]


class Tmx(BaseTmxElement, WithChildren[Tu]):
  __slots__ = ("header", "_children")
  header: Header
  _children: list[Tu]

  def __init__(
    self,
    header: Header,
    tus: list[Tu] | None = None,
  ) -> None:
    self.header = header
    self._children = [tu for tu in tus] if tus is not None else []

  @classmethod
  def from_xml(cls: type[Tmx], element: AnyXmlElement) -> Tmx:
    try:
      check_element_is_usable(element)
      if element.tag != "tmx":
        raise WrongTagError(element.tag, "tmx")
      if element.text is not None:
        raise ValueError("Tmx element cannot have text")
      header: Header | None = None
      tus: list[Tu] | None = None
      for child in element:
        if child.tag == "header":
          if header is not None:
            raise WrongTagError(child.tag, "header") from ValueError("Multiple headers")
          header = Header.from_xml(child)
        elif child.tag == "body":
          if tus is not None:  # type: ignore
            raise WrongTagError(child.tag, "body") from ValueError("Multiple bodies")
          tus = []
          for tu in child:
            if not tu.tag == "tu":
              raise WrongTagError(tu.tag, "tu")
            tus.append(Tu.from_xml(tu))
        else:
          raise WrongTagError(child.tag, "header or body")
      if header is None:
        raise ValueError("Missing header")
      if tus is None:  # type: ignore
        raise ValueError("Missing body")
      return cls(header, tus)
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
      element = _factory("tmx", self._make_attrib_dict())
      if not isinstance(self.header, Header):  # type: ignore
        raise TypeError(
          f"Unexpected child element in tmx element - Expected Header, got {type(self.header)!r}",
        )
      element.append(self.header.to_xml(factory=factory))
      body = _factory("body", {})
      for child in self:
        if not isinstance(child, Tu):  # type: ignore
          raise TypeError(
            f"Unexpected child element in tmx element - Expected Tu, got {type(child)!r}",
          )
        body.append(child.to_xml(factory=factory))
      element.append(body)
      return element
    except ValidationError as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    return {"version": "1.4"}
