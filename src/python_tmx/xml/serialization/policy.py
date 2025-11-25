from dataclasses import dataclass
import logging
from typing import Literal


@dataclass(slots=True, frozen=True)
class SerializationPolicy:
  strict: bool = True
  log_level: int = logging.WARNING
  clip_length: int | None = 80
  required_attribute_missing: Literal["raise", "warn", "ignore"] = "raise"
  invalid_attribute_type: Literal["raise", "warn", "coerce", "ignore"] = "raise"
  invalid_text_content: Literal["raise", "warn", "coerce", "empty", "ignore"] = "raise"
  invalid_element: Literal["raise", "warn", "ignore"] = "raise"
  missing_handler: Literal["raise", "default", "ignore"] = "raise"
  incorrect_child_element: Literal["raise", "warn", "ignore"] = "raise"
