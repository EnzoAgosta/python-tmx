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

class UnusableElementError(Exception):
  missing_field: str

  def __str__(self):
        if hasattr(self, "missing_field"):
            return f"{super().__str__()}\nMissing required field {self.missing_field}"
        else:
            return super().__str__()

  def __init__(self, msg: str, **extra: Any):
    super().__init__(msg)
    for key, value in extra.items():
      setattr(self, key, value)

class MissingDefaultFactoryError(Exception):
  pass