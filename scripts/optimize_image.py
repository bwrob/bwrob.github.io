# ruff: noqa: INP001
"""CLI tool to convert and compress images to WebP format for bwrob.dev."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from PIL import Image, ImageOps, ImageSequence

app = typer.Typer(
    add_completion=False,
    help="Convert and compress images to WebP format for bwrob.dev.",
)


def optimize_image(  # noqa: PLR0913
    src: Path,
    dest: Path | None = None,
    quality: int = 85,
    max_dim: int | None = None,
    resize_exact: tuple[int, int] | None = None,
    *,
    lossless: bool = False,
    keep_original: bool = False,
) -> Path:
    """Convert an image to WebP with optional resizing and compression."""
    target_dest = src.with_suffix(".webp") if dest is None else dest

    with Image.open(src) as im:
        if getattr(im, "is_animated", False):
            frames = [f.copy().convert("RGBA") for f in ImageSequence.Iterator(im)]
            durations = [
                f.info.get("duration", 100) for f in ImageSequence.Iterator(im)
            ]
            frames[0].save(
                target_dest,
                format="WEBP",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                quality=quality,
                method=6,
            )
        else:
            processed = ImageOps.exif_transpose(im)
            if resize_exact:
                processed = processed.resize(resize_exact, Image.Resampling.LANCZOS)
            elif max_dim:
                processed.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

            if lossless:
                processed.save(target_dest, format="WEBP", lossless=True, method=6)
            else:
                processed.save(target_dest, format="WEBP", quality=quality, method=6)

    orig_sz = src.stat().st_size
    dest_sz = target_dest.stat().st_size
    diff = orig_sz - dest_sz
    pct = (diff / orig_sz) * 100 if orig_sz else 0.0

    print(
        f"✅ Optimized: {src} -> {target_dest} "
        f"({orig_sz / 1024:.1f} KB -> {dest_sz / 1024:.1f} KB, -{pct:.1f}%)"
    )

    if not keep_original and src.resolve() != target_dest.resolve():
        src.unlink()

    return target_dest


def _collect_image_files(items: list[Path]) -> list[Path]:
    """Collect supported image files from a list of paths."""
    supported_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
    files: list[Path] = []
    for item in items:
        if item.is_dir():
            files.extend(
                f
                for f in item.rglob("*")
                if f.is_file() and f.suffix.lower() in supported_exts
            )
        elif item.is_file():
            files.append(item)
        else:
            print(f"Warning: File not found: {item}", file=sys.stderr)
    return files


@app.command()
def main(  # noqa: PLR0913
    images: Annotated[
        list[Path],
        typer.Argument(
            help="Path(s) to image files or directories to optimize.",
        ),
    ],
    *,
    quality: Annotated[
        int,
        typer.Option(
            "--quality",
            help="WebP quality (1-100, default: 85).",
        ),
    ] = 85,
    cover: Annotated[
        bool,
        typer.Option(
            "--cover",
            help="Resize exactly to 900x600 blog post cover standard.",
        ),
    ] = False,
    max_dim: Annotated[
        int | None,
        typer.Option(
            "--max-dim",
            help="Max width or height in pixels.",
        ),
    ] = None,
    lossless: Annotated[
        bool,
        typer.Option(
            "--lossless",
            help="Encode with lossless WebP compression.",
        ),
    ] = False,
    keep_original: Annotated[
        bool,
        typer.Option(
            "--keep-original",
            help="Preserve source image file after conversion.",
        ),
    ] = False,
) -> None:
    """CLI entry point for image optimization."""
    files = _collect_image_files(images)
    if not files:
        print("No eligible image files found to optimize.", file=sys.stderr)
        raise typer.Exit(code=1)

    resize_exact = (900, 600) if cover else None

    for f in files:
        try:
            optimize_image(
                f,
                quality=quality,
                max_dim=max_dim,
                resize_exact=resize_exact,
                lossless=lossless,
                keep_original=keep_original,
            )
        except Exception as e:  # noqa: BLE001
            print(f"Error optimizing {f}: {e}", file=sys.stderr)


if __name__ == "__main__":
    app()
