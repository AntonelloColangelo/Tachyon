"""Render the README command walkthroughs: python docs/demo/render.py.

Requires Pillow and a monospaced TrueType font; ffmpeg optionally reduces size.
These are illustrated command
walkthroughs, not recordings of an installation or an alignment benchmark.
"""

from pathlib import Path
import os
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
FONT_PATH = os.environ.get("DEMO_FONT", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
S = 2                                   # HD: every size below is doubled
FONT = ImageFont.truetype(FONT_PATH, 19 * S)
SMALL = ImageFont.truetype(FONT_PATH, 14 * S)
TITLE = ImageFont.truetype(FONT_PATH, 22 * S)
BG, PANEL = "#0b1120", "#111b2e"
TEXT, MUTED, CYAN, GREEN = "#e6edf3", "#a1afc4", "#67e8f9", "#a3e635"
W, H = 960 * S, 430 * S


def frame(title, subtitle, lines, active=None, cursor=False):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((14 * S, 14 * S, W - 15 * S, H - 15 * S), radius=16 * S, fill=PANEL, outline="#293850", width=S)
    for x, color in [(38, "#fb7185"), (59, "#fbbf24"), (80, "#a3e635")]:
        d.ellipse((x * S, 35 * S, (x + 10) * S, 45 * S), fill=color)
    d.text((112 * S, 27 * S), "TACHYON / " + title, font=SMALL, fill=TEXT)
    label = "COMMAND WALKTHROUGH"
    d.text((W - 38 * S - d.textlength(label, font=SMALL), 27 * S), label, font=SMALL, fill=CYAN)
    d.line((32 * S, 65 * S, W - 33 * S, 65 * S), fill="#293850", width=S)
    d.text((38 * S, 87 * S), subtitle, font=TITLE, fill=TEXT)
    for i, (text, color) in enumerate(lines):
        y = (144 + i * 31) * S
        if i == active:
            d.rounded_rectangle((28 * S, y - 4 * S, W - 29 * S, y + 27 * S), radius=5 * S, fill="#1b2c42")
        d.text((38 * S, y), text, font=FONT, fill=color)
    if cursor and lines:
        text = lines[-1][0]
        x = 38 * S + d.textlength(text, font=FONT)
        y = (144 + (len(lines) - 1) * 31) * S
        d.rectangle((x + 2 * S, y + 3 * S, x + 11 * S, y + 23 * S), fill=CYAN)
    d.line((32 * S, 369 * S, W - 33 * S, 369 * S), fill="#293850", width=S)
    d.text((38 * S, 385 * S), "Illustrated commands / example paths / playback speed is illustrative", font=SMALL, fill=MUTED)
    return im


def animate(name, title, subtitle, commands, intro, outro):
    frames, durations = [], []
    lines = [(intro, MUTED), ("", TEXT)]

    def add(ms, active=None, cursor=False):
        frames.append(frame(title, subtitle, lines, active, cursor))
        durations.append(ms)

    add(1100)
    for command in commands:
        lines.append(("", CYAN))
        for n in range(0, len(command), 3):
            lines[-1] = (command[:n + 3], CYAN)
            add(65, cursor=True)
        add(450, cursor=True)
    add(1800)
    lines[0] = (outro, GREEN)
    add(2500)
    frames[0].save(OUT / name, save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True, disposal=1)
    frames[-1].save(OUT / (Path(name).stem + "-preview.png"))


def migration():
    frames, durations = [], []
    lines = [("# Keep your STAR 2.7.11b index and command options.", MUTED), ("", TEXT)]
    commands = [
        "$ STAR --runThreadN 8 \\",
        "    --genomeDir /path/to/index \\",
        "    --readFilesIn reads_1.fastq.gz reads_2.fastq.gz \\",
        "    --readFilesCommand zcat \\",
        "    --outSAMtype BAM SortedByCoordinate",
    ]
    for command in commands:
        lines.append(("", TEXT))
        for n in range(0, len(command), 3):
            lines[-1] = (command[:n + 3], TEXT)
            frames.append(frame("ALIGN", "Same command. Change the program name.", lines, cursor=True))
            durations.append(55)
    frames.append(frame("ALIGN", "Same command. Change the program name.", lines))
    durations.append(1800)
    for word in ["STA", "ST", "S", "", "T", "Ta", "Tac", "Tach", "Tachy", "Tachyo", "Tachyon"]:
        lines[2] = ("$ " + word + " --runThreadN 8 \\", GREEN)
        frames.append(frame("ALIGN", "Same command. Change the program name.", lines, active=2))
        durations.append(130)
    lines[0] = ("# Ready to run with your own index and input files.", GREEN)
    frames.append(frame("ALIGN", "Same command. Change the program name.", lines, active=2))
    durations.append(3800)
    frames[0].save(OUT / "align.gif", save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True, disposal=1)
    frames[-1].save(OUT / "align-preview.png")


if __name__ == "__main__":
    animate("install.gif", "INSTALL", "Install from your terminal.", [
        "$ curl -fsSL https://raw.githubusercontent.com/AntonelloColangelo/Tachyon/\\",
        "    tachyon-0.4.1/install.sh | bash",
    ], "# Linux x86-64 + AVX2 / no GitHub account needed",
        "# Installer: download / verify checksums / install to ~/.local/bin")
    migration()
    if shutil.which("ffmpeg"):
        for path in OUT.glob("*.gif"):
            temporary = path.with_suffix(".tmp.gif")
            subprocess.run([
                "ffmpeg", "-v", "error", "-i", str(path), "-filter_complex",
                "[0:v]split[a][b];[a]palettegen=max_colors=32:stats_mode=diff[p];"
                "[b][p]paletteuse=dither=none:diff_mode=rectangle",
                "-gifflags", "+transdiff", "-y", str(temporary),
            ], check=True)
            temporary.replace(path)
