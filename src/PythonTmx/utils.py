import os
import pathlib as pl
import typing as tp
import xml.etree.ElementTree as pyet
from warnings import warn

import lxml.etree as lxet

from PythonTmx import (
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

__ElementMap: tp.Dict[str, tp.Type[TmxElement]] = {
  "tmx": Tmx,
  "header": Header,
  "note": Note,
  "prop": Prop,
  "ude": Ude,
  "map": Map,
  "tu": Tu,
  "tuv": Tuv,
  "bpt": Bpt,
  "ept": Ept,
  "hi": Hi,
  "it": It,
  "ph": Ph,
  "sub": Sub,
  "ut": Ut,
}


def from_element(element: pyet.Element | lxet._Element) -> TmxElement:
  if str(element.tag) not in __ElementMap:
    raise ValueError(f"Unknown tag: {element.tag!r}")
  return __ElementMap[str(element.tag)].from_element(element)


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
  else:
    raise TypeError(
      f"Path must be str, a pathLike object, or a file-like object, not {type(path).__name__!r}"
    )


def from_file(
  path: tp.Union[str, pl.Path, os.PathLike, tp.TextIO, tp.BinaryIO],
  engine: tp.Literal["lxml", "python"] = "lxml",
) -> Tmx:
  _check_path(path)
  root = lxet.parse(path).getroot() if engine == "lxml" else pyet.parse(path).getroot()
  if root.tag != "tmx":
    raise ValueError(f"Expected <tmx> as root but got {root.tag!r}")
  return Tmx.from_element(root)
