import xml.etree.ElementTree
from functools import partial
from os import PathLike
from typing import Literal

import lxml.etree

from .models import (
    Bpt,
    Ept,
    Header,
    Hi,
    It,
    Map,
    Note,
    Ph,
    Prop,
    Sub,
    Tmx,
    TmxElement,
    Tu,
    Tuv,
    Ude,
    Ut,
)

XML = "{http://www.w3.org/XML/1998/namespace}"

__all__ = [
    "to_element",
    "from_element",
    "to_file",
    "from_file",
]


def from_element(
    element: lxml.etree._Element | xml.etree.ElementTree.Element,
) -> TmxElement:
    def _content_from_elem(
        element: lxml.etree._Element | xml.etree.ElementTree.Element,
    ) -> list[str | TmxElement] | str:
        content = [element.text]
        for child in element:
            content.append(from_element(child))
            content.append(child.tail)
        content = (
            list(filter(lambda x: x is not None, content))
            if len(content) > 1
            else content[0]
        )
        return content

    match element.tag:
        case "note":
            return Note(
                content=element.text,
                encoding=element.get("o-encoding"),
                lang=element.get(f"{XML}lang"),
            )
        case "prop":
            return Prop(
                content=element.text,
                type=element.get("type"),
                lang=element.get(f"{XML}lang"),
                encoding=element.get("o-encoding"),
            )
        case "map":
            return Map(
                unicode=element.get("unicode"),
                code=element.get("code"),
                ent=element.get("ent"),
                subst=element.get("subst"),
            )
        case "ude":
            maps = []
            for child in element:
                if not child.tag == "map":
                    raise ValueError(
                        f"Ude elements are only allowed to have Map elements as children but found: {child.tag}"
                    )
                maps.append(from_element(child))
            return Ude(maps=maps, name=element.get("name"), base=element.get("base"))
        case "header":
            notes, props, udes = [], [], []
            for child in element:
                if child.tag == "note":
                    notes.append(from_element(child))
                elif child.tag == "prop":
                    props.append(from_element(child))
                elif child.tag == "ude":
                    udes.append(from_element(child))
            return Header(
                notes=notes,
                props=props,
                udes=udes,
                creationtool=element.get("creationtool"),
                creationtoolversion=element.get("creationtoolversion"),
                segtype=element.get("segtype"),
                tmf=element.get("o-tmf"),
                adminlang=element.get("adminlang"),
                srclang=element.get("srclang"),
                datatype=element.get("datatype"),
                encoding=element.get("o-encoding"),
                creationdate=element.get("creationdate"),
                creationid=element.get("creationid"),
                changedate=element.get("changedate"),
                changeid=element.get("changeid"),
            )
        case "tu":
            notes, props, tuvs = [], [], []
            for child in element:
                if child.tag == "note":
                    notes.append(from_element(child))
                elif child.tag == "prop":
                    props.append(from_element(child))
                elif child.tag == "tuv":
                    tuvs.append(from_element(child))
            return Tu(
                tuvs=tuvs,
                notes=notes,
                props=props,
                tuid=element.get("tuid"),
                encoding=element.get("o-encoding"),
                datatype=element.get("datatype"),
                usagecount=element.get("usagecount"),
                lastusagedate=element.get("lastusagedate"),
                creationtool=element.get("creationtool"),
                creationtoolversion=element.get("creationtoolversion"),
                creationdate=element.get("creationdate"),
                creationid=element.get("creationid"),
                changedate=element.get("changedate"),
                segtype=element.get("segtype"),
                changeid=element.get("changeid"),
                tmf=element.get("o-tmf"),
                srclang=element.get("srclang"),
            )
        case "tuv":
            notes, props, segment = [], [], []
            for child in element:
                if child.tag == "note":
                    notes.append(from_element(child))
                elif child.tag == "prop":
                    props.append(from_element(child))
            seg = element.find("seg")
            segment.append(seg.text)
            for child in seg:
                segment.append(from_element(child))
                segment.append(child.tail)
            segment = (
                list(filter(lambda x: x is not None, segment))
                if len(segment) > 1
                else segment[0]
            )
            return Tuv(
                content=segment,
                notes=notes,
                props=props,
                lang=element.get(f"{XML}lang"),
                encoding=element.get("o-encoding"),
                datatype=element.get("datatype"),
                usagecount=element.get("usagecount"),
                lastusagedate=element.get("lastusagedate"),
                creationtool=element.get("creationtool"),
                creationtoolversion=element.get("creationtoolversion"),
                creationdate=element.get("creationdate"),
                creationid=element.get("creationid"),
                changedate=element.get("changedate"),
                changeid=element.get("changeid"),
                tmf=element.get("o-tmf"),
            )
        case "tmx":
            header = from_element(element.find("header"))
            tus = [from_element(child) for child in element.iter("tu")]
            return Tmx(header=header, tus=tus)
        case "bpt":
            return Bpt(
                content=_content_from_elem(element),
                i=element.get("i"),
                x=element.get("x"),
                type=element.get("type"),
            )
        case "ept":
            return Ept(
                content=_content_from_elem(element),
                i=element.get("i"),
            )
        case "ph":
            return Ph(
                content=_content_from_elem(element),
                assoc=element.get("assoc"),
                x=element.get("x"),
                type=element.get("type"),
            )
        case "it":
            return It(
                content=_content_from_elem(element),
                pos=element.get("pos"),
                x=element.get("x"),
                type=element.get("type"),
            )
        case "hi":
            return Hi(
                content=_content_from_elem(element),
                x=element.get("x"),
                type=element.get("type"),
            )
        case "sub":
            return Sub(
                content=_content_from_elem(element),
                datatype=element.get("datatype"),
                type=element.get("type"),
            )
        case "ut":
            return Ut(
                content=_content_from_elem(element),
                x=element.get("x"),
            )


def to_element(
    obj: TmxElement, engine: Literal["lxml", "stdlib"] = "lxml"
) -> lxml.etree._Element | xml.etree.ElementTree.Element:
    obj.model_validate(obj)
    if engine == "lxml":
        e = lxml.etree.Element
    elif engine == "stdlib":
        e = xml.etree.ElementTree.Element

    element = e(
        obj.__repr_name__().lower(),
        attrib=obj.model_dump(
            exclude_none=True,
        ),
    )
    if hasattr(obj, "header"):
        element.append(to_element(obj.header))
    if hasattr(obj, "tus"):
        for child in obj.tus:
            element.append(to_element(child))
    if hasattr(obj, "notes"):
        for child in obj.notes:
            element.append(to_element(child))
    if hasattr(obj, "props"):
        for child in obj.props:
            element.append(to_element(child))
    if hasattr(obj, "tuvs"):
        for child in obj.tuvs:
            element.append(to_element(child))
    if hasattr(obj, "maps"):
        for child in obj.maps:
            element.append(to_element(child))
    if hasattr(obj, "udes"):
        for child in obj.udes:
            element.append(to_element(child))
    if hasattr(obj, "content"):
        if element.tag == ("tuv"):
            element.append(e("seg"))
            content = element[-1]
        else:
            content = element
        if isinstance(obj.content, str):
            content.text = obj.content
        else:
            for child in content:
                if isinstance(child, str):
                    if len(content):
                        content[-1].tail = child
                    elif content.text:
                        content.text += child
                    else:
                        content.text = child
                else:
                    content.append(to_element(child))
    return element


def from_file(
    file: str | bytes | PathLike[str] | PathLike[bytes],
    engine: Literal["lxml", "stdlib"] = "lxml",
    encoding: str = "utf-8",
) -> TmxElement:
    if engine == "lxml":
        p = partial(lxml.etree.parse, parser=lxml.etree.XMLParser(encoding=encoding))
    elif engine == "stdlib":
        p = xml.etree.ElementTree.parse
    if not isinstance(file, (str, bytes, PathLike)):
        raise TypeError
    with open(file, "r", encoding=encoding) as f:
        tree = p(f)
    return from_element(tree.getroot())


def to_file(
    tmx: Tmx,
    file: str | bytes | PathLike[str] | PathLike[bytes],
    engine: Literal["lxml", "stdlib"] = "lxml",
    encoding: str = "utf-8",
) -> None:
    if engine == "lxml":
        t = lxml.etree.ElementTree
        w = lxml.etree._ElementTree.write
    elif engine == "stdlib":
        t = xml.etree.ElementTree.ElementTree
        w = t.write
    if not isinstance(file, (str, bytes, PathLike)):
        raise TypeError
    tree = t(to_element(tmx))
    if engine == "lxml":
        with open(file, "wb") as f:
            w(tree, f, encoding=encoding, xml_declaration=True)
    elif engine == "stdlib":
        with open(file, "w", encoding=encoding) as f:
            w(tree, f, encoding=encoding, xml_declaration=True)
