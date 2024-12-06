import xml.etree.ElementTree as ET
from typing import TypeAlias

import lxml.etree as et

XmlElement: TypeAlias = et._Element | ET.Element
