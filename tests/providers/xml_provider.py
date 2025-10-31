from collections import OrderedDict
from typing import Generic
from faker.providers import BaseProvider
import lxml.etree as LET
import xml.etree.ElementTree as ET
from python_tmx.xml import XmlElement

XML_NS = "{http://www.w3.org/XML/1998/namespace}"


class XmlElementProvider(BaseProvider, Generic[XmlElement]):
  backend: type[XmlElement]

  def note_element(self) -> XmlElement:
    elem = self.backend(
      "note",
      attrib={
        "o-encoding": self.generator.encoding(),
        f"{XML_NS}lang": self.generator.language_code(),
      },
    )
    elem.text = self.generator.sentence(self.generator.random_number(2, False))
    return elem

  def prop_element(self) -> XmlElement:
    elem = self.backend(
      "prop",
      attrib={
        "type": self.generator.word(),
        "o-encoding": self.generator.encoding(),
        f"{XML_NS}lang": self.generator.language_code(),
      },
    )
    elem.text = self.generator.sentence(self.generator.random_number(2, False))
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
        "o-encoding": self.generator.encoding(),
        "creationdate": self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ"),
        "creationid": self.generator.user_name(),
        "changedate": self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ"),
        "changeid": self.generator.user_name(),
      },
    )
    elem.extend(self.generator.prop_element() for _ in range(self.generator.random_number(2, False)))
    elem.extend(self.generator.note_element() for _ in range(self.generator.random_number(2, False)))
    return elem

  def _fill_element(self, elem: XmlElement, sub_only: bool) -> None:
    if self.generator.random_int(0, 1):
      elem.text = self.generator.sentence(self.generator.random_number(2, False))
    for _ in range(self.generator.random_number(1, True)):
      if sub_only:
        elem.append(self.generator.sub())
      else:
        match item_type := self.generator.random_element(
          OrderedDict({"bpt": 0.3, "ept": 0.3, "it": 0.1, "ph": 0.2, "hi": 0.1})
        ):
          case "bpt":
            elem.append(self.generator.bpt_element())
          case "ept":
            elem.append(self.generator.ept_element())
          case "it":
            elem.append(self.generator.it_element())
          case "ph":
            elem.append(self.generator.ph_element())
          case "hi":
            elem.append(self.generator.hi_element())
          case _:
            raise RuntimeError(f"Unexpected item type: {item_type!r}")
      if self.generator.random_int(0, 1):
        elem.tail = self.generator.sentence(self.generator.random_number(2, False))

  def sub_element(self) -> XmlElement:
    elem = self.backend(
      "sub",
      attrib={
        "datatype": self.generator.datatype(),
        "type": self.generator.word(),
        "o-encoding": self.generator.encoding(),
      },
    )
    self._fill_element(elem, False)
    return elem

  def bpt_element(self) -> XmlElement:
    elem = self.backend(
      "bpt",
      attrib={
        "i": str(self.generator.random_number(1, False)),
        "x": str(self.generator.random_number(1, False)),
        "type": self.generator.word(),
        "o-encoding": self.generator.encoding(),
      },
    )
    self._fill_element(elem, True)
    return elem

  def ept_element(self) -> XmlElement:
    elem = self.backend(
      "ept",
      attrib={
        "i": str(self.generator.random_number(1, False)),
        "o-encoding": self.generator.encoding(),
      },
    )
    self._fill_element(elem, True)
    return elem

  def it_element(self) -> XmlElement:
    elem = self.backend(
      "it",
      attrib={
        "pos": self.generator.pos(),
        "x": str(self.generator.random_number(1, False)),
        "type": self.generator.word(),
        "o-encoding": self.generator.encoding(),
      },
    )
    self._fill_element(elem, True)
    return elem

  def ph_element(self) -> XmlElement:
    elem = self.backend(
      "ph",
      attrib={
        "x": str(self.generator.random_number(1, False)),
        "type": self.generator.word(),
        "assoc": self.generator.assoc(),
        "o-encoding": self.generator.encoding(),
      },
    )
    self._fill_element(elem, True)
    return elem

  def hi_element(self) -> XmlElement:
    elem = self.backend(
      "hi",
      attrib={
        "x": str(self.generator.random_number(1, False)),
        "type": self.generator.word(),
        "o-encoding": self.generator.encoding(),
      },
    )
    self._fill_element(elem, False)
    return elem

  def tuv_element(self) -> XmlElement:
    elem = self.backend(
      "tuv",
      attrib={
        f"{XML_NS}lang": self.generator.language_code(),
        "o-encoding": self.generator.encoding(),
        "datatype": self.generator.datatype(),
        "usagecount": str(self.generator.random_number(3, False)),
        "lastusagedate": self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ"),
        "creationtool": self.generator.word(),
        "creationtoolversion": self.generator.version(),
        "creationdate": self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ"),
        "creationid": self.generator.user_name(),
        "changedate": self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ"),
        "changeid": self.generator.user_name(),
      },
    )
    elem.extend(self.generator.prop_element() for _ in range(self.generator.random_number(2, False)))
    elem.extend(self.generator.note_element() for _ in range(self.generator.random_number(2, False)))
    seg = self.backend("seg")
    self._fill_element(seg, False)
    elem.append(seg)
    return elem

  def tu_element(self) -> XmlElement:
    elem = self.backend(
      "tu",
      attrib={
        "tuid": self.generator.uuid4(),
        "o-encoding": self.generator.encoding(),
        "datatype": self.generator.datatype(),
        "usagecount": str(self.generator.random_number(3, False)),
        "lastusagedate": self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ"),
        "creationtool": self.generator.word(),
        "creationtoolversion": self.generator.version(),
        "creationdate": self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ"),
        "creationid": self.generator.user_name(),
        "changedate": self.generator.date_time_this_century().strftime("%Y%m%dT%H%M%SZ"),
        "segtype": self.generator.segtype(),
        "changeid": self.generator.user_name(),
        "o-tmf": self.generator.word(),
        "srclang": self.generator.language_code(),
      },
    )
    elem.extend(self.generator.prop_element() for _ in range(self.generator.random_number(2, False)))
    elem.extend(self.generator.note_element() for _ in range(self.generator.random_number(2, False)))
    elem.extend(self.generator.tuv_element() for _ in range(2))
    return elem

  def tmx_element(self) -> XmlElement:
    elem = self.backend(
      "tmx",
      attrib={
        "version": self.generator.version(),
      },
    )
    elem.append(self.generator.header_element())
    body = self.backend("body")
    for _ in range(self.generator.random_number(3, False)):
      body.append(self.generator.tu())
    elem.append(body)
    return elem


class LxmlProvider(XmlElementProvider[LET.Element]):
  backend = LET.Element


class StdProvider(XmlElementProvider[ET.Element]):
  backend = ET.Element  # type: ignore[assignment]
