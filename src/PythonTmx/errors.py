class ValidationError(Exception):
  def __init__(self, obj: object, /, field: str | None = None) -> None:
    if field:
      super().__init__(
        f"Error while validating {field!r} of {obj.__class__.__name__!r}"
      )
    else:
      super().__init__(f"Error while validating {obj.__class__.__name__!r}")
