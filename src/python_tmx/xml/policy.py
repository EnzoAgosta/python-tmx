from dataclasses import dataclass, field
import logging
from typing import Literal, TypeVar


Behavior = TypeVar("Behavior", bound=str)


@dataclass(slots=True)
class PolicyValue[Behavior]:
  behavior: Behavior
  log_level: int


def _default_policy(
  behavior: Behavior = "raise", level: int = logging.DEBUG
) -> PolicyValue[Behavior]:
  return field(default_factory=lambda: PolicyValue(behavior, level))


@dataclass(slots=True, kw_only=True)
class DeserializationPolicy:
  missing_handler: PolicyValue[Literal["raise", "ignore", "default"]] = _default_policy()
  invalid_tag: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  required_attribute_missing: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  invalid_attribute_value: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  extra_text: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  invalid_child_element: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  multiple_headers: PolicyValue[Literal["raise", "keep_first", "keep_last"]] = _default_policy()
  missing_header: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  missing_seg: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  multiple_seg: PolicyValue[Literal["raise", "keep_first", "keep_last"]] = _default_policy()
  empty_content: PolicyValue[Literal["raise", "ignore", "empty"]] = _default_policy()


@dataclass(slots=True, kw_only=True)
class SerializationPolicy:
  required_attribute_missing: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  invalid_attribute_type: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  invalid_content_type: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  missing_handler: PolicyValue[Literal["raise", "ignore", "default"]] = _default_policy()
  invalid_object_type: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
  invalid_child_element: PolicyValue[Literal["raise", "ignore"]] = _default_policy()
