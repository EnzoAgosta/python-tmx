# python-tmx

[![PyPI version](https://badge.fury.io/py/python-tmx.svg)](https://badge.fury.io/py/python-tmx)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**The industrial-grade TMX framework for Python.**

`python-tmx` is a strictly typed, policy-driven parser and generator for the [TMX 1.4b](https://www.gala-global.org/tmx-14b) standard. It provides a robust infrastructure for building Localization and NLP tools, designed to handle messy translation memories without crashing.

## 🚀 Why this library?

Most TMX parsers are simple XML wrappers. `python-tmx` is an infrastructure library offering:

*   **🛡️ Policy-Driven Recovery:** Configure exactly how to handle errors (missing segments, extra text, invalid tags). Choose between `raise`, `ignore`, `log`, or `repair`.
*   **🔌 Backend Agnostic:** Runs on `lxml` for speed or standard `xml.etree` for zero-dependency environments.
*   **✨ Type Safe:** Fully annotated with modern Python 3.12+ types. Returns structured Dataclasses, not raw XML nodes.
*   **🏗️ Symmetrical:** Deserialize XML to Objects, manipulate them, and Serialize back to XML with roundtrip integrity.

## 📦 Installation

```bash
pip install python-tmx
OR
uv add python-tmx
```

*For maximum performance, install with lxml support and use the LxmlBackend:*
```bash
pip install "python-tmx[lxml]"
OR
uv add python-tmx[lxml]
```

## ⚡ Usage (Low-Level API)

*Note: v0.4 exposes the core architecture components. Better docs and high-level convenience facades (`load`/`dump`) are coming in v0.5.*

### 1. Deserializing (Reading)

To parse a file, you compose a **Backend** (the parser) with a **Deserializer** (the logic).

```python
import xml.etree.ElementTree as ET
from python_tmx.xml.backends.standard import StandardBackend
from python_tmx.xml.deserialization import Deserializer
from python_tmx.base.types import Tmx

# 1. Initialize the Backend
backend = StandardBackend()

# 2. Initialize the Deserializer
deserializer = Deserializer(backend=backend)

# 3. Parse content (using standard ET for I/O in this example)
tree = ET.parse("memory.tmx")
root_element = tree.getroot()

# 4. Deserialize to Python Objects
tmx: Tmx = deserializer.deserialize(root_element)

print(f"Source Language: {tmx.header.srclang}")
for tu in tmx.body:
    print(f"TU: {tu.tuid}")
```

### 2. Handling Dirty Data (Policies)

Real-world TMX files are often broken. Configure a `DeserializationPolicy` to handle errors gracefully.

If not specified, the default policy is strict on purpose to fail fast and prevent silent data corruption.

You can configure also configure the logging level for each policy value independently of its behavior.

```python
from python_tmx.xml.policy import DeserializationPolicy, PolicyValue
from python_tmx.xml.deserialization import Deserializer
import logging

# Configure a permissive policy
policy = DeserializationPolicy()

# If a <tuv> has no <seg>, don't crash -> ignore the error (returns empty content)
policy.missing_seg = PolicyValue("ignore", logging.WARNING)

# If a <tu> has garbage text between tags, ignore it
policy.extra_text = PolicyValue("ignore", logging.INFO)

deserializer = Deserializer(backend=backend, policy=policy)
tmx = deserializer.deserialize(root_element)
```

### 3. Serializing (Writing)

```python
from datetime import datetime, timezone
from python_tmx.base.types import Tmx, Header, Tu, Tuv, Segtype
from python_tmx.xml.serialization import Serializer

# 1. Build the object tree
tmx_obj = Tmx(
    version="1.4",
    header=Header(
        creationtool="MyScript",
        creationtoolversion="1.0",
        segtype=Segtype.SENTENCE,
        o_tmf="JSON",
        adminlang="en-US",
        srclang="en-US",
        datatype="plaintext",
        creationdate=datetime.now(timezone.utc)
    ),
    body=[
        Tu(
            tuid="1",
            srclang="en-US",
            variants=[
                Tuv(lang="en-US", content=["Hello World"]),
                Tuv(lang="fr-FR", content=["Bonjour le monde"])
            ]
        )
    ]
)

# 2. Serialize to XML Element
serializer = Serializer(backend=backend)
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

TMX segments often contain inline markup like placeholders (`<ph>`) or formatting (`<bpt>`). `python-tmx` parses these into a mixed list of strings and objects.

```python
from python_tmx.base.types import Ph, Bpt

# Content is a list of strings and Inline objects
# XML: Hello <ph x="1">Name</ph>
print(variant.content) 
# Output: ["Hello ", Ph(x=1, content=["Name"])]
```

## 🤝 Contributing

We welcome contributions!

Before you submit a pull request, please ensure:
- Your code is fully typed with no Type Error from Pylance in `standard` mode
- All tests pass
- Your code is formatted with `ruff` using the config
- Code coverage is 100% 

## 📄 License

MIT