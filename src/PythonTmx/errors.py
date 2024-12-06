class RequiredAttributeError(Exception):
  def __init__(self, *args):
    super().__init__(f"required attribute {self.args[0]} is missing")
