from collections.abc import Generator
import logging

import pytest

from python_tmx.xml.backends.base import XMLBackend

from python_tmx.xml.backends.lxml import LxmlBackend
from python_tmx.xml.backends.standard import StandardBackend
from strict_backend import StrictBackend


@pytest.fixture(
  params=["standard", "lxml", "test"],
  ids=["Backend=Standard library, ", "Backend=Lxml, ", "Backend=Strict, "],
)
def backend(request: pytest.FixtureRequest) -> Generator[XMLBackend, None, None]:
  if request.param == "lxml":
    yield LxmlBackend()
  elif request.param == "standard":
    yield StandardBackend()
  elif request.param == "test":
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
