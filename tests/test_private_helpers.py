from pathlib import Path

from scanc.tree import build_markdown_tree
from scanc.core import ScannedFile


def test_build_markdown_tree_single_file(tmp_path: Path):
    p = tmp_path / "x.txt"
    p.write_text("x")
    files = [ScannedFile(path=p.relative_to(tmp_path), language="text", content="x")]
    md = build_markdown_tree([p], files)
    assert "└── x.txt" in md