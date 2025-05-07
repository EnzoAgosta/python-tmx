import xml.etree.ElementTree as pyet
from abc import ABC
from collections.abc import Callable, MutableMapping
from datetime import datetime
from enum import StrEnum
from typing import Any, ClassVar, Literal, Optional, Protocol, TypeVar, overload
from xml.dom import XML_NAMESPACE

import lxml.etree as lxet

T = TypeVar("T", bound=Any)


class ElementLike(Protocol):
  tag: str
  tail: Optional[str]
  text: Optional[str]
  attrib: MutableMapping | lxet._Attrib

class SEGTYPE(StrEnum):
  BLOCK = "block"
  PARAGRAPH = "paragraph"
  SENTENCE = "sentence"
  PHRASE = "phrase"


__TEMP_ELEMENT__ = pyet.Element("temp")
XML_NAMESPACE
type XmlElement = lxet._Element | pyet.Element | ElementLike


class BaseElement(ABC):
  _export_tag: ClassVar[str]
  _source_element: Optional[XmlElement]
  __slots__ = "_source_element"

  def __init__(self, **kwargs) -> None:
    source_element: XmlElement = kwargs.get("element", __TEMP_ELEMENT__)
    for attribute in self.__slots__:
      if attribute in kwargs:
        self.__setattr__(attribute, kwargs[attribute])
      else:
        if attribute in source_element.attrib:
          self.__setattr__(attribute, source_element.attrib[attribute])
        elif f"o-{attribute}" in source_element.attrib:
          self.__setattr__(attribute, source_element.attrib[f"o-{attribute}"])
        elif f"{XML_NAMESPACE}{attribute}" in source_element.attrib:
          self.__setattr__(
            attribute, source_element.attrib[f"{XML_NAMESPACE}{attribute}"]
          )
    self._source_element = (
      source_element if source_element is not __TEMP_ELEMENT__ else None
    )

  
  def to_element(
    self, engine: Literal["python", "lxml"] | Callable[[str, dict[str, str]], XmlElement] = "python"
  ) -> XmlElement:
    factory: Callable
    if engine == "python":
      factory = pyet.Element
    elif engine == "lxml":
      factory = lxet.Element
    else:
      factory = engine
    
    return __TEMP_ELEMENT__
    


class Header(BaseElement):
  _export_tag = "header"
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
  )
  creationtool: str
  creationtoolversion: str
  segtype: SEGTYPE
  tmf: str
  adminlang: str
  srclang: str
  datatype: str
  encoding: Optional[str]
  creationdate: Optional[datetime]
  creationid: Optional[str]
  changedate: Optional[datetime]
  changeid: Optional[str]

  @overload
  def __init__(self, *, element: XmlElement) -> None: ...
  @overload
  def __init__(
    self,
    *,
    element: XmlElement,
    creationtool: Optional[str] = None,
    creationtoolversion: Optional[str] = None,
    segtype: Optional[
      SEGTYPE | Literal["block", "paragraph", "sentence", "phrase"]
    ] = None,
    tmf: Optional[str] = None,
    adminlang: Optional[str] = None,
    srclang: Optional[str] = None,
    datatype: Optional[str] = None,
    encoding: Optional[str] = None,
    creationdate: Optional[str | datetime] = None,
    creationid: Optional[str] = None,
    changedate: Optional[str] = None,
    changeid: Optional[str] = None,
  ) -> None: ...
  @overload
  def __init__(
    self,
    *,
    creationtool: str,
    creationtoolversion: str,
    segtype: SEGTYPE | Literal["block", "paragraph", "sentence", "phrase"],
    tmf: str,
    adminlang: str,
    srclang: str,
    datatype: str,
    encoding: Optional[str] = None,
    creationdate: Optional[str | datetime] = None,
    creationid: Optional[str] = None,
    changedate: Optional[str] = None,
    changeid: Optional[str] = None,
  ) -> None: ...
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
    if isinstance(self.changedate, str):
      self.changedate = datetime.fromisoformat(self.changedate)
    if isinstance(self.creationdate, str):
      self.creationdate = datetime.fromisoformat(self.creationdate)
    if isinstance(self.segtype, str):
      self.segtype = SEGTYPE(self.segtype)
