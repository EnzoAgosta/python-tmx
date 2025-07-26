from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from types import NoneType
from typing import Generator

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
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
  try_parse_enum,
)


@dataclass(slots=True)
class Header(BaseTmxElement):
  creationtool: str = field(metadata={"expected_types": (str,)})
  creationtoolversion: str = field(metadata={"expected_types": (str,)})
  segtype: SEGTYPE | str = field(metadata={"expected_types": (SEGTYPE)})
  tmf: str = field(metadata={"expected_types": (str,)})
  adminlang: str = field(metadata={"expected_types": (str,)})
  srclang: str = field(metadata={"expected_types": (str,)})
  datatype: str = field(metadata={"expected_types": (str,)})
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
  udes: list[Ude] = field(
    default_factory=list[Ude], metadata={"expected_types": (Iterable,)}
  )
  props: list[Prop] = field(
    default_factory=list[Prop], metadata={"expected_types": (Iterable,)}
  )
  notes: list[Note] = field(
    default_factory=list[Note], metadata={"expected_types": (Iterable,)}
  )

  def __iter__(self) -> Generator[Note | Prop | Ude]:
    yield from self.udes
    yield from self.notes
    yield from self.props

  def __len__(self) -> int:
    return len(self.udes) + len(self.notes) + len(self.props)

  @classmethod
  def from_xml(cls: type[Header], element: AnyXmlElement) -> Header:
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
        "tmf",
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
      segtype = try_parse_enum(element.attrib["segtype"], SEGTYPE, True)
    except TypeError as e:
      raise_serialization_errors(element.tag, e)
    base_header = Header(
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
    )
    for child in element:
      if child.tag == "ude":
        base_header.udes.append(Ude.from_xml(child))
      elif child.tag == "note":
        base_header.notes.append(Note.from_xml(child))
      elif child.tag == "prop":
        base_header.props.append(Prop.from_xml(child))
      else:
        raise SerializationError(
          f"Unexpected child element in header element - Expected Ude, Note or Prop, got {child.tag}",
          "header",
          ValueError(),
        )
    return base_header

  def to_xml(self, factory: AnyElementFactory[..., R] | None = None) -> R:
    _factory = get_factory(self, factory)
    element = _factory(
      "header", self._make_attrib_dict(("udes", "notes", "props"))
    )
    for ude in self.udes:
      if not isinstance(ude, Ude):  # type: ignore
        raise SerializationError(
          f"Unexpected child element in header element - Expected Ude, got {type(ude)}",
          "header",
          TypeError(),
        )
      element.append(ude.to_xml())
    for note in self.notes:
      if not isinstance(note, Note):  # type: ignore
        raise SerializationError(
          f"Unexpected child element in header element - Expected Note, got {type(note)}",
          "header",
          TypeError(),
        )
      element.append(note.to_xml())
    for prop in self.props:
      if not isinstance(prop, Prop):  # type: ignore
        raise SerializationError(
          f"Unexpected child element in header element - Expected Prop, got {type(prop)}",
          "header",
          TypeError(),
        )
      element.append(prop.to_xml())
    return element
