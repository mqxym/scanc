from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional
import contextlib

import click

from . import __version__
from .core import DEFAULT_EXCLUDES, scan_directory
from .formatter import format_result, MARKDOWN

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _comma_separated(ctx, param, value):  # click callback
    if value is None:
        return None
    parts = sorted({p.strip().lower().lstrip(".") for p in value.split(",") if p.strip()})
    return parts if parts else None


# --------------------------------------------------------------------------- #
# CLI definition
# --------------------------------------------------------------------------- #

@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(__version__, "--version", "-V", prog_name="scanc")
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(file_okay=True, dir_okay=True, exists=True, path_type=Path),
    required=False,
)
@click.option(
    "-e",
    "--ext",
    "extensions",
    callback=_comma_separated,
    metavar="EXTS",
    help="Comma-separated list of file extensions to include (e.g. py,js,ts). "
    "Case-insensitive, leading dots optional. Omit to include all.",
)
@click.option(
    "-i",
    "--include-regex",
    "include_regex",
    multiple=True,
    help="Regex pattern(s) to **include**.  Evaluated against the full path.",
)
@click.option(
    "-x",
    "--exclude-regex",
    "exclude_regex",
    multiple=True,
    help="Regex pattern(s) to **exclude**.  Evaluated against the full path.",
)
@click.option(
    "--no-default-excludes",
    is_flag=True,
    help=f"Do not use the built-in ignore list (default: {', '.join(sorted(DEFAULT_EXCLUDES))}).",
)
@click.option(
    "-t",
    "--tree/--no-tree",
    default=False,
    help="Prepend a Markdown directory tree to the scan result.",
)
@click.option(
    "-T",
    "--tokens",
    "model_name",
    metavar="MODEL",
    help="Show token count for MODEL (e.g. gpt-4o, gpt-3.5-turbo). "
    "Suppresses normal output.",
)
@click.option(
    "--max-size",
    type=int,
    metavar="BYTES",
    default=1_048_576,  # 1 MiB
    show_default=True,
    help="Skip individual files above this size.",
)
@click.option(
    "-o",
    "--out",
    "outfile",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
    help="Write result to <outfile> instead of STDOUT.",
)
@click.option(
    "-f",
    "--format",
    "format_name",
    type=click.Choice(["markdown"], case_sensitive=False),
    default="markdown",
    show_default=True,
    help="Output format.  Additional formats can be added via entry-points.",
)
@click.option("--follow-symlinks/--no-follow-symlinks", default=False, help="Traverse symlinks.")
def main(
    paths: List[Path],
    extensions: Optional[List[str]],
    include_regex: List[str],
    exclude_regex: List[str],
    no_default_excludes: bool,
    tree: bool,
    model_name: Optional[str],
    max_size: int,
    outfile: Optional[Path],
    format_name: str,
    follow_symlinks: bool,
) -> None:
    """
    Scan project source code and emit AI-ready Markdown.

    Examples

    --------

    • Scan current directory, default rules::
        scanc .

    • Scan only JS & TS files, include tree, write to file::

        scanc -e js,ts --tree -o scan.md .

    • Token count only::

        scanc --tokens gpt-4o
    """
    if not paths:
        paths = [Path.cwd()]
    # --------------------------------------------------------------------- #
    # Collect files
    files, tree_md = scan_directory(
        paths=paths,
        extensions=extensions,
        include_regex=include_regex,
        exclude_regex=exclude_regex,
        use_default_excludes=not no_default_excludes,
        include_tree=tree,
        max_size=max_size,
        follow_symlinks=follow_symlinks,
    )

    if model_name:
        from .token_counter import count_tokens, _require_tiktoken

        _require_tiktoken(cli=True)
        token_count = count_tokens(files, model_name)
        click.echo(f"{token_count:,.2f}")
        return

    formatted = format_result(
        files=files,
        tree_md=tree_md if tree else None,
        formatter=MARKDOWN,
    )

    try:
        stream_ctx = (
            outfile.open("w", encoding="utf-8")      # file handle
            if outfile
            else contextlib.nullcontext(click.get_text_stream("stdout"))  # keep stdout open
        )
        with stream_ctx as dest:
            dest.write(formatted)
    except OSError as exc:
        click.echo(f"✗ Could not write output: {exc}", err=True)
        sys.exit(1)
    if outfile:
        click.echo(f"✓ Saved to {outfile}", err=True)


if __name__ == "__main__":  # pragma: no cover
    main()