from collections.abc import Iterator

from lxml.etree import QName, iterparse, tostring

from PythonTmx.core import BaseTmxElement, TmxParser
from PythonTmx.errors import ParsingError
from PythonTmx.tag_map import __TAG_MAP__


class LxmlTmxParser(TmxParser):
  def iter(
    self, mask: str | tuple[str, ...] | None = None
  ) -> Iterator[BaseTmxElement]:
    tag_mask = (
      tuple(__TAG_MAP__.keys())
      if mask is None
      else (mask,)
      if isinstance(mask, str)
      else mask
    )
    if not all(x in __TAG_MAP__ for x in tag_mask):
      raise ValueError("All elements in mask must be valid tmx tags")
    for _, element in iterparse(self.source, events=("end",)):
      localname = QName(element).localname
      if localname in tag_mask:
        try:
          yield __TAG_MAP__[localname].from_xml(element)
        except Exception as e:
          elem_preview = tostring(
            element, encoding="unicode", pretty_print=True
          )
          line_no: str = (
            "?" if not element.sourceline else str(element.sourceline)
          )
          msg = f"Error at line {line_no} parsing <{localname}>: {e}\nElement:\n{elem_preview}"
          match e:
            case KeyError():
              raise ParsingError(
                f"Missing attribute: {msg}", localname, line_no, elem_preview, e
              ) from e
            case AttributeError():
              raise ParsingError(
                f"Missing property: {msg}", localname, line_no, elem_preview, e
              ) from e
            case ValueError():
              raise ParsingError(
                f"Invalid value: {msg}", localname, line_no, elem_preview, e
              ) from e
            case TypeError():
              raise ParsingError(
                f"Type error: {msg}", localname, line_no, elem_preview, e
              ) from e
            case _:
              raise ParsingError(
                f"Unknown error: {msg}", localname, line_no, elem_preview, e
              ) from e
        finally:
          element.clear()
