from typing import TypeVar

from hypomnema.base.types import Assoc, Pos, Segtype

__all__ = ["XML_NS", "T_XmlElement", "T_Enum"]

XML_NS = "{http://www.w3.org/XML/1998/namespace}"
T_XmlElement = TypeVar("T_XmlElement")
T_Enum = TypeVar("T_Enum", Pos, Segtype, Assoc)
