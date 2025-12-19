import logging
from dataclasses import dataclass, field
from typing import Literal

__all__ = ["DeserializationPolicy", "SerializationPolicy", "PolicyValue"]


def _default[DefaultBehavior: str](
  default_behavior: DefaultBehavior,
) -> PolicyValue[DefaultBehavior]:
  return field(default_factory=lambda: PolicyValue(default_behavior, logging.DEBUG))


@dataclass(slots=True)
class PolicyValue[Behavior: str]:
  """
  Container for policy behavior and logging configuration.

  Parameters
  ----------
  behavior : Behavior
      The action to execute when a policy condition is met.
  log_level : int
      The logging level to use before executing the behavior.

  Attributes
  ----------
  behavior : Behavior
      The action to execute when a policy condition is met.
  log_level : int
      The logging level to use before executing the behavior.
  """

  behavior: Behavior
  log_level: int


@dataclass(slots=True, kw_only=True)
class DeserializationPolicy:
  """
  Configuration policy for TMX to Python object conversion.

  Attributes
  ----------
  missing_handler : PolicyValue[Literal["raise", "ignore", "default"]]
      Action when no handler is registered for a TMX element.
      "default" attempts fallback to internal library handlers.
  invalid_tag : PolicyValue[Literal["raise", "ignore"]]
      Action when an unexpected XML tag is encountered.
  required_attribute_missing : PolicyValue[Literal["raise", "ignore"]]
      Action when a mandatory TMX attribute is absent.
  invalid_attribute_value : PolicyValue[Literal["raise", "ignore"]]
      Action when an attribute value violates TMX specifications.
  extra_text : PolicyValue[Literal["raise", "ignore"]]
      Action when unexpected non-whitespace text is found within elements.
  invalid_child_element : PolicyValue[Literal["raise", "ignore"]]
      Action when a child element is not permitted by TMX structure.
  multiple_headers : PolicyValue[Literal["raise", "keep_first", "keep_last"]]
      Action when more than one `<header>` element exists in `<tmx>`.
  missing_header : PolicyValue[Literal["raise", "ignore"]]
      Action when the mandatory `<header>` element is missing.
  missing_seg : PolicyValue[Literal["raise", "ignore"]]
      Action when a `<tu>` or `<tuv>` is missing the required `<seg>` element.
  multiple_seg : PolicyValue[Literal["raise", "keep_first", "keep_last"]]
      Action when a `<tuv>` contains more than one `<seg>` element.
  empty_content : PolicyValue[Literal["raise", "ignore", "empty"]]
      Action when an element has no text content. "empty" converts
      None to an empty string.
  """

  missing_handler: PolicyValue[Literal["raise", "ignore", "default"]] = _default("raise")
  invalid_tag: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
  required_attribute_missing: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
  invalid_attribute_value: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
  extra_text: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
  invalid_child_element: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
  multiple_headers: PolicyValue[Literal["raise", "keep_first", "keep_last"]] = _default("raise")
  missing_header: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
  missing_seg: PolicyValue[Literal["raise", "ignore", "empty"]] = _default("raise")
  multiple_seg: PolicyValue[Literal["raise", "keep_first", "keep_last"]] = _default("raise")
  empty_content: PolicyValue[Literal["raise", "ignore", "empty"]] = _default("raise")


@dataclass(slots=True, kw_only=True)
class SerializationPolicy:
  """
  Configuration policy for Python object to TMX XML conversion.

  Attributes
  ----------
  required_attribute_missing : PolicyValue[Literal["raise", "ignore"]]
      Action when a mandatory dataclass field is None.
  invalid_attribute_type : PolicyValue[Literal["raise", "ignore"]]
      Action when a field type is incompatible with XML attribute standards.
  invalid_content_type : PolicyValue[Literal["raise", "ignore"]]
      Action when element text content is not a string.
  missing_handler : PolicyValue[Literal["raise", "ignore", "default"]]
      Action when no Serializer class is found for a specific dataclass.
      "default" attempts fallback to internal library serializers.
  invalid_object_type : PolicyValue[Literal["raise", "ignore"]]
      Action when a handler receives an unexpected object type.
  invalid_child_element : PolicyValue[Literal["raise", "ignore"]]
      Action when a child object is not valid for the parent TMX element.
  """

  required_attribute_missing: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
  invalid_attribute_type: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
  invalid_content_type: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
  missing_handler: PolicyValue[Literal["raise", "ignore", "default"]] = _default("raise")
  invalid_object_type: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
  invalid_child_element: PolicyValue[Literal["raise", "ignore"]] = _default("raise")
