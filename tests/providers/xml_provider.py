from collections import OrderedDict
from typing import Generic
from faker.providers import BaseProvider
import lxml.etree as LET
import xml.etree.ElementTree as ET
from python_tmx.xml import XmlElement

XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


class XmlElementProvider(BaseProvider, Generic[XmlElement]):
  backend: type[XmlElement]
  max_depth: int

  def note_element(self) -> XmlElement:
    elem = self.backend(
      "note",
    )
    elem.text = self.generator.sentence(self.generator.random_number(2, False))
    if self.generator.pybool():
      elem.attrib[XML_LANG] = self.generator.language_code()
    if self.generator.pybool():
      elem.attrib["o-encoding"] = self.generator.encoding()
    return elem

  def prop_element(self) -> XmlElement:
    elem = self.backend(
      "prop",
      attrib={
        "type": self.generator.word(),
      },
    )
    elem.text = self.generator.sentence(self.generator.random_number(2, False))
    if self.generator.pybool():
      elem.attrib[XML_LANG] = self.generator.language_code()
    if self.generator.pybool():
      elem.attrib["o-encoding"] = self.generator.encoding()
    return elem

  def header_element(self) -> XmlElement:
    elem = self.backend(
      "header",
      attrib={
        "creationtool": self.generator.word(),
        "creationtoolversion": self.generator.version(),
        "segtype": self.generator.segtype().value,
        "o-tmf": self.generator.word(),
        "adminlang": self.generator.language_code(),
        "srclang": self.generator.language_code(),
        "datatype": self.generator.datatype(),
      },
    )
    if self.generator.pybool():
      elem.attrib["o-encoding"] = self.generator.encoding()
    if self.generator.pybool():
      elem.attrib["creationdate"] = self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ")
    if self.generator.pybool():
      elem.attrib["creationid"] = self.generator.user_name()
    if self.generator.pybool():
      elem.attrib["changedate"] = self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ")
    if self.generator.pybool():
      elem.attrib["changeid"] = self.generator.user_name()
    elem.extend(self.generator.prop_element() for _ in range(self.generator.random_number(2, False)))
    elem.extend(self.generator.note_element() for _ in range(self.generator.random_number(2, False)))
    return elem

  def _fill_element(self, elem: XmlElement, sub_only: bool, max_depth: int) -> None:
    if self.generator.pybool():
      elem.text = self.generator.sentence(self.generator.random_number(2, False))
    next_depth = max_depth - self.generator.random_int(1, 2)
    if max_depth < 1:
      return 
    for _ in range(self.generator.random_number(1, True)):
      if sub_only:
        elem.append(self.generator.sub_element(max_depth=next_depth))
      else:
        match item_type := self.generator.random_element(
          OrderedDict({"bpt": 0.3, "ept": 0.3, "it": 0.1, "ph": 0.2, "hi": 0.1})
        ):
          case "bpt":
            elem.append(self.generator.bpt_element(max_depth=next_depth))
          case "ept":
            elem.append(self.generator.ept_element(max_depth=next_depth))
          case "it":
            elem.append(self.generator.it_element(max_depth=next_depth))
          case "ph":
            elem.append(self.generator.ph_element(max_depth=next_depth))
          case "hi":
            elem.append(self.generator.hi_element(max_depth=next_depth))
          case _:
            raise RuntimeError(f"Unexpected item type: {item_type!r}")
      if self.generator.pybool():
        elem.tail = self.generator.sentence(self.generator.random_number(2, False))

  def sub_element(self, max_depth: int | None = None) -> XmlElement:
    _max_depth = max_depth if max_depth is not None else self.max_depth
    elem = self.backend("sub")
    if self.generator.pybool():
      elem.attrib["datatype"] = self.generator.datatype()
    if self.generator.pybool():
      elem.attrib["type"] = self.generator.word()
    self._fill_element(elem, False, max_depth=_max_depth)
    return elem

  def bpt_element(self, max_depth: int | None = None) -> XmlElement:
    _max_depth = max_depth if max_depth is not None else self.max_depth
    elem = self.backend("bpt", attrib={"i": str(self.generator.random_number(1, False))})
    if self.generator.pybool():
      elem.attrib["x"] = str(self.generator.random_number(1, False))
    if self.generator.pybool():
      elem.attrib["type"] = self.generator.word()
    self._fill_element(elem, True, max_depth=_max_depth)
    return elem

  def ept_element(self, max_depth: int | None = None) -> XmlElement:
    _max_depth = max_depth if max_depth is not None else self.max_depth
    elem = self.backend("ept", attrib={"i": str(self.generator.random_number(1, False))})
    self._fill_element(elem, True, max_depth=_max_depth)
    return elem

  def it_element(self, max_depth: int | None = None) -> XmlElement:
    _max_depth = max_depth if max_depth is not None else self.max_depth
    elem = self.backend("it", attrib={"pos": self.generator.pos().value})
    if self.generator.pybool():
      elem.attrib["x"] = str(self.generator.random_number(1, False))
    if self.generator.pybool():
      elem.attrib["type"] = self.generator.word()
    self._fill_element(elem, True, max_depth=_max_depth)
    return elem

  def ph_element(self, max_depth: int | None = None) -> XmlElement:
    _max_depth = max_depth if max_depth is not None else self.max_depth
    elem = self.backend("ph", attrib={"x": str(self.generator.random_number(1, False))})
    if self.generator.pybool():
      elem.attrib["type"] = self.generator.word()
    if self.generator.pybool():
      elem.attrib["assoc"] = self.generator.assoc().value
    self._fill_element(elem, True, max_depth=_max_depth)
    return elem

  def hi_element(self, max_depth: int | None = None) -> XmlElement:
    _max_depth = max_depth if max_depth is not None else self.max_depth
    elem = self.backend("hi")
    if self.generator.pybool():
      elem.attrib["x"] = str(self.generator.random_number(1, False))
    if self.generator.pybool():
      elem.attrib["type"] = self.generator.word()
    self._fill_element(elem, False, max_depth=_max_depth)
    return elem

  def tuv_element(self, max_depth: int | None = None) -> XmlElement:
    _max_depth = max_depth if max_depth is not None else self.max_depth
    elem = self.backend("tuv", attrib={XML_LANG: self.generator.language_code()})
    if self.generator.pybool():
      elem.attrib["o-encoding"] = self.generator.encoding()
    if self.generator.pybool():
      elem.attrib["datatype"] = self.generator.datatype()
    if self.generator.pybool():
      elem.attrib["usagecount"] = str(self.generator.random_number(3, False))
    if self.generator.pybool():
      elem.attrib["lastusagedate"] = self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ")
    if self.generator.pybool():
      elem.attrib["creationtool"] = self.generator.word()
    if self.generator.pybool():
      elem.attrib["creationtoolversion"] = self.generator.version()
    if self.generator.pybool():
      elem.attrib["creationdate"] = self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ")
    if self.generator.pybool():
      elem.attrib["creationid"] = self.generator.user_name()
    if self.generator.pybool():
      elem.attrib["changedate"] = self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ")
    if self.generator.pybool():
      elem.attrib["changeid"] = self.generator.user_name()
    if self.generator.pybool():
      elem.attrib["o-tmf"] = self.generator.word()
    elem.extend(self.generator.prop_element() for _ in range(self.generator.random_number(2, False)))
    elem.extend(self.generator.note_element() for _ in range(self.generator.random_number(2, False)))
    seg = self.backend("seg")
    self._fill_element(seg, False, max_depth=_max_depth)
    elem.append(seg)
    return elem

  def tu_element(self) -> XmlElement:
    elem = self.backend("tu")
    if self.generator.pybool():
      elem.attrib["tuid"] = self.generator.uuid4()
    if self.generator.pybool():
      elem.attrib["o-encoding"] = self.generator.encoding()
    if self.generator.pybool():
      elem.attrib["datatype"] = self.generator.datatype()
    if self.generator.pybool():
      elem.attrib["usagecount"] = str(self.generator.random_number(3, False))
    if self.generator.pybool():
      elem.attrib["lastusagedate"] = self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ")
    if self.generator.pybool():
      elem.attrib["creationtool"] = self.generator.word()
    if self.generator.pybool():
      elem.attrib["creationtoolversion"] = self.generator.version()
    if self.generator.pybool():
      elem.attrib["creationdate"] = self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ")
    if self.generator.pybool():
      elem.attrib["creationid"] = self.generator.user_name()
    if self.generator.pybool():
      elem.attrib["changedate"] = self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ")
    if self.generator.pybool():
      elem.attrib["segtype"] = self.generator.segtype().value
    if self.generator.pybool():
      elem.attrib["changeid"] = self.generator.user_name()
    if self.generator.pybool():
      elem.attrib["o-tmf"] = self.generator.word()
    if self.generator.pybool():
      elem.attrib["srclang"] = self.generator.language_code()
    elem.extend(self.generator.prop_element() for _ in range(self.generator.random_number(2, False)))
    elem.extend(self.generator.note_element() for _ in range(self.generator.random_number(2, False)))
    elem.extend(self.generator.tuv_element() for _ in range(self.generator.random_number(1, False)))
    return elem

  def tmx_element(self) -> XmlElement:
    elem = self.backend("tmx", attrib={"version": self.generator.version()})
    elem.append(self.generator.header_element())
    body = self.backend("body")
    for _ in range(self.generator.random_number(2, True)):
      body.append(self.generator.tu_element())
    elem.append(body)
    return elem


class LxmlProvider(XmlElementProvider[LET.Element]):
  backend = LET.Element


class StdProvider(XmlElementProvider[ET.Element]):
  backend = ET.Element  # type: ignore[assignment]
