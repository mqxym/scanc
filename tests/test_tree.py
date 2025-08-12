from pathlib import Path

from scanc.core import scan_directory


def test_tree_included(tmp_path: Path):
    (tmp_path / "a.py").write_text("pass")
    files, tree_md = scan_directory(paths=[tmp_path], include_tree=True)
    assert tree_md is not None
    assert "a.py" in tree_md