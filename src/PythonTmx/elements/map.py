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


class Map(BaseTmxElement):
  __slots__ = ("unicode", "code", "ent", "subst")
  unicode: str
  code: str | None
  ent: str | None
  subst: str | None

  def __init__(
    self,
    unicode: str,
    code: str | None = None,
    ent: str | None = None,
    subst: str | None = None,
  ) -> None:
    self.unicode = unicode
    self.code = code
    self.ent = ent
    self.subst = subst

  @classmethod
  def from_xml(cls: type[Map], element: AnyXmlElement) -> Map:
    try:
      check_element_is_usable(element)
      if element.tag != "map":
        raise WrongTagError(element.tag, "map")
      if element.text is not None:
        raise ValueError("Map element cannot have text")
      return cls(
        unicode=element.attrib["unicode"],
        code=element.attrib.get("code", None),
        ent=element.attrib.get("ent", None),
        subst=element.attrib.get("subst", None),
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
      return _factory("map", self._make_attrib_dict())
    except ValidationError as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(
    self,
  ) -> dict[str, str]:
    if not isinstance(self.unicode, str):  # type: ignore
      raise ValidationError("unicode", str, type(self.unicode), None)
    attrs: dict[str, str] = {"unicode": self.unicode}
    for k in ("code", "ent", "subst"):
      v = getattr(self, k)
      if v is None:
        continue
      if not isinstance(v, str):  # type: ignore
        raise ValidationError(k, str, type(v), None)
      attrs[k] = v
    return attrs
