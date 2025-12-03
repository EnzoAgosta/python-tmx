from typing import TypeVar

from python_tmx.base.types import Assoc, Pos, Segtype

XML_NS = "{http://www.w3.org/XML/1998/namespace}"
T_XmlElement = TypeVar("T_XmlElement")
T_Enum = TypeVar("T_Enum", Pos, Segtype, Assoc)
