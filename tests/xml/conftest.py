from hypomnema.xml.backends import XmlBackend
import logging
from collections.abc import Generator

import pytest
from strict_backend import StrictBackend

import hypomnema as hm


@pytest.fixture(
  params=["standard", "lxml", "strict"],
  ids=["Backend=Standard library, ", "Backend=Lxml, ", "Backend=Strict, "],
)
def backend(request: pytest.FixtureRequest) -> Generator[XmlBackend]:
  if request.param == "lxml":
    yield hm.LxmlBackend()
  elif request.param == "standard":
    yield hm.StandardBackend()
  elif request.param == "strict":
    yield StrictBackend()
  else:
    raise ValueError(f"Invalid backend: {request.param}")


@pytest.fixture(autouse=True, scope="session")
def test_logger() -> logging.Logger:
  logger = logging.getLogger("tests.capture_all")
  logger.setLevel(1)
  return logger


@pytest.fixture(
  params=["debug", "info", "warning", "error"],
  ids=["log_level=debug, ", "log_level=info, ", "log_level=warning, ", "log_level=error, "],
)
def log_level(request: pytest.FixtureRequest) -> int:
  match request.param:
    case "debug":
      return logging.DEBUG
    case "info":
      return logging.INFO
    case "warning":
      return logging.WARNING
    case "error":
      return logging.ERROR
    case _:
      raise ValueError(f"Invalid log level: {request.param}")
