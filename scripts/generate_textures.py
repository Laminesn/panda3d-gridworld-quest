"""
generate_textures.py — Bake simple placeholder textures using Pillow.

Produces four 64x64 PNGs in assets/textures/ that match the game's color
scheme. The game itself uses setColor() and doesn't require these files to
run, but they make the repo feel complete and demonstrate Pillow integration.

Usage:
    python scripts/generate_textures.py
"""

import os

from PIL import Image, ImageDraw

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "textures")
SIZE = 64


def _save(img: Image.Image, name: str) -> None:
    path = os.path.join(OUT_DIR, name)
    img.save(path)
    print(f"  wrote {path}")


def make_floor() -> Image.Image:
    """Light beige tile with faint grid lines."""
    img = Image.new("RGB", (SIZE, SIZE), (210, 200, 175))
    draw = ImageDraw.Draw(img)
    mid = SIZE // 2
    draw.line([(0, mid), (SIZE, mid)], fill=(190, 180, 155), width=1)
    draw.line([(mid, 0), (mid, SIZE)], fill=(190, 180, 155), width=1)
    return img


def make_wall() -> Image.Image:
    """Dark gray stone with horizontal and staggered vertical brick lines."""
    img = Image.new("RGB", (SIZE, SIZE), (92, 92, 100))
    draw = ImageDraw.Draw(img)
    row_h = 16
    for row, y in enumerate(range(0, SIZE, row_h)):
        draw.line([(0, y), (SIZE, y)], fill=(60, 60, 68), width=2)
        # Stagger vertical joints on alternating rows
        offset = (row % 2) * (row_h // 2)
        for x in range(offset, SIZE, row_h):
            draw.line([(x, y), (x, y + row_h)], fill=(60, 60, 68), width=1)
    return img


def make_coin() -> Image.Image:
    """Gold circle on a dark background."""
    img = Image.new("RGB", (SIZE, SIZE), (30, 28, 20))
    draw = ImageDraw.Draw(img)
    margin = 6
    draw.ellipse(
        [margin, margin, SIZE - margin, SIZE - margin],
        fill=(230, 185, 20),
        outline=(200, 140, 0),
        width=3,
    )
    # Inner highlight
    hi = margin + 10
    draw.ellipse([hi, hi, hi + 8, hi + 8], fill=(255, 240, 120))
    return img


def make_goal() -> Image.Image:
    """Green tile with two concentric target rings."""
    img = Image.new("RGB", (SIZE, SIZE), (30, 170, 55))
    draw = ImageDraw.Draw(img)
    for r in (6, 14):
        draw.ellipse(
            [r, r, SIZE - r, SIZE - r],
            outline=(255, 255, 120),
            width=2,
        )
    return img


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Writing textures to {os.path.abspath(OUT_DIR)}/")
    _save(make_floor(), "floor.png")
    _save(make_wall(),  "wall.png")
    _save(make_coin(),  "coin.png")
    _save(make_goal(),  "goal.png")
    print("Done.")
