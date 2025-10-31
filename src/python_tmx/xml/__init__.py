from typing import TypeVar
import xml.etree.ElementTree as ET
import lxml.etree as LET

XmlElement = TypeVar("XmlElement", ET.Element, LET.Element)
