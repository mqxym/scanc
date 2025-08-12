from __future__ import annotations

import importlib
import types
from pathlib import Path
from types import SimpleNamespace
import warnings

import pytest

from scanc.core import ScannedFile
from scanc.token_counter import _get_encoder, count_tokens, tiktoken as _tiktoken_mod


@pytest.fixture
def tiny_files(tmp_path: Path):
    p = tmp_path / "a.py"
    p.write_text("print(1)")
    return [ScannedFile(path=p, language="py", content="print(1)")]


@pytest.mark.skipif(_tiktoken_mod is None, reason="tiktoken missing")
def test_get_encoder_unknown_model_defaults(monkeypatch):
    calls = {}

    class FakeEnc:
        def encode(self, s):  # pragma: no cover
            return [0]

    def fake_encoding_for_model(name):
        raise KeyError

    def fake_get_encoding(name):
        calls["name"] = name
        return FakeEnc()

    monkeypatch.setattr(_tiktoken_mod, "encoding_for_model", fake_encoding_for_model)
    monkeypatch.setattr(_tiktoken_mod, "get_encoding", fake_get_encoding)

    with warnings.catch_warnings(record=True) as w:
        enc = _get_encoder("does-not-exist")
        assert isinstance(enc, FakeEnc)
        assert calls["name"] == "cl100k_base"
        assert any("Unknown model" in str(wi.message) for wi in w)


def test_count_tokens_without_tiktoken(monkeypatch, tiny_files):
    # Pretend that tiktoken is not installed
    import scanc
    from scanc import token_counter as tc

    monkeypatch.setattr(tc, "tiktoken", None)
    with pytest.raises(RuntimeError):
        tc.count_tokens(tiny_files, "gpt-3.5-turbo")


@pytest.mark.skipif(_tiktoken_mod is None, reason="tiktoken missing")
def test_count_tokens_positive(tiny_files):
    total = count_tokens(tiny_files, "gpt-3.5-turbo")
    assert total > 0