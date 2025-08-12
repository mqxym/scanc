from pathlib import Path
from subprocess import run
import pytest
import sys

def test_cli_basic(tmp_path: Path):
    (tmp_path / "x.js").write_text("console.log(1);")

    result = run(
        ["scanc", "-e", "js", str(tmp_path)],
        capture_output=True,
        text=True,
    )

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    assert result.returncode == 0
    assert "**x.js**" in result.stdout