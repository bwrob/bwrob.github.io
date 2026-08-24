"""Technical logo generation for the workstation aesthetic."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Configuration
ASCII_LOGO = """
 ██████╗ ██╗    ██╗██████╗  ██████╗ ██████╗     ██████╗ ██╗      ██████╗  ██████╗
 ██╔══██╗██║    ██║██╔══██╗██╔═══██╗██╔══██╗    ██╔══██╗██║     ██╔═══██╗██╔════╝
 ██████╔╝██║ █╗ ██║██████╔╝██║   ██║██████╔╝    ██████╔╝██║     ██║   ██║██║  ███╗
 ██╔══██╗██║███╗██║██╔══██╗██║   ██║██╔══██╗    ██╔══██╗██║     ██║   ██║██║   ██║
 ██████╔╝╚███╔███╔╝██║  ██║╚██████╔╝██████╔╝    ██████╔╝███████╗╚██████╔╝╚██████╔╝
 ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝     ╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝
""".strip("\n")

ASCII_BWROB = """
 ██████╗ ██╗    ██╗██████╗  ██████╗ ██████╗
 ██╔══██╗██║    ██║██╔══██╗██╔═══██╗██╔══██╗
 ██████╔╝██║ █╗ ██║██████╔╝██║   ██║██████╔╝
 ██╔══██╗██║███╗██║██╔══██╗██║   ██║██╔══██╗
 ██████╔╝╚███╔███╔╝██║  ██║╚██████╔╝██████╔╝
 ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝
""".strip("\n")

ASCII_BW = """
 ██████╗ ██╗    ██╗
 ██╔══██╗██║    ██║
 ██████╔╝██║ █╗ ██║
 ██╔══██╗██║███╗██║
 ██████╔╝╚███╔███╔╝
 ╚═════╝  ╚══╝╚══╝
""".strip("\n")

FONT_PATH = "/usr/share/fonts/TTF/JetBrainsMonoNLNerdFontPropo-Bold.ttf"
MAGENTA = (187, 154, 247, 255)  # Tokyo Night Magenta
PAPER = (26, 27, 38, 255)  # Tokyo Night Background


def get_font(
    font_path: str | None = None,
    font_size: int = 80,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Find and load a TrueType font, falling back to system defaults if needed."""
    if font_path:
        path = Path(font_path)
        if path.exists():
            return ImageFont.truetype(str(path), font_size)
        print(
            f"Warning: Specified font_path '{font_path}' does not exist."
            " Searching standard locations."
        )

    # Try common font locations
    candidates = [
        FONT_PATH,  # original default
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
        "/System/Library/Fonts/Courier.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "C:\\Windows\\Fonts\\consola.ttf",
        "C:\\Windows\\Fonts\\couri.ttf",
    ]

    for cand in candidates:
        if cand and Path(cand).exists():
            try:
                return ImageFont.truetype(cand, font_size)
            except Exception as e:  # noqa: BLE001
                print(f"Warning: Failed to load font candidate '{cand}': {e}")

    # Ultimate fallback
    print("Warning: No TrueType fonts found. Falling back to default font.")
    try:
        # Pillow 10+ supports size in load_default
        return ImageFont.load_default(size=font_size)
    except TypeError:
        return ImageFont.load_default()


def generate_logo(  # noqa: PLR0913, PLR0917
    logo_text: str = ASCII_LOGO,
    font_size: int = 100,
    font_path: str | None = None,
    output_path: str = "assets/logo/logo_full.png",
    fill_color: tuple = MAGENTA,
    line_height_factor: float = 0.85,
    padding: int = 50,
) -> None:
    """Render the ASCII logo to PNG with customizable inputs."""
    font = get_font(font_path, font_size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = logo_text.split("\n")

    line_h = int(font_size * line_height_factor)

    try:
        widths = [dummy.textbbox((0, 0), line, font=font)[2] for line in lines]
        max_w = int(max(widths))
    except Exception:  # noqa: BLE001
        max_w = int(max(len(line) for line in lines) * (font_size * 0.6))

    canvas_size = (max_w + padding * 2, (line_h * len(lines)) + padding * 2)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    for i, line in enumerate(lines):
        draw.text((padding, padding + i * line_h), line, font=font, fill=fill_color)

    bbox = canvas.getbbox()
    if bbox:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        canvas.crop(bbox).save(output_file)
        print(f"Generated: {output_file}")
    else:
        print(f"Warning: Empty bounding box for {output_path}")


def generate_favicon(  # noqa: PLR0913, PLR0917
    text: str = "BW",
    side: int = 512,
    font_size: int = 300,
    font_path: str | None = None,
    output_path: str = "assets/logo/favicon.png",
    radius: int = 80,
    bg_color: tuple = PAPER,
    fill_color: tuple = MAGENTA,
    offset_y: int = -40,
) -> None:
    """Generate a sharp BW glyph favicon.

    Uses Tokyo Night styling and adjustable inputs.
    """
    img = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background (Tokyo Night Paper)
    draw.rounded_rectangle([20, 20, side - 20, side - 20], radius=radius, fill=bg_color)

    # Sharp glyphs
    font = get_font(font_path, font_size)

    # Center text
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        w = int(bbox[2] - bbox[0])
        h = int(bbox[3] - bbox[1])
    except Exception:  # noqa: BLE001
        w = int(len(text) * (font_size * 0.6))
        h = font_size

    # Adjust y for baseline
    draw.text(
        ((side - w) // 2, (side - h) // 2 + offset_y), text, font=font, fill=fill_color
    )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_file)
    print(f"Generated: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate workstation aesthetic logos."
    )
    parser.add_argument(
        "--font-size", type=int, default=80, help="Font size for the logo ASCII text."
    )
    parser.add_argument(
        "--font-path", type=str, default=None, help="Path to custom TTF/OTF font."
    )
    parser.add_argument(
        "--line-height-factor",
        type=float,
        default=0.85,
        help="Line height scale factor.",
    )
    parser.add_argument(
        "--padding", type=int, default=50, help="Padding around the logo text."
    )
    parser.add_argument(
        "--favicon-size", type=int, default=512, help="Favicon image side length."
    )
    parser.add_argument(
        "--favicon-font-size", type=int, default=300, help="Favicon text font size."
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        choices=["full", "bwrob"],
        help="Custom text type.",
    )

    args = parser.parse_args()

    # Ensure parent directory exists
    Path("assets/logo").mkdir(parents=True, exist_ok=True)

    if args.text == "bwrob":
        generate_logo(
            logo_text=ASCII_BWROB,
            font_size=args.font_size,
            font_path=args.font_path,
            line_height_factor=args.line_height_factor,
            padding=args.padding,
            output_path="assets/logo/logo_bwrob.png",
        )
    elif args.text == "full":
        generate_logo(
            logo_text=ASCII_LOGO,
            font_size=args.font_size,
            font_path=args.font_path,
            line_height_factor=args.line_height_factor,
            padding=args.padding,
            output_path="assets/logo/logo_full.png",
        )
    else:
        # Default behavior: generate both logos and favicon
        generate_logo(
            logo_text=ASCII_LOGO,
            font_size=args.font_size,
            font_path=args.font_path,
            line_height_factor=args.line_height_factor,
            padding=args.padding,
            output_path="assets/logo/logo_full.png",
        )
        generate_logo(
            logo_text=ASCII_BWROB,
            font_size=args.font_size,
            font_path=args.font_path,
            line_height_factor=args.line_height_factor,
            padding=args.padding,
            output_path="assets/logo/logo_bwrob.png",
        )
        generate_favicon(
            side=args.favicon_size,
            font_size=args.favicon_font_size,
            font_path=args.font_path,
        )
