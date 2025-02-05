from typing import TypeAlias

from PythonTmx.classes.inline import Bpt, Ept, Hi, It, Ph, Sub, Ut
from PythonTmx.classes.structural import Header, Map, Note, Prop, Tmx, Tu, Tuv, Ude

Structural: TypeAlias = Tmx | Tu | Tuv | Header | Note | Prop | Map | Ude
Inline: TypeAlias = Bpt | Ept | It | Ph | Hi | Ut | Sub
