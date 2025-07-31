from collections import deque
from collections.abc import Generator, Iterable
from os import PathLike
from typing import Literal
from xml.etree.ElementTree import (
  Element,
  iterparse,
  parse,
)

from PythonTmx.core import BaseTmxElement, TmxFileParser
from PythonTmx.elements import __TAG_MAP__
from PythonTmx.elements.tmx import Tmx
from PythonTmx.errors import SerializationError, WrongTagError, XmlParsingError
from PythonTmx.parsers.utils import create_tag_mask
from PythonTmx.utils import ensure_file_exists, get_local_name


class StandardParser(TmxFileParser):
  """Implementation of TMX file parser using the Standard library.

  This parser provides a complete implementation of the TmxFileParser interface,
  using standard for XML processing. It offers both full document parsing with configurable
  traversal strategies and memory-efficient lazy parsing for large files.

  It acts as a drop-in replacement for the LxmlParser though due to limitations
  from the Standard library ElementTree API, it might not be as performant as
  the LxmlParser and it cannot provide line numbers when encountering errors.

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
    *,
    include_tmx: bool = False,
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
      root_node: Element, tag_mask: tuple[str, ...]
    ) -> Generator[BaseTmxElement]:
      """Depth-first traversal implementation using a stack.

      Args:
        root_node: The root XML element to traverse.
        tag_mask: Tuple of tag names to include/exclude.

      Yields:
        BaseTmxElement: Elements matching the tag mask in depth-first order.
      """
      stack: deque[tuple[Element, bool]] = deque([(root_node, False)])
      while stack:
        node, yielded_ancestor = stack.pop()
        tag = get_local_name(node.tag)
        if tag not in __TAG_MAP__ and tag not in ("body", "seg"):
          tag_err = WrongTagError(tag, ", ".join(__TAG_MAP__.keys()))
          raise XmlParsingError(tag, original_exception=tag_err) from tag_err
        if tag in tag_mask and not yielded_ancestor:
          try:
            elem = __TAG_MAP__[tag].from_xml(node)
            elem.set_default_factory(factory=Element)
            yield elem
          except SerializationError as e:
            raise XmlParsingError(tag, original_exception=e) from e
          continue
        for child in reversed(node):
          stack.append((child, yielded_ancestor))

    def _breadth_first(
      root_node: Element, tag_mask: tuple[str, ...]
    ) -> Generator[BaseTmxElement]:
      """Breadth-first traversal implementation using a queue.

      Args:
        root_node: The root XML element to traverse.
        tag_mask: Tuple of tag names to include/exclude.

      Yields:
        BaseTmxElement: Elements matching the tag mask in breadth-first order.
      """
      queue: deque[Element] = deque([root_node])
      while queue:
        node = queue.popleft()
        tag = get_local_name(node.tag)
        if tag not in __TAG_MAP__ and tag not in ("body", "seg"):
          tag_err = WrongTagError(tag, ", ".join(__TAG_MAP__.keys()))
          raise XmlParsingError(tag, original_exception=tag_err) from tag_err
        if tag in tag_mask:
          try:
            elem = __TAG_MAP__[tag].from_xml(node)
            elem.set_default_factory(factory=Element)
            yield elem
          except SerializationError as e:
            raise XmlParsingError(tag, original_exception=e) from e
          continue
        for child in node:
          queue.append(child)

    tag_mask = create_tag_mask(mask, exclude, include_tmx)
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
    include_tmx: bool = False,
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
    tag_mask = create_tag_mask(mask, exclude, include_tmx)
    context = iterparse(self.source, events=("start", "end"))

    _, __ = next(context)
    node_to_yield = None
    for event, node in context:
      tag = get_local_name(node.tag)
      if tag not in __TAG_MAP__ and tag not in ("body", "seg"):
        tag_err = WrongTagError(tag, ", ".join(__TAG_MAP__.keys()))
        raise XmlParsingError(tag, original_exception=tag_err) from tag_err
      if node_to_yield is not None:
        if node is node_to_yield and event == "end":
          try:
            elem = __TAG_MAP__[tag].from_xml(node)
            elem.set_default_factory(factory=Element)
            yield elem
          except SerializationError as e:
            raise XmlParsingError(tag, original_exception=e) from e
          node_to_yield = None
          node.clear()
        continue
      if tag in tag_mask:
        node_to_yield = node
        continue

  def get_tmx(self) -> Tmx:
    """Get the TMX element from the parsed file.

    Returns:
      The TMX element from the parsed file.

    Raises:
      ValueError: If the TMX element is not present in the parsed file.
    """
    root = parse(self.source).getroot()
    tag = get_local_name(root.tag)
    if not tag == "tmx":
      raise WrongTagError(tag, "tmx")
    return Tmx.from_xml(root)
