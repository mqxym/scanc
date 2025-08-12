from __future__ import annotations

import re
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from .tree import build_markdown_tree

# --------------------------------------------------------------------------- #
# Defaults
# --------------------------------------------------------------------------- #

DEFAULT_EXCLUDES: set[str] = {
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    "target",
    ".gradle",
    ".cargo",
    ".next",
    ".tox",
    ".DS_Store",
    ".bin",
}

TEXT_CHUNK = 8192  # bytes used to check if file is text/binary

# --------------------------------------------------------------------------- #
# Models
# --------------------------------------------------------------------------- #

import sys
from dataclasses import dataclass

if sys.version_info >= (3, 10):
    _dataclass = dataclass 
    _slots_kw = {"slots": True}
else:
    from functools import partial
    _dataclass = partial(dataclass)
    _slots_kw = {}

@_dataclass(**_slots_kw)                      # expands to slots=True when valid
class ScannedFile:
    path: Path
    language: str
    content: str

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _is_binary(file_path: Path) -> bool:
    """
    Return True for “binary-ish” files.

    Heuristic:
    1.  If any NUL byte is found in the first TEXT_CHUNK, the file is binary.
    2.  If the bytes do not decode as UTF-8, the file is binary.
    """
    try:
        with file_path.open("rb") as fh:
            chunk = fh.read(TEXT_CHUNK)
    except OSError:
        return True

    if b"\x00" in chunk:
        return True

    try:
        chunk.decode("utf-8")
    except UnicodeDecodeError:
        return True

    return False 


def _normalise_ext(exts: Sequence[str] | None) -> set[str] | None:
    """
    Return a normalised *non-empty* set of lowercase extensions or ``None``.
    Raises ``ValueError`` if a list was provided but all entries were blank,
    preventing the surprising “match everything” situation.
    """
    if exts is None:
        return None
    norm = {e.strip().lower().lstrip(".") for e in exts or [] if e and e.strip()}
    if not norm:
        raise ValueError("extensions list contained no usable entries")
    return norm


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def scan_directory(
    *,
    paths: Iterable[Path],
    extensions: Sequence[str] | None = None,
    include_regex: Sequence[str] | None = None,
    exclude_regex: Sequence[str] | None = None,
    use_default_excludes: bool = True,
    include_tree: bool = False,
    max_size: int = 1_048_576,
    follow_symlinks: bool = False,
) -> Tuple[List[ScannedFile], str | None]:
    """
    Return list of ScannedFile + optional pre-rendered tree Markdown.
    """
    exts = _normalise_ext(extensions)
    inc_patterns = [re.compile(p) for p in (include_regex or [])]
    exc_patterns = [re.compile(p) for p in (exclude_regex or [])]

    files: List[ScannedFile] = []

    def _excluded(p: Path) -> bool:
        # If the file matches ANY include-regex, it is explicitly kept.
        if inc_patterns and any(r.search(str(p)) for r in inc_patterns):
            return False

        # Built-in block-lists (node_modules etc.)
        if use_default_excludes and any(part in DEFAULT_EXCLUDES for part in p.parts):
            return True

        # User exclude-regexes
        posix = p.as_posix()
        if any(r.search(posix) for r in exc_patterns):
            return True

        # If include-regexes exist but we haven’t matched any yet → exclude
        if inc_patterns:
            return True

        return False

    for root in paths:
        root = root.resolve()
        walker = root.rglob("*") if root.is_dir() else [root]  # type: ignore[arg-type]
        for path in walker:
            if path.is_dir():
                continue
            if not follow_symlinks and path.is_symlink():
                continue
            try:
                size = (
                    path.stat().st_size        # follows symlinks
                    if follow_symlinks
                    else path.lstat().st_size  # metadata of the link itself
                )
            except OSError:                    # broken link, permission issue, race…
                continue
            if size > max_size:
                continue
            if _excluded(path):
                continue
            lang = path.suffix.lower().lstrip(".")
            if exts and lang not in exts:
                continue
            if _is_binary(path):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue
            common_root = Path(os.path.commonpath([*paths]))
            relative = path.relative_to(common_root) if path.is_absolute() else path
            files.append(ScannedFile(path=relative, language=lang or "text", content=text))

    tree_md = build_markdown_tree(paths, files) if include_tree else None
    return files, tree_md