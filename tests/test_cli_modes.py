from __future__ import annotations

import sys
from pathlib import Path
from subprocess import run
import textwrap

import pytest
import re


def _run_cli(args: list[str]):
    """Thin wrapper to execute the installed `scanc` executable."""
    return run(["scanc", *args], text=True, capture_output=True, check=False)


def test_cli_token_count_only(tmp_path: Path):
    """
    When --tokens is used the tool prints *only* the numeric count
    (integer or float, with optional thousands-separators) and exits 0.
    """
    (tmp_path / "a.py").write_text("print('hi')")
    res = _run_cli(["--tokens", "gpt-3.5-turbo", str(tmp_path)])

    assert res.returncode == 0, res.stderr
    assert re.fullmatch(r"\d[\d,]*(\.\d+)?\s*", res.stdout), res.stdout


def test_cli_tree_and_outfile(tmp_path: Path):
    (tmp_path / "b.ts").write_text("console.log('hi')")
    out = tmp_path / "result.md"
    res = _run_cli(["-e", "ts", "--tree", "-o", str(out), str(tmp_path)])
    assert res.returncode == 0
    assert "**File Structure**\n\n```text" in out.read_text(encoding="utf-8")
    # stderr should mention saved message
    assert "Saved to" in res.stderr