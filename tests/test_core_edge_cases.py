from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from scanc.core import DEFAULT_EXCLUDES, ScannedFile, scan_directory


def _write(tmp: Path, rel: str, content: str = "x") -> Path:
    p = tmp / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def test_include_overrides_exclude(tmp_path: Path) -> None:
    _write(tmp_path, "build/keep.js")
    files, _ = scan_directory(
        paths=[tmp_path],
        extensions=["js"],
        exclude_regex=[r"build/"],
        include_regex=[r"keep\.js$"],
    )
    assert [f.path.as_posix() for f in files] == ["build/keep.js"]


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="OS does not support symlinks")
def test_symlink_traversal(tmp_path: Path) -> None:
    real = _write(tmp_path, "real.py", "print(1)")
    sym = tmp_path / "link.py"
    os.symlink(real, sym)
    # default: no symlinks
    files, _ = scan_directory(paths=[tmp_path], extensions=["py"])
    assert {f.path.name for f in files} == {"real.py"}
    # follow symlinks
    files, _ = scan_directory(paths=[tmp_path], extensions=["py"], follow_symlinks=True)
    assert {f.path.name for f in files} == {"real.py", "link.py"}


def test_max_size_filter(tmp_path: Path) -> None:
    big = _write(tmp_path, "big.txt", "a" * (2 * 1024 * 1024))  # 2 MiB
    small = _write(tmp_path, "small.txt", "ok")
    files, _ = scan_directory(paths=[tmp_path], max_size=1024 * 1024)  # 1 MiB
    assert [f.path.name for f in files] == ["small.txt"]


def test_binary_files_are_skipped(tmp_path: Path) -> None:
    binf = tmp_path / "b.bin"
    binf.write_bytes(b"\x00\x01\x02")
    textf = _write(tmp_path, "ok.txt", "hi")
    files, _ = scan_directory(paths=[tmp_path])
    assert [f.path.name for f in files] == ["ok.txt"]