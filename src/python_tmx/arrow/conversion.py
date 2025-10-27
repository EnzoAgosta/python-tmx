from typing import TypeVar

from python_tmx.arrow.dicts import (
  BptDict,
  EptDict,
  HeaderDict,
  HiDict,
  ItDict,
  NoteDict,
  PhDict,
  PropDict,
  SubDict,
  TuvDict,
)
from python_tmx.base.classes import Assoc, Bpt, Ept, Header, Hi, It, Note, Ph, Pos, Prop, Segtype, Sub, Tuv


def prop_from_dict(prop_dict: PropDict) -> Prop:
  return Prop(**prop_dict)


def note_from_dict(note_dict: NoteDict) -> Note:
  return Note(**note_dict)


def header_from_dict(header_dict: HeaderDict) -> Header:
  return Header(
    creationtool=header_dict["creationtool"],
    creationtoolversion=header_dict["creationtoolversion"],
    segtype=Segtype[header_dict["segtype"]],
    o_tmf=header_dict["o_tmf"],
    adminlang=header_dict["adminlang"],
    srclang=header_dict["srclang"],
    datatype=header_dict["srclang"],
    o_encoding=header_dict.get("o_encoding"),
    creationdate=header_dict.get("creationdate"),
    creationid=header_dict.get("creationid"),
    changedate=header_dict.get("changedate"),
    changeid=header_dict.get("changeid"),
    props=[prop_from_dict(prop) for prop in header_dict["props"]],
    notes=[note_from_dict(note) for note in header_dict["notes"]],
  )


T = TypeVar("T", bound=Bpt | Ept | Hi | It | Ph | Sub | str)


def content_from_list(
  content_list: list[str | BptDict | EptDict | HiDict | SubDict | ItDict | PhDict], filter: tuple[type[T], ...]
) -> list[T]:
  parts: list = []
  for item in content_list:
    if isinstance(item, str):
      parts.append(item)
      continue
    if "i" in item:
      if "x" in item:
        if Bpt not in filter:
          raise ValueError("Unexpected Bpt Element found")
        parts.append(
          Bpt(
            content=content_from_list(item["content"], (Sub,)),
            i=item["i"],
            x=item.get("x"),
            type=item.get("type"),
          )
        )
      else:
        if Ept in filter:
          raise ValueError("Unexpected Ept Element found")
        parts.append(
          Ept(
            content=content_from_list(item["content"], (Sub,)),
            i=item["i"],
          )
        )
    elif "pos" in item:
      if It not in filter:
        raise ValueError("Unexpected It Element found")
      parts.append(
        It(
          content=content_from_list(item["content"], (Sub,)),
          pos=Pos(item["pos"]),
          x=item.get("x"),
          type=item.get("type"),
        )
      )
    elif "assoc" in item:
      if Ph not in filter:
        raise ValueError("Unexpected Ph Element found")
      parts.append(
        Ph(
          content=content_from_list(item["content"], (Sub,)),
          x=item.get("x"),
          type=item.get("type"),
          assoc=Assoc(item["assoc"]),
        )
      )
    elif "datatype" in item:
      if Sub not in filter:
        raise ValueError("Unexpected Sub Element found")
      parts.append(
        Sub(
          content=content_from_list(item["content"], (Bpt, Ept, It, Hi, Ph)),
          datatype=item.get("datatype"),
          type=item.get("type"),
        )
      )
    else:
      if Hi not in filter:
        raise ValueError("Unexpected Hi Element found")
      parts.append(
        Hi(
          content=content_from_list(item["content"], (Bpt, Ept, It, Hi, Ph)),
          x=item.get("x"),
          type=item.get("type"),
        )
      )
  return parts


def tuv_from_dict(tuv_dict: TuvDict) -> Tuv:
  return Tuv(
    lang=tuv_dict["lang"],
    o_encoding=tuv_dict.get("o_encoding"),
    datatype=tuv_dict.get("datatype"),
    usagecount=tuv_dict.get("usagecount"),
    lastusagedate=tuv_dict.get("lastusagedate"),
    creationtool=tuv_dict.get("creationtool"),
    creationtoolversion=tuv_dict.get("creationtoolversion"),
    creationdate=tuv_dict.get("creationdate"),
    creationid=tuv_dict.get("creationid"),
    changedate=tuv_dict.get("changedate"),
    changeid=tuv_dict.get("changeid"),
    o_tmf=tuv_dict.get("o_tmf"),
    props=[prop_from_dict(prop) for prop in tuv_dict["props"]],
    notes=[note_from_dict(note) for note in tuv_dict["notes"]],
    content=content_from_list(tuv_dict["content"], (Bpt, Ept, It, Hi, Ph)),
  )
