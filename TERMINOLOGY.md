# Terminology

This document provides a quick reference for TMX 1.4b terminology used in Hypomnema.

**Important:** Read the [official TMX 1.4b specification](https://resources.gala-global.org/tbx14b) - it is short and essential for understanding the data model.

## Core Structure

| Element | Description |
|---------|-------------|
| `<tmx>` | Root container for translation memory files |
| `<header>` | Metadata about the TMX file (creation tool, source language, etc.) |
| `<body>` | Container for translation units |
| `<tu>` | Translation Unit - container for one or more language variants |
| `<tuv>` | Translation Unit Variant - one language version of a `<tu>` |
| `<seg>` | Segment - the actual translatable content within a `<tuv>` |

## Inline Elements

These elements appear inside `<seg>` content to mark up formatting, placeholders, etc.

| Element | Description |
|---------|-------------|
| `<bpt>` | Begin Paired Tag - opening half of an inline tag pair |
| `<ept>` | End Paired Tag - closing half of an inline tag pair |
| `<it>` | Isolated Tag - standalone placeholder |
| `<ph>` | Placeholder - replaces a native code fragment |
| `<hi>` | Highlight - marks highlighted/emphasized text |
| `<sub>` | Sub-flow - nested translatable unit |

## Auxiliary Elements

| Element | Description |
|---------|-------------|
| `<prop>` | Property - key-value metadata attached to `<header>`, `<tu>`, or `<tuv>` |
| `<note>` | Annotation/comment attached to `<header>`, `<tu>`, or `<tuv>` |

## Enumerations

| Enum | Values | Description |
|------|--------|-------------|
| `segtype` | `block`, `paragraph`, `sentence`, `phrase` | Segmentation level |
| `pos` | `begin`, `end` | Position of isolated tag (`<it>`) |
| `assoc` | `p`, `f`, `b` | Association of placeholder (`<ph>`) with surrounding text |

## Intentionally Omitted Elements

The following TMX 1.4b elements are **not modeled** in Hypomnema:

- `<ude>` - User Defined Encoding (custom encoding handling)
- `<map>` - Character mapping

These elements relate to custom encodings and character mapping, which introduce significant complexity. They are rarely encountered in practice and were intentionally excluded to keep the library focused and maintainable.
