class ValidationError(Exception):
  def __init__(self, field: str, *args):
    super().__init__(f"{field} failed validation!", *args)
