from .header import Header
from .inline import Bpt, Ept, Hi, It, Ph, Sub, Ut
from .map import Map
from .note import Note
from .prop import Prop
from .tmx import Tmx
from .tu import Tu
from .tuv import Tuv
from .ude import Ude

type InlineElement = Bpt | Ept | Hi | It | Ph | Sub | Ut
type StructuralElement = Header | Ude | Map | Note | Prop | Tu | Tuv | Tmx

__all__ = [
  "Prop",
  "Note",
  "Map",
  "Ude",
  "Header",
  "Tu",
  "Tuv",
  "Tmx",
  "Bpt",
  "Ept",
  "Hi",
  "It",
  "Ph",
  "Sub",
  "Ut",
  "InlineElement",
  "StructuralElement",
]
