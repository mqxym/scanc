from __future__ import annotations

from typing import Callable, List, Protocol
from pathlib import Path
from xml.sax.saxutils import escape

from .core import ScannedFile

# --------------------------------------------------------------------------- #
# Formatter protocol
# --------------------------------------------------------------------------- #


class Formatter(Protocol):
    def __call__(self, files: List[ScannedFile], tree_md: str | None) -> str: ...


# --------------------------------------------------------------------------- #
# Default markdown formatter
# --------------------------------------------------------------------------- #


def _markdown(files: List[ScannedFile], tree: str | None) -> str:
    
    def tree_md (tree_str: str) -> str:
        return f"**File Structure**\n\n```text\n{tree_str}\n```\n"
    
    blocks: list[str] = []
    blocks.append("---\n\n## Codebase Scan\n\n")
    if tree:
        blocks.append(tree_md(tree).rstrip() + "\n")
    for f in files:
        blocks.append(f"**{f.path}**\n\n```{f.language}\n{f.content}\n```\n")
    return "\n".join(blocks)


MARKDOWN: Formatter = _markdown

# --------------------------------------------------------------------------- #
# XML formatter
# --------------------------------------------------------------------------- #


def _xml(files: List[ScannedFile], tree: str | None) -> str:
    
    parts: list[str] = []
    parts.append("<scan>")

    if tree:
        parts.append("<tree><![CDATA[\n" + tree.strip() + "\n]]></tree>")

    for f in files:
        ext = Path(f.path).suffix.lstrip(".") or (f.language or "")
        path_attr = escape(str(f.path), {'"': "&quot;"})
        lang_attr = escape(str(ext), {'"': "&quot;"})

        parts.append(
            f'<file path="{path_attr}">'
            f'<code language="{lang_attr}"><![CDATA[\n{f.content}\n]]></code>'
            f"</file>"
        )

    parts.append("</scan>")
    return "\n".join(parts)


XML: Formatter = _xml

# --------------------------------------------------------------------------- #
# Extensibility hook
# --------------------------------------------------------------------------- #

FORMATTERS: dict[str, Formatter] = {
    "markdown": MARKDOWN,
    "xml": XML,
}


# --------------------------------------------------------------------------- #
# Format dispatcher
# --------------------------------------------------------------------------- #

def format_result(
    files: List[ScannedFile],
    tree: str | None,
    format_name: str,
) -> str:
    """Format scan results using the given format name."""
    try:
        formatter = FORMATTERS[format_name.lower()]
    except KeyError:
        raise ValueError(f"Unknown format: {format_name}")
    return formatter(files, tree)