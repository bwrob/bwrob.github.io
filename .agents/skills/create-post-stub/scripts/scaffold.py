#!/usr/bin/env python3
"""Standardized Blog Post Scaffolding Script for bwrob.dev.

Creates a new blog post directory with proper date prefixes, placeholder cover
image, and normalized index.qmd frontmatter.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime
import re
import shutil
import sys
from pathlib import Path

CANONICAL_CATEGORIES = [
    "Dev Env",
    "Python Recipes",
    "Data Science",
    "Performance",
    "Financial Markets",
    "Pythonic Distractions",
    "Career",
]

DEFAULT_HOOK = (
    "Opening hook paragraph introducing the problem, tool, or pattern. "
    "Explain why this matters to developers and what the post demonstrates."
)
DEFAULT_CONTEXT = (
    "Provide background context. Why does this challenge arise? "
    "What alternatives exist? Outline the architecture or design choice."
)
DEFAULT_EXPLANATION = (
    "Explain the code mechanics, key arguments, and non-obvious nuances."
)


def parse_args() -> argparse.Namespace:
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scaffold a new draft blog post for bwrob.dev"
    )
    parser.add_argument(
        "--slug",
        required=True,
        help="Kebab-case post slug identifier (e.g., 'fast-ipc-pyarrow')",
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Post title (e.g., 'Fast IPC with PyArrow')",
    )
    parser.add_argument(
        "--description",
        default="A short, engaging description of the post topic.",
        help="Brief 1-2 sentence description of the post",
    )
    parser.add_argument(
        "--category",
        action="append",
        dest="categories",
        help="Category name (can be repeated for multiple categories)",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Post date in YYYY-MM-DD format (defaults to current date)",
    )
    parser.add_argument(
        "--hook",
        default=None,
        help="Optional opening hook paragraph for the post body",
    )
    parser.add_argument(
        "--target-dir",
        default="posts",
        help="Target base directory relative to repo root (default: 'posts')",
    )
    parser.add_argument(
        "--from-not-posted",
        default=None,
        help="Seed implementation code from a script/note in _not_posted/",
    )
    parser.add_argument(
        "--bilingual",
        action="store_true",
        help="Scaffold bilingual edition (index.qmd and index-pl.qmd with switcher)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing post folder if it already exists",
    )
    return parser.parse_args()


def validate_slug(slug: str) -> None:
    """Validate that the post slug follows kebab-case convention."""
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", slug):
        msg = (
            f"Invalid slug '{slug}'. Must be lower-case alphanumeric "
            "with hyphens (e.g., 'my-post-slug')."
        )
        raise ValueError(msg)


def resolve_post_date(date_str: str | None) -> datetime.date:
    """Parse string date or return today's date."""
    if date_str:
        try:
            return datetime.date.fromisoformat(date_str)
        except ValueError:
            sys.exit(f"Error: Invalid date format '{date_str}'. Expected YYYY-MM-DD.")
    return datetime.datetime.now(tz=datetime.UTC).date()


def validate_categories(categories: list[str]) -> None:
    """Warn if any provided category is outside the canonical taxonomy."""
    for cat in categories:
        if cat not in CANONICAL_CATEGORIES:
            warning_msg = (
                f"Warning: Category '{cat}' is not in canonical list: "
                f"{CANONICAL_CATEGORIES}"
            )
            print(warning_msg, file=sys.stderr)


def load_seed_code(repo_root: Path, from_not_posted: str | None) -> str | None:
    """Read seed code from _not_posted if specified."""
    if not from_not_posted:
        return None
    candidate = repo_root / "_not_posted" / from_not_posted
    if not candidate.exists():
        candidate = repo_root / from_not_posted
    if not candidate.exists():
        matches = list((repo_root / "_not_posted").rglob(from_not_posted))
        if matches and matches[0].is_file():
            candidate = matches[0]
    if candidate.exists() and candidate.is_file():
        code = candidate.read_text(encoding="utf-8").strip()
        print(f"📦 Seeded prototype from: {candidate.relative_to(repo_root)}")
        return code
    print(f"Warning: Seed file not found for '{from_not_posted}'", file=sys.stderr)
    return None


@dataclasses.dataclass(frozen=True)
class PostContext:
    """Encapsulates template rendering parameters."""

    title: str
    description: str
    iso_date: str
    categories: list[str]
    hook: str | None = None
    seed_code: str | None = None
    is_pl: bool = False
    is_bilingual: bool = False


def render_content(template: str, ctx: PostContext) -> str:
    """Render the post template with metadata and code."""
    switcher = ""
    if ctx.is_bilingual:
        en_active = "" if ctx.is_pl else " .active"
        pl_active = " .active" if ctx.is_pl else ""
        switcher = (
            "::: {.lang-switcher}\n"
            f"[English 🇬🇧](index.qmd){{.lang-btn{en_active}}}\n"
            f"[Polski 🇵🇱](index-pl.qmd){{.lang-btn{pl_active}}}\n"
            ":::\n\n"
        )

    categories_formatted = ", ".join(ctx.categories)
    hook_text = ctx.hook or DEFAULT_HOOK

    content = (
        template.replace("{{TITLE}}", ctx.title)
        .replace("{{DESCRIPTION}}", ctx.description)
        .replace("{{DATE}}", ctx.iso_date)
        .replace("{{CATEGORIES}}", categories_formatted)
        .replace("{{HOOK_PARAGRAPH}}", hook_text)
        .replace("{{CONTEXT_AND_BACKGROUND}}", DEFAULT_CONTEXT)
        .replace("{{EXPLANATION}}", DEFAULT_EXPLANATION)
        .replace("{{LANG_SWITCHER}}", switcher)
    )

    if ctx.seed_code:
        default_block = 'def main() -> None:\n    """Demonstrate the core pattern."""'
        content = content.replace(default_block, ctx.seed_code)

    return content


def main() -> None:
    """Scaffold a new blog post directory and template files."""
    args = parse_args()
    validate_slug(args.slug)

    post_date = resolve_post_date(args.date)
    iso_date = post_date.strftime("%Y-%m-%d")
    folder_prefix = post_date.strftime("%y-%m-%d")
    folder_name = f"{folder_prefix}-{args.slug}"

    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent
    repo_root = skill_dir.parents[2]
    target_post_dir = repo_root / args.target_dir / folder_name

    if target_post_dir.exists() and not args.force:
        err_msg = (
            f"Error: Target directory already exists: {target_post_dir}\n"
            "Use --force to overwrite."
        )
        sys.exit(err_msg)

    categories = args.categories or ["Dev Env"]
    validate_categories(categories)

    placeholder_cover = skill_dir / "resources" / "placeholder-cover.jpg"
    template_file = skill_dir / "resources" / "post-template.qmd"

    if not placeholder_cover.exists():
        sys.exit(f"Error: Placeholder cover not found at {placeholder_cover}")
    if not template_file.exists():
        sys.exit(f"Error: Template file not found at {template_file}")

    target_post_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(placeholder_cover, target_post_dir / "cover.jpg")

    template_text = template_file.read_text(encoding="utf-8")
    seed_code = load_seed_code(repo_root, args.from_not_posted)

    ctx_en = PostContext(
        title=args.title,
        description=args.description,
        iso_date=iso_date,
        categories=categories,
        hook=args.hook,
        seed_code=seed_code,
        is_pl=False,
        is_bilingual=args.bilingual,
    )
    (target_post_dir / "index.qmd").write_text(
        render_content(template_text, ctx_en), encoding="utf-8"
    )

    if args.bilingual:
        ctx_pl = PostContext(
            title=args.title,
            description=args.description,
            iso_date=iso_date,
            categories=categories,
            hook=args.hook,
            seed_code=seed_code,
            is_pl=True,
            is_bilingual=True,
        )
        (target_post_dir / "index-pl.qmd").write_text(
            render_content(template_text, ctx_pl), encoding="utf-8"
        )

    rel_post_dir = target_post_dir.relative_to(repo_root)
    print(f"✅ Successfully scaffolded post stub in '{rel_post_dir}':")
    print(f"   - Index file:  {rel_post_dir / 'index.qmd'}")
    if args.bilingual:
        print(f"   - Polish file: {rel_post_dir / 'index-pl.qmd'}")
    print(f"   - Cover image: {rel_post_dir / 'cover.jpg'} (900x600 placeholder)")
    print("   - Status:      draft: true")
    print(f"   - Categories:  [{', '.join(categories)}]")


if __name__ == "__main__":
    main()
