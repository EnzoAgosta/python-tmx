from PythonTmx.core import BaseTmxElement
from PythonTmx.elements import Prop

__TAG_MAP__: dict[str, type[BaseTmxElement]] = {
  "prop": Prop,
}

__all__ = ["__TAG_MAP__"]