from enum import Enum

__all__ = [
  "SEGTYPE",
  "ASSOC",
  "POS",
  "DATATYPE",
  "TYPE",
  "PHTYPE",
  "BPTITTYPE",
]


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


class DATATYPE(Enum):
  UNKNOWN = "unknown"
  ALPTEXT = "alptext"
  CDF = "cdf"
  CMX = "cmx"
  CPP = "cpp"
  HPTAG = "hptag"
  HTML = "html"
  INTERLEAF = "interleaf"
  IPF = "ipf"
  JAVA = "java"
  JAVASCRIPT = "javascript"
  LISP = "lisp"
  MIF = "mif"
  OPENTAG = "opentag"
  PASCAL = "pascal"
  PLAINTEXT = "plaintext"
  PM = "pm"
  RTF = "rtf"
  SGML = "sgml"
  STFF = "stf-f"
  STFI = "stf-i"
  TRANSIT = "transit"
  VBSCRIPT = "vbscript"
  WINRES = "winres"
  XML = "xml"
  XPTAG = "xptag"


class PHTYPE(Enum):
  INDEX = "index"
  DATE = "date"
  TIME = "time"
  FNOTE = "fnote"
  ENOTE = "enote"
  ALT = "alt"
  IMAGE = "image"
  PB = "pb"
  LB = "lb"
  CB = "cb"
  INSET = "inset"


class BPTITTYPE(Enum):
  BOLD = "bold"
  COLOR = "color"
  DULINED = "dulined"
  FONT = "font"
  ITALIC = "italic"
  LINK = "link"
  SCAP = "scap"
  STRUCT = "struct"
  ULINED = "ulined"


class TYPE(Enum):
  INDEX = "index"
  DATE = "date"
  TIME = "time"
  FNOTE = "fnote"
  ENOTE = "enote"
  ALT = "alt"
  IMAGE = "image"
  PB = "pb"
  LB = "lb"
  CB = "cb"
  INSET = "inset"
