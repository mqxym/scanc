from pathlib import Path

from scanc.core import scan_directory


def test_scan_filters(tmp_path: Path):
    # Arrange - create some files & dirs
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules/skip.js").write_text("console.log('skip');")
    (tmp_path / "keep.py").write_text("print('ok')")
    (tmp_path / "README.md").write_text("# Readme")

    # Act
    files, _ = scan_directory(paths=[tmp_path], extensions=["py"])

    # Assert - only keep.py should survive
    assert len(files) == 1
    assert files[0].path.name == "keep.py"


def test_scan_single_file_path(tmp_path: Path):
    """
    A single-file scan should yield exactly one ScannedFile whose *relative*
    path is ``"."`` (implementation detail) or the filename.
    """
    f = tmp_path / "solo.py"
    f.write_text("pass")

    files, tree = scan_directory(paths=[f], include_tree=True)

    assert len(files) == 1
    assert str(files[0].path) in {".", "solo.py"}
    assert "solo.py" in tree


def test_scan_include_then_exclude_regex(tmp_path: Path):
    """
    The implementation treats *include* patterns as a whitelist; if any are
    supplied the file *must* match at least one of them even if it also
    matches an exclude pattern.
    """
    bad = tmp_path / "bad.py"
    good = tmp_path / "good.py"
    bad.write_text("raise")
    good.write_text("print(1)")

    files, _ = scan_directory(
        paths=[tmp_path],
        extensions=["py"],
        exclude_regex=[r"bad"],
        include_regex=[r"good"],
    )

    assert {f.path.name for f in files} == {"good.py"}