import pytest
import os

def test_get_encoder_warning_stacklevel(monkeypatch):
    import warnings
    from scanc.token_counter import _get_encoder, tiktoken as _tk
    if _tk is None:
        pytest.skip("tiktoken missing")

    def fake_encoding_for_model(name):
        raise KeyError
    monkeypatch.setattr(_tk, "encoding_for_model", fake_encoding_for_model)
    with warnings.catch_warnings(record=True) as w:
        _get_encoder("weird-model")
        assert w, "warning not emitted"
        assert os.path.basename(w[0].filename) == "test_token_counter_edge.py"