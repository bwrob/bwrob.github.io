---
description: >-
  Run code quality, formatting, and linting checks on blog posts and scripts.
  Use this skill whenever formatting or verifying Quarto Markdown files, Python code
  blocks, or preparing to commit changes.
name: check-quality
---

# Code & Markdown Quality

This skill standardizes formatting and linting across [bwrob.dev](https://bwrob.dev),
ensuring Quarto documents (`.qmd`), Markdown (`.md`), and Python files adhere to project
conventions.

## Tooling Suite Overview

| Tool          | Scope                  | Configuration                                    | Command                        |
| :------------ | :--------------------- | :----------------------------------------------- | :----------------------------- |
| **`rumdl`**   | Markdown & Quarto      | `flavor = "quarto"`, line-length 88, code tools  | `uv run rumdl fmt` / `check`   |
| **`ruff`**    | Python files & blocks  | `line-length = 88`, py313, docstring formatting  | `uv run ruff check` / `format` |
| **`pyrefly`** | Static Type Checker    | Configured via `pyrefly.toml`                    | `uv run pyrefly check`         |
| **`CNAME`**   | Domain integrity       | Verifies `CNAME` contains `bwrob.dev`            | `poe _check_cname`             |

> [!NOTE]
> `rumdl` is configured with `code-block-tools` enabled in `pyproject.toml`. Running
> `rumdl fmt` automatically runs `ruff` format and lint checks directly against
> embedded `{python}` chunks within `.qmd` files.

## Workflow

Follow these workflows to maintain consistent formatting and code quality:

### 1. Full Repository Suite (Recommended)

Run the unified `poe code-quality` task, which executes formatting and linting in
sequence:

```bash
uv run poe code-quality
```

This task automatically:

1. Validates `CNAME`.
2. Formats Python files with `ruff format .`.
3. Formats Quarto & Markdown documents with `rumdl fmt` (including embedded Python
   blocks).
4. Fixes lint errors with `ruff check --fix --unsafe-fixes .`.
5. Verifies remaining lint issues with `ruff check .`.
6. Runs static type checking with `pyrefly check`.

To verify git pre-commit hooks before committing:

```bash
uv run pre-commit run --all-files
```

### 2. Targeted Formatting for Single Post or Lesson

When editing a specific post or teaching lesson, format and check the file directly:

#### Format Markdown & Embedded Code Blocks

```bash
# Auto-format line wraps (88 chars), tables, and Python code blocks:
uv run rumdl fmt "posts/<post-slug>/index.qmd"
# Or for teaching modules:
uv run rumdl fmt "teaching/2025-python-academy/<lesson-slug>/index.qmd"

# Check for remaining Quarto / Markdown issues:
uv run rumdl check "posts/<post-slug>/index.qmd"
```

#### Format Standalone Python Scripts

```bash
uv run ruff format "assets/python/" "posts/<post-slug>/"
uv run ruff check --fix "assets/python/" "posts/<post-slug>/"
```

## Known Lint Traps & Best Practices

- **Bash Annotation Backslashes**: In shell code blocks, never place Quarto callout
  annotations (`# <1>`) on lines ending with a continuation backslash (`\`). It breaks
  bash command execution. Place annotations on the terminal line or after closing
  quotes.
- **Descriptive Link Text (MD059)**: Never use generic link text like `[here]` or
  `[link]`. Always use descriptive labels like `[Pydantic tree walker script](...)`.
- **Unused `noqa` Directives (RUF100)**: Avoid blanket `# ruff: noqa: ...` comments
  inside `.qmd` code blocks unless the rule is actively triggered; otherwise, Ruff will
  fail on unused `noqa` directives.
- **Python Import Sorting in QMD**: When importing modules inside `{python}` blocks:
  1. Standard library imports (e.g. `import dataclasses`).
  2. Blank line.
  3. Third-party standard imports (e.g. `import plotly.graph_objects as go`).
  4. Third-party `from` imports (e.g. `from IPython.display import Markdown, display`).
- **Long Markdown Lines**: Use `uv run rumdl fmt <path>` to wrap prose paragraphs
  cleanly to the 88-column standard.
- **Frontmatter Syntax**: Wrap YAML title or description strings in quotes if they
  contain colons, ampersands, or apostrophes.
