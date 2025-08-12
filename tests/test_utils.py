from __future__ import annotations

import pytest
from pathlib import Path

from scanc.cli import _comma_separated
from scanc.core import _is_binary, _normalise_ext


# --------------------------------------------------------------------------- #
# _normalise_ext
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ([".Py", " js ", "PY"], {"py", "js"}),
    ],
)
def test_normalise_ext_various(raw, expected) -> None:
    assert _normalise_ext(raw) == expected


def test_normalise_ext_blank_list_raises() -> None:
    with pytest.raises(ValueError):
        _normalise_ext(["", "   "])


def test_normalise_ext_none_returns_none() -> None:
    assert _normalise_ext(None) is None


# --------------------------------------------------------------------------- #
# _is_binary
# --------------------------------------------------------------------------- #

def test_is_binary_detects_null_bytes(tmp_path: Path) -> None:
    p = tmp_path / "bin.dat"
    p.write_bytes(b"\x00\x01\x02")
    assert _is_binary(p) is True


def test_is_binary_handles_non_utf8(tmp_path: Path) -> None:
    p = tmp_path / "latin1.txt"
    p.write_bytes("olá".encode("latin1"))  # not valid UTF-8
    assert _is_binary(p) is True


# --------------------------------------------------------------------------- #
# _comma_separated
# --------------------------------------------------------------------------- #

def test_comma_separated_callback() -> None:
    assert _comma_separated(None, None, None) is None
    assert _comma_separated(None, None, "py, js ,,  ts") == ["js", "py", "ts"]
    
def test_normalise_ext_whitespace_and_dupes():
    assert _normalise_ext(["  .Js ", "js", "JS  "]) == {"js"}