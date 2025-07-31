from collections import deque
from collections.abc import Generator, Iterable
from os import PathLike
from typing import Literal
from xml.etree.ElementTree import Element, iterparse, parse

from PythonTmx.core import BaseTmxElement, TmxFileParser
from PythonTmx.elements import __TAG_MAP__
from PythonTmx.utils import ensure_file_exists


def create_tag_mask(mask: str | Iterable[str] | None, exclude: bool) -> tuple[str, ...]:
  tag_mask: tuple[str, ...]
  match mask:
    case None:
      tag_mask = tuple(__TAG_MAP__.keys())
    case str():
      if mask not in __TAG_MAP__:
        raise ValueError(f"Unknown tag {mask!r}")
      if exclude:
        tag_mask = tuple(tag for tag in __TAG_MAP__.keys() if tag != mask)
      else:
        tag_mask = (mask,)
    case Iterable():
      _mask = tuple(mask)
      for tag in _mask:
        if tag not in __TAG_MAP__:
          raise ValueError(f"Unknown tag {tag!r}")
      if exclude:
        tag_mask = tuple(tag for tag in __TAG_MAP__.keys() if tag not in _mask)
      else:
        tag_mask = _mask
  return tag_mask


class StandardParser(TmxFileParser):
  def __init__(self, source: str | PathLike[str]) -> None:
    self.source = ensure_file_exists(source)

  def iter(
    self,
    mask: str | Iterable[str] | None = None,
    /,
    strategy: Literal["breadth_first", "depth_first"] = "breadth_first",
    exclude: bool = False,
  ) -> Generator[BaseTmxElement]:
    def _depth_first(
      root_node: Element, tag_mask: tuple[str, ...]
    ) -> Generator[BaseTmxElement]:
      stack: deque[tuple[Element, bool]] = deque([(root_node, False)])
      while stack:
        node, yielded_ancestor = stack.pop()
        if node.tag in tag_mask and not yielded_ancestor:
          yield __TAG_MAP__[node.tag].from_xml(node)
          continue
        for child in reversed(node):
          stack.append((child, yielded_ancestor))

    def _breadth_first(
      root_node: Element, tag_mask: tuple[str, ...]
    ) -> Generator[BaseTmxElement]:
      queue: deque[Element] = deque([root_node])
      while queue:
        node = queue.popleft()
        if node.tag in tag_mask:
          yield __TAG_MAP__[node.tag].from_xml(node)
          continue
        for child in node:
          queue.append(child)

    tag_mask = create_tag_mask(mask, exclude)
    root = parse(self.source).getroot()

    match strategy:
      case "breadth_first":
        yield from _breadth_first(root, tag_mask)
      case "depth_first":
        yield from _depth_first(root, tag_mask)
      case _:  # type: ignore
        raise ValueError(f"Unknown strategy {strategy!r}")

  def lazy_iter(
    self,
    mask: str | Iterable[str] | None = None,
    exclude: bool = False,
  ) -> Generator[BaseTmxElement]:
    tag_mask = create_tag_mask(mask, exclude)
    context = iterparse(self.source, events=("start", "end"))

    _, root = next(context)
    stack: list[Element] = []
    yielded: set[Element] = set()

    for event, element in context:
      if event == "start":
        stack.append(element)
      else:
        if element.tag in tag_mask:
          if not any(parent in yielded for parent in stack[:-1]):
            yield __TAG_MAP__[element.tag].from_xml(element)
            yielded.add(element)
          if element is not root:
            element.clear()
          stack.pop()
