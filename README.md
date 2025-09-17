# scanc

![Test Status](https://github.com/mqxym/scanc/actions/workflows/python-publish.yml/badge.svg)

> scanc = scan c(ode) <br>
> A fast, pure‑Python project code‑scanner that outputs clean, AI‑ready Markdown or XML.

`scanc` helps you **spill an entire codebase into an LLM prompt** (or a file) in seconds—while keeping noise low, controlling token budgets, and giving you full visibility.

---

## Features

| Feature                         | Description                                                      |
| ------------------------------- | ---------------------------------------------------------------- |
|  **Blazing Fast, Pure‑Python** | Zero native dependencies; easy to install and run anywhere.      |
|  **Smart Default Ignores**    | Automatically skips `node_modules`, `.venv`, `.git`, and more.   |
|  **Flexible Filters**         | Include/exclude by *extension*, *filename*, or *regex* patterns. |
|  **Optional Directory Tree**  | Prepend a fenced tree diagram of your project structure.         |
|  **Token Counter**            | Estimate LLM token costs with `tiktoken` before you paste.       |
|  **Cross‑Platform CLI**       | Works on macOS, Linux, and Windows out of the box.               |

---

## Installation

```bash
# Optional: Use a virutal environment
python3 -m venv --prompt scanc-env .venv
source .venv/bin/activate

pip install scanc[tiktoken]  # installs optional token‑counter support
```

## Quickstart

Scan a directory and emit Markdown:

```bash
scanc .                         # scan current folder
scanc -e py,js --tree           # only .py and .js files + directory tree
scanc -f xml                    # output scan in xml format (new in v1.2.0)
scanc -e py -x "tests" | less   # only py files exclude tests in path
scanc --tokens gpt-4o           # show token count for gpt 4o only
scanc -e py | pbcopy            # scan and copy (macOS copy command example)
```

Write output directly to a file:

```bash
scanc -e ts --tree -o scan.md src/
cat scan.md
```

---

## CLI Reference

```bash
scanc [OPTIONS] [PATHS...]
```

* `-e, --ext EXTS`          Comma‑separated extensions to include (e.g. `py,js`).
* `-i, --include-regex`     Regex patterns to include (full path match).
* `-x, --exclude-regex`     Regex patterns to exclude (full path match).
* `--no-default-excludes`   Disable built‑in ignore list.
* `-t, --tree`              Prepend directory tree (fenced code block).
* `-T, --tokens MODEL`      Output only token count for given LLM model.
* `--max-size BYTES`        Skip files larger than BYTES (default 1 MiB).
* `--follow-symlinks`       Traverse symlinks when scanning.
* `-o, --out OUTFILE`       Write result to `OUTFILE` instead of stdout.
* `-f, --format FORMAT`     Output format (default: `markdown`).
* `-V, --version`           Show version and exit.

## Integration & Extensibility

- **Formatter Hook:** Customize output by passing your own formatter via entry points.
- **Extras:** Use `scanc[tiktoken]` to enable token counting; more extras may follow.

## Licence

Released under the MIT Licence. See [LICENCE](LICENCE) for details.
