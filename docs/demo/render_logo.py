"""Render the exact Tachyon ASCII banner with a moving cyan highlight.

Run: python docs/demo/render_logo.py
Requires Pillow. Optional ffmpeg optimizes GIF size. DEMO_FONT selects a
monospaced TrueType font; the default is DejaVu Sans Mono on Linux.
"""

from pathlib import Path
import math
import os
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ART = """████████╗ █████╗  ██████╗██╗  ██╗██╗   ██╗ ██████╗ ███╗   ██╗
╚══██╔══╝██╔══██╗██╔════╝██║  ██║╚██╗ ██╔╝██╔═══██╗████╗  ██║
   ██║   ███████║██║     ███████║ ╚████╔╝ ██║   ██║██╔██╗ ██║
   ██║   ██╔══██║██║     ██╔══██║  ╚██╔╝  ██║   ██║██║╚██╗██║
   ██║   ██║  ██║╚██████╗██║  ██║   ██║   ╚██████╔╝██║ ╚████║
   ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝"""

OUT = Path(__file__).resolve().parent
W, H = 960, 230
FONT = ImageFont.truetype(os.environ.get("DEMO_FONT",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"), 23)
mask = Image.new("L", (W, H))
draw = ImageDraw.Draw(mask)
left = (W - draw.textlength(ART.splitlines()[0], font=FONT)) / 2
for i, line in enumerate(ART.splitlines()):
    draw.text((left, 34 + i * 26), line, font=FONT, fill=255)
assert mask.getbbox() and mask.getbbox()[0] > 20 and mask.getbbox()[2] < W - 20

background = Image.new("RGB", (W, H), "#0b1120")
ImageDraw.Draw(background).rounded_rectangle((1, 1, W - 2, H - 2),
    radius=18, outline="#24364a", width=1)
base_glow = mask.filter(ImageFilter.GaussianBlur(5)).point(lambda p: p // 5)
background = Image.composite(Image.new("RGB", (W, H), "#28778b"), background, base_glow)
base = Image.composite(Image.new("RGB", (W, H), "#75bfd0"), background, mask)


def scan(center):
    # Wide, soft wake behind a narrower bright leading edge.
    weights = []
    for x in range(W):
        head = math.exp(-((x - center) / 34) ** 2)
        wake = 0.45 * math.exp(-((x - (center - 80)) / 100) ** 2)
        weights.append(min(255, int(255 * (head + wake))))
    sweep = Image.new("L", (W, 1))
    sweep.putdata(weights)
    sweep = sweep.resize((W, H))
    from PIL import ImageChops
    bright_mask = ImageChops.multiply(mask, sweep)
    halo = bright_mask.filter(ImageFilter.GaussianBlur(8))
    im = Image.composite(Image.new("RGB", (W, H), "#12b8d5"), base, halo)
    return Image.composite(Image.new("RGB", (W, H), "#d7fcff"), im, bright_mask)


if __name__ == "__main__":
    frames = [base] + [scan(-200 + i * (W + 500) / 41) for i in range(42)] + [base]
    durations = [900] + [60] * 42 + [1700]
    path = OUT / "tachyon.gif"
    frames[0].save(path, save_all=True, append_images=frames[1:],
        duration=durations, loop=0, optimize=True, disposal=1)
    if shutil.which("ffmpeg"):
        temporary = path.with_suffix(".tmp.gif")
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(path),
            "-filter_complex", "[0:v]split[a][b];[a]palettegen=max_colors=64[p];"
            "[b][p]paletteuse=dither=none:diff_mode=rectangle",
            "-gifflags", "+transdiff", "-y", str(temporary)], check=True)
        temporary.replace(path)
    base.save(OUT / "tachyon-static.png")
    preview = Image.new("RGB", (W, H * 3), "#0b1120")
    for row, im in enumerate([base, scan(280), scan(680)]):
        preview.paste(im, (0, row * H))
    preview.save(OUT / "tachyon-preview.png")
    print(f"{path.name}: {path.stat().st_size} bytes")
