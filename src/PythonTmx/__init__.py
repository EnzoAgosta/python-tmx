import os
import pathlib as pl
import typing as tp
import xml.etree.ElementTree as pyet
from warnings import warn

import lxml.etree as lxet

from PythonTmx.classes import (
  ASSOC,
  POS,
  SEGTYPE,
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
  Tu,
  Tuv,
  Ude,
  Ut,
)

TmxElement = tp.Union[
  Tmx,
  Header,
  Ude,
  Map,
  Note,
  Prop,
  Tu,
  Tuv,
  Bpt,
  Ept,
  Hi,
  It,
  Ph,
  Sub,
  Ut,
]


def from_element(element: pyet.Element | lxet._Element) -> TmxElement:
  match element.tag:
    case "bpt":
      return Bpt.from_element(element)
    case "ept":
      return Ept.from_element(element)
    case "header":
      return Header.from_element(element)
    case "hi":
      return Hi.from_element(element)
    case "it":
      return It.from_element(element)
    case "map":
      return Map.from_element(element)
    case "note":
      return Note.from_element(element)
    case "ph":
      return Ph.from_element(element)
    case "prop":
      return Prop.from_element(element)
    case "sub":
      return Sub.from_element(element)
    case "tmx":
      return Tmx.from_element(element)
    case "tu":
      return Tu.from_element(element)
    case "tuv":
      return Tuv.from_element(element)
    case "ude":
      return Ude.from_element(element)
    case "ut":
      return Ut.from_element(element)
    case _:
      raise ValueError(f"Unknown tag: {element.tag!r}")


def from_string(string: str) -> TmxElement:
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
) -> TmxElement:
  _check_path(path)
  root = lxet.parse(path).getroot()
  return from_element(root)
