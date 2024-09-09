from __future__ import annotations

from datetime import datetime
from os import PathLike
from typing import Annotated, Literal, Optional, Self

from lxml.etree import Element, ElementTree, _Element, _ElementTree
from pydantic import BaseModel, Field, ValidationInfo, field_serializer, field_validator

XML = "{http://www.w3.org/XML/1998/namespace}"
__all__ = [
    "TmxElement",
    "Tmx",
    "Tu",
    "Tuv",
    "Header",
    "Note",
    "Prop",
    "Ude",
    "Map",
    "Bpt",
    "Ept",
    "It",
    "Hi",
    "Sub",
    "Ph",
    "Ut",
]


class TmxElement(BaseModel):
    @field_validator(
        "creationdate", "changedate", "lastusagedate", mode="after", check_fields=False
    )
    @classmethod
    def check_datetime(cls, timestamp: str | datetime | None) -> datetime:
        if not timestamp:
            return timestamp
        if isinstance(timestamp, datetime):
            return timestamp
        try:
            return datetime.strptime(timestamp, r"%Y%m%dT%H%M%SZ")
        except TypeError as e:
            raise ValueError(e.__cause__)
        except ValueError as e:
            raise e

    @field_validator("segment", mode="after", check_fields=False)
    @classmethod
    def check_paired(
        cls, segment: str | list[str | TmxElement]
    ) -> str | list[str | TmxElement]:
        if isinstance(segment, str):
            return segment
        if len([item for item in segment if isinstance(item, Bpt)]) != len(
            [item for item in segment if isinstance(item, Ept)]
        ):
            raise ValueError(
                "the amount of Bpt and Ept elements in a segment must be equal"
            )
        return segment

    @field_serializer(
        "creationdate",
        "changedate",
        "lastusagedate",
        return_type=str,
        check_fields=False,
    )
    def serialize_dt(dt: datetime) -> str:
        return dt.strftime(r"%Y%m%dT%H%M%SZ")

    @field_serializer("x", "i", "usagecount", return_type=str, check_fields=False)
    def serialize_int(num: int) -> str:
        return str(num)

    def to_element(self) -> _Element:
        e = Element(
            self.__qualname__.lower(), attrib=self.model_dump(exclude_none=True)
        )
        e.text = ""
        for field in self.model_fields_set:
            match field:
                case "header":
                    e.append(self.header.to_element())
                case "notes":
                    e.extend([note.to_element() for note in self.notes])
                case "props":
                    e.extend([prop.to_element() for prop in self.props])
                case "udes":
                    e.extend([ude.to_element() for ude in self.udes])
                case "maps":
                    e.extend([map_.to_element() for map_ in self.maps])
                case "tuvs":
                    e.extend([tuv.to_element() for tuv in self.tuvs])
                case "tus":
                    b = Element("body")
                    b.text = ""
                    b.extend([tu.to_element() for tu in self.tus])
                    e.append(b)
                case "segment":
                    s = Element("seg")
                    s.text = ""
                    if isinstance(self.segment, str):
                        s.text = self.segment
                        e.append(s)
                    else:
                        for i in self.segment:
                            if isinstance(i, str):
                                if len(e):
                                    e[-1].text += i
                                else:
                                    e.text += i
                            else:
                                e.append(i.to_element())
                case "content":
                    for i in self.content:
                        if isinstance(i, str):
                            if len(e):
                                e[-1].text += i
                            else:
                                e.text += i
                        else:
                            e.append(i.to_element())
        return e


class Note(TmxElement):
    content: str = Field(exclude=True)
    lang: Optional[str] = Field(None, serialization_alias=f"{XML}lang")
    encoding: Optional[str] = Field(None, serialization_alias="o-encoding")


class Prop(TmxElement):
    content: str = Field(exclude=True)
    type: str
    lang: Optional[str] = Field(None, serialization_alias=f"{XML}lang")
    encoding: Optional[str] = Field(None, serialization_alias="o-encoding")


class Map(TmxElement):
    unicode: str
    code: Optional[str] = None
    ent: Optional[str] = None
    subst: Optional[str] = None


class Ude(TmxElement):
    maps: list[Map] = Field(exclude=True, default_factory=list)
    name: str
    base: Annotated[Optional[str], Field(validate_default=True)] = None

    @field_validator("base", mode="after")
    @classmethod
    def check_for_base(cls, base: str | None, info: ValidationInfo) -> str:
        if base is not None:
            return base
        _maps = info.data["maps"]
        if not len(_maps):
            return base
        for _map in _maps:
            if _map.code:
                raise ValueError(
                    "a value for base is required if one or more of the Map elements contains a code attribute"
                )


class Header(TmxElement):
    notes: list[Note] = Field(exclude=True, default_factory=list)
    props: list[Prop] = Field(exclude=True, default_factory=list)
    udes: list[Ude] = Field(exclude=True, default_factory=list)
    creationtool: str
    creationtoolversion: str
    segtype: Literal["block", "paragraph", "sentence", "phrase"]
    tmf: Optional[str] = Field(None, serialization_alias="o-tmf")
    adminlang: str
    srclang: str
    datatype: str
    encoding: Optional[str] = Field(None, serialization_alias="o-encoding")
    creationdate: Optional[str | datetime] = None
    creationid: Optional[str] = None
    changedate: Optional[str | datetime] = None
    changeid: Optional[str] = None


class Tuv(TmxElement):
    content: str | list[str | Bpt | Ept | It | Hi | Ph] = Field(
        exclude=True, default_factory=list
    )
    notes: list[Note] = Field(exclude=True, default_factory=list)
    props: list[Prop] = Field(exclude=True, default_factory=list)
    lang: Optional[str] = Field(None, serialization_alias=f"{XML}lang")
    encoding: Optional[str] = Field(None, serialization_alias="o-encoding")
    datatype: Optional[str] = None
    usagecount: Optional[int] = None
    lastusagedate: Optional[str | datetime] = None
    creationtool: Optional[str] = None
    creationtoolversion: Optional[str] = None
    creationdate: Optional[str | datetime] = None
    creationid: Optional[str] = None
    changedate: Optional[str | datetime] = None
    changeid: Optional[str] = None
    tmf: Optional[str] = Field(None, serialization_alias="o-tmf")


class Tu(TmxElement):
    tuvs: list[Tuv] = Field(exclude=True, default_factory=list)
    notes: list[Note] = Field(exclude=True, default_factory=list)
    props: list[Prop] = Field(exclude=True, default_factory=list)
    tuid: Optional[str] = None
    encoding: Optional[str] = Field(None, serialization_alias="o-encoding")
    datatype: Optional[str] = None
    usagecount: Optional[int] = None
    lastusagedate: Optional[str | datetime] = None
    creationtool: Optional[str] = None
    creationtoolversion: Optional[str] = None
    creationdate: Optional[str | datetime] = None
    creationid: Optional[str] = None
    changedate: Optional[str | datetime] = None
    segtype: Optional[Literal["block", "paragraph", "sentence", "phrase"]] = None
    changeid: Optional[str] = None
    tmf: Optional[str] = Field(None, serialization_alias="o-tmf")
    srclang: Optional[str] = None


class Tmx(TmxElement):
    version: str = "1.4"
    header: Header = Field(exclude=True)
    tus: list[Tu] = Field(exclude=True, default_factory=list)

    def to_file(self, file: str | bytes | PathLike, encoding: str = "utf-8") -> None:
        tree: _ElementTree = ElementTree(self.to_element())
        tree.write(
            file,
            encoding=encoding,
            xml_declaration=True,
        )


class Sub(TmxElement):
    content: str | list[Bpt | Ept | It | Ph | Hi] = Field(
        exclude=True, default_factory=list
    )
    datatype: Optional[str] = None
    type: Optional[str] = None


class Ut(TmxElement):
    content: str | list[str | Sub] = Field(exclude=True, default_factory=list)
    x: Optional[int] = None


class Bpt(TmxElement):
    content: str | list[str | Sub] = Field(exclude=True, default_factory=list)
    i: int
    x: Optional[int] = None
    type: Optional[str] = None


class Ept(TmxElement):
    content: str | list[str | Sub] = Field(exclude=True, default_factory=list)
    i: Optional[int]


class It(TmxElement):
    content: str | list[str | Sub] = Field(exclude=True, default_factory=list)
    pos: Literal["begin", "end"]
    x: Optional[int] = None
    type: Optional[str] = None


class Ph(TmxElement):
    content: str | list[str | Sub] = Field(exclude=True, default_factory=list)
    assoc: Optional[Literal["p", "f", "b"]] = None
    x: Optional[int] = None
    type: Optional[str] = None


class Hi(TmxElement):
    content: str | list[str | Bpt | Ept | It | Ph | Self] = Field(
        exclude=True, default_factory=list
    )
    x: Optional[int] = None
    type: Optional[str] = None
