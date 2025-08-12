# src/scanc/tree.py
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
from io import StringIO

from treelib import Tree


def _to_tree(paths: Iterable[Path]) -> str:
    """
    Build an ASCII directory tree using treelib.
    """
    tree = Tree()
    # Create a dummy root
    tree.create_node(tag=".", identifier=".")
    for p in sorted(set(paths)):
        parts = p.parts
        parent = "."
        for part in parts:
            node_id = f"{parent}/{part}"
            if not tree.contains(node_id):
                tree.create_node(tag=part, identifier=node_id, parent=parent)
            parent = node_id
    # Capture output without printing to stdout
    raw = tree.show(stdout=False)
    # tree.show returns bytes in recent versions
    if isinstance(raw, (bytes, bytearray)):
        text = raw.decode("utf-8")
    else:
        text = str(raw)
    lines = text.splitlines()
    # Drop the root line
    tree_lines = lines[1:]
    return "\n".join(tree_lines)


def build_markdown_tree(scan_roots: Iterable[Path], files: List[ScannedFile]) -> str:
    """
    Return a fenced Markdown code-block containing the directory tree,
    respecting what was actually scanned.
    """
    all_paths = [f.path for f in files]
    for r in scan_roots:
        if r.is_file():
            all_paths.append(Path(r.name))
    tree_str = _to_tree(all_paths)
    return f"**File Structure**\n\n```text\n{tree_str}\n```\n"
