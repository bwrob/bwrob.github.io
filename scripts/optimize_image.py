# ruff: noqa: INP001
"""CLI tool to convert and compress images to WebP format for bwrob.dev."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps, ImageSequence


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


def main() -> None:
    """CLI entry point for image optimization."""
    parser = argparse.ArgumentParser(
        description="Convert and compress images to WebP format."
    )
    parser.add_argument(
        "images",
        nargs="+",
        help="Path(s) to image files or directories to optimize.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="WebP quality (1-100, default: 85).",
    )
    parser.add_argument(
        "--cover",
        action="store_true",
        help="Resize exactly to 900x600 blog post cover standard.",
    )
    parser.add_argument(
        "--max-dim",
        type=int,
        default=None,
        help="Max width or height in pixels.",
    )
    parser.add_argument(
        "--lossless",
        action="store_true",
        help="Encode with lossless WebP compression.",
    )
    parser.add_argument(
        "--keep-original",
        action="store_true",
        help="Preserve source image file after conversion.",
    )

    args = parser.parse_args()

    files: list[Path] = []
    supported_exts = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}

    for item in args.images:
        p = Path(item)
        if p.is_dir():
            files.extend(
                f
                for f in p.rglob("*")
                if f.is_file() and f.suffix.lower() in supported_exts
            )
        elif p.is_file():
            files.append(p)
        else:
            print(f"Warning: File not found: {item}", file=sys.stderr)

    if not files:
        print("No eligible image files found to optimize.")
        sys.exit(1)

    resize_exact = (900, 600) if args.cover else None

    for f in files:
        try:
            optimize_image(
                f,
                quality=args.quality,
                max_dim=args.max_dim,
                resize_exact=resize_exact,
                lossless=args.lossless,
                keep_original=args.keep_original,
            )
        except Exception as e:  # noqa: BLE001
            print(f"Error optimizing {f}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
