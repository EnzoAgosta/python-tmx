# Hypomnema

[![PyPI version](https://badge.fury.io/py/hypomnema.svg)](https://badge.fury.io/py/hypomnema)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)

**Industrial-grade TMX 1.4b parsing and serialization for Python.**

Hypomnema is a strictly typed infrastructure library for working with [TMX 1.4b](https://resources.gala-global.org/tbx14b) (Translation Memory eXchange) files. It is designed as a foundation for building localization tools, CAT software, and NLP pipelines.

> **Warning:** Hypomnema is pre-1.0 software. Expect breaking changes without notice until version 1.0.0.

## TMX 1.4b Level 2 Compliance

Hypomnema is the **only Python library** that fully implements the TMX 1.4b Level 2 specification. Key capabilities include:

- **Arbitrary Nesting Depth**: No arbitrary limits on inline element nesting. `<bpt>`/`<ept>` pairs, `<ph>` placeholders, and `<sub>` elements can be nested to any depth, matching the full expressiveness of the TMX 1.4b spec.
- **Complete Inline Element Support**: All six inline markup elements (`<bpt>`, `<ept>`, `<it>`, `<ph>`, `<hi>`, `<sub>`) with proper handling of mixed content (text and elements intermixed).
- **Full Attribute Modeling**: Every TMX attribute is modeled with proper types, including enumerations for `segtype`, `pos`, and `assoc`.
- **Metadata Preservation**: Properties (`<prop>`) and notes (`<note>`) are fully supported at all valid nesting levels.

### Intentionally Omitted Elements

The following TMX 1.4b elements are **not implemented**:

- `<ude>` — User Defined Encoding (custom encoding handling)
- `<map>` — Character mapping

These elements relate to custom encodings and character mapping. They are rarely encountered in practice and were excluded to keep the library focused and maintainable. If you need support for them, you can implement custom handlers by subclassing the existing handler classes — the architecture is designed to be extensible. See the source code in `xml/deserialization/_handlers.py` and `xml/serialization/_handlers.py` for patterns to follow.

## What is TMX?

TMX (Translation Memory eXchange) is an open XML standard for exchanging translation memory data between tools and providers. A TMX file contains translation units (TU) with source and target language variants (TUV), each containing segmented text. TMX files often include inline markup for formatting, placeholders, and tags that must be preserved during processing.

## Why Hypomnema?

Most TMX parsers are simple XML wrappers. Hypomnema offers:

- **Policy-Driven Error Handling**: Configure exactly how to handle malformed data (missing segments, extra text, invalid tags, etc.)
- **Backend Agnostic**: Use `lxml` for speed or standard library `xml.etree` for zero-dependency deployments
- **Full Type Safety**: Modern Python 3.14+ type annotations with structured dataclasses, not raw XML nodes
- **Roundtrip Integrity**: Deserialize to objects, manipulate, serialize back — with optional validation at each step
- **Streaming API**: Process large TMX files element-by-element without loading everything into memory

## Installation

```bash
pip install hypomnema
# or
uv add hypomnema
```

For maximum performance with large files:

```bash
pip install "hypomnema[lxml]"
# or
uv add hypomnema[lxml]
```

## Quick Start

```python
import hypomnema as hm

# Load a TMX file
tmx = hm.load("translations.tmx")

# Inspect the content
print(f"Source language: {tmx.header.srclang}")
print(f"Translation units: {len(tmx.body)}")

# Find a specific translation unit
for tu in tmx.body:
    for tuv in tu.variants:
        if tuv.lang == "fr":
            print(f"French: {tuv.content}")
```

## High-Level API

The `load()` and `save()` functions provide the simplest interface for common tasks:

```python
import hypomnema as hm

# Load entire file
tmx = hm.load("input.tmx")

# Filter loading - only get translation units (streaming, memory efficient)
for tu in hm.load("large.tmx", filter="tu"):
    print(tu.tuid)

# Load specific element types
for element in hm.load("file.tmx", filter=["tu", "header"]):
    if isinstance(element, hm.Header):
        print(element.creationtool)

# Save back to disk
hm.save(tmx, "output.tmx")

# Specify encoding
tmx = hm.load("file.tmx", encoding="utf-16")
hm.save(tmx, "output.tmx", encoding="utf-16")
```

## Low-Level API

For finer control over parsing and serialization, use the `Deserializer` and `Serializer` classes directly:

```python
import hypomnema as hm

# Choose your backend
backend = hm.LxmlBackend()   # Fast, feature-rich
# or
backend = hm.StandardBackend()  # Portable, stdlib only

# Deserialize
deserializer = hm.Deserializer(backend=backend)
xml_tree = backend.parse("file.tmx")
tmx = deserializer.deserialize(xml_tree)

# Manipulate the object model
new_tuv = hm.create_tuv("de", content=["Guten Tag"])
new_tu = hm.create_tu(variants=[new_tuv])
tmx.body.append(new_tu)

# Serialize back
serializer = hm.Serializer(backend=backend)
xml_element = serializer.serialize(tmx)

# Write to file
backend.write(xml_element, "output.tmx")
```

## Policy Configuration

Real-world TMX files are often imperfect. Policies let you configure how Hypomnema handles validation errors:

```python
import hypomnema as hm
from hypomnema.xml.policy import PolicyValue
import logging

# Configure deserialization policy
policy = hm.DeserializationPolicy(
    missing_seg=PolicyValue("ignore", logging.WARNING),
    extra_text=PolicyValue("ignore", logging.INFO),
    invalid_attribute_value=PolicyValue("ignore", logging.DEBUG),
)

# Use custom policy when loading
tmx = hm.load("messy.tmx", policy=policy)

# Configure serialization policy
serial_policy = hm.SerializationPolicy(
    required_attribute_missing=PolicyValue("ignore", logging.ERROR),
)

hm.save(tmx, "clean.tmx", policy=serial_policy)
```

Available deserialization policies:

- `missing_handler`: No handler for element type
- `invalid_tag`: Unexpected XML tag encountered
- `required_attribute_missing`: Mandatory TMX attribute absent
- `invalid_attribute_value`: Attribute violates TMX spec
- `extra_text`: Unexpected text within elements
- `invalid_child_element`: Child not permitted by TMX structure
- `multiple_headers`: Multiple `<header>` elements
- `missing_header`: Mandatory `<header>` missing
- `missing_seg`: `<tu>`/`<tuv>` missing required `<seg>`
- `multiple_seg`: `<tuv>` has multiple `<seg>` elements
- `empty_content`: Element has no text content

Available serialization policies:

- `required_attribute_missing`: Mandatory dataclass field is None
- `invalid_attribute_type`: Field type incompatible with XML
- `invalid_content_type`: Content is not a string
- `missing_handler`: No serializer for dataclass type
- `invalid_object_type`: Handler received unexpected type
- `invalid_child_element`: Child invalid for parent element

## Creating TMX from Scratch

```python
import hypomnema as hm
from datetime import datetime

# Create a header with metadata
header = hm.create_header(
    srclang="en",
    creationtool="my-tool",
    segtype=hm.Segtype.SENTENCE,
)

# Create a segment with complex nested inline markup demonstrating arbitrary depth
# This example shows the full expressiveness of TMX 1.4b Level 2
segment_content = [
    "Click the ",
    hm.create_bpt(
        i=1,
        type="link",
        x=100,
        content=[
            hm.create_sub(
                content=["here", hm.create_hi(content=["important"])],
                datatype="text",
            )
        ],
    ),
    " button to proceed. ",
    "For special cases, use ",
    hm.create_ph(
        assoc=hm.Assoc.B,
        type="variable",
        x=200,
        content=[
            hm.create_sub(
                content=[
                    "the ",
                    hm.create_bpt(i=2, type="emphasis", content=[hm.create_sub(content=["default"])]),
                    " value",
                ],
                datatype="text",
            )
        ],
    ),
    ". ",
    "End of ",
    hm.create_it(pos=hm.Pos.BEGIN, type="closing", x=300),
    "document",
    hm.create_it(pos=hm.Pos.END, type="closing", x=300),
    ".",
]

source_tuv = hm.create_tuv("en", content=segment_content)

# Create target with equivalent nested structure
target_content = [
    "Cliquez sur le ",
    hm.create_bpt(
        i=1,
        type="lien",
        x=100,
        content=[
            hm.create_sub(
                content=["ici", hm.create_hi(content=["important"])],
                datatype="text",
            )
        ],
    ),
    " pour continuer. ",
    "Pour les cas spéciaux, utilisez ",
    hm.create_ph(
        assoc=hm.Assoc.B,
        type="variable",
        x=200,
        content=[
            hm.create_sub(
                content=[
                    "la ",
                    hm.create_bpt(i=2, type="emphasis", content=[hm.create_sub(content=["valeur par défaut"])]),
                    " valeur",
                ],
                datatype="text",
            )
        ],
    ),
    ". ",
    "Fin du ",
    hm.create_it(pos=hm.Pos.BEGIN, type="closing", x=300),
    "document",
    hm.create_it(pos=hm.Pos.END, type="closing", x=300),
    ".",
]

target_tuv = hm.create_tuv("fr", content=target_content)

# Create a translation unit with metadata
tu = hm.create_tu(
    tuid="complex-nesting-001",
    srclang="en",
    variants=[source_tuv, target_tuv],
    props=[
        hm.create_prop("customer", "acme-corp"),
        hm.create_prop("domain", "technical"),
    ],
    notes=[hm.create_note("Demonstrates full TMX 1.4b Level 2 nesting support")],
)

# Assemble the TMX
tmx = hm.create_tmx(header=header, body=[tu])

# Save
hm.save(tmx, "complex.tmx")

# Verify the nesting structure
print(f"Source TUV has {len(source_tuv.content)} content elements")
print(f"Target TUV has {len(target_tuv.content)} content elements")

# Inspect the nested structure programmatically
def inspect_content(content, indent=0):
    prefix = "  " * indent
    for item in content:
        if isinstance(item, str):
            print(f"{prefix}Text: {repr(item[:50])}...")
        else:
            print(f"{prefix}{item.__class__.__name__}")
            if hasattr(item, 'content') and item.content:
                inspect_content(item.content, indent + 1)

print("\nSource content structure:")
inspect_content(source_tuv.content)
```

## Architecture

Hypomnema is built on three decoupled layers:

1. **Backend Layer** (`hypomnema.xml.backends`)

   - Abstracts the XML parser implementation
   - `LxmlBackend`: Fast, feature-rich (requires `lxml`)
   - `StandardBackend`: Portable, stdlib only
   - Implement `XmlBackend` to add custom backends

2. **Orchestration Layer** (`hypomnema.xml`)

   - `Serializer`: Converts Python objects to XML
   - `Deserializer`: Converts XML to Python objects
   - Manages recursion and dispatches to handlers

3. **Handler Layer**
   - Specialized classes for each TMX element type
   - Implement business logic and policy checks
   - Examples: `NoteSerializer`, `PropDeserializer`

## Supported Elements

Hypomnema implements the complete TMX 1.4b object model:

**Structural elements:** `Tmx`, `Header`, `Tu` (Translation Unit), `Tuv` (Translation Unit Variant)

**Inline elements:** `Bpt` (Begin Paired Tag), `Ept` (End Paired Tag), `It` (Isolated Tag), `Ph` (Placeholder), `Hi` (Highlight), `Sub` (Sub-flow)

**Auxiliary elements:** `Prop` (Property), `Note` (Annotation)

**Enumerations:** `Segtype` (segmentation level), `Pos` (tag position), `Assoc` (placeholder association)

## Terminology Reference

See [TERMINOLOGY.md](./TERMINOLOGY.md) for a quick reference of TMX 1.4b terminology used throughout the library.

## Contributing

Contributions are welcome. Please read the [TMX 1.4b specification](https://resources.gala-global.org/tbx14b) first — it is essential understanding for any changes to this library.

## License

MIT
