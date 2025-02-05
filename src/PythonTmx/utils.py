import dataclasses as dc
import datetime as dt
import enum
import typing as tp
import xml.etree.ElementTree as pyet

import lxml.etree as lxet


def _make_xml_attrs(obj: object, **kwargs) -> dict[str, str]:
  if not dc.is_dataclass(obj):
    raise TypeError(f"Expected a dataclass but got {type(obj)!r}")
  xml_attrs: dict[str, str] = dict()
  for field in dc.fields(obj):
    type_: tp.Type
    if "int" in field.type:
      type_ = int
    elif "SEGTYPE" in field.type:
      type_ = enum.Enum
    elif "ASSOC" in field.type:
      type_ = enum.Enum
    elif "POS" in field.type:
      type_ = enum.Enum
    elif "dt" in field.type:
      type_ = dt.datetime
    else:
      type_ = str
    if not field.metadata.get("exclude", False):
      val = kwargs.pop(field.name, getattr(obj, field.name))
      if val is None and field.default is not dc.MISSING:
        continue
      if not isinstance(val, type_):
        raise TypeError(f"Expected {type_!r} for {field.name!r} but got {type(val)!r}")
      if isinstance(val, int):
        val = str(val)
      elif isinstance(val, enum.Enum):
        val = val.value
      elif isinstance(val, dt.datetime):
        val = val.strftime("%Y%m%dT%H%M%SZ")
      elif isinstance(val, str):
        pass
      xml_attrs[field.metadata.get("export_name", field.name)] = val
  return xml_attrs


def _make_elem(
  tag: str, attrib: dict[str, str], engine: tp.Literal["python", "lxml"]
) -> lxet._Element | pyet.Element:
  if engine == "lxml":
    return lxet.Element(tag, attrib=attrib)
  elif engine == "python":
    return pyet.Element(tag, attrib=attrib)
  else:
    raise ValueError(f"Unknown engine: {engine!r}")
