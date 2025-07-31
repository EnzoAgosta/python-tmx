from collections import deque
from collections.abc import Generator, Iterable
from os import PathLike
from typing import Literal

from lxml.etree import Element, QName, _Element, iterparse, parse  # type: ignore

from PythonTmx.core import BaseTmxElement, TmxFileParser
from PythonTmx.elements import __TAG_MAP__
from PythonTmx.parsers.utils import create_tag_mask
from PythonTmx.utils import ensure_file_exists


class LxmlParser(TmxFileParser):
  """Standard implementation of TMX file parser using ElementTree.

  This parser provides a complete implementation of the TmxFileParser interface,
  using Python's built-in xml.etree.ElementTree for XML processing. It offers
  both full document parsing with configurable traversal strategies and memory-efficient
  lazy parsing for large files.

  The StandardParser is the default parser implementation and is suitable for
  most TMX processing needs. It supports filtering by tag names and provides
  both breadth-first and depth-first traversal strategies.

  Attributes:
    source: The validated file path to the TMX file being parsed.
  """

  def __init__(self, source: str | PathLike[str]) -> None:
    """Initialize the standard parser with a TMX file source.

    Args:
      source: Path to the TMX file to parse. Must be a valid file path.

    Raises:
      FileNotFoundError: If the specified file does not exist.
      PermissionError: If the file cannot be read due to permissions.
    """
    self.source = ensure_file_exists(source)

  def iter(
    self,
    mask: str | Iterable[str] | None = None,
    /,
    strategy: Literal["breadth_first", "depth_first"] = "breadth_first",
    exclude: bool = False,
  ) -> Generator[BaseTmxElement]:
    """Iterate through TMX elements with specified filtering and traversal strategy.

    This method parses the entire TMX file into memory and yields elements
    according to the specified strategy and filtering criteria. It provides
    full access to the document structure but requires more memory than lazy_iter.


    The method supports two traversal strategies:
    - Breadth-first: Yields all matching siblings before checking children of each node, in document order
    - Depth-first: Yields all children of a node before moving to the next sibling, in document order

    Assuming the following (simplified) TMX file and a mask of "prop":
    .. code-block:: xml
        <?xml version="1.0" encoding="UTF-8"?>
        <tmx>
          <header>
            <prop>Header prop</prop>
          </header>
          <tu>
            <tuv>
              <prop>tuv prop</prop>
            </tuv>
          </tu>
          <tu>
            <prop>tu prop</prop>
          </tu>
        </tmx>

    Breadth-first traversal will yield in order:
    - Header prop
    - tu prop
    - tuv prop

    Depth-first traversal will yield in order:
    - Header prop
    - tuv prop
    - tu prop

    Args:
      mask: Tag names to filter by. Can be a single string, iterable of strings,
            or None to include all elements. Defaults to None.
      strategy: Traversal strategy for processing the XML tree.
                - "breadth_first": Process all children before grandchildren (default)
                - "depth_first": Process each branch completely before moving to siblings
      exclude: If True, exclude elements matching the mask instead of including them.
               Defaults to False.

    Yields:
      BaseTmxElement: TMX elements matching the filter criteria.

    Raises:
      ValueError: If an unknown strategy is specified.
      XMLSyntaxError: If the TMX file contains invalid XML.
    """

    def _depth_first(
      root_node: _Element, tag_mask: tuple[str, ...]
    ) -> Generator[BaseTmxElement]:
      """Depth-first traversal implementation using a stack.

      Args:
        root_node: The root XML element to traverse.
        tag_mask: Tuple of tag names to include/exclude.

      Yields:
        BaseTmxElement: Elements matching the tag mask in depth-first order.
      """
      stack: deque[tuple[_Element, bool]] = deque([(root_node, False)])
      while stack:
        node, yielded_ancestor = stack.pop()
        tag = QName(node.tag).localname
        if tag in tag_mask and not yielded_ancestor:
          elem = __TAG_MAP__[tag].from_xml(node)
          elem.set_default_factory(factory=Element)
          yield elem
          continue
        for child in reversed(node):
          stack.append((child, yielded_ancestor))

    def _breadth_first(
      root_node: _Element, tag_mask: tuple[str, ...]
    ) -> Generator[BaseTmxElement]:
      """Breadth-first traversal implementation using a queue.

      Args:
        root_node: The root XML element to traverse.
        tag_mask: Tuple of tag names to include/exclude.

      Yields:
        BaseTmxElement: Elements matching the tag mask in breadth-first order.
      """
      queue: deque[_Element] = deque([root_node])
      while queue:
        node = queue.popleft()
        tag = QName(node.tag).localname
        if node.tag in tag_mask:
          elem = __TAG_MAP__[tag].from_xml(node)
          elem.set_default_factory(factory=Element)
          yield elem
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
    """Iterate through TMX elements using memory-efficient lazy parsing.

    This method uses incremental XML parsing to yield elements as they are
    encountered, without loading the entire document into memory. It's ideal
    for processing large TMX files efficiently, but provides less control
    over traversal order as it can only yield elements in document order
    (i.e. depth-first).

    Args:
      mask: Tag names to filter by. Can be a single string, iterable of strings,
            or None to include all elements. Defaults to None.
      exclude: If True, exclude elements matching the mask instead of including them.
               Defaults to False.

    Yields:
      BaseTmxElement: TMX elements matching the filter criteria in document order.

    Raises:
      XMLSyntaxError: If the TMX file contains invalid XML.
    """
    tag_mask = create_tag_mask(mask, exclude)
    context = iterparse(self.source, events=("start", "end"))

    _, root = next(context)
    stack: list[_Element] = []
    yielded: set[_Element] = set()

    for event, node in context:
      if event == "start":
        stack.append(node)
      else:
        tag = QName(node.tag).localname
        if node.tag in tag_mask:
          if not any(parent in yielded for parent in stack[:-1]):
            elem = __TAG_MAP__[tag].from_xml(node)
            elem.set_default_factory(factory=Element)
            yield elem
            yielded.add(node)
          if node is not root:
            node.clear()
          stack.pop()
