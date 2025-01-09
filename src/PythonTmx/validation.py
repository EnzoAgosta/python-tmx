import datetime as dt
import unicodedata as ud


def validate_unicode_value(string: str) -> None:
  if not string.startswith("#x"):
    raise ValueError("Value must start with #x")
  codepoint = int(string[2:], 16)
  ud.category(chr(codepoint))


def validate_dt_from_str(string: str):
  try:
    dt.datetime.fromisoformat(string)
  except ValueError:
    raise ValueError("value must be a datetime object or a string in ISO format")


def validate_int_from_str(string: str) -> None:
  try:
    int(string)
  except (ValueError, TypeError):
    raise ValueError("value must be convertible to an integer")
