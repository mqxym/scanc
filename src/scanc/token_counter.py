from __future__ import annotations

import importlib
import warnings
import sys
import click
from typing import List

from .core import ScannedFile

try:
    tiktoken = importlib.import_module("tiktoken")  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    tiktoken = None


def _require_tiktoken(cli: bool = False) -> None:
    if tiktoken is None:
        msg = (
            "Token counting requires the optional 'tiktoken' package.\n"
            "Install with: pip install scanc[tiktoken]"
        )
        if cli:
            click.echo(f"✗ {msg}", err=True)
            sys.exit(2)
        raise RuntimeError(msg)


def _get_encoder(model_name: str = "gpt-3.5-turbo"):
    _require_tiktoken()
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        warnings.warn(
            f"Unknown model '{model_name}'. Falling back to 'cl100k_base'. "
            "Update tiktoken or pass --tokens MODEL explicitly.",
            stacklevel=2,
        )
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(files: List[ScannedFile], model_name: str = "gpt-3.5-turbo") -> float:
    """
    Return total token count (float allows '%.2f' formatting) across all files.
    """
    _require_tiktoken()
    enc = _get_encoder(model_name)
    total = 0
    for f in files:
        total += len(enc.encode(f.content))
    return float(total)