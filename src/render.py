#!/usr/bin/env python3
"""Render "ROUND ONE, ON YOU" — 4-panel CC0 Halloween comic (one PNG, 2080x2080).

Nouns characters are decoded with the official @nouns/sdk buildSVG (v1.2.0,
vendored as src/sdk/nouns-sdk.cjs, an ESM-to-CJS adaptation of the official
dist bundle — see sources.md). All scenery (sky, stars, moon, graveyard,
tombstones, the glowing treat, speech bubbles, lettering, motion trail) is
drawn in code with Pillow.

Fonts are BUNDLED with the source (src/fonts/): Liberation Sans Bold and
Regular, SIL OFL 1.1 (src/fonts/OFL.txt). No system fonts are required at
render time.

Deterministic: no randomness, no network access. Re-running on any machine
with the same Pillow/FreeType builds yields the same PNG (same sha256).

Usage:  python3 src/render.py --out PATH
"""
import argparse
import json
import math
import os
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "image-data.json")
SDK_DIR = os.path.join(HERE, "sdk")
FONT_BOLD = os.path.join(HERE, "fonts", "LiberationSans-Bold.ttf")
FONT_REG = os.path.join(HERE, "fonts", "LiberationSans-Regular.ttf")

PANEL = 980
MARGIN = 40
GUTTER = 40
W = H = 2 * PANEL + 2 * MARGIN + GUTTER  # 2080

BUBBLE_FILL = (246, 244, 238)
BUBBLE_EDGE = (26, 24, 38)
INK = (22, 20, 36)
GRID = 32


# ---------- decode via official @nouns/sdk ----------
def noun_rects(data, filenames):
    """Return list of (x, y, w, h, r, g, b) in 32x32 grid units (10px = 1 unit)."""
    parts = []
    for fn in filenames:
        if not fn:
            continue
        found = None
        for layer in ("bodies", "accessories", "heads", "glasses"):
            for item in data["images"][layer]:
                if item["filename"] == fn:
                    found = item["data"]
                    break
            if found:
                break
        if not found:
            raise ValueError("Nouns part not found: " + fn)
        parts.append({"data": found})
    if not parts:
        return []
    cjs = os.path.join(SDK_DIR, "nouns-sdk.cjs")
    js = (
        'const {buildSVG}=require("%s");\n' % cjs
        + "const parts=%s;\n" % json.dumps(parts)
        + "const palette=%s;\n" % json.dumps(data["palette"])
        + 'process.stdout.write(buildSVG(parts,palette,"%s"));' % data["bgcolors"][0]
    )
    import tempfile
    tdir = tempfile.mkdtemp(prefix="nouns_decode_")
    tmp = os.path.join(tdir, "decode.js")
    try:
        with open(tmp, "w") as f:
            f.write(js)
        r = subprocess.run(
            ["node", tmp],
            cwd=SDK_DIR, capture_output=True, text=True, timeout=60,
        )
    finally:
        import shutil
        shutil.rmtree(tdir, ignore_errors=True)
    if r.returncode != 0:
        raise RuntimeError("node decode failed: " + r.stderr[:300])
    rects = re.findall(
        r'<rect width="(\d+)" height="(\d+)" x="(\d+)" y="(\d+)" fill="#([0-9a-f]{6})"\s*/>',
        r.stdout,
    )
    out = []
    for wu, hu, xu, yu, col in rects:
        # regex order is (width, height, x, y, fill-color) -> map to (x, y, w, h, rgb)
        out.append((
            int(xu) // 10, int(yu) // 10, int(wu) // 10, int(hu) // 10,
            int(col[0:2], 16), int(col[2:4], 16), int(col[4:6], 16),
        ))
    return out


def render_noun(data, body, head, glasses=None, acc=None, scale=18):
    rects = noun_rects(data, [body, acc, head, glasses])
    size = GRID * scale
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    for x, y, w, h, r, g, b in rects:
        for dy in range(h * scale):
            for dx in range(w * scale):
                px[x * scale + dx, y * scale + dy] = (r, g, b, 255)
    return img


# ---------- scenery ----------
def sky(dr, w, h):
    top, bot = (27, 25, 60), (70, 46, 104)
    for y in range(h):
        t = y / h
        dr.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))


STARS = [
    (0.05, 0.08, 3), (0.12, 0.22, 2), (0.19, 0.05, 2), (0.26, 0.30, 3),
    (0.33, 0.10, 2), (0.41, 0.20, 2), (0.47, 0.06, 3), (0.55, 0.16, 2),
    (0.62, 0.33, 2), (0.68, 0.09, 3), (0.74, 0.24, 2), (0.81, 0.13, 2),
    (0.88, 0.30, 3), (0.94, 0.07, 2), (0.30, 0.42, 2), (0.50, 0.40, 2),
    (0.70, 0.44, 2), (0.90, 0.42, 3), (0.08, 0.38, 2), (0.16, 0.50, 2),
]


def stars(dr, w, h):
    for sx, sy, r in STARS:
        x, y = int(sx * w), int(sy * h)
        if y < h * 0.70:
            dr.ellipse([x - r, y - r, x + r, y + r], fill=(216, 214, 238))


def moon(dr, cx, cy, r):
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(243, 238, 212))
    for dx, dy, dr2 in ((-0.3, -0.15, 0.16), (0.2, 0.25, 0.11),
                        (0.05, -0.35, 0.08), (-0.1, 0.3, 0.07)):
        rr = r * dr2
        dr.ellipse([cx + dx * r - rr, cy + dy * r - rr,
                    cx + dx * r + rr, cy + dy * r + rr], fill=(221, 214, 188))


def ground(dr, w, h, y0):
    dr.rectangle([0, y0, w, h], fill=(30, 45, 32))
    for gx in (0.06, 0.2, 0.4, 0.6, 0.8, 0.94):
        x = int(gx * w)
        for dx, ch in ((-14, 26), (0, 38), (14, 22)):
            dr.polygon([(x + dx, y0), (x + dx + 8, y0), (x + dx + 4, y0 - ch)],
                       fill=(43, 65, 43))


def tombstone(dr, x, ybase, w, h, text, sub, fbig, fsub):
    r = w // 2
    dr.rounded_rectangle([x, ybase - h + r, x + w, ybase], radius=r,
                         fill=(121, 127, 139), outline=(73, 77, 89), width=4)
    dr.text((x + w / 2, ybase - h + r + h * 0.28), text, font=fbig,
            fill=(52, 55, 64), anchor="mm")
    if sub:
        dr.text((x + w / 2, ybase - h + r + h * 0.62), sub, font=fsub,
                fill=(70, 73, 82), anchor="mm")


def treat(dr, cx, cy, r):
    """The glowing sweet. Drawn LAST in its panel so it is always visible."""
    for i in range(8):
        a = i * math.pi / 4
        dr.line([(cx + math.cos(a) * r * 1.12, cy + math.sin(a) * r * 1.12),
                 (cx + math.cos(a) * r * 1.72, cy + math.sin(a) * r * 1.72)],
                fill=(255, 203, 88), width=6)
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 156, 44),
               outline=(184, 94, 20), width=4)
    dr.ellipse([cx - r * 0.45, cy - r * 0.52, cx + r * 0.22, cy + r * 0.12],
               fill=(255, 216, 104))
    dr.ellipse([cx - r * 0.32, cy - r * 0.40, cx - r * 0.10, cy - r * 0.18],
               fill=(255, 245, 205))


def lift_lines(dr, cx, y, w):
    for dx, lw in ((-w * 0.45, 26), (-w * 0.1, 40), (w * 0.3, 22)):
        dr.line([(cx + dx - lw // 2, y), (cx + dx + lw // 2, y)],
                fill=(168, 172, 206), width=5)


def trail(dr, x0, y0, x1, y1, r):
    """Motion dashes from giver to sweet (panel 2: the hand-off)."""
    n = 5
    for i in range(n):
        t = (i + 0.5) / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        dr.ellipse([x - r, y - r, x + r, y + r],
                   fill=(255, 203, 88), outline=(184, 94, 20), width=3)


def place_noun(panel, img, cx, feet_y, alpha=255):
    if alpha >= 255:
        panel.alpha_composite(img, (int(cx - img.width / 2), int(feet_y - img.height)))
        return
    copy = img.copy()
    a = copy.getchannel("A").point(lambda v: int(v * alpha / 255))
    copy.putalpha(a)
    panel.alpha_composite(copy, (int(cx - img.width / 2), int(feet_y - img.height)))


def bubble(dr, panel, x, y, w, h, text, font, tail_cx):
    """Speech bubble with a tail whose TIP is at tail_cx (the speaker's x).
    The tip is NOT clamped to the bubble box, so even short text on a centered
    bubble points its tail clearly at the correct speaker."""
    dr.rounded_rectangle([x, y, x + w, y + h], radius=26, fill=BUBBLE_FILL,
                         outline=BUBBLE_EDGE, width=5)
    dr.text((x + w / 2, y + h / 2), text, font=font, fill=INK, anchor="mm")
    # tail tip sits just past the bubble bottom, at the speaker's x (unclamped)
    tip_x = int(tail_cx)
    base_x = max(x + 10, min(tip_x, x + w - 10))   # base attaches inside the bubble
    base_y = y + h
    tip_y = base_y + 40
    # triangle: two base points on the bubble bottom edge, one tip below
    dr.polygon([(base_x - 22, base_y), (base_x + 22, base_y), (tip_x, tip_y)],
               fill=BUBBLE_FILL, outline=BUBBLE_EDGE, width=5)
    # re-cover the interior so the outline doesn't cut across the tail
    dr.polygon([(base_x - 15, base_y - 1), (base_x + 15, base_y - 1),
                (tip_x, tip_y - 6)], fill=BUBBLE_FILL)


def label(dr, cx, cy, text, font, fill):
    dr.text((cx, cy), text, font=font, fill=fill, anchor="mm")


def make_panel(left_img, right_img, text, ftext,
               left_alpha, right_alpha, left_float, right_float,
               tail_frac, fonts, left_label, right_label,
               show_trail_from=None):
    """Draw one panel. LEFT figure at x=0.36*PANEL, RIGHT figure at x=0.64*PANEL.
    The speech-bubble tail is pointed at tail_frac (the SPEAKER's x)."""
    panel = Image.new("RGBA", (PANEL, PANEL), (0, 0, 0, 255))
    dr = ImageDraw.Draw(panel)
    sky(dr, PANEL, PANEL)
    stars(dr, PANEL, PANEL)
    moon(dr, int(PANEL * 0.80), int(PANEL * 0.22), 118)
    gy = int(PANEL * 0.80)
    ground(dr, PANEL, PANEL, gy)
    tombstone(dr, int(PANEL * 0.03), gy + 10, 148, 206, "RIP", "est. 2020",
              fonts[30], fonts[22])
    tombstone(dr, int(PANEL * 0.87), gy + 6, 118, 164, "RIP", "",
              fonts[28], fonts[22])

    gh_px = GRID * 18
    base_feet = gy + 22
    lx = int(PANEL * 0.36)
    rx = int(PANEL * 0.64)
    left_feet = base_feet - (140 if left_float else 40)
    right_feet = base_feet - (140 if right_float else 40)

    # characters: LEFT then RIGHT (draw order: right first so the left/foreground
    # figure overlaps the right one slightly where they meet — keeps each face visible)
    if right_float:
        lift_lines(dr, rx, right_feet + 6, gh_px * 0.55)
    place_noun(panel, right_img, rx, right_feet, right_alpha)
    if left_float:
        lift_lines(dr, lx, left_feet + 6, gh_px * 0.55)
    place_noun(panel, left_img, lx, left_feet, left_alpha)

    # motion trail from the GIVER toward the sweet (the treat is being handed over)
    candy_cx = int(PANEL * 0.50)
    candy_cy = int(PANEL * 0.50)
    if show_trail_from is not None:
        trail(dr, int(PANEL * show_trail_from), candy_cy - 40,
              candy_cx - 70, candy_cy, 10)

    # THE SWEET — drawn after both figures so it is never hidden behind either
    treat(dr, candy_cx, candy_cy, 44)

    # character name labels, below each figure's feet (who is who, every panel)
    lab_y = min(base_feet + 60, PANEL - 46)
    label(dr, lx, lab_y, left_label, fonts[22], (205, 210, 235))
    label(dr, rx, lab_y, right_label, fonts[22], (205, 210, 235))

    # speech bubble: tail points at the SPEAKER (tail_frac is the speaker's x)
    tw = dr.textlength(text, font=ftext)
    bw = int(tw + 92)
    bh = 112
    bx = max(24, min(PANEL - bw - 24, PANEL // 2 - bw // 2))
    by = 42
    bubble(dr, panel, bx, by, bw, bh, text, ftext,
           tail_cx=int(PANEL * tail_frac))
    return panel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="output PNG path")
    args = ap.parse_args()
    out = os.path.abspath(args.out)

    with open(DATA) as f:
        data = json.load(f)

    fonts = {
        52: ImageFont.truetype(FONT_BOLD, 52),
        30: ImageFont.truetype(FONT_BOLD, 30),
        28: ImageFont.truetype(FONT_BOLD, 28),
        22: ImageFont.truetype(FONT_REG, 22),
    }

    # cast — Nouns CC0 image data (nouns-monorepo commit 2213eea)
    ghost_noun = render_noun(data, "body-blue-sky", "head-ghost-B", "glasses-square-black")
    pumpkin_noun = render_noun(data, "body-orange", "head-pumpkin")

    # Four-panel arc — the SAME two Nouns (GHOST and PUMPKIN) in every panel:
    #  1. GHOST (left, floating) offers PUMPKIN a sweet.      "A treat for you."
    #  2. PUMPKIN (right) eats it — bubble tail on PUMPKIN.   "Mmm. Spooky-good."
    #  3. The soul transfers: GHOST fades, PUMPKIN rises.     "Whoops."
    #  4. Role reversal: PUMPKIN (now the ghost, left) offers
    #     a fresh sweet back to the original GHOST (right).   "Round one, on you."
    panels = [
        # p1: GHOST left(0.36) offers; tail on GHOST
        make_panel(ghost_noun, pumpkin_noun, "A treat for you.", fonts[52],
                   left_alpha=235, right_alpha=255,
                   left_float=True, right_float=False,
                   tail_frac=0.36, fonts=fonts,
                   left_label="GHOST", right_label="PUMPKIN",
                   show_trail_from=0.42),
        # p2: PUMPKIN right(0.64) eats; tail on PUMPKIN
        make_panel(ghost_noun, pumpkin_noun, "Mmm. Spooky-good.", fonts[52],
                   left_alpha=235, right_alpha=255,
                   left_float=True, right_float=False,
                   tail_frac=0.64, fonts=fonts,
                   left_label="GHOST", right_label="PUMPKIN",
                   show_trail_from=0.42),
        # p3: GHOST (left) fading = the one losing its soul; PUMPKIN (right)
        #     solid and rising; tail on GHOST
        make_panel(ghost_noun, pumpkin_noun, "Whoops.", fonts[52],
                   left_alpha=110, right_alpha=255,
                   left_float=True, right_float=True,
                   tail_frac=0.36, fonts=fonts,
                   left_label="GHOST", right_label="PUMPKIN",
                   show_trail_from=0.42),
        # p4: swap slots — PUMPKIN (now the ghost, left, floating) offers
        #     the original GHOST (right) a fresh sweet; tail on PUMPKIN
        make_panel(pumpkin_noun, ghost_noun, "Round one, on you.", fonts[52],
                   left_alpha=235, right_alpha=255,
                   left_float=True, right_float=False,
                   tail_frac=0.36, fonts=fonts,
                   left_label="PUMPKIN (NOW A GHOST)", right_label="GHOST",
                   show_trail_from=0.42),
    ]

    canvas = Image.new("RGB", (W, H), (12, 11, 22))
    pos = [
        (MARGIN, MARGIN),
        (MARGIN + PANEL + GUTTER, MARGIN),
        (MARGIN, MARGIN + PANEL + GUTTER),
        (MARGIN + PANEL + GUTTER, MARGIN + PANEL + GUTTER),
    ]
    for i, p in enumerate(panels):
        canvas.paste(p.convert("RGB"), pos[i])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    canvas.save(out)
    print("wrote", out, canvas.size)


if __name__ == "__main__":
    main()
