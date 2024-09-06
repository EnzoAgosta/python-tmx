from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Optional, Self

from pydantic import BaseModel, Field, ValidationInfo, field_serializer, field_validator

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


class Note(TmxElement):
    content: str = Field(exclude=True)
    lang: Optional[str] = None
    encoding: Optional[str] = None


class Prop(TmxElement):
    content: str = Field(exclude=True)
    type: str
    lang: Optional[str] = None
    encoding: Optional[str] = None


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
    tmf: str
    adminlang: str
    srclang: str
    datatype: str
    encoding: Optional[str] = None
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
    lang: str
    encoding: Optional[str] = None
    datatype: Optional[str] = None
    usagecount: Optional[int] = None
    lastusagedate: Optional[str | datetime] = None
    creationtool: Optional[str] = None
    creationtoolversion: Optional[str] = None
    creationdate: Optional[str | datetime] = None
    creationid: Optional[str] = None
    changedate: Optional[str | datetime] = None
    changeid: Optional[str] = None
    tmf: Optional[str] = None


class Tu(TmxElement):
    tuvs: list[Tuv] = Field(exclude=True, default_factory=list)
    notes: list[Note] = Field(exclude=True, default_factory=list)
    props: list[Prop] = Field(exclude=True, default_factory=list)
    tuid: Optional[str] = None
    encoding: Optional[str] = None
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
    tmf: Optional[str] = None
    srclang: Optional[str] = None


class Tmx(TmxElement):
    version: str = "1.4"
    header: Header = Field(exclude=True)
    tus: list[Tu] = Field(exclude=True, default_factory=list)


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
