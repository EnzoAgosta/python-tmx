from collections.abc import Iterator
from os import PathLike
from pathlib import Path

from lxml.etree import QName, iterparse

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  TmxParser,
)
from PythonTmx.tag_map import __TAG_MAP__
from PythonTmx.utils import ensure_file, raise_parsing_errors


class LazyLxmlParser(TmxParser):
  def __init__(self, source: PathLike[str] | Path | str) -> None:
    source = ensure_file(source)
    self.source = source

  def iter(
    self,
    mask: str | tuple[str, ...] | None = None,
    mask_exclude: bool = False,
    default_factory: AnyElementFactory[..., AnyXmlElement] | None = None,
  ) -> Iterator[BaseTmxElement]:
    tag_mask = (
      tuple(__TAG_MAP__.keys())
      if mask is None
      else (mask,)
      if isinstance(mask, str)
      else tuple(mask)
    )
    if not all(x in __TAG_MAP__ for x in tag_mask):
      raise ValueError("All elements in mask must be valid tmx tags")
    if mask_exclude and mask is not None:
      tag_mask = tuple(tag for tag in __TAG_MAP__ if tag not in tag_mask)
    for _, element in iterparse(self.source, events=("end",)):
      localname = QName(element).localname
      if localname in tag_mask:
        try:
          tmx_element = __TAG_MAP__[localname].from_xml(element)
          if default_factory is not None:
            tmx_element.set_default_factory(default_factory)
          yield tmx_element
        except Exception as e:
          line_no: str = (
            "?" if element.sourceline in (None, 0) else str(element.sourceline)
          )
          raise_parsing_errors(localname, line_no, e)
        finally:
          element.clear()
