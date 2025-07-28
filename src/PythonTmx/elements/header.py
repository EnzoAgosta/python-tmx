from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from types import NoneType

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
from PythonTmx.enums import SEGTYPE
from PythonTmx.errors import SerializationError
from PythonTmx.utils import (
  ensure_element_structure,
  ensure_required_attributes_are_present,
  get_factory,
  raise_serialization_errors,
  try_parse_datetime,
)


@dataclass(slots=True)
class Header(BaseTmxElement, WithChildren[Note | Prop | Ude]):
  _children: list[Note | Prop | Ude] = field(
    metadata={"expected_types": (Iterable,)},
  )
  creationtool: str = field(metadata={"expected_types": (str,)})
  creationtoolversion: str = field(metadata={"expected_types": (str,)})
  segtype: SEGTYPE | str = field(metadata={"expected_types": (SEGTYPE)})
  tmf: str = field(metadata={"expected_types": (str,)})
  adminlang: str = field(metadata={"expected_types": (str,)})
  srclang: str = field(metadata={"expected_types": (str,)})
  datatype: str = field(metadata={"expected_types": (str,)})
  xml_factory: AnyElementFactory[..., AnyXmlElement] | None = None
  encoding: str | None = field(
    default=None, metadata={"expected_types": (str, NoneType)}
  )
  creationdate: datetime | str | None = field(
    default=None, metadata={"expected_types": (datetime, NoneType)}
  )
  creationid: str | None = field(
    default=None, metadata={"expected_types": (str, NoneType)}
  )
  changedate: str | datetime | None = field(
    default=None, metadata={"expected_types": (datetime, NoneType)}
  )
  changeid: str | None = field(
    default=None, metadata={"expected_types": (str, NoneType)}
  )

  @property
  def notes(self) -> list[Note]:
    return [note for note in self._children if isinstance(note, Note)]

  @property
  def props(self) -> list[Prop]:
    return [prop for prop in self._children if isinstance(prop, Prop)]

  @property
  def udes(self) -> list[Ude]:
    return [ude for ude in self._children if isinstance(ude, Ude)]

  @classmethod
  def from_xml(cls: type[Header], element: AnyXmlElement) -> Header:
    def _dispatch(child: AnyXmlElement) -> Note | Prop | Ude:
      if child.tag == "ude":
        return Ude.from_xml(child)
      elif child.tag == "note":
        return Note.from_xml(child)
      elif child.tag == "prop":
        return Prop.from_xml(child)
      else:
        raise SerializationError(
          f"Unexpected child element in header element - Expected Ude, Note or Prop, got {child.tag}",
          "header",
          ValueError(),
        )

    ensure_element_structure(element, expected_tag="header")
    if element.text:
      raise SerializationError(
        f"Unexpected text in header element: {element.text!r}",
        "header",
        ValueError(),
      )
    ensure_required_attributes_are_present(
      element,
      (
        "creationtool",
        "creationtoolversion",
        "segtype",
        "o-tmf",
        "adminlang",
        "srclang",
        "datatype",
      ),
    )
    try:
      creationdate = try_parse_datetime(
        element.attrib.get("creationdate", None), False
      )
      changedate = try_parse_datetime(
        element.attrib.get("changedate", None), False
      )
    except TypeError as e:
      raise_serialization_errors(element.tag, e)
    try:
      segtype = SEGTYPE(element.attrib["segtype"])
    except (TypeError, ValueError) as e:
      raise_serialization_errors(element.tag, e)
    try:
      return cls(
        creationtool=element.attrib["creationtool"],
        creationtoolversion=element.attrib["creationtoolversion"],
        segtype=segtype,
        tmf=element.attrib["o-tmf"],
        adminlang=element.attrib["adminlang"],
        srclang=element.attrib["srclang"],
        datatype=element.attrib["datatype"],
        encoding=element.attrib.get("o-encoding", None),
        creationdate=creationdate,
        creationid=element.attrib.get("creationid", None),
        changedate=changedate,
        changeid=element.attrib.get("changeid", None),
        _children=[_dispatch(child) for child in element],
      )
    except Exception as e:
      raise_serialization_errors(element.tag, e)

  def to_xml(self, factory: AnyElementFactory[..., R] | None = None) -> R:
    _factory = get_factory(self, factory)
    element = _factory("header", self._make_attrib_dict(("_children",)))
    for child in self:
      if not isinstance(child, Note | Prop | Ude):  # type: ignore
        raise SerializationError(
          f"Unexpected child element in header element - Expected Ude, Note or Prop, got {type(child)}",
          "header",
          TypeError(),
        )
      element.append(child.to_xml())
    return element
