import logging
import lxml.etree as LET

from python_tmx.xml.backends.base import XMLBackend

logger = logging.getLogger(__name__)

__all__ = ["LxmlBackend"]

class LxmlBackend(XMLBackend[LET._Element]):
  """lxml-based XML backend."""

  def __init__(self):
    logger.info("Initialized lxml backend")

  def make_elem(self, tag: str) -> LET.Element:
    return LET.Element(tag)

  def set_attr(self, element: LET._Element, key: str, val: str) -> None:
    element.set(key, val)

  def set_text(self, element: LET._Element, text: str | None) -> None:
    element.text = text

  def append(self, parent: LET._Element, child: LET._Element) -> None:
    parent.append(child)
