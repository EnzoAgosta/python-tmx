import os
import pathlib as pl
import typing as tp
import xml.etree.ElementTree as pyet
from warnings import warn

import lxml.etree as lxet

import PythonTmx.classes as cl

__TYPES: tp.Dict[str, tp.Type[tp.Any]] = {
  "ude": cl.Ude,
  "map": cl.Map,
}


def from_element(element: pyet.Element | lxet._Element) -> tp.Optional[tp.Any]:
  tag = str(element.tag)
  if tag.lower() not in __TYPES:
    raise ValueError(f"Unknown tag: {tag!r}")
  return __TYPES[tag.lower()].from_element(element)


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
