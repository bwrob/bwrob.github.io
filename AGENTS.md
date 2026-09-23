# Repository Agent Guidelines: Bwrob.dev

Welcome to the codebase for [bwrob.dev](https://bwrob.dev), a personal software
engineering, data systems, and quantitative computing blog built with Quarto.

## 1. Architecture & Tooling Stack

- **Framework**: [Quarto](https://quarto.org/) static site generator (`_quarto.yml`).
- **Runtime & Environment**: Python 3.13 managed via [`uv`](https://docs.astral.sh/uv/).
- **Task Runner**: [Poe the Poet](https://poethepoet.natn.io/) (`poe_tasks.toml`).
  Always use `poe <task>` or `uv run poe <task>` for maintenance operations:
  - `poe code-quality`: Runs CNAME validation, `ruff format`, `rumdl fmt`,
    `prettier` (CSS/SCSS), `prettier` (YAML), `taplo` (TOML), `ruff check --fix`,
    and `pyrefly check`.
  - `poe preview`: Launches local Quarto preview on port 3333 via `hap`.
  - `poe publish`: Runs pre-commit checks and publishes to GitHub Pages (`gh-pages`).
- **Linters & Formatters**:
  - **`prettier`**: CSS, SCSS, and YAML formatter.
  - **`taplo`**: TOML formatter and linter.
  - **`rumdl`**: Markdown and Quarto linter/formatter (`flavor = "quarto"`, line-length
    88).
  - **`ruff`**: Python linter and formatter (`target-version = "py313"`, line-length 88,
    docstring formatting enabled).
  - **`pyrefly`**: Static type checker.

## 2. Content Standards & Conventions

All technical blog posts reside in `posts/`, and course curricula reside in
`teaching/` (e.g. `teaching/2025-python-academy/`).

### Directory & File Structure

- **Folder naming**: `posts/<YY-MM-DD>-<slug>/` (e.g.
  `posts/26-09-20-tmux-cheatsheet/`) or `teaching/<curriculum>/<YY-MM-DD-slug>/`.
- **Entrypoint**: `index.qmd` inside the post folder.
- **Bilingual Editions**: Optional Polish translations use `index-pl.qmd` co-located
  alongside `index.qmd`, paired with a `.lang-switcher` component.
- **Cover art**: `cover.jpg` (900×600 px JPEG, ~40–85 KB) co-located directly in the
  post folder.
- **Incubation Drawer**: Prototype scripts, benchmarks, and scratch notes live in
  `_not_posted/`. When ready, promote them using `create-post-stub --from-not-posted`.

### Required Frontmatter (`index.qmd`)

```yaml
---
title: "Engaging, Concise Post Title"
description: "1-2 sentence description explaining why this matters to developers."
date: "YYYY-MM-DD"
date-modified: "YYYY-MM-DD"
draft: true
categories: [Dev Env]
image: cover.jpg
format-links: [html]
toc-depth: 2
---

![](cover.jpg){width="98%" fig-align="center"}
```

### Canonical Category Taxonomy

Use standard categories to avoid tag fragmentation:

- **`Dev Env`**: Shell, tmux, terminal tools, Linux/macOS workflows.
- **`Python Recipes`**: Idiomatic Python, design patterns, standard library tricks,
  modern typing.
- **`Data Science`**: Polars, PyArrow, Marimo, Pandas, data engineering.
- **`Performance`**: Profiling (Memray), memory optimization, OOM debugging, compiled
  extensions.
- **`Financial Markets`**: Quantitative finance, merger arbitrage, market structure,
  risk modeling.
- **`Pythonic Distractions`**: Recreational math, puzzles, algorithms, creative coding.
- **`Career`**: Software engineering reflections, developer growth.

## 3. Editorial Philosophy & Writing Tone

- **Conversational & Pragmatic**: Write like an experienced engineer talking to a
  colleague over coffee. Avoid academic stuffiness, dry textbook exposition, and generic
  AI filler phrases. Keep it punchy, witty, and grounded.
- **Zero AI Speech**: Strictly eradicate AI-generated writing tropes and clichés:
  - Banned filler words: *delve*, *tapestry*, *testament*, *pivotal*, *beacon*,
    *foster*, *harness*, *leverage*, *plethora*, *demystify*, *unleash*, *game-changer*.
  - Banned structural tropes: "Rule of three" buzzwords (*fast, scalable, and robust*),
    throat-clearing openings (*"In today's fast-paced tech world..."*), superficial
    cheerleading, and patronizing moralizing conclusions (*"Remember, the journey of
    a thousand commits begins with..."*).
  - Write with authentic engineer conviction: state trade-offs, show concrete
    benchmarks, and acknowledge awkward edges or clunky APIs directly.
- **Socratic Method for Teaching**: When explaining complex patterns, algorithms, or
  mechanics, guide the reader through inquiry:
  - Frame a real problem or surprise ("What happens when your dataset exceeds RAM by
    10MB?").
  - Ask guiding questions before presenting the answer ("Why did this line trigger a
    copy instead of a view?").
  - Lead the reader to discover the solution through code experiments and tangible
    observations.
- **Code First**: Provide runnable, copy-pasteable, verified snippets with clear
  annotations (`<1>`, `<2>`) instead of hand-waving pseudocode.

## 4. Post Lifecycle & Skills

The repository includes specialized skills in `.agents/skills/`:

1. **Scaffold a new draft**: Use `create-post-stub` to generate
   `posts/<YY-MM-DD>-<slug>/` with the placeholder cover and template.
2. **Quality & Formatting**: Use `check-quality` to format markdown (`rumdl fmt`) and
   run Python linters.
3. **Editorial Review**: Use `editorial-review` to audit tone, technical clarity, and
   Socratic structure.
4. **Finalize & Publish**: Use `finalize-post` to undraft, bump dates, generate final
   cover art via `generate-post-image`, and verify rendering.
