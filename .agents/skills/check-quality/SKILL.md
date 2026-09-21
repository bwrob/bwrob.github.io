---
name: check-quality
description: >-
  Run code quality, formatting, and linting checks on blog posts and scripts.
  Use this skill whenever formatting or verifying Quarto Markdown files, Python code
  blocks, or preparing to commit changes.
---

# Code & Markdown Quality

This skill standardizes formatting and linting across [bwrob.dev](https://bwrob.dev),
ensuring Quarto documents (`.qmd`), Markdown (`.md`), and Python files adhere to project
conventions.

---

## Tooling Suite Overview

| Tool          | Scope               | Configuration                                    | Command                        |
| :------------ | :------------------ | :----------------------------------------------- | :----------------------------- |
| **`rumdl`**   | Markdown & Quarto   | `flavor = "quarto"`, line-length 88              | `uv run rumdl fmt` / `check`   |
| **`ruff`**    | Python files & code | `line-length = 88`, py313, docstring code format | `uv run ruff check` / `format` |
| **`pyrefly`** | Static Type Checker | Configured via `pyrefly.toml`                    | `uv run pyrefly check`         |
| **`CNAME`**   | Domain integrity    | Verifies `CNAME` contains `bwrob.dev`            | `poe _check_cname`             |

---

## Workflow

### 1. Full Repository Suite (Recommended)

Run the unified `poe code-quality` task, which executes formatting and linting in
sequence:

```bash
uv run poe code-quality
```

This task automatically:

1. Validates `CNAME`.
2. Formats Python with `ruff format .`.
3. Formats Markdown with `rumdl fmt`.
4. Fixes lint errors with `ruff check --fix --unsafe-fixes .`.
5. Verifies remaining lint issues with `ruff check .`.
6. Runs static type checking with `pyrefly check`.

---

### 2. Targeted Formatting for Single Post

When editing a specific post, format and check the post file directly:

#### Format Markdown

```bash
# Auto-format line wraps and tables to 88 characters
uv run rumdl fmt "posts/<post-slug>/index.qmd"

# Check for remaining Quarto / Markdown issues
uv run rumdl check "posts/<post-slug>/index.qmd"
```

#### Format Python Snippets / Scripts

```bash
# Format Python scripts or extracted snippets
uv run ruff format "posts/<post-slug>/"
uv run ruff check --fix "posts/<post-slug>/"
```

---

## Common Linter Fixes

- **Long Markdown lines**: Run `uv run rumdl fmt <path>` to wrap paragraphs cleanly to
  88 columns.
- **Unclosed code fences**: Ensure code blocks open
  with ````python` and close with ````.
- **Indentation in lists**: Ensure list items and sub-lists use consistent 2-space
  indentation.
- **Frontmatter syntax**: Ensure YAML strings with colons or special characters are
  quoted.
