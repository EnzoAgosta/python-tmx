from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
  WithChildren,
)
from PythonTmx.elements.note import Note
from PythonTmx.elements.prop import Prop
from PythonTmx.elements.ude import Ude
from PythonTmx.enums import DATATYPE, SEGTYPE
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
  try_parse_datetime,
)

__all__ = ["Header"]


class Header(BaseTmxElement, WithChildren[Note | Prop | Ude]):
  """Represents a header element in a TMX file.

  A header element contains metadata and configuration information about the TMX file
  and the translation process. The header provides essential information such as
  the creation tool, language settings, data type, and segment type that apply
  to the entire translation memory.

  Headers can contain optional child elements including notes, properties, and
  user-defined entities that provide additional context or configuration.

  Attributes:
    creationtool: The name of the tool that created the TMX file.
    creationtoolversion: The version of the creation tool.
    segtype: The type of segmentation used (sentence, paragraph, etc.).
    tmf: The translation memory format identifier.
    adminlang: The administrative language code.
    srclang: The source language code.
    datatype: The data type of the content (plaintext, html, etc.).
    encoding: Optional encoding specification for the content.
    creationdate: Optional timestamp when the TMX was created.
    creationid: Optional identifier for the creator.
    changedate: Optional timestamp when the TMX was last modified.
    changeid: Optional identifier for the last modifier.
    _children: List of Note, Prop, or Ude child elements.
  """

  __slots__ = (
    "creationtool",
    "creationtoolversion",
    "segtype",
    "tmf",
    "adminlang",
    "srclang",
    "datatype",
    "encoding",
    "creationdate",
    "creationid",
    "changedate",
    "changeid",
    "_children",
  )
  creationtool: str
  creationtoolversion: str
  segtype: SEGTYPE
  tmf: str
  adminlang: str
  srclang: str
  datatype: str | DATATYPE
  encoding: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  changeid: str | None
  _children: list[Note | Prop | Ude]

  def __init__(
    self,
    creationtool: str,
    creationtoolversion: str,
    segtype: SEGTYPE | str,
    tmf: str,
    adminlang: str,
    srclang: str,
    datatype: str | DATATYPE,
    encoding: str | None = None,
    creationdate: str | datetime | None = None,
    creationid: str | None = None,
    changedate: str | datetime | None = None,
    changeid: str | None = None,
    children: Sequence[Note | Prop | Ude] | None = None,
  ) -> None:
    """Initialize a Header element.

    Args:
      creationtool: The name of the tool that created the TMX file.
      creationtoolversion: The version of the creation tool.
      segtype: The type of segmentation used. Can be a SEGTYPE enum or string.
      tmf: The translation memory format identifier.
      adminlang: The administrative language code (e.g., "en", "fr").
      srclang: The source language code (e.g., "en", "fr").
      datatype: The data type of the content. Can be a DATATYPE enum or string.
      encoding: Optional encoding specification (e.g., "UTF-8", "ISO-8859-1").
      creationdate: Optional creation timestamp. Can be string or datetime.
      creationid: Optional identifier for the creator.
      changedate: Optional modification timestamp. Can be string or datetime.
      changeid: Optional identifier for the last modifier.
      children: Optional sequence of Note, Prop, or Ude child elements.
    """
    self.creationtool = creationtool
    self.creationtoolversion = creationtoolversion
    self.tmf = tmf
    self.adminlang = adminlang
    self.srclang = srclang
    self.encoding = encoding
    self.creationid = creationid
    self.creationdate = try_parse_datetime(creationdate, False)
    self.changeid = changeid
    self.changedate = try_parse_datetime(changedate, False)
    self._children = [child for child in children] if children is not None else []
    self.segtype = SEGTYPE(segtype)
    try:
      self.datatype = DATATYPE(datatype)
    except ValueError:
      self.datatype = datatype

  @property
  def notes(self) -> list[Note]:
    """Get the list of Note elements in this header.

    Returns:
      A list of Note elements that provide additional information about the TMX.
    """
    return [note for note in self._children if isinstance(note, Note)]

  @property
  def props(self) -> list[Prop]:
    """Get the list of Prop elements in this header.

    Returns:
      A list of Prop elements that provide metadata about the TMX.
    """
    return [prop for prop in self._children if isinstance(prop, Prop)]

  @property
  def udes(self) -> list[Ude]:
    """Get the list of Ude elements in this header.

    Returns:
      A list of Ude elements that define custom character mappings.
    """
    return [ude for ude in self._children if isinstance(ude, Ude)]

  @classmethod
  def from_xml(cls: type[Header], element: AnyXmlElement) -> Header:
    """Create a Header instance from an XML element.

    This method parses a TMX header element and creates a corresponding Header object.
    The XML element must have the tag "header" and cannot contain text content.

    Args:
      element: The XML element to parse. Must have tag "header" and no text content.

    Returns:
      A new Header instance with the parsed data.

    Raises:
      WrongTagError: If the element tag is not "header".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      ValueError: If the header element has text content or multiple headers/bodies.
      SerializationError: If any other parsing error occurs.
    """

    def _dispatch(child: AnyXmlElement) -> Note | Prop | Ude:
      if child.tag == "ude":
        return Ude.from_xml(child)
      elif child.tag == "note":
        return Note.from_xml(child)
      elif child.tag == "prop":
        return Prop.from_xml(child)
      else:
        raise WrongTagError(child.tag, "ude, note or prop")

    try:
      check_element_is_usable(element)
      if element.tag != "header":
        raise WrongTagError(element.tag, "header")
      if element.text is not None:
        raise ValueError("Header element cannot have text")

      header: Header = cls(
        creationtool=element.attrib["creationtool"],
        creationtoolversion=element.attrib["creationtoolversion"],
        segtype=SEGTYPE(element.attrib["segtype"]),
        tmf=element.attrib["o-tmf"],
        adminlang=element.attrib["adminlang"],
        srclang=element.attrib["srclang"],
        datatype=element.attrib["datatype"],
        encoding=element.attrib.get("o-encoding", None),
        creationdate=element.attrib.get("creationdate", None),
        creationid=element.attrib.get("creationid", None),
        changedate=element.attrib.get("changedate", None),
        changeid=element.attrib.get("changeid", None),
        children=[_dispatch(child) for child in element],
      )
      try:
        header.datatype = DATATYPE(header.datatype)
      except ValueError:
        pass
      return header
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
    """Convert this Header instance to an XML element.

    Creates an XML element with tag "header" and the appropriate attributes.
    All child elements (notes, props, udes) are serialized and appended.

    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.

    Returns:
      An XML element representing this Header.

    Raises:
      TypeError: If any child element is not a Note, Prop, or Ude instance.
      ValidationError: If any attribute has an invalid type.
      MissingDefaultFactoryError: If no factory is available.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("header", self._make_attrib_dict())
      for child in self:
        if not isinstance(child, Note | Prop | Ude):  # type: ignore
          raise TypeError(
            f"Unexpected child element in header element - Expected Ude, Note or Prop, got {type(child)!r}",
          )
        element.append(child.to_xml(factory=factory))
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  # Defensive coding, lots of type: ignore to shut up type checkers
  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Header.

    Builds the attribute dictionary that will be used when serializing
    this Header to XML. Only includes attributes that have non-None values.

    Returns:
      A dictionary mapping attribute names to string values.

    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    if not isinstance(self.creationtool, str):  # type: ignore
      raise ValidationError("creationtool", str, type(self.creationtool), None)
    if not isinstance(self.creationtoolversion, str):  # type: ignore
      raise ValidationError(
        "creationtoolversion", str, type(self.creationtoolversion), None
      )
    if not isinstance(self.segtype, SEGTYPE):  # type: ignore
      raise ValidationError("segtype", SEGTYPE, type(self.segtype), None)
    if not isinstance(self.tmf, str):  # type: ignore
      raise ValidationError("tmf", str, type(self.tmf), None)
    if not isinstance(self.adminlang, str):  # type: ignore
      raise ValidationError("adminlang", str, type(self.adminlang), None)
    if not isinstance(self.srclang, str):  # type: ignore
      raise ValidationError("srclang", str, type(self.srclang), None)
    attrs: dict[str, str] = {
      "creationtool": self.creationtool,
      "creationtoolversion": self.creationtoolversion,
      "segtype": self.segtype.value,
      "o-tmf": self.tmf,
      "adminlang": self.adminlang,
      "srclang": self.srclang,
    }
    if not isinstance(self.datatype, (str, DATATYPE)):  # type: ignore
      raise ValidationError("datatype", str, type(self.datatype), None)
    attrs["datatype"] = (
      self.datatype if isinstance(self.datatype, str) else self.datatype.value
    )
    if self.encoding is not None:
      if not isinstance(self.encoding, str):  # type: ignore
        raise ValidationError("encoding", str, type(self.encoding), None)
      attrs["o-encoding"] = self.encoding
    if self.creationdate is not None:
      if not isinstance(self.creationdate, datetime):  # type: ignore
        raise ValidationError("creationdate", datetime, type(self.creationdate), None)
      attrs["creationdate"] = self.creationdate.strftime("%Y%m%dT%H%M%SZ")
    if self.creationid is not None:
      if not isinstance(self.creationid, str):  # type: ignore
        raise ValidationError("creationid", str, type(self.creationid), None)
      attrs["creationid"] = self.creationid
    if self.changedate is not None:
      if not isinstance(self.changedate, datetime):  # type: ignore
        raise ValidationError("changedate", datetime, type(self.changedate), None)
      attrs["changedate"] = self.changedate.strftime("%Y%m%dT%H%M%SZ")
    if self.changeid is not None:
      if not isinstance(self.changeid, str):  # type: ignore
        raise ValidationError("changeid", str, type(self.changeid), None)
      attrs["changeid"] = self.changeid
    return attrs
