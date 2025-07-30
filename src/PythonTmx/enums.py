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
  """Segment type enumeration for TMX content.
  
  Defines the different types of text segmentation that can be used
  in TMX files. Segment types determine how text content is divided
  into translatable units.
  
  Attributes:
    BLOCK: Represents a block-level segment (e.g., paragraph, section).
    PARAGRAPH: Represents a paragraph-level segment.
    SENTENCE: Represents a sentence-level segment.
    PHRASE: Represents a phrase-level segment.
  """
  BLOCK = "block"
  """Block-level segment (e.g., paragraph, section)."""
  
  PARAGRAPH = "paragraph"
  """Paragraph-level segment."""
  
  SENTENCE = "sentence"
  """Sentence-level segment."""
  
  PHRASE = "phrase"
  """Phrase-level segment."""


class ASSOC(Enum):
  """Association type enumeration for TMX elements.
  
  Defines the different types of associations that can be specified
  for various TMX elements, particularly placeholders and formatting tags.
  
  Attributes:
    P: Primary association - the main or primary content.
    F: Formatting association - formatting-related content.
    B: Both association - applies to both primary and formatting content.
  """
  P = "p"
  """Primary association - the main or primary content."""
  
  F = "f"
  """Formatting association - formatting-related content."""
  
  B = "b"
  """Both association - applies to both primary and formatting content."""


class POS(Enum):
  """Position enumeration for isolated tags.
  
  Defines the position of isolated tags within TMX content.
  Isolated tags can appear at the beginning or end of content.
  
  Attributes:
    BEGIN: Tag appears at the beginning of content.
    END: Tag appears at the end of content.
  """
  BEGIN = "begin"
  """Tag appears at the beginning of content."""
  
  END = "end"
  """Tag appears at the end of content."""


class DATATYPE(Enum):
  """Data type enumeration for TMX content.
  
  Defines the different data types that can be specified for TMX content.
  Data types indicate the format or nature of the content being translated.
  
  Attributes:
    UNKNOWN: Unknown or unspecified data type.
    ALPTEXT: Alphanumeric text content.
    CDF: Common Data Format content.
    CMX: Corel Metafile Exchange content.
    CPP: C++ source code content.
    HPTAG: HP Tag content.
    HTML: HyperText Markup Language content.
    INTERLEAF: Interleaf document content.
    IPF: Information Presentation Facility content.
    JAVA: Java source code content.
    JAVASCRIPT: JavaScript source code content.
    LISP: Lisp source code content.
    MIF: Maker Interchange Format content.
    OPENTAG: OpenTag content.
    PASCAL: Pascal source code content.
    PLAINTEXT: Plain text content.
    PM: Presentation Manager content.
    RTF: Rich Text Format content.
    SGML: Standard Generalized Markup Language content.
    STFF: Structured Text Format content.
    STFI: Structured Text Format Interleaf content.
    TRANSIT: Transit content.
    VBSCRIPT: VBScript source code content.
    WINRES: Windows Resource content.
    XML: Extensible Markup Language content.
    XPTAG: XPTag content.
  """
  UNKNOWN = "unknown"
  """Unknown or unspecified data type."""
  
  ALPTEXT = "alptext"
  """Alphanumeric text content."""
  
  CDF = "cdf"
  """Common Data Format content."""
  
  CMX = "cmx"
  """Corel Metafile Exchange content."""
  
  CPP = "cpp"
  """C++ source code content."""
  
  HPTAG = "hptag"
  """HP Tag content."""
  
  HTML = "html"
  """HyperText Markup Language content."""
  
  INTERLEAF = "interleaf"
  """Interleaf document content."""
  
  IPF = "ipf"
  """Information Presentation Facility content."""
  
  JAVA = "java"
  """Java source code content."""
  
  JAVASCRIPT = "javascript"
  """JavaScript source code content."""
  
  LISP = "lisp"
  """Lisp source code content."""
  
  MIF = "mif"
  """Maker Interchange Format content."""
  
  OPENTAG = "opentag"
  """OpenTag content."""
  
  PASCAL = "pascal"
  """Pascal source code content."""
  
  PLAINTEXT = "plaintext"
  """Plain text content."""
  
  PM = "pm"
  """Presentation Manager content."""
  
  RTF = "rtf"
  """Rich Text Format content."""
  
  SGML = "sgml"
  """Standard Generalized Markup Language content."""
  
  STFF = "stf-f"
  """Structured Text Format content."""
  
  STFI = "stf-i"
  """Structured Text Format Interleaf content."""
  
  TRANSIT = "transit"
  """Transit content."""
  
  VBSCRIPT = "vbscript"
  """VBScript source code content."""
  
  WINRES = "winres"
  """Windows Resource content."""
  
  XML = "xml"
  """Extensible Markup Language content."""
  
  XPTAG = "xptag"
  """XPTag content."""


class PHTYPE(Enum):
  """Placeholder type enumeration for TMX placeholders.
  
  Defines the different types of placeholders that can be used
  in TMX content for various purposes like notes, images, and formatting.
  
  Attributes:
    INDEX: Index-related placeholder.
    DATE: Date-related placeholder.
    TIME: Time-related placeholder.
    FNOTE: Footnote placeholder.
    ENOTE: Endnote placeholder.
    ALT: Alternative text placeholder.
    IMAGE: Image placeholder.
    PB: Page break placeholder.
    LB: Line break placeholder.
    CB: Column break placeholder.
    INSET: Inset content placeholder.
  """
  INDEX = "index"
  """Index-related placeholder."""
  
  DATE = "date"
  """Date-related placeholder."""
  
  TIME = "time"
  """Time-related placeholder."""
  
  FNOTE = "fnote"
  """Footnote placeholder."""
  
  ENOTE = "enote"
  """Endnote placeholder."""
  
  ALT = "alt"
  """Alternative text placeholder."""
  
  IMAGE = "image"
  """Image placeholder."""
  
  PB = "pb"
  """Page break placeholder."""
  
  LB = "lb"
  """Line break placeholder."""
  
  CB = "cb"
  """Column break placeholder."""
  
  INSET = "inset"
  """Inset content placeholder."""


class BPTITTYPE(Enum):
  """Beginning paired tag and isolated tag type enumeration.
  
  Defines the different types that can be specified for beginning
  paired tags (Bpt) and isolated tags (It) in TMX content.
  
  Attributes:
    BOLD: Bold formatting type.
    COLOR: Color formatting type.
    DULINED: Double underlined formatting type.
    FONT: Font formatting type.
    ITALIC: Italic formatting type.
    LINK: Link formatting type.
    SCAP: Small caps formatting type.
    STRUCT: Structural formatting type.
    ULINED: Underlined formatting type.
  """
  BOLD = "bold"
  """Bold formatting type."""
  
  COLOR = "color"
  """Color formatting type."""
  
  DULINED = "dulined"
  """Double underlined formatting type."""
  
  FONT = "font"
  """Font formatting type."""
  
  ITALIC = "italic"
  """Italic formatting type."""
  
  LINK = "link"
  """Link formatting type."""
  
  SCAP = "scap"
  """Small caps formatting type."""
  
  STRUCT = "struct"
  """Structural formatting type."""
  
  ULINED = "ulined"
  """Underlined formatting type."""


class TYPE(Enum):
  """General type enumeration for TMX elements.
  
  Defines general types that can be used across various TMX elements
  for categorization and specification purposes.
  
  Attributes:
    INDEX: Index-related type.
    DATE: Date-related type.
    TIME: Time-related type.
    FNOTE: Footnote type.
    ENOTE: Endnote type.
    ALT: Alternative text type.
    IMAGE: Image type.
    PB: Page break type.
    LB: Line break type.
    CB: Column break type.
    INSET: Inset content type.
  """
  INDEX = "index"
  """Index-related type."""
  
  DATE = "date"
  """Date-related type."""
  
  TIME = "time"
  """Time-related type."""
  
  FNOTE = "fnote"
  """Footnote type."""
  
  ENOTE = "enote"
  """Endnote type."""
  
  ALT = "alt"
  """Alternative text type."""
  
  IMAGE = "image"
  """Image type."""
  
  PB = "pb"
  """Page break type."""
  
  LB = "lb"
  """Line break type."""
  
  CB = "cb"
  """Column break type."""
  
  INSET = "inset"
  """Inset content type."""
