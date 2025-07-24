from typing import Any


class ParsingError(Exception):
  tag: str
  line: str
  original_exception: Exception

  def __str__(self):
        return f"{super().__str__()}\nTag: {self.tag}\nLine: {self.line}\nCaused by: {self.original_exception}"

  def __init__(
    self,
    msg: str,
    tag: str,
    line: str,
    original_exception: Exception,
    **extra: Any,
  ):
    super().__init__(msg)
    self.tag = tag
    self.line = line
    self.original_exception = original_exception
    for key, value in extra.items():
      setattr(self, key, value)


class SerializationError(Exception):
  tag: str
  original_exception: Exception

  def __str__(self):
        return f"{super().__str__()}\nTag: {self.tag}\nCaused by: {self.original_exception}"

  def __init__(
    self, msg: str, tag: str, original_exception: Exception, **extra: Any
  ):
    super().__init__(msg)
    self.tag = tag
    self.original_exception = original_exception
    for key, value in extra.items():
      setattr(self, key, value)

class MalFormedElementError(Exception):
  missing_field: str

  def __str__(self):
        return f"{super().__str__()}\nMissing field: {self.missing_field}"

  def __init__(self, msg: str, missing_field: str, **extra: Any):
    super().__init__(msg)
    self.missing_field = missing_field
    for key, value in extra.items():
      setattr(self, key, value)