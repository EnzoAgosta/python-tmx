import logging
from python_tmx.xml.serialization.policy import SerializationPolicy

fileLogger = logging.getLogger(__name__)


class SerializationLogger:
  def __init__(self, policy: SerializationPolicy):
    self.policy = policy
    self.logger = fileLogger.getChild("SerializationLogger")
    self.logger.setLevel(policy.log_level)

  def debug_action(self, msg: str, *args) -> None:
    self.logger.debug(msg, *args)

  def log_missing_attr(self, attr_name: str) -> None:
    level = logging.WARNING if self.policy.required_attribute_missing == "warn" else logging.DEBUG
    self.logger.log(level, "Missing value for required attribute %r", attr_name)

  def log_invalid_attribute_type(self, attr_name: str, expected_type: str, received: object) -> None:
    level = logging.WARNING if self.policy.invalid_attribute_type == "warn" else logging.DEBUG
    self.logger.log(
      level,
      "Invalid value type for attribute %r: expected %s, got %s",
      attr_name,
      expected_type,
      type(received).__name__,
    )

  def log_invalid_element(self, expected_type: str, received_type: str) -> None:
    level = logging.WARNING if self.policy.invalid_element == "warn" else logging.DEBUG
    self.logger.log(level, "Invalid element type: expected %s, got %s", expected_type, received_type)

  def log_missing_handler(self, obj: str) -> None:
    level = logging.WARNING if self.policy.missing_handler == "default" else logging.DEBUG
    self.logger.log(level, "Missing handler for %s", obj)
