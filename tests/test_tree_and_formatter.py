from __future__ import annotations

from pathlib import Path

from scanc.core import scan_directory
from scanc.formatter import MARKDOWN
from scanc.tree import _to_tree


def test_to_tree_nested(tmp_path: Path) -> None:
    (tmp_path / "a/b").mkdir(parents=True)
    (tmp_path / "a/b/file.py").write_text("pass")
    tree = _to_tree([(tmp_path / "a/b/file.py").relative_to(tmp_path)])
    assert "└── file.py" in tree


def test_markdown_formatter_with_tree(tmp_path: Path) -> None:
    (tmp_path / "x.js").write_text("console.log(1)")
    files, tree_md = scan_directory(paths=[tmp_path], include_tree=True)
    md = MARKDOWN(files, tree_md)

    # one code fence pair for the tree and another pair for the file
    assert "**File Structure**\n\n```text" in md.strip()
    assert md.count("```") == 4
    assert "**x.js**" in md