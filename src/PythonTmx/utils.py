from __future__ import annotations

import datetime as dt


def _try_parse_dt(dt_str: str) -> dt.datetime | str:
  if not isinstance(dt_str, str):
    return dt_str
  try:
    return dt.datetime.fromisoformat(dt_str)
  except ValueError:
    return dt_str
