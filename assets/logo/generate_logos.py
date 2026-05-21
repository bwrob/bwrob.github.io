"""Technical logo generation for the workstation aesthetic."""

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


def generate_logo() -> None:
    """Render the full BWROB BLOG ASCII logo to PNG."""
    font = ImageFont.truetype(FONT_PATH, 80)
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = ASCII_LOGO.split("\n")

    line_h = int(80 * 0.85)
    widths = [dummy.textbbox((0, 0), line, font=font)[2] for line in lines]
    max_w = int(max(widths))

    canvas_size = (max_w + 100, (line_h * len(lines)) + 100)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    for i, line in enumerate(lines):
        draw.text((50, 50 + i * line_h), line, font=font, fill=MAGENTA)

    bbox = canvas.getbbox()
    if bbox:
        canvas.crop(bbox).save("assets/logo/logo_full.png")
    print("Generated: assets/logo/logo_full.png")


def generate_favicon() -> None:
    """Generate a sharp BW glyph favicon with Tokyo Night styling."""
    # Square icon with rounded corners (panel style)
    side = 512
    img = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background (Tokyo Night Paper)
    radius = 80
    draw.rounded_rectangle([20, 20, 492, 492], radius=radius, fill=PAPER)

    # Sharp glyphs instead of ASCII blocks for readability
    font = ImageFont.truetype(FONT_PATH, 300)
    text = "BW"

    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    w = int(bbox[2] - bbox[0])
    h = int(bbox[3] - bbox[1])

    # Adjust y for baseline
    draw.text(((side - w) // 2, (side - h) // 2 - 40), text, font=font, fill=MAGENTA)

    img.save("assets/logo/favicon.png")
    print("Generated: assets/logo/favicon.png")


if __name__ == "__main__":
    Path("assets/logo").mkdir(parents=True, exist_ok=True)
    generate_logo()
    generate_favicon()
