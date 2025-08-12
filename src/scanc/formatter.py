from __future__ import annotations

from typing import Callable, List, Protocol

from .core import ScannedFile

# --------------------------------------------------------------------------- #
# Formatter protocol
# --------------------------------------------------------------------------- #


class Formatter(Protocol):
    def __call__(self, files: List[ScannedFile], tree_md: str | None) -> str: ...


# --------------------------------------------------------------------------- #
# Default markdown formatter
# --------------------------------------------------------------------------- #


def _markdown(files: List[ScannedFile], tree_md: str | None) -> str:
    blocks: list[str] = []
    blocks.append("---\n\n## Codebase Scan\n\n")
    if tree_md:
        blocks.append(tree_md.rstrip() + "\n")
    for f in files:
        blocks.append(f"**{f.path}**\n\n```{f.language}\n{f.content}\n```\n")
    return "\n".join(blocks)


MARKDOWN: Formatter = _markdown


# --------------------------------------------------------------------------- #
# Extensibility hook
# --------------------------------------------------------------------------- #


def format_result(files: List[ScannedFile], tree_md: str | None, formatter: Formatter) -> str:
    return formatter(files, tree_md)