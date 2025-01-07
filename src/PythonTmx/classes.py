from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Map(BaseModel):
  model_config = ConfigDict()
