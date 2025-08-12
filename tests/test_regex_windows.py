from pathlib import PureWindowsPath
from scanc.core import scan_directory
from pathlib import Path

def test_regex_paths_are_posix(tmp_path: Path):
    p = tmp_path / "bad.py"
    p.write_text("raise")
    # pattern uses forward slash only
    files, _ = scan_directory(
        paths=[tmp_path],
        extensions=["py"],
        exclude_regex=[r"bad\.py$"],
    )
    assert not files