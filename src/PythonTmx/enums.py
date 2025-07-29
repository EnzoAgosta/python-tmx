from enum import Enum


class SEGTYPE(Enum):
  BLOCK = "block"
  PARAGRAPH = "paragraph"
  SENTENCE = "sentence"
  PHRASE = "phrase"


class ASSOC(Enum):
  P = "p"
  F = "f"
  B = "b"


class POS(Enum):
  BEGIN = "begin"
  END = "end"
