from __future__ import annotations

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  ConvertibleToInt,
  P,
  R,
  WithChildren,
)
from PythonTmx.enums import ASSOC, POS
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  RequiredAttributeMissingError,
  SerializationError,
  ValidationError,
  WrongTagError,
)
from PythonTmx.utils import check_element_is_usable, get_factory


def _xml_to_inline_sub_only(element: AnyXmlElement) -> list[str | Sub]:
  result: list[str | Sub] = []
  if element.text is not None:
    result.append(element.text)
  for child in element:
    if child.tag != "sub":
      raise WrongTagError(child.tag, "sub")
    result.append(Sub.from_xml(child))
    if child.tail is not None:
      result.append(child.tail)
  return result


def _xml_to_inline(element: AnyXmlElement) -> list[Ph | Bpt | Ept | It | Hi | Ut | str]:
  result: list[Ph | Bpt | Ept | It | Hi | Ut | str] = []
  if element.text is not None:
    result.append(element.text)
  for child in element:
    match child.tag:
      case "ph":
        result.append(Ph.from_xml(child))
      case "bpt":
        result.append(Bpt.from_xml(child))
      case "ept":
        result.append(Ept.from_xml(child))
      case "it":
        result.append(It.from_xml(child))
      case "hi":
        result.append(Hi.from_xml(child))
      case "ut":
        result.append(Ut.from_xml(child))
      case _:
        raise ValueError(f"Unexpected tag {child.tag!r}")
    if child.tail is not None:
      result.append(child.tail)
  return result


def inline_tmx_to_xml(
  tmx_obj: Sub | Ph | Bpt | Ept | It | Hi | Ut,
  element: R,
  factory: AnyElementFactory[P, R],
) -> R:
  if isinstance(tmx_obj, (Sub, Hi)):
    expected = (Ph, Bpt, Ept, It, Hi, Ut)
  else:
    expected = (Sub,)
  current = element
  for child in tmx_obj:
    if isinstance(child, str):
      if current.text is None:
        current.text = child
      elif current is element:
        current.text += child
      else:
        current.tail = child
    elif isinstance(child, expected):  # type: ignore
      current = child.to_xml(factory=factory)
      element.append(current)
    else:
      raise TypeError(
        f"Unexpected child element in sub element - Expected str, Bpt, Ept, It, Ph, Hi or Ut, got {type(child)}",
      )
  return element


class Sub(BaseTmxElement, WithChildren["str | Bpt | Ept | It | Ph | Hi | Ut"]):
  __slots__ = ("_children", "datatype", "type")
  _children: list[str | Bpt | Ept | It | Ph | Hi | Ut]
  datatype: str | None
  type: str | None

  def __init__(
    self,
    datatype: str | None = None,
    type: str | None = None,
    children: list[str | Bpt | Ept | It | Ph | Hi | Ut] | None = None,
  ) -> None:
    self.datatype = datatype
    self.type = type
    self._children = children if children is not None else []

  @classmethod
  def from_xml(cls: type[Sub], element: AnyXmlElement) -> Sub:
    try:
      check_element_is_usable(element)
      if element.tag != "sub":
        raise WrongTagError(element.tag, "sub")
      return cls(
        datatype=element.attrib.get("datatype", None),
        type=element.attrib.get("type", None),
        children=_xml_to_inline(element),
      )
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R:
    _factory = get_factory(self, factory)
    try:
      element = _factory("sub", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    attrs: dict[str, str] = {}
    if self.type is not None:
      if not isinstance(self.type, str):  # type: ignore
        raise ValidationError("type", str, type(self.type), None)
      attrs["type"] = self.type
    if self.datatype is not None:
      if not isinstance(self.datatype, str):  # type: ignore
        raise ValidationError("datatype", str, type(self.datatype), None)
      attrs["datatype"] = self.datatype
    return attrs


class Ph(BaseTmxElement, WithChildren[Sub | str]):
  __slots__ = ("x", "assoc", "type", "_children")
  x: int | None
  assoc: ASSOC | None
  type: str | None
  _children: list[Sub | str]

  def __init__(
    self,
    x: ConvertibleToInt | None = None,
    assoc: ASSOC | str | None = None,
    type: str | None = None,
    children: list[Sub | str] | None = None,
  ) -> None:
    self.type = type
    self.assoc = ASSOC(assoc) if assoc is not None else assoc
    self.x = int(x) if x is not None else x
    self._children = [child for child in children] if children is not None else []

  @classmethod
  def from_xml(cls: type[Ph], element: AnyXmlElement) -> Ph:
    try:
      check_element_is_usable(element)
      if element.tag != "ph":
        raise WrongTagError(element.tag, "ph")
      return cls(
        x=element.attrib["x"],
        assoc=element.attrib.get("assoc", None),
        type=element.attrib.get("type", None),
        children=_xml_to_inline_sub_only(element),
      )
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R:
    _factory = get_factory(self, factory)
    try:
      element = _factory("ph", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    attrs: dict[str, str] = {}
    if self.x is not None:
      if not isinstance(self.x, int):  # type: ignore
        raise ValidationError("x", int, type(self.x), None)
      attrs["x"] = str(self.x)
    if self.assoc is not None:
      if not isinstance(self.assoc, ASSOC):  # type: ignore
        raise ValidationError("assoc", ASSOC, type(self.assoc), None)
      attrs["assoc"] = self.assoc.value
    if self.type is not None:
      if not isinstance(self.type, str):  # type: ignore
        raise ValidationError("type", str, type(self.type), None)
      attrs["type"] = self.type
    return attrs


class Bpt(BaseTmxElement, WithChildren[Sub | str]):
  __slots__ = ("_children", "i", "x", "type")
  _children: list[Sub | str]
  i: int
  x: int | None
  type: str | None

  def __init__(
    self,
    i: ConvertibleToInt,
    x: ConvertibleToInt | None = None,
    type: str | None = None,
    children: list[Sub | str] | None = None,
  ) -> None:
    self.i = int(i)
    self.x = int(x) if x is not None else x
    self.type = type
    self._children = [child for child in children] if children is not None else []

  @classmethod
  def from_xml(cls: type[Bpt], element: AnyXmlElement) -> Bpt:
    try:
      check_element_is_usable(element)
      if element.tag != "bpt":
        raise WrongTagError(element.tag, "bpt")
      return cls(
        i=element.attrib["i"],
        x=element.attrib.get("x", None),
        type=element.attrib.get("type", None),
        children=_xml_to_inline_sub_only(element),
      )
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R:
    _factory = get_factory(self, factory)
    try:
      element = _factory("bpt", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    if not isinstance(self.i, int):  # type: ignore
      raise ValidationError("i", int, type(self.i), None)
    attrs: dict[str, str] = {"i": str(self.i)}
    if self.x is not None:
      if not isinstance(self.x, int):  # type: ignore
        raise ValidationError("x", int, type(self.x), None)
      attrs["x"] = str(self.x)
    if self.type is not None:
      if not isinstance(self.type, str):  # type: ignore
        raise ValidationError("type", str, type(self.type), None)
      attrs["type"] = self.type
    return attrs


class Ept(BaseTmxElement, WithChildren[Sub | str]):
  __slots__ = ("_children", "i")
  _children: list[Sub | str]
  i: int

  def __init__(
    self,
    i: ConvertibleToInt,
    children: list[Sub | str] | None = None,
  ) -> None:
    self.i = int(i)
    self._children = [child for child in children] if children is not None else []

  @classmethod
  def from_xml(cls: type[Ept], element: AnyXmlElement) -> Ept:
    try:
      check_element_is_usable(element)
      if element.tag != "ept":
        raise WrongTagError(element.tag, "ept")
      return cls(
        i=element.attrib["i"],
        children=_xml_to_inline_sub_only(element),
      )
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R:
    _factory = get_factory(self, factory)
    try:
      element = _factory("ept", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    if not isinstance(self.i, int):  # type: ignore
      raise ValidationError("i", int, type(self.i), None)
    return {"i": str(self.i)}


class It(BaseTmxElement, WithChildren[Sub | str]):
  __slots__ = ("_children", "pos", "x", "type")
  _children: list[Sub | str]
  pos: POS
  x: int | None
  type: str | None

  def __init__(
    self,
    pos: POS | str,
    x: ConvertibleToInt | None = None,
    type: str | None = None,
    children: list[Sub | str] | None = None,
  ) -> None:
    self.pos = POS(pos)
    self.x = int(x) if x is not None else x
    self.type = type
    self._children = [child for child in children] if children is not None else []

  @classmethod
  def from_xml(cls: type[It], element: AnyXmlElement) -> It:
    try:
      check_element_is_usable(element)
      if element.tag != "it":
        raise WrongTagError(element.tag, "it")
      return cls(
        pos=element.attrib["pos"],
        x=element.attrib.get("x", None),
        type=element.attrib.get("type", None),
        children=_xml_to_inline_sub_only(element),
      )
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R:
    _factory = get_factory(self, factory)
    try:
      element = _factory("it", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    if not isinstance(self.pos, POS):  # type: ignore
      raise ValidationError("pos", POS, type(self.pos), None)
    attrs: dict[str, str] = {"pos": self.pos.value}
    if self.x is not None:
      if not isinstance(self.x, int):  # type: ignore
        raise ValidationError("x", int, type(self.x), None)
      attrs["x"] = str(self.x)
    if self.type is not None:
      if not isinstance(self.type, str):  # type: ignore
        raise ValidationError("type", str, type(self.type), None)
      attrs["type"] = self.type
    return attrs


class Ut(BaseTmxElement, WithChildren[Sub | str]):
  __slots__ = ("_children", "x")
  _children: list[Sub | str]
  x: int | None

  def __init__(
    self,
    x: ConvertibleToInt | None,
    children: list[Sub | str] | None = None,
  ) -> None:
    self.x = int(x) if x is not None else x
    self._children = [child for child in children] if children is not None else []

  @classmethod
  def from_xml(cls: type[Ut], element: AnyXmlElement) -> Ut:
    try:
      check_element_is_usable(element)
      if element.tag != "ut":
        raise WrongTagError(element.tag, "ut")
      return cls(
        x=element.attrib.get("x"),
        children=_xml_to_inline_sub_only(element),
      )
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R:
    _factory = get_factory(self, factory)
    try:
      element = _factory("ut", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    if self.x is not None:
      if not isinstance(self.x, int):  # type: ignore
        raise ValidationError("x", int, type(self.x), None)
      return {"x": str(self.x)}
    else:
      return {}


class Hi(BaseTmxElement, WithChildren["Bpt | Ept | It | Ph | Hi | Ut | str"]):
  __slots__ = ("_children", "x", "type")
  _children: list[Bpt | Ept | It | Ph | Hi | Ut | str]
  x: int | None
  type: str | None

  def __init__(
    self,
    x: ConvertibleToInt | None = None,
    type: str | None = None,
    children: list[Bpt | Ept | It | Ph | Hi | Ut | str] | None = None,
  ) -> None:
    self.x = int(x) if x is not None else x
    self.type = type
    self._children = [child for child in children] if children is not None else []

  @classmethod
  def from_xml(cls: type[Hi], element: AnyXmlElement) -> Hi:
    try:
      check_element_is_usable(element)
      if element.tag != "hi":
        raise WrongTagError(element.tag, "hi")
      return cls(
        x=element.attrib.get("x", None),
        type=element.attrib.get("type", None),
        children=_xml_to_inline(element),
      )
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R:
    _factory = get_factory(self, factory)
    try:
      element = _factory("hi", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    attrs: dict[str, str] = {}
    if self.x is not None:
      if not isinstance(self.x, int):  # type: ignore
        raise ValidationError("x", int, type(self.x), None)
      attrs["x"] = str(self.x)
    if self.type is not None:
      if not isinstance(self.type, str):  # type: ignore
        raise ValidationError("type", str, type(self.type), None)
      attrs["type"] = self.type
    return attrs
