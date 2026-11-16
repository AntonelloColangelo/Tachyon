"""Render the exact Tachyon ASCII banner with a moving cyan highlight.

Run: python docs/demo/render_logo.py
Requires Pillow. DEMO_FONT selects a
monospaced TrueType font; the default is DejaVu Sans Mono on Linux.
"""

from pathlib import Path
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ART = """████████╗ █████╗  ██████╗██╗  ██╗██╗   ██╗ ██████╗ ███╗   ██╗
╚══██╔══╝██╔══██╗██╔════╝██║  ██║╚██╗ ██╔╝██╔═══██╗████╗  ██║
   ██║   ███████║██║     ███████║ ╚████╔╝ ██║   ██║██╔██╗ ██║
   ██║   ██╔══██║██║     ██╔══██║  ╚██╔╝  ██║   ██║██║╚██╗██║
   ██║   ██║  ██║╚██████╗██║  ██║   ██║   ╚██████╔╝██║ ╚████║
   ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝"""

OUT = Path(__file__).resolve().parent
S = 2                                   # HD: every size below is doubled
W, H = 960 * S, 230 * S
FONT = ImageFont.truetype(os.environ.get("DEMO_FONT",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"), 23 * S)
mask = Image.new("L", (W, H))
draw = ImageDraw.Draw(mask)
left = (W - draw.textlength(ART.splitlines()[0], font=FONT)) / 2
for i, line in enumerate(ART.splitlines()):
    draw.text((left, (34 + i * 26) * S), line, font=FONT, fill=255)
assert mask.getbbox() and mask.getbbox()[0] > 20 * S and mask.getbbox()[2] < W - 20 * S

background = Image.new("RGB", (W, H), "#0b1120")
ImageDraw.Draw(background).rounded_rectangle((1, 1, W - 2, H - 2),
    radius=18 * S, outline="#24364a", width=S)
base_glow = mask.filter(ImageFilter.GaussianBlur(5 * S)).point(lambda p: p // 5)
background = Image.composite(Image.new("RGB", (W, H), "#28778b"), background, base_glow)
base = Image.composite(Image.new("RGB", (W, H), "#75bfd0"), background, mask)


def scan(center):
    # Wide, soft wake behind a narrower bright leading edge.
    weights = []
    for x in range(W):
        head = math.exp(-((x - center) / (34 * S)) ** 2)
        wake = 0.45 * math.exp(-((x - (center - 80 * S)) / (100 * S)) ** 2)
        weights.append(min(255, int(255 * (head + wake))))
    sweep = Image.new("L", (W, 1))
    sweep.putdata(weights)
    sweep = sweep.resize((W, H))
    from PIL import ImageChops
    bright_mask = ImageChops.multiply(mask, sweep)
    halo = bright_mask.filter(ImageFilter.GaussianBlur(8 * S))
    im = Image.composite(Image.new("RGB", (W, H), "#12b8d5"), base, halo)
    return Image.composite(Image.new("RGB", (W, H), "#d7fcff"), im, bright_mask)


if __name__ == "__main__":
    frames = [base] + [scan(-200 * S + i * (W + 500 * S) / 41) for i in range(42)] + [base]
    durations = [900] + [60] * 42 + [1700]
    path = OUT / "tachyon.gif"
    sample = Image.new("RGB", (W, H * 4))
    for row, im in enumerate(frames[5::10]):
        sample.paste(im, (0, row * H))
    palette = sample.quantize(64)
    frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
    frames[0].save(path, save_all=True, append_images=frames[1:],
        duration=durations, loop=0, optimize=True, disposal=1)
    base.save(OUT / "tachyon-static.png")
    preview = Image.new("RGB", (W, H * 3), "#0b1120")
    for row, im in enumerate([base, scan(280 * S), scan(680 * S)]):
        preview.paste(im, (0, row * H))
    preview.save(OUT / "tachyon-preview.png")
    print(f"{path.name}: {path.stat().st_size} bytes")
