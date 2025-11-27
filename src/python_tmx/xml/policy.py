from dataclasses import dataclass
import logging
from typing import Literal, NamedTuple, TypeVar


Behavior = TypeVar("Behavior", bound=str)


class PolicyValue[Behavior](NamedTuple):
  behavior: Behavior
  log_level: int


@dataclass(slots=True)
class DeserializationPolicy:
  invalid_tag: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  required_attribute_missing: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  invalid_attribute_value: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  missing_text: PolicyValue[Literal["raise", "empty", "ignore"]] = PolicyValue("raise", logging.ERROR)
  extra_text: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  invalid_inline_tag: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  invalid_child_element: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  multiple_headers: PolicyValue[Literal["raise", "keep_first", "keep_last"]] = PolicyValue("raise", logging.ERROR)
  missing_handler: PolicyValue[Literal["raise", "ignore", "default"]] = PolicyValue("raise", logging.ERROR)
  missing_seg: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  multiple_seg: PolicyValue[Literal["raise", "keep_first", "keep_last"]] = PolicyValue("raise", logging.ERROR)

@dataclass(slots=True)
class SerializationPolicy:
  missing_required_attribute: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  invalid_attribute_type: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  invalid_inline_tag: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  invalid_inline_content: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  invalid_object_type: PolicyValue[Literal["raise", "ignore"]] = PolicyValue("raise", logging.ERROR)
  missing_handler: PolicyValue[Literal["raise", "ignore", "default"]] = PolicyValue("raise", logging.ERROR)