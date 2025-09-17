from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from click.testing import CliRunner

from scanc.core import scan_directory, ScannedFile
from scanc.formatter import format_result
from scanc.cli import main as cli_main


def _parse(xml_text: str) -> ET.Element:
    # Will raise if the output isn't well-formed XML
    return ET.fromstring(xml_text)


def test_xml_formatter_basic_structure_and_languages(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("print('hi')")
    (tmp_path / "README").write_text("no extension here")
    # include_tree=True to exercise <tree><![CDATA[...]]></tree>
    files, tree = scan_directory(paths=[tmp_path], include_tree=True)

    xml_text = format_result(files=files, tree=tree, format_name="xml")
    root = _parse(xml_text)

    assert root.tag == "scan"

    # tree is optional but should be present because include_tree=True
    tree_nodes = root.findall("tree")
    assert len(tree_nodes) == 1
    assert "a.py" in (tree_nodes[0].text or "")

    # There should be a <file> entry per input file
    file_nodes = root.findall("file")
    paths_in_xml = {n.attrib["path"] for n in file_nodes}
    assert paths_in_xml == {"a.py", "README"}  # relative paths

    # Check code blocks + language attribute mapping
    by_path = {n.attrib["path"]: n for n in file_nodes}
    code_a = by_path["a.py"].find("code")
    code_readme = by_path["README"].find("code")
    assert code_a is not None and code_readme is not None

    # language is the suffix without dot, or falls back to ScannedFile.language
    assert code_a.attrib.get("language") == "py"
    assert code_readme.attrib.get("language") == "text"

    # CDATA should preserve content; ElementTree exposes it as .text
    assert "print('hi')" in (code_a.text or "")
    assert "no extension here" in (code_readme.text or "")


def test_xml_formatter_escapes_path_and_preserves_special_content(tmp_path: Path) -> None:
    # Use a path that is safe on all platforms but requires XML escaping (&)
    weird = tmp_path / "a&b.py"
    weird.write_text("<tag attr=\"x\">& ' \"</tag>")
    files, tree = scan_directory(paths=[tmp_path], include_tree=False)

    xml_text = format_result(files=files, tree=tree, format_name="xml")
    root = _parse(xml_text)

    node = root.find("file")
    assert node is not None
    # Attribute should round-trip through XML escaping
    assert node.attrib["path"].endswith("a&b.py")

    code = node.find("code")
    assert code is not None
    # The raw special characters must survive inside CDATA
    body = (code.text or "")
    assert "<tag attr=\"x\">& ' \"</tag>" in body


def test_xml_formatter_unknown_format_raises(tmp_path: Path) -> None:
    p = tmp_path / "x.txt"
    p.write_text("x")
    files = [ScannedFile(path=p.relative_to(tmp_path), language="text", content="x")]

    with pytest.raises(ValueError):
        format_result(files=files, tree=None, format_name="not-a-format")


def test_cli_emits_valid_xml_with_tree(tmp_path: Path) -> None:
    (tmp_path / "m.py").write_text("print(1)")
    (tmp_path / "n.js").write_text("console.log(2)")

    runner = CliRunner()
    res = runner.invoke(
        cli_main,
        ["--tree", "-f", "xml", str(tmp_path)],
    )

    assert res.exit_code == 0, res.output
    root = _parse(res.stdout)

    # sanity checks
    assert root.tag == "scan"
    tree_nodes = root.findall("tree")
    assert len(tree_nodes) == 1
    txt = tree_nodes[0].text or ""
    assert "m.py" in txt and "n.js" in txt

    file_nodes = root.findall("file")
    paths = sorted(n.attrib["path"] for n in file_nodes)
    assert paths == ["m.py", "n.js"]

    # languages mapped correctly
    langs = {n.attrib["path"]: n.find("code").attrib.get("language") for n in file_nodes}
    assert langs == {"m.py": "py", "n.js": "js"}