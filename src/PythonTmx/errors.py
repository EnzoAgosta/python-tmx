class ParsingError(Exception):
  tag: str
  line: str
  element: str
  original_exception: Exception

  def __init__(
    self,
    msg: str,
    tag: str,
    line: str,
    element: str,
    original_exception: Exception,
  ):
    super().__init__(msg)
    self.tag = tag
    self.line = line
    self.element = element
    self.original_exception = original_exception
