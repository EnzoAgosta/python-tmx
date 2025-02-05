from typing import TypeAlias

from PythonTmx.classes.structural import Header, Map, Note, Prop, Tmx, Tu, Tuv, Ude

Structural: TypeAlias = Tmx | Tu | Tuv | Header | Note | Prop | Map | Ude
