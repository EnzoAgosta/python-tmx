import logging
import xml.etree.ElementTree as ET

from python_tmx.xml.backends.base import XMLBackend

logger = logging.getLogger(__name__)

__all__ = ["StandardBackend"]

class StandardBackend(XMLBackend[ET.Element]):
  """Standard Library-based XML backend."""

  def __init__(self):
    logger.info("Initialized Standard Library backend")

  def make_elem(self, tag: str) -> ET.Element:
    return ET.Element(tag)

  def set_attr(self, element: ET.Element, key: str, val: str) -> None:
    element.set(key, val)

  def set_text(self, element: ET.Element, text: str | None) -> None:
    element.text = text

  def append(self, parent: ET.Element, child: ET.Element) -> None:
    parent.append(child)
