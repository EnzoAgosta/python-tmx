from typing import Any


def join_top_level_strings(arr: list[Any]) -> list[Any]:
  if not arr:
    return []
  result: list[Any] = []
  buffer: list[str] = []
  for item in arr:
    if isinstance(item, str):
      buffer.append(item)
    else:
      if buffer:
        result.append("".join(buffer))
        buffer.clear()
      result.append(item)
  if buffer:
    result.append("".join(buffer))
  return result
