import dataclasses as dc
import datetime as dt
import enum
import os
import pathlib as pl
import typing as tp
import xml.etree.ElementTree as pyet
from warnings import warn

import lxml.etree as lxet

import PythonTmx.classes as cl

__TYPES: tp.Dict[str, tp.Type[cl.Structural | cl.Inline]] = {
  "ude": cl.Ude,
  "map": cl.Map,
  "note": cl.Note,
  "prop": cl.Prop,
  "tmx": cl.Tmx,
  "tu": cl.Tu,
  "tuv": cl.Tuv,
  "header": cl.Header,
  "ph": cl.Ph,
  "bpt": cl.Bpt,
  "ept": cl.Ept,
  "it": cl.It,
  "hi": cl.Hi,
  "sub": cl.Sub,
  "ut": cl.Ut,
}


def from_element(element: pyet.Element | lxet._Element) -> tp.Optional[tp.Any]:
  tag = str(element.tag)
  if tag.lower() not in __TYPES:
    raise ValueError(f"Unknown tag: {tag!r}")
  return __TYPES[tag.lower()].from_element(element)  # type:ignore


def from_string(string: str) -> tp.Optional[tp.Any]:
  return from_element(lxet.fromstring(string))


def _check_path(
  path: tp.Union[str, pl.Path, os.PathLike, tp.TextIO, tp.BinaryIO],
) -> None:
  if isinstance(path, (tp.TextIO, tp.BinaryIO)):
    return
  if isinstance(path, (str, os.PathLike)):
    path = pl.Path(path)
  if isinstance(path, pl.Path):
    if not path.exists():
      raise FileNotFoundError(f"Path not found: {path!r}")
    if not path.is_file():
      raise IsADirectoryError(f"Path is not a file: {path!r}")
    if path.suffix.lower() != ".tmx":
      warn(f"File suffix is not .tmx: {path!r}")


def from_file(
  path: tp.Union[str, pl.Path, os.PathLike, tp.TextIO, tp.BinaryIO],
) -> tp.Optional[tp.Any]:
  _check_path(path)
  root = lxet.parse(path).getroot()
  return from_element(root)


def _make_xml_attrs(obj: dc._DataclassT, kwargs: dict[str, tp.Any]) -> dict[str, str]:
  xml_attrs: dict[str, str] = dict()
  for field in dc.fields(obj):
    if not field.metadata.get("exclude", False):
      val = kwargs.pop(field.name, getattr(obj, field.name))
      if not isinstance(val, field.type):  # type:ignore
        raise TypeError(
          f"Expected one of {field.type!r} for {field.name!r} but got {type(val)!r}"
        )
      if isinstance(val, int):
        val = str(val)
      elif isinstance(val, enum.Enum):
        val = val.value
      elif isinstance(val, dt.datetime):
        val = val.strftime("%Y%m%dT%H%M%SZ")
      elif isinstance(val, str):
        pass
      xml_attrs[field.metadata.get("export_name", field.name)] = val
  return xml_attrs


def _make_elem(
  tag: str, attrib: dict[str, str], engine: tp.Literal["python", "lxml"]
) -> lxet._Element | pyet.Element:
  if engine == "lxml":
    return lxet.Element(tag, attrib=attrib)
  elif engine == "python":
    return pyet.Element(tag, attrib=attrib)
  else:
    raise ValueError(f"Unknown engine: {engine!r}")


def _parse_content(element: pyet.Element | lxet._Element) -> list[str | cl.Inline]:
  content: list[str | cl.Inline] = []
  if element.text:
    content.append(element.text)
  for child in element:
    if child.tag not in __TYPES:
      raise ValueError(f"Unknown tag: {child.tag!r}")
    if child.tag not in {"sub", "it", "hi", "bpt", "ept", "ph", "ut"}:
      raise ValueError(f"Non inline tag: {child.tag!r}")
    content.append(__TYPES[child.tag].from_element(child))  # type:ignore
    if child.tail:
      content.append(child.tail)
  return content


def _add_content(
  elem: lxet._Element | pyet.Element,
  content: list[str | cl.Inline],
  engine: tp.Literal["lxml", "python"],
  allowed_types: tuple[tp.Type, ...],
) -> None:
  last: pyet.Element | lxet._Element = elem
  for item in content:
    if not isinstance(item, allowed_types):
      raise TypeError(
        f"Expected a str or one of {allowed_types!r} element but got {type(item)!r}"
      )
    if isinstance(item, str):
      if last is elem:
        if elem.text:
          elem.text += item
        else:
          elem.text = item
      else:
        if last.tail:
          last.tail += item
        else:
          last.tail = item
    elif isinstance(item, cl.Inline):
      last = item.to_element(engine)
      elem.append(last)  # type:ignore
