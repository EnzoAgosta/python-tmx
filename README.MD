# Hypomnema

[![PyPI version](https://badge.fury.io/py/hypomnema.svg)](https://badge.fury.io/py/hypomnema)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**The industrial-grade TMX framework for Python.**

`Hypomnema` is a strictly typed, policy-driven parser and generator for the [TMX 1.4b](https://www.gala-global.org/tmx-14b) standard. It provides a robust infrastructure for building Localization and NLP tools, designed to handle messy translation memories without crashing.

## 🚀 Why this library?

Most TMX parsers are simple XML wrappers. `Hypomnema` is an infrastructure library offering:

*   **🛡️ Policy-Driven Recovery:** Configure exactly how to handle errors (missing segments, extra text, invalid tags). Choose between `raise`, `ignore`, `log`, or `repair`.
*   **🔌 Backend Agnostic:** Runs on `lxml` for speed or standard `xml.etree` for zero-dependency environments.
*   **✨ Type Safe:** Fully annotated with modern Python 3.12+ types. Returns structured Dataclasses, not raw XML nodes.
*   **🏗️ Symmetrical:** Deserialize XML to Objects, manipulate them, and Serialize back to XML with roundtrip integrity.

## 📦 Installation

```bash
pip install hypomnema
OR
uv add hypomnema
```

*For maximum performance, install with lxml support and use the LxmlBackend:*
```bash
pip install "hypomnema[lxml]"
OR
uv add hypomnema[lxml]
```

## ⚡ Usage (Low-Level API)

*Note: v0.4.2 exposes the core architecture components. Better docs and high-level convenience facades (`load`/`dump`) are coming in v0.5.*

### 1. Deserializing (Reading)

To parse a file, you compose a **Backend** (the parser) with a **Deserializer** (the logic).

```python
import xml.etree.ElementTree as ET
import hypomnema as hm

# 1. Initialize the Backend
backend = hm.StandardBackend()

# 2. Initialize the Deserializer
deserializer = hm.Deserializer(backend=backend)

# 3. Parse content (using standard ET for I/O in this example)
tree = ET.parse("memory.tmx")
root_element = tree.getroot()

# 4. Deserialize to Python Objects
tmx: hm.Tmx = deserializer.deserialize(root_element)

print(f"Source Language: {tmx.header.srclang}")
for tu in tmx.body:
    print(f"TU: {tu.tuid}")
```

### 2. Handling Dirty Data (Policies)

Real-world TMX files are often broken. Configure a `DeserializationPolicy` to handle errors gracefully.

If not specified, the default policy is strict on purpose to fail fast and prevent silent data corruption.

You can configure also configure the logging level for each policy value independently of its behavior.

```python
import hypomnema as hm
import logging

# Configure a permissive policy
policy = hm.DeserializationPolicy()

# If a <tuv> has no <seg>, don't crash -> ignore the error (returns empty content)
hm.policy.missing_seg = PolicyValue("ignore", logging.WARNING)

# If a <tu> has garbage text between tags, ignore it
policy.extra_text = hm.PolicyValue("ignore", logging.INFO)

deserializer = hm.Deserializer(backend=backend, policy=policy)
tmx = deserializer.deserialize(root_element)
```

### 3. Serializing (Writing)

```python
from datetime import datetime, timezone
import hypomnema as hm

# 1. Build the object tree
tmx_obj = hm.Tmx(
    version="1.4",
    header=hm.Header(
        creationtool="MyScript",
        creationtoolversion="1.0",
        segtype=hm.Segtype.SENTENCE,
        o_tmf="JSON",
        adminlang="en-US",
        srclang="en-US",
        datatype="plaintext",
        creationdate=datetime.now(timezone.utc)
    ),
    body=[
        hm.Tu(
            tuid="1",
            srclang="en-US",
            variants=[
                hm.Tuv(lang="en-US", content=["Hello World"]),
                hm.Tuv(lang="fr-FR", content=["Bonjour le monde"])
            ]
        )
    ]
)

# 2. Serialize to XML Element
serializer = hm.Serializer(backend=backend)
xml_root = serializer.serialize(tmx_obj)

# 3. Write to file (using backend specifics)
ET.ElementTree(xml_root).write("output.tmx", encoding="utf-8", xml_declaration=True)
```

## 🧩 Architecture

The library is built on three decoupled layers:

1.  **Backend Layer:** Abstracts the XML parser. `LxmlBackend` (fast, features) vs `StandardBackend` (portable).
2.  **Orchestration Layer:** `Serializer` and `Deserializer` classes that manage recursion and dispatch.
3.  **Handler Layer:** Specialized classes (`TuvDeserializer`, `NoteSerializer`) that implement the business logic and policy checks for specific TMX elements.

## 🛠️ Advanced Usage

### Working with Mixed Content (Tags)

TMX segments often contain inline markup like placeholders (`<ph>`) or formatting (`<bpt>`). `hypomnema` parses these into a mixed list of strings and objects.

```python
import hypomnema as hm

# Content is a list of strings and Inline objects
# XML: Hello <ph x="1">Name</ph>
print(variant.content) 
# Output: ["Hello ", Ph(x=1, content=["Name"])]
```