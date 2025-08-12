from pathlib import Path
import os
import sys
import io
import pytest

from scanc.core import scan_directory, _is_binary
from scanc.cli import main as cli_main
import click.testing as ct

def test_is_binary_large_file(tmp_path: Path):
    big = tmp_path / "big.dat"
    big.write_bytes(b"\x00" + b"x" * (5 * 1024 * 1024))
    assert _is_binary(big) is True 

def test_scan_broken_symlink(tmp_path: Path):
    broken = tmp_path / "dangling"
    broken.symlink_to(tmp_path / "missing.txt")
    files, _ = scan_directory(paths=[tmp_path], follow_symlinks=False)
    assert files == []                         # silently skipped

def test_cli_duplicate_write(tmp_path: Path, monkeypatch):
    # run `scanc` with outfile and check only one write
    src = tmp_path / "a.py"
    src.write_text("print(1)")

    out = tmp_path / "out.md"
    runner = ct.CliRunner()
    result = runner.invoke(cli_main, ["-e", "py", "-o", str(out), str(tmp_path)])
    assert result.exit_code == 0
    text = out.read_text()
    assert text.count("print(1)") == 1         # written exactly once