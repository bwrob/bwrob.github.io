# ruff: noqa: INP001
"""CLI tool to render blog posts to PDF in the assets directory using Typer."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(
    add_completion=False,
    help="Render a blog post or curriculum document to PDF in the assets directory.",
)


def extract_slug(post_dir: Path) -> str:
    """Extract a clean slug from a directory name by stripping YY-MM-DD- prefixes."""
    return re.sub(r"^\d{2}-\d{2}-\d{2}-", "", post_dir.name)


def _search_post_candidates(query: str, repo_root: Path) -> list[Path]:
    """Search for matching index.qmd files under posts/ and teaching/."""
    candidates: list[Path] = []
    for parent in [repo_root / "posts", repo_root / "teaching"]:
        if not parent.is_dir():
            continue
        for child in parent.iterdir():
            candidate = child / "index.qmd"
            if (
                child.is_dir()
                and query.lower() in child.name.lower()
                and candidate.is_file()
            ):
                candidates.append(candidate)
    return candidates


def find_post_entrypoint(target: str | Path, repo_root: Path) -> Path:
    """Resolve a target string or path to an existing index.qmd file."""
    path_target = Path(target)
    if not path_target.is_absolute():
        path_target = (repo_root / path_target).resolve()

    if path_target.is_file() and path_target.suffix == ".qmd":
        return path_target

    if path_target.is_dir():
        index_file = path_target / "index.qmd"
        if index_file.is_file():
            return index_file

    candidates = _search_post_candidates(str(target).strip("/\\"), repo_root)
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        opts = "\n".join(f"  - {c.parent.name}" for c in candidates)
        msg = f"Ambiguous post reference '{target}'. Multiple candidates found:\n{opts}"
        raise ValueError(msg)

    msg = f"Could not find a post matching '{target}' in posts/ or teaching/."
    raise FileNotFoundError(msg)


def _build_quarto_cmd(
    quarto_bin: str,
    rel_qmd: Path,
    *,
    toc: bool,
    toc_depth: int | None,
) -> list[str]:
    """Construct quarto render command line."""
    cmd = [
        quarto_bin,
        "render",
        str(rel_qmd),
        "--to",
        "typst",
        "-M",
        "code-line-numbers:true",
    ]
    if toc or toc_depth is not None:
        cmd.extend(["-M", "toc:true"])
        if toc_depth is not None:
            cmd.extend(["-M", f"toc-depth:{toc_depth}"])
    else:
        cmd.extend(["-M", "toc:false"])
    return cmd


def _locate_rendered_pdf(repo_root: Path, post_dir: Path) -> Path:
    """Find the output PDF produced by Quarto."""
    rel_post_dir = post_dir.relative_to(repo_root)
    site_pdf = repo_root / "_site" / rel_post_dir / "index.pdf"
    fallback_pdf = post_dir / "index.pdf"

    if site_pdf.is_file():
        return site_pdf
    if fallback_pdf.is_file():
        return fallback_pdf
    msg = f"Expected rendered PDF not found at {site_pdf} or {fallback_pdf}."
    raise FileNotFoundError(msg)


def _clean_render_artifacts(post_dir: Path) -> None:
    """Remove intermediate figures and typst files."""
    index_files = post_dir / "index_files"
    if index_files.is_dir():
        shutil.rmtree(index_files)
    index_typ = post_dir / "index.typ"
    if index_typ.is_file():
        index_typ.unlink()


def render_post_to_pdf(  # noqa: PLR0913
    post_qmd: Path,
    repo_root: Path,
    output_dir: Path | None = None,
    output_file: Path | None = None,
    *,
    toc: bool = False,
    toc_depth: int | None = None,
    clean_intermediate: bool = True,
) -> Path:
    """Render a post's index.qmd to PDF via Quarto Typst and save to target."""
    quarto_bin = shutil.which("quarto")
    if not quarto_bin:
        msg = "quarto binary not found in PATH."
        raise RuntimeError(msg)

    post_dir = post_qmd.parent
    rel_qmd = post_qmd.relative_to(repo_root)
    print(f"📄 Rendering {rel_qmd} to PDF (typst)...")

    cmd = _build_quarto_cmd(quarto_bin, rel_qmd, toc=toc, toc_depth=toc_depth)
    env = os.environ.copy()
    venv_python = repo_root / ".venv" / "bin" / "python"
    if venv_python.is_file():
        env["QUARTO_PYTHON"] = str(venv_python)

    result = subprocess.run(cmd, cwd=repo_root, env=env, check=False)  # noqa: S603
    if result.returncode != 0:
        msg = f"Quarto render failed with exit code {result.returncode}."
        raise RuntimeError(msg)

    source_pdf = _locate_rendered_pdf(repo_root, post_dir)

    if output_file is not None:
        dest_path = (
            output_file if output_file.is_absolute() else (repo_root / output_file)
        )
    else:
        dest_dir = (
            output_dir
            if output_dir and output_dir.is_absolute()
            else (repo_root / (output_dir or Path("assets/pdf")))
        )
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / f"{extract_slug(post_dir)}.pdf"

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_pdf, dest_path)

    if clean_intermediate:
        _clean_render_artifacts(post_dir)

    sz_kb = dest_path.stat().st_size / 1024
    print(f"✅ Created: {dest_path.relative_to(repo_root)} ({sz_kb:.1f} KB)")
    return dest_path


@app.command()
def main(  # noqa: PLR0913
    post: Annotated[
        str,
        typer.Argument(
            help=(
                "Post path, directory, or slug to render "
                "(e.g., 'posts/26-10-03-agentic-harness-fundamentals')."
            ),
        ),
    ],
    *,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Destination directory for rendered PDF (default: assets/pdf).",
        ),
    ] = Path("assets/pdf"),
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Explicit output path for the rendered PDF file.",
        ),
    ] = None,
    toc: Annotated[
        bool,
        typer.Option(
            "--toc/--no-toc",
            help="Enable or disable table of contents (default: disabled).",
        ),
    ] = False,
    toc_depth: Annotated[
        int | None,
        typer.Option(
            "--toc-depth",
            help="Table of contents depth (e.g. 1, 2, 3).",
        ),
    ] = None,
    clean: Annotated[
        bool,
        typer.Option(
            "--clean/--no-clean",
            help="Clean up intermediate figure files after render.",
        ),
    ] = True,
) -> None:
    """Render a post's index.qmd to PDF in the assets directory."""
    repo_root = Path(__file__).resolve().parent.parent

    try:
        post_qmd = find_post_entrypoint(post, repo_root)
        render_post_to_pdf(
            post_qmd=post_qmd,
            repo_root=repo_root,
            output_dir=output_dir,
            output_file=output,
            toc=toc,
            toc_depth=toc_depth,
            clean_intermediate=clean,
        )
    except Exception as exc:
        print(f"❌ Error rendering post to PDF: {exc}", file=sys.stderr)
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
