from __future__ import annotations

from typing import Type, TypeVar

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  ConvertibleToInt,
  P,
  R,
  WithChildren,
)
from PythonTmx.enums import ASSOC, BPTITTYPE, DATATYPE, PHTYPE, POS, TYPE
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  RequiredAttributeMissingError,
  SerializationError,
  ValidationError,
  WrongTagError,
)
from PythonTmx.utils import check_element_is_usable, get_factory

__all__ = [
  "Bpt",
  "Ept",
  "Hi",
  "It",
  "Ph",
  "Sub",
  "Ut",
]


def _xml_to_inline_sub_only(element: AnyXmlElement) -> list[str | Sub]:
  """Parse XML element content to extract Sub elements and text.
  
  This helper function parses the content of an XML element that can only
  contain Sub elements and text, returning a list of Sub objects and strings.
  
  Args:
    element: The XML element to parse.
  
  Returns:
    A list containing Sub objects and text strings in order of appearance.
  
  Raises:
    WrongTagError: If any child element is not a "sub" tag.
  """
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


def _xml_to_inline(
  element: AnyXmlElement,
) -> list[Ph | Bpt | Ept | It | Hi | Ut | str]:
  """Parse XML element content to extract inline elements and text.
  
  This helper function parses the content of an XML element that can contain
  various inline elements (ph, bpt, ept, it, hi, ut) and text, returning
  a list of inline objects and strings.
  
  Args:
    element: The XML element to parse.
  
  Returns:
    A list containing inline elements and text strings in order of appearance.
  
  Raises:
    ValueError: If any child element has an unexpected tag.
  """
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


T = TypeVar("T", bound=AnyXmlElement)


def inline_tmx_to_xml(
  tmx_obj: Sub | Ph | Bpt | Ept | It | Hi | Ut,
  element: T,
  factory: AnyElementFactory[P, T],
) -> T:
  """Convert inline TMX elements to XML with proper text handling.
  
  This helper function serializes inline TMX elements to XML, handling
  text content, element content, and tail text appropriately.
  
  Args:
    tmx_obj: The inline TMX element to serialize.
    element: The XML element to populate.
    factory: The XML element factory to use.
  
  Returns:
    The populated XML element.
  
  Raises:
    TypeError: If any child element has an unexpected type.
  """
  expected: (
    tuple[Type[Sub], ...]
    | tuple[Type[Ph], Type[Bpt], Type[Ept], Type[It], Type[Hi], Type[Ut]]
  )
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
        f"Unexpected child element in sub element - Expected str, Bpt, Ept, It, Ph, Hi or Ut, got {type(child)!r}",
      )
  return element


class Sub(BaseTmxElement, WithChildren["str | Bpt | Ept | It | Ph | Hi | Ut"]):
  """Represents a substitution element in TMX content.
  
  A substitution element allows for the replacement of text content with
  alternative forms or translations. Sub elements can contain text and
  various inline formatting elements.
  
  Attributes:
    datatype: Optional data type specification for the substitution content.
    type: Optional type specification for the substitution.
    _children: List of text strings and inline elements that form the substitution content.
  """
  __slots__ = ("_children", "datatype", "type")
  _children: list[str | Bpt | Ept | It | Ph | Hi | Ut]
  datatype: str | DATATYPE | None
  type: str | TYPE | None

  def __init__(
    self,
    datatype: str | DATATYPE | None = None,
    type: str | TYPE | None = None,
    children: list[str | Bpt | Ept | It | Ph | Hi | Ut] | None = None,
  ) -> None:
    """Initialize a Sub element.
    
    Args:
      datatype: Optional data type specification. Can be a DATATYPE enum or string.
      type: Optional type specification. Can be a TYPE enum or string.
      children: Optional list of text strings and inline elements. If None, starts empty.
    """
    self._children = children if children is not None else []
    if datatype is not None:
      try:
        self.datatype = DATATYPE(datatype)
      except ValueError:
        self.datatype = datatype
    else:
      self.datatype = DATATYPE.UNKNOWN
    if type is not None:
      try:
        self.type = TYPE(type)
      except ValueError:
        self.type = type
    else:
      self.type = type

  @classmethod
  def from_xml(cls: Type[Sub], element: AnyXmlElement) -> Sub:
    """Create a Sub instance from an XML element.
    
    This method parses a TMX substitution element and creates a corresponding
    Sub object. The XML element must have the tag "sub".
    
    Args:
      element: The XML element to parse. Must have tag "sub".
    
    Returns:
      A new Sub instance with the parsed data.
    
    Raises:
      WrongTagError: If the element tag is not "sub".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      SerializationError: If any other parsing error occurs.
    """
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
    """Convert this Sub instance to an XML element.
    
    Creates an XML element with tag "sub" and the appropriate attributes.
    The content is serialized using the inline_tmx_to_xml helper function.
    
    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.
    
    Returns:
      An XML element representing this Sub.
    
    Raises:
      TypeError: If any child element has an unexpected type.
      ValidationError: If any attribute has an invalid type.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("sub", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Sub.
    
    Builds the attribute dictionary that will be used when serializing
    this Sub to XML. Only includes attributes that have non-None values.
    
    Returns:
      A dictionary mapping attribute names to string values.
    
    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    attrs: dict[str, str] = {}
    if self.type is not None:
      if not isinstance(self.type, (str, TYPE)):  # type: ignore
        raise ValidationError("type", (str, TYPE), type(self.type), None)
      attrs["type"] = self.type.value if isinstance(self.type, TYPE) else self.type
    if self.datatype is not None:
      if not isinstance(self.datatype, (str, DATATYPE)):  # type: ignore
        raise ValidationError("datatype", (str, DATATYPE), type(self.datatype), None)
      attrs["datatype"] = (
        self.datatype.value if isinstance(self.datatype, DATATYPE) else self.datatype
      )
    return attrs


class Ph(BaseTmxElement, WithChildren[Sub | str]):
  """Represents a placeholder element in TMX content.
  
  A placeholder element marks a position in text where content can be
  inserted or substituted. Placeholders are commonly used for variables,
  formatting markers, or other dynamic content.
  
  Attributes:
    x: Optional position identifier for the placeholder.
    assoc: Optional association type (p, f, b).
    type: Optional placeholder type specification.
    _children: List of Sub elements and text that form the placeholder content.
  """
  __slots__ = ("x", "assoc", "type", "_children")
  x: int | None
  assoc: ASSOC | str | None
  type: str | PHTYPE | None
  _children: list[Sub | str]

  def __init__(
    self,
    x: ConvertibleToInt | None = None,
    assoc: ASSOC | str | None = None,
    type: str | PHTYPE | None = None,
    children: list[Sub | str] | None = None,
  ) -> None:
    """Initialize a Ph element.
    
    Args:
      x: Optional position identifier for the placeholder.
      assoc: Optional association type. Can be an ASSOC enum or string.
      type: Optional placeholder type. Can be a PHTYPE enum or string.
      children: Optional list of Sub elements and text. If None, starts empty.
    """
    self.x = int(x) if x is not None else x
    self._children = [child for child in children] if children is not None else []
    try:
      self.assoc = ASSOC(assoc) if assoc is not None else assoc
    except ValueError:
      self.assoc = assoc
    try:
      self.type = PHTYPE(type) if type is not None else type
    except ValueError:
      self.type = type

  @classmethod
  def from_xml(cls: Type[Ph], element: AnyXmlElement) -> Ph:
    """Create a Ph instance from an XML element.
    
    This method parses a TMX placeholder element and creates a corresponding
    Ph object. The XML element must have the tag "ph".
    
    Args:
      element: The XML element to parse. Must have tag "ph".
    
    Returns:
      A new Ph instance with the parsed data.
    
    Raises:
      WrongTagError: If the element tag is not "ph".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      SerializationError: If any other parsing error occurs.
    """
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
    """Convert this Ph instance to an XML element.
    
    Creates an XML element with tag "ph" and the appropriate attributes.
    The content is serialized using the inline_tmx_to_xml helper function.
    
    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.
    
    Returns:
      An XML element representing this Ph.
    
    Raises:
      TypeError: If any child element has an unexpected type.
      ValidationError: If any attribute has an invalid type.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("ph", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Ph.
    
    Builds the attribute dictionary that will be used when serializing
    this Ph to XML. Only includes attributes that have non-None values.
    
    Returns:
      A dictionary mapping attribute names to string values.
    
    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    attrs: dict[str, str] = {}
    if self.type is not None:
      if not isinstance(self.type, (str, PHTYPE)):  # type: ignore
        raise ValidationError("type", (str, PHTYPE), type(self.type), None)
      attrs["type"] = self.type.value if isinstance(self.type, PHTYPE) else self.type
    if self.assoc is not None:
      if not isinstance(self.assoc, (str, ASSOC)):  # type: ignore
        raise ValidationError("assoc", (str, ASSOC), type(self.assoc), None)
      attrs["assoc"] = self.assoc.value if isinstance(self.assoc, ASSOC) else self.assoc
    if self.x is not None:
      if not isinstance(self.x, int):  # type: ignore
        raise ValidationError("x", int, type(self.type), None)
      attrs["x"] = str(self.x)
    return attrs


class Bpt(BaseTmxElement, WithChildren[Sub | str]):
  """Represents a beginning paired tag element in TMX content.
  
  A beginning paired tag marks the start of a paired formatting element.
  It is paired with a corresponding Ept (ending paired tag) element.
  
  Attributes:
    i: The identifier that pairs this tag with its corresponding Ept.
    x: Optional position identifier for the tag.
    type: Optional type specification for the paired tag.
    _children: List of Sub elements and text that form the tag content.
  """
  __slots__ = ("_children", "i", "x", "type")
  _children: list[Sub | str]
  i: int
  x: int | None
  type: str | BPTITTYPE | None

  def __init__(
    self,
    i: ConvertibleToInt,
    x: ConvertibleToInt | None = None,
    type: str | None = None,
    children: list[Sub | str] | None = None,
  ) -> None:
    """Initialize a Bpt element.
    
    Args:
      i: The identifier that pairs this tag with its corresponding Ept.
      x: Optional position identifier for the tag.
      type: Optional type specification. Can be a BPTITTYPE enum or string.
      children: Optional list of Sub elements and text. If None, starts empty.
    """
    self.i = int(i)
    self.x = int(x) if x is not None else x
    self._children = [child for child in children] if children is not None else []
    try:
      self.type = BPTITTYPE(type) if type is not None else type
    except ValueError:
      self.type = type

  @classmethod
  def from_xml(cls: Type[Bpt], element: AnyXmlElement) -> Bpt:
    """Create a Bpt instance from an XML element.
    
    This method parses a TMX beginning paired tag element and creates a
    corresponding Bpt object. The XML element must have the tag "bpt".
    
    Args:
      element: The XML element to parse. Must have tag "bpt".
    
    Returns:
      A new Bpt instance with the parsed data.
    
    Raises:
      WrongTagError: If the element tag is not "bpt".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      SerializationError: If any other parsing error occurs.
    """
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
    """Convert this Bpt instance to an XML element.
    
    Creates an XML element with tag "bpt" and the appropriate attributes.
    The content is serialized using the inline_tmx_to_xml helper function.
    
    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.
    
    Returns:
      An XML element representing this Bpt.
    
    Raises:
      TypeError: If any child element has an unexpected type.
      ValidationError: If any attribute has an invalid type.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("bpt", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Bpt.
    
    Builds the attribute dictionary that will be used when serializing
    this Bpt to XML. Only includes attributes that have non-None values.
    
    Returns:
      A dictionary mapping attribute names to string values.
    
    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    if not isinstance(self.i, int):  # type: ignore
      raise ValidationError("i", int, type(self.i), None)
    attrs: dict[str, str] = {"i": str(self.i)}
    if self.x is not None:
      if not isinstance(self.x, int):  # type: ignore
        raise ValidationError("x", int, type(self.x), None)
      attrs["x"] = str(self.x)
    if self.type is not None:
      if not isinstance(self.type, (str, BPTITTYPE)):  # type: ignore
        raise ValidationError("type", (str, BPTITTYPE), type(self.type), None)
      attrs["type"] = self.type.value if isinstance(self.type, BPTITTYPE) else self.type
    return attrs


class Ept(BaseTmxElement, WithChildren[Sub | str]):
  """Represents an ending paired tag element in TMX content.
  
  An ending paired tag marks the end of a paired formatting element.
  It is paired with a corresponding Bpt (beginning paired tag) element.
  
  Attributes:
    i: The identifier that pairs this tag with its corresponding Bpt.
    _children: List of Sub elements and text that form the tag content.
  """
  __slots__ = ("_children", "i")
  _children: list[Sub | str]
  i: int

  def __init__(
    self,
    i: ConvertibleToInt,
    children: list[Sub | str] | None = None,
  ) -> None:
    """Initialize an Ept element.
    
    Args:
      i: The identifier that pairs this tag with its corresponding Bpt.
      children: Optional list of Sub elements and text. If None, starts empty.
    """
    self.i = int(i)
    self._children = [child for child in children] if children is not None else []

  @classmethod
  def from_xml(cls: Type[Ept], element: AnyXmlElement) -> Ept:
    """Create an Ept instance from an XML element.
    
    This method parses a TMX ending paired tag element and creates a
    corresponding Ept object. The XML element must have the tag "ept".
    
    Args:
      element: The XML element to parse. Must have tag "ept".
    
    Returns:
      A new Ept instance with the parsed data.
    
    Raises:
      WrongTagError: If the element tag is not "ept".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      SerializationError: If any other parsing error occurs.
    """
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
    """Convert this Ept instance to an XML element.
    
    Creates an XML element with tag "ept" and the appropriate attributes.
    The content is serialized using the inline_tmx_to_xml helper function.
    
    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.
    
    Returns:
      An XML element representing this Ept.
    
    Raises:
      TypeError: If any child element has an unexpected type.
      ValidationError: If any attribute has an invalid type.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("ept", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Ept.
    
    Builds the attribute dictionary that will be used when serializing
    this Ept to XML. Only includes attributes that have non-None values.
    
    Returns:
      A dictionary mapping attribute names to string values.
    
    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    if not isinstance(self.i, int):  # type: ignore
      raise ValidationError("i", int, type(self.i), None)
    return {"i": str(self.i)}


class It(BaseTmxElement, WithChildren[Sub | str]):
  """Represents an isolated tag element in TMX content.
  
  An isolated tag represents a standalone formatting element that doesn't
  require a paired closing tag. It can contain text and Sub elements.
  
  Attributes:
    pos: The position of the isolated tag (begin or end).
    x: Optional position identifier for the tag.
    type: Optional type specification for the isolated tag.
    _children: List of Sub elements and text that form the tag content.
  """
  __slots__ = ("_children", "pos", "x", "type")
  _children: list[Sub | str]
  pos: POS | str
  x: int | None
  type: str | BPTITTYPE | None

  def __init__(
    self,
    pos: POS | str,
    x: ConvertibleToInt | None = None,
    type: str | None = None,
    children: list[Sub | str] | None = None,
  ) -> None:
    """Initialize an It element.
    
    Args:
      pos: The position of the isolated tag. Can be a POS enum or string.
      x: Optional position identifier for the tag.
      type: Optional type specification. Can be a BPTITTYPE enum or string.
      children: Optional list of Sub elements and text. If None, starts empty.
    """
    self.x = int(x) if x is not None else x
    self._children = [child for child in children] if children is not None else []
    try:
      self.pos = POS(pos)
    except ValueError:
      self.pos = pos
    try:
      self.type = BPTITTYPE(type) if type is not None else type
    except ValueError:
      self.type = type

  @classmethod
  def from_xml(cls: Type[It], element: AnyXmlElement) -> It:
    """Create an It instance from an XML element.
    
    This method parses a TMX isolated tag element and creates a corresponding
    It object. The XML element must have the tag "it".
    
    Args:
      element: The XML element to parse. Must have tag "it".
    
    Returns:
      A new It instance with the parsed data.
    
    Raises:
      WrongTagError: If the element tag is not "it".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      SerializationError: If any other parsing error occurs.
    """
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
    """Convert this It instance to an XML element.
    
    Creates an XML element with tag "it" and the appropriate attributes.
    The content is serialized using the inline_tmx_to_xml helper function.
    
    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.
    
    Returns:
      An XML element representing this It.
    
    Raises:
      TypeError: If any child element has an unexpected type.
      ValidationError: If any attribute has an invalid type.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("it", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this It.
    
    Builds the attribute dictionary that will be used when serializing
    this It to XML. Only includes attributes that have non-None values.
    
    Returns:
      A dictionary mapping attribute names to string values.
    
    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    if not isinstance(self.pos, (POS, str)):  # type: ignore
      raise ValidationError("pos", POS, type(self.pos), None)
    attrs: dict[str, str] = {
      "pos": self.pos.value if isinstance(self.pos, POS) else self.pos
    }
    if self.x is not None:
      if not isinstance(self.x, int):  # type: ignore
        raise ValidationError("x", int, type(self.x), None)
      attrs["x"] = str(self.x)
    if self.type is not None:
      if not isinstance(self.type, (str, BPTITTYPE)):  # type: ignore
        raise ValidationError("type", (str, BPTITTYPE), type(self.type), None)
      attrs["type"] = self.type.value if isinstance(self.type, BPTITTYPE) else self.type
    return attrs


class Ut(BaseTmxElement, WithChildren[Sub | str]):
  """Represents an unpaired tag element in TMX content.
  
  An unpaired tag represents a standalone formatting element that doesn't
  require a paired closing tag. It can contain text and Sub elements.
  
  Attributes:
    x: Optional position identifier for the tag.
    _children: List of Sub elements and text that form the tag content.
  """
  __slots__ = ("_children", "x")
  _children: list[Sub | str]
  x: int | None

  def __init__(
    self,
    x: ConvertibleToInt | None,
    children: list[Sub | str] | None = None,
  ) -> None:
    """Initialize a Ut element.
    
    Args:
      x: Optional position identifier for the tag.
      children: Optional list of Sub elements and text. If None, starts empty.
    """
    self.x = int(x) if x is not None else x
    self._children = [child for child in children] if children is not None else []

  @classmethod
  def from_xml(cls: Type[Ut], element: AnyXmlElement) -> Ut:
    """Create a Ut instance from an XML element.
    
    This method parses a TMX unpaired tag element and creates a corresponding
    Ut object. The XML element must have the tag "ut".
    
    Args:
      element: The XML element to parse. Must have tag "ut".
    
    Returns:
      A new Ut instance with the parsed data.
    
    Raises:
      WrongTagError: If the element tag is not "ut".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      SerializationError: If any other parsing error occurs.
    """
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
    """Convert this Ut instance to an XML element.
    
    Creates an XML element with tag "ut" and the appropriate attributes.
    The content is serialized using the inline_tmx_to_xml helper function.
    
    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.
    
    Returns:
      An XML element representing this Ut.
    
    Raises:
      TypeError: If any child element has an unexpected type.
      ValidationError: If any attribute has an invalid type.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("ut", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Ut.
    
    Builds the attribute dictionary that will be used when serializing
    this Ut to XML. Only includes attributes that have non-None values.
    
    Returns:
      A dictionary mapping attribute names to string values.
    
    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    if self.x is not None:
      if not isinstance(self.x, int):  # type: ignore
        raise ValidationError("x", int, type(self.x), None)
      return {"x": str(self.x)}
    else:
      return {}


class Hi(BaseTmxElement, WithChildren["Bpt | Ept | It | Ph | Hi | Ut | str"]):
  """Represents a highlighting element in TMX content.
  
  A highlighting element marks text that should be highlighted or emphasized
  in some way. It can contain text and various inline formatting elements.
  
  Attributes:
    x: Optional position identifier for the highlighting.
    type: Optional type specification for the highlighting.
    _children: List of inline elements and text that form the highlighted content.
  """
  __slots__ = ("_children", "x", "type")
  _children: list[Bpt | Ept | It | Ph | Hi | Ut | str]
  x: int | None
  type: str | TYPE | None

  def __init__(
    self,
    x: ConvertibleToInt | None = None,
    type: str | None = None,
    children: list[Bpt | Ept | It | Ph | Hi | Ut | str] | None = None,
  ) -> None:
    """Initialize a Hi element.
    
    Args:
      x: Optional position identifier for the highlighting.
      type: Optional type specification. Can be a TYPE enum or string.
      children: Optional list of inline elements and text. If None, starts empty.
    """
    self.x = int(x) if x is not None else x
    self._children = [child for child in children] if children is not None else []
    try:
      self.type = TYPE(type) if type is not None else type
    except ValueError:
      self.type = type

  @classmethod
  def from_xml(cls: Type[Hi], element: AnyXmlElement) -> Hi:
    """Create a Hi instance from an XML element.
    
    This method parses a TMX highlighting element and creates a corresponding
    Hi object. The XML element must have the tag "hi".
    
    Args:
      element: The XML element to parse. Must have tag "hi".
    
    Returns:
      A new Hi instance with the parsed data.
    
    Raises:
      WrongTagError: If the element tag is not "hi".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      SerializationError: If any other parsing error occurs.
    """
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
    """Convert this Hi instance to an XML element.
    
    Creates an XML element with tag "hi" and the appropriate attributes.
    The content is serialized using the inline_tmx_to_xml helper function.
    
    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.
    
    Returns:
      An XML element representing this Hi.
    
    Raises:
      TypeError: If any child element has an unexpected type.
      ValidationError: If any attribute has an invalid type.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("hi", self._make_attrib_dict())
      element = inline_tmx_to_xml(self, element, _factory)
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Hi.
    
    Builds the attribute dictionary that will be used when serializing
    this Hi to XML. Only includes attributes that have non-None values.
    
    Returns:
      A dictionary mapping attribute names to string values.
    
    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    attrs: dict[str, str] = {}
    if self.x is not None:
      if not isinstance(self.x, int):  # type: ignore
        raise ValidationError("x", int, type(self.x), None)
      attrs["x"] = str(self.x)
    if self.type is not None:
      if not isinstance(self.type, (str, TYPE)):  # type: ignore
        raise ValidationError("type", (str, TYPE), type(self.type), None)
      attrs["type"] = self.type.value if isinstance(self.type, TYPE) else self.type
    return attrs
