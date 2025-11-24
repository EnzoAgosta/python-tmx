import encodings
import encodings.aliases

from python_tmx.base.types import Assoc, Pos, Segtype
from faker.providers import BaseProvider


class ExtraProvider(BaseProvider):
  datatypes: tuple[str, ...] = (
    "unknown",
    "alptext",
    "cdf",
    "cmx",
    "cpp",
    "hptag",
    "html",
    "interleaf",
    "ipf",
    "java",
    "javascript",
    "lisp",
    "mif",
    "opentag",
    "pascal",
    "plaintext",
    "pm",
    "rtf",
    "sgml",
    "stf-f",
    "stf-i",
    "transit",
    "vbscript",
    "winres",
    "xml",
    "xptag",
  )

  def encoding(self) -> str:
    return self.generator.random_element(encodings.aliases.aliases.keys())

  def datatype(self) -> str:
    return self.generator.random_element(self.datatypes)

  def version(self) -> str:
    return ".".join(str(self.generator.random_number(3, False)) for _ in range(3))

  def assoc(self) -> Assoc:
    return self.generator.enum(Assoc)

  def pos(self) -> Pos:
    return self.generator.enum(Pos)

  def segtype(self) -> Segtype:
    return self.generator.enum(Segtype)
