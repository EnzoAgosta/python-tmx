from os import PathLike
from pathlib import Path


def ensure_file(path: PathLike[str] | Path | str) -> Path:
  path = Path(path).resolve()
  if not path.exists():
    raise FileNotFoundError(f"file {path} doesn't exist")
  if not path.is_file():
    raise IsADirectoryError(f"file {path} is not a file")
  return path