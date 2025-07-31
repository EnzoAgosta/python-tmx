# PythonTmx Roadmap

A living roadmap for the v0.4+ rewrite of PythonTmx

---

## ✅ Core Architecture

- ✅ Robust error hierarchy
- ✅ Strongly-typed element protocols and base classes
- ✅ Pluggable, library-agnostic parser base
- ✅ Utilities for validation, file checks, and error raising

## TMX Element Implementations

- ✅ Structural Elements
  - ✅ `Prop`
  - ✅ `Note`
  - ✅ `Map`
  - ✅ `Ude`
  - ✅ `Header`
  - ✅ `Tu`
  - ✅ `Tuv`
- ✅ Inline Elements 
  - ✅ `Bpt`
  - ✅ `Ept`
  - ✅ `Ph`
  - ✅ `Hi`
  - ✅ `It`
  - ✅ `Ut`

## ✅ Parser Backends

- ✅`LxmlParser`
- ✅`StandardParser`

## Testing

- ✅ Test structure and pytest setup
- ✅ Full Prop element test suite (happy/error paths)
- ✅ Test coverage for each new element
- ✅ Test parser backends (basic + edge cases)
- ✅ Error-path, malformed XML, and roundtrip tests

## 🚧 Documentation

- ✅ Google style docstrings for core classes
- ✅ Docstrings for all element and parser classes
- ✅ Sphinx config and basic API docs
- Contributor guide, usage examples, and FAQ

## Scripts & Demos

- CLI for validating and pretty-printing TMX files
- Example: convert between XML backends
- Example: TMX roundtrip/merge
- Showcase scripts for localization workflows

## Release/Community

- v0.4 alpha release
- Migration guide from old version
- Gather feedback, iterate, and roadmap v1.0

---

**Legend:**  
- ✅ = Done  
- 🚧 = In progress / Next up
- 🔜 = Next up
