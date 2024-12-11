from collections.abc import Callable

import lxml.etree as et

import PythonTmx.classes as cl

__all__ = ["from_element", "to_element"]

__from_elem_func_dict__: dict[str, Callable[..., cl.TmxElement]] = {
  "tu": cl.Tu._from_element,
  "tuv": cl.Tuv._from_element,
  "note": cl.Note._from_element,
  "prop": cl.Prop._from_element,
  "tmx": cl.Tmx._from_element,
  "ude": cl.Ude._from_element,
  "map": cl.Map._from_element,
  "bpt": cl.Bpt._from_element,
  "ept": cl.Ept._from_element,
  "it": cl.It._from_element,
  "hi": cl.Hi._from_element,
  "ph": cl.Ph._from_element,
  "ut": cl.Ut._from_element,
  "sub": cl.Sub._from_element,
}
__to_elem_func_dict__: dict[str, Callable[..., et._Element]] = {
  "tu": cl.Tu._to_element,
  "tuv": cl.Tuv._to_element,
  "note": cl.Note._to_element,
  "prop": cl.Prop._to_element,
  "tmx": cl.Tmx._to_element,
  "ude": cl.Ude._to_element,
  "map": cl.Map._to_element,
  "bpt": cl.Bpt._to_element,
  "ept": cl.Ept._to_element,
  "it": cl.It._to_element,
  "hi": cl.Hi._to_element,
  "ph": cl.Ph._to_element,
  "ut": cl.Ut._to_element,
  "sub": cl.Sub._to_element,
}


def from_element(
  element: cl.XmlElement, ignore_unknown: bool = False
) -> cl.TmxElement | None:
  """
  This the main and recommended way to create TmxElement objects from xml
  elements, for example when reading from a file.

  It will create any possible TmxElement from the given element based on its tag.
  If the tag is not recognized, it will raise a ValueError (or silently move to
  the next if ignore_unknown is True).

  Parameters
  ----------
  element : XmlElement
      The element to create the TmxElement from.
  ignore_unknown : bool, optional
      Whether to silently ignore unknown tags. If False, any unknown tag will
      raise a ValueError. Default is False.

  Returns
  -------
  TmxElement
      Any TmxElement that can be created from the provided xml element.
  """
  global __from_elem_func_dict__
  e: Callable[..., cl.TmxElement] | None = __from_elem_func_dict__.get(str(element.tag))
  if e is None:
    if ignore_unknown:
      return None
    else:
      raise ValueError(f"Unknown element {str(element.tag)}")
  else:
    return e(element)


def to_element(obj: cl.TmxElement) -> et._Element:
  global __to_elem_func_dict__
  e: Callable[..., et._Element] | None = __to_elem_func_dict__.get(
    obj.__class__.__name__.lower()
  )
  if e is None:
    raise ValueError(f"Unknown element {str(obj.__class__.__name__)}")
  else:
    return e(obj)
