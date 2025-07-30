from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  ConvertibleToInt,
  R,
  WithChildren,
)
from PythonTmx.elements.note import Note
from PythonTmx.elements.prop import Prop
from PythonTmx.elements.tuv import Tuv
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

__all__ = ["Tu"]


class Tu(BaseTmxElement, WithChildren[Prop | Note | Tuv]):
  """Represents a translation unit (tu) element in a TMX file.
  
  A translation unit is the core element of a TMX file that contains a source
  text and one or more target translations. Each tu represents a single
  translatable segment or unit of text along with its translations.
  
  Translation units can contain metadata (properties, notes) and multiple
  translation variants (tuv elements) for different target languages.
  
  Attributes:
    tuid: Optional unique identifier for this translation unit.
    encoding: Optional encoding specification for the content.
    datatype: The data type of the content (plaintext, html, etc.).
    usagecount: Optional count of how many times this unit has been used.
    lastusagedate: Optional timestamp of the last usage.
    creationtool: Optional name of the tool that created this unit.
    creationtoolversion: Optional version of the creation tool.
    creationdate: Optional timestamp when this unit was created.
    creationid: Optional identifier for the creator.
    changedate: Optional timestamp when this unit was last modified.
    segtype: Optional type of segmentation used for this unit.
    changeid: Optional identifier for the last modifier.
    tmf: Optional translation memory format identifier.
    srclang: Optional source language code.
    _children: List of Prop, Note, or Tuv child elements.
  """
  __slots__ = (
    "tuid",
    "encoding",
    "datatype",
    "usagecount",
    "lastusagedate",
    "creationtool",
    "creationtoolversion",
    "creationdate",
    "creationid",
    "changedate",
    "segtype",
    "changeid",
    "tmf",
    "srclang",
    "_children",
  )
  tuid: str | None
  encoding: str | None
  datatype: str | DATATYPE | None
  usagecount: int | None
  lastusagedate: datetime | None
  creationtool: str | None
  creationtoolversion: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  segtype: SEGTYPE | None
  changeid: str | None
  tmf: str | None
  srclang: str | None
  _children: list[Prop | Note | Tuv]

  def __init__(
    self,
    tuid: str | None = None,
    encoding: str | None = None,
    datatype: str | DATATYPE | None = None,
    usagecount: ConvertibleToInt | None = None,
    lastusagedate: str | datetime | None = None,
    creationtool: str | None = None,
    creationtoolversion: str | None = None,
    creationdate: str | datetime | None = None,
    creationid: str | None = None,
    changedate: str | datetime | None = None,
    segtype: str | SEGTYPE | None = None,
    changeid: str | None = None,
    tmf: str | None = None,
    srclang: str | None = None,
    children: Sequence[Note | Prop | Tuv] | None = None,
  ) -> None:
    """Initialize a Tu element.
    
    Args:
      tuid: Optional unique identifier for this translation unit.
      encoding: Optional encoding specification (e.g., "UTF-8", "ISO-8859-1").
      datatype: The data type of the content. Can be a DATATYPE enum or string.
      usagecount: Optional count of how many times this unit has been used.
      lastusagedate: Optional timestamp of the last usage. Can be string or datetime.
      creationtool: Optional name of the tool that created this unit.
      creationtoolversion: Optional version of the creation tool.
      creationdate: Optional timestamp when this unit was created. Can be string or datetime.
      creationid: Optional identifier for the creator.
      changedate: Optional timestamp when this unit was last modified. Can be string or datetime.
      segtype: Optional type of segmentation used. Can be a SEGTYPE enum or string.
      changeid: Optional identifier for the last modifier.
      tmf: Optional translation memory format identifier.
      srclang: Optional source language code (e.g., "en", "fr").
      children: Optional sequence of Note, Prop, or Tuv child elements.
    """
    self.tuid = tuid
    self.encoding = encoding
    self.usagecount = int(usagecount) if usagecount is not None else usagecount
    self.lastusagedate = try_parse_datetime(lastusagedate, False)
    self.creationtool = creationtool
    self.creationtoolversion = creationtoolversion
    self.creationdate = try_parse_datetime(creationdate, False)
    self.creationid = creationid
    self.changedate = try_parse_datetime(changedate, False)
    self.segtype = SEGTYPE(segtype) if segtype is not None else segtype
    self.changeid = changeid
    self.tmf = tmf
    self.srclang = srclang
    self._children = [child for child in children] if children is not None else []
    if datatype is not None:
      try:
        self.datatype = DATATYPE(datatype)
      except ValueError:
        self.datatype = datatype
    else:
      self.datatype = DATATYPE.UNKNOWN

  @property
  def props(self) -> list[Prop]:
    """Get the list of Prop elements in this translation unit.
    
    Returns:
      A list of Prop elements that provide metadata about this translation unit.
    """
    return [child for child in self if isinstance(child, Prop)]

  @property
  def notes(self) -> list[Note]:
    """Get the list of Note elements in this translation unit.
    
    Returns:
      A list of Note elements that provide additional information about this unit.
    """
    return [child for child in self if isinstance(child, Note)]

  @property
  def tuvs(self) -> list[Tuv]:
    """Get the list of Tuv elements in this translation unit.
    
    Returns:
      A list of Tuv elements that contain the source and target translations.
    """
    return [child for child in self if isinstance(child, Tuv)]

  @classmethod
  def from_xml(cls: type[Tu], element: AnyXmlElement) -> Tu:
    """Create a Tu instance from an XML element.
    
    This method parses a TMX translation unit element and creates a corresponding
    Tu object. The XML element must have the tag "tu".
    
    Args:
      element: The XML element to parse. Must have tag "tu".
    
    Returns:
      A new Tu instance with the parsed data.
    
    Raises:
      WrongTagError: If the element tag is not "tu".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      SerializationError: If any other parsing error occurs.
    """
    try:
      check_element_is_usable(element)
      if element.tag != "tu":
        raise WrongTagError(element.tag, "tu")

      children: list[Prop | Note | Tuv] = []
      for child in element:
        if child.tag == "prop":
          children.append(Prop.from_xml(child))
        elif child.tag == "note":
          children.append(Note.from_xml(child))
        elif child.tag == "tuv":
          children.append(Tuv.from_xml(child))
        else:
          raise WrongTagError(child.tag, "prop, note or tuv")

      return cls(
        tuid=element.attrib.get("tuid"),
        encoding=element.attrib.get("o-encoding"),
        datatype=element.attrib.get("datatype"),
        usagecount=element.attrib.get("usagecount"),
        lastusagedate=element.attrib.get("lastusagedate"),
        creationtool=element.attrib.get("creationtool"),
        creationtoolversion=element.attrib.get("creationtoolversion"),
        creationdate=element.attrib.get("creationdate"),
        creationid=element.attrib.get("creationid"),
        changedate=element.attrib.get("changedate"),
        segtype=element.attrib.get("segtype"),
        changeid=element.attrib.get("changeid"),
        tmf=element.attrib.get("o-tmf"),
        srclang=element.attrib.get("srclang"),
        children=children,
      )
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[..., R] | None = None) -> R:
    """Convert this Tu instance to an XML element.
    
    Creates an XML element with tag "tu" and the appropriate attributes.
    All child elements (props, notes, tuvs) are serialized and appended.
    
    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.
    
    Returns:
      An XML element representing this Tu.
    
    Raises:
      ValidationError: If any attribute has an invalid type.
      MissingDefaultFactoryError: If no factory is available.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("tu", self._make_attrib_dict())
      for child in self:
        element.append(child.to_xml(_factory))
      return element
    except ValidationError as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Tu.
    
    Builds the attribute dictionary that will be used when serializing
    this Tu to XML. Only includes attributes that have non-None values.
    
    Returns:
      A dictionary mapping attribute names to string values.
    
    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    attrs: dict[str, str] = {}
    if self.tuid is not None:
      if not isinstance(self.tuid, str):  # type: ignore
        raise ValidationError("tuid", str, type(self.tuid), None)
      attrs["tuid"] = self.tuid
    if self.encoding is not None:
      if not isinstance(self.encoding, str):  # type: ignore
        raise ValidationError("encoding", str, type(self.encoding), None)
      attrs["o-encoding"] = self.encoding
    if self.datatype is not None:
      if not isinstance(self.datatype, (str, DATATYPE)):  # type: ignore
        raise ValidationError("datatype", (str, DATATYPE), type(self.datatype), None)
      attrs["datatype"] = (
        self.datatype.value if isinstance(self.datatype, DATATYPE) else self.datatype
      )
    if self.usagecount is not None:
      if not isinstance(self.usagecount, int):  # type: ignore
        raise ValidationError("usagecount", int, type(self.usagecount), None)
      attrs["usagecount"] = str(self.usagecount)
    if self.lastusagedate is not None:
      if not isinstance(self.lastusagedate, datetime):  # type: ignore
        raise ValidationError("lastusagedate", datetime, type(self.lastusagedate), None)
      attrs["lastusagedate"] = self.lastusagedate.strftime("%Y%m%dT%H%M%S%Z")
    if self.creationtool is not None:
      if not isinstance(self.creationtool, str):  # type: ignore
        raise ValidationError("creationtool", str, type(self.creationtool), None)
      attrs["creationtool"] = self.creationtool
    if self.creationtoolversion is not None:
      if not isinstance(self.creationtoolversion, str):  # type: ignore
        raise ValidationError(
          "creationtoolversion", str, type(self.creationtoolversion), None
        )
      attrs["creationtoolversion"] = self.creationtoolversion
    if self.creationdate is not None:
      if not isinstance(self.creationdate, datetime):  # type: ignore
        raise ValidationError("creationdate", datetime, type(self.creationdate), None)
      attrs["creationdate"] = self.creationdate.strftime("%Y%m%dT%H%M%S%Z")
    if self.creationid is not None:
      if not isinstance(self.creationid, str):  # type: ignore
        raise ValidationError("creationid", str, type(self.creationid), None)
      attrs["creationid"] = self.creationid
    if self.changedate is not None:
      if not isinstance(self.changedate, datetime):  # type: ignore
        raise ValidationError("changedate", datetime, type(self.changedate), None)
      attrs["changedate"] = self.changedate.strftime("%Y%m%dT%H%M%S%Z")
    if self.segtype is not None:
      if not isinstance(self.segtype, SEGTYPE):  # type: ignore
        raise ValidationError("segtype", SEGTYPE, type(self.segtype), None)
      attrs["segtype"] = self.segtype.value
    if self.changeid is not None:
      if not isinstance(self.changeid, str):  # type: ignore
        raise ValidationError("changeid", str, type(self.changeid), None)
      attrs["changeid"] = self.changeid
    if self.tmf is not None:
      if not isinstance(self.tmf, str):  # type: ignore
        raise ValidationError("tmf", str, type(self.tmf), None)
      attrs["o-tmf"] = self.tmf
    if self.srclang is not None:
      if not isinstance(self.srclang, str):  # type: ignore
        raise ValidationError("srclang", str, type(self.srclang), None)
      attrs["srclang"] = self.srclang
    return attrs
