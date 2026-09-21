#!/usr/bin/env python3
"""Standardized Blog Post Scaffolding Script for bwrob.dev.

Creates a new blog post directory with proper date prefixes, placeholder cover
image, and normalized index.qmd frontmatter.
"""

from __future__ import annotations

import argparse
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


def main() -> None:
    """Scaffold a new blog post directory and template files."""
    args = parse_args()
    validate_slug(args.slug)

    # Resolve date
    if args.date:
        try:
            post_date = datetime.date.fromisoformat(args.date)
        except ValueError:
            sys.exit(f"Error: Invalid date format '{args.date}'. Expected YYYY-MM-DD.")
    else:
        post_date = datetime.datetime.now(tz=datetime.UTC).date()

    iso_date = post_date.strftime("%Y-%m-%d")
    folder_prefix = post_date.strftime("%y-%m-%d")
    folder_name = f"{folder_prefix}-{args.slug}"

    # Determine directories
    script_dir = Path(__file__).resolve().parent
    skill_dir = script_dir.parent
    repo_root = skill_dir.parents[2]
    posts_root = repo_root / "posts"
    target_post_dir = posts_root / folder_name

    if target_post_dir.exists() and not args.force:
        err_msg = (
            f"Error: Target directory already exists: {target_post_dir}\n"
            "Use --force to overwrite."
        )
        sys.exit(err_msg)

    # Validate categories
    categories = args.categories or ["Dev Env"]
    for cat in categories:
        if cat not in CANONICAL_CATEGORIES:
            warning_msg = (
                f"Warning: Category '{cat}' is not in canonical list: "
                f"{CANONICAL_CATEGORIES}"
            )
            print(warning_msg, file=sys.stderr)

    # Ensure resource files exist
    placeholder_cover = skill_dir / "resources" / "placeholder-cover.jpg"
    template_file = skill_dir / "resources" / "post-template.qmd"

    if not placeholder_cover.exists():
        sys.exit(f"Error: Placeholder cover not found at {placeholder_cover}")
    if not template_file.exists():
        sys.exit(f"Error: Template file not found at {template_file}")

    # Create target directory
    target_post_dir.mkdir(parents=True, exist_ok=True)

    # Copy placeholder cover
    target_cover = target_post_dir / "cover.jpg"
    shutil.copyfile(placeholder_cover, target_cover)

    # Render template
    template_content = template_file.read_text(encoding="utf-8")
    categories_formatted = ", ".join(categories)
    hook_text = args.hook or (
        "Opening hook paragraph introducing the problem, tool, or pattern. "
        "Explain why this matters to developers and what the post demonstrates."
    )
    context_text = (
        "Provide background context. Why does this challenge arise? "
        "What alternatives exist? Outline the architecture or design choice."
    )
    explanation_text = (
        "Explain the code mechanics, key arguments, and non-obvious nuances."
    )

    content = (
        template_content.replace("{{TITLE}}", args.title)
        .replace("{{DESCRIPTION}}", args.description)
        .replace("{{DATE}}", iso_date)
        .replace("{{CATEGORIES}}", categories_formatted)
        .replace("{{HOOK_PARAGRAPH}}", hook_text)
        .replace("{{CONTEXT_AND_BACKGROUND}}", context_text)
        .replace("{{EXPLANATION}}", explanation_text)
    )

    target_index = target_post_dir / "index.qmd"
    target_index.write_text(content, encoding="utf-8")

    # Output confirmation
    rel_post_dir = target_post_dir.relative_to(repo_root)
    print(f"✅ Successfully scaffolded post stub in '{rel_post_dir}':")
    print(f"   - Index file:  {rel_post_dir / 'index.qmd'}")
    print(f"   - Cover image: {rel_post_dir / 'cover.jpg'} (900x600 placeholder)")
    print("   - Status:      draft: true")
    print(f"   - Categories:  [{categories_formatted}]")


if __name__ == "__main__":
    main()
