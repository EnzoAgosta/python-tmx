from os import PathLike

from lxml.etree import XMLParser, _Element, parse

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
    "from_element",
    "from_file",
]


def from_element(element: _Element) -> TmxElement:
    def _content_from_elem(element: _Element) -> list[str | TmxElement] | str:
        content = [element.text]
        for child in element:
            content.append(from_element(child))
            content.append(child.tail)
        content = (
            [x for x in content if x is not None] if len(content) > 1 else content[0]
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
            return Ude(
                maps=[Map(**m.attrib) for m in element.iter("map")],
                name=element.get("name"),
                base=element.get("base"),
            )
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
            if not isinstance(segment, str):
                segment = [i for i in segment if i is not None]
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


def from_file(
    file: str | bytes | PathLike[str] | PathLike[bytes],
    encoding: str = "utf-8",
) -> TmxElement:
    return from_element(parse(file, XMLParser(encoding=encoding)).getroot())
