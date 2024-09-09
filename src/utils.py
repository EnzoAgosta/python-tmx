import re
from typing import Literal

from src.models import Bpt, Ept, Hi, It, Ph, Sub, TmxElement, Ut


def text_to_tag(
    source,
    pattern: str,
    tag: Literal["bpt", "ept", "ut", "sub", "hi", "it", "ph"],
    **extra,
) -> list[str | TmxElement]:
    _pattern = re.compile(pattern)
    split_source = re.split(_pattern, source)
    split_source = [x for x in split_source if x is not None]
    if "".join(split_source) != source:
        raise ValueError
    tagged_list = []
    for item in split_source:
        if re.match(_pattern, item):
            match tag:
                case "bpt":
                    tagged_list.append(Bpt(content=item, **extra))
                case "ept":
                    tagged_list.append(Ept(content=item, **extra))
                case "ut":
                    tagged_list.append(Ut(content=item, **extra))
                case "sub":
                    tagged_list.append(Sub(content=item, **extra))
                case "it":
                    tagged_list.append(It(content=item, **extra))
                case "hi":
                    tagged_list.append(Hi(content=item, **extra))
                case "ph":
                    tagged_list.append(Ph(content=item, **extra))
        else:
            tagged_list.append(item)
    return tagged_list
