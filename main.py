#!/usr/bin/env python3
"""The Poster for a Place That Isn't There — MIRALUNE.

Deterministic PIL travel poster (1024x1024 PNG) for an invented lake
city at night: aurora over a still lake, a pale Moon Arch standing in
the water, crescent boats with lanterns. The only text in the picture
is the place name. No network; fixed-seed pseudo-random detail only.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = "/output/entry.png"
rng = random.Random(20261121)

# ---------- fonts ----------
FONT_DIRS = ["/usr/share/fonts/truetype/liberation", "/usr/share/fonts/truetype/dejavu"]

def font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()

SERIF_B = lambda s: font(["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"], s)

# ---------- palette ----------
PAPER   = (238, 234, 222)
INK     = (10, 16, 34)
NAVY    = (10, 18, 42)
LAKE_D  = (10, 26, 56)
LAKE    = (18, 48, 80)
LAKE_L  = (70, 130, 150)
AURORA  = (96, 230, 170)
AURORA2 = (150, 240, 200)
MOON    = (242, 240, 222)
GOLD    = (244, 200, 110)
CREAM   = (250, 246, 230)
PINE    = (12, 30, 44)
ARCH    = (226, 232, 238)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# poster field (inside the paper margin)
X0, Y0, X1, Y1 = 36, 36, W - 36, H - 36
HOR = 560          # far-shore line
BAND = 872         # top of the name band

# ---------- night sky ----------
sky_stops = [
    (0.00, (8, 14, 38)),
    (0.35, (14, 28, 64)),
    (0.65, (20, 52, 84)),
    (0.85, (26, 84, 96)),
    (1.00, (38, 110, 104)),
]
def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))

def sky_color(t):
    for i in range(len(sky_stops) - 1):
        t0, c0 = sky_stops[i]
        t1, c1 = sky_stops[i + 1]
        if t0 <= t <= t1:
            return lerp(c0, c1, (t - t0) / (t1 - t0))
    return sky_stops[-1][1]

for y in range(Y0, HOR):
    t = (y - Y0) / (HOR - Y0)
    d.line([(X0, y), (X1, y)], fill=sky_color(t))

# ---------- stars ----------
for _ in range(160):
    x = rng.randint(X0 + 8, X1 - 8)
    y = rng.randint(Y0 + 8, HOR - 120)
    r = rng.choice([1, 1, 1, 2])
    d.ellipse([x - r, y - r, x + r, y + r], fill=(226, 234, 248))

# ---------- aurora: layered flowing ribbons with curtain streaks ----------
aur = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ad = ImageDraw.Draw(aur)
def ribbon(ybase, amp, thick, col, alpha):
    top, bot = [], []
    for i in range(25):
        x = X0 + i * (X1 - X0) // 24
        import math
        y = ybase + int(amp * math.sin(i * 0.55 + ybase))
        top.append((x, y))
        bot.append((x, y + thick + int(10 * math.sin(i * 0.8))))
    ad.polygon(top + bot[::-1], fill=col + (alpha,))
    ad.line(bot, fill=(190, 255, 220, 120), width=3)
ribbon(128, 30, 34, (140, 245, 195), 52)
ribbon(168, 24, 26, (170, 252, 210), 64)
ribbon(204, 18, 20, (120, 240, 185), 76)
# faint curtain streaks hanging from the lowest ribbon
for i in range(30):
    x = X0 + 20 + i * 31 + rng.randint(-5, 5)
    import math
    ytop = 220 + int(18 * math.sin(i * 0.5 + 204))
    ad.line([(x, ytop), (x + rng.randint(-4, 4), ytop + rng.randint(22, 44))],
            fill=(160, 248, 205, 26), width=3)
img.paste(Image.alpha_composite(img.convert("RGBA"), aur).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img)

# (the moon is drawn after the lake reflection is taken, below,
#  so its reflection is the shimmering path, not a flipped disc)

# ---------- far shore: pine ridge with stilt houses ----------
ridge = [(X0, HOR), (X0, HOR - 60), (180, HOR - 84), (340, HOR - 58), (520, HOR - 88),
         (700, HOR - 60), (860, HOR - 80), (X1, HOR - 56), (X1, HOR)]
d.polygon(ridge, fill=PINE)
for px in range(X0 + 30, X1 - 20, 46):
    ph = rng.randint(38, 64)
    base = HOR - rng.randint(48, 72)
    d.polygon([(px - 11, base), (px + 11, base), (px, base - ph)], fill=PINE)
# stilt houses along the shore, warm windows lit
for hx, hw in [(120, 44), (210, 38), (640, 42), (730, 36), (880, 44)]:
    hy = HOR - 34
    d.line([(hx + 6, hy + 22), (hx + 6, HOR + 4)], fill=INK, width=3)
    d.line([(hx + hw - 6, hy + 22), (hx + hw - 6, HOR + 4)], fill=INK, width=3)
    d.rectangle([hx, hy, hx + hw, hy + 22], fill=(32, 44, 66))
    d.polygon([(hx - 4, hy), (hx + hw + 4, hy), (hx + hw // 2, hy - 13)], fill=(20, 30, 52))
    d.rectangle([hx + 8, hy + 7, hx + 15, hy + 15], fill=GOLD)
    d.rectangle([hx + hw - 15, hy + 7, hx + hw - 8, hy + 15], fill=GOLD)

# ---------- the Moon Arch (landmark) ----------
ax, ay, ar = 430, HOR + 40, 190
d.arc([ax - ar, ay - ar, ax + ar, ay + ar], start=180, end=360, fill=ARCH, width=20)

# ---------- lake: gradient + mirror reflection of sky and shore ----------
for y in range(HOR, BAND):
    t = (y - HOR) / (BAND - HOR)
    d.line([(X0, y), (X1, y)], fill=lerp(LAKE, LAKE_D, t))
sky_img = img.crop((X0, Y0, X1, HOR)).transpose(Image.FLIP_TOP_BOTTOM)
sky_img = sky_img.resize((X1 - X0, BAND - HOR))
sky_img = Image.blend(sky_img, Image.new("RGB", sky_img.size, LAKE_D), 0.52)
fade = Image.new("L", sky_img.size, 0)
fd = ImageDraw.Draw(fade)
for yy in range(sky_img.size[1]):
    fd.line([(0, yy), (sky_img.size[0], yy)], fill=int(165 - 120 * yy / sky_img.size[1]))
img.paste(sky_img, (X0, HOR), fade)
d = ImageDraw.Draw(img)
# redraw the arch so its feet stand in the water, over its reflection
d.arc([ax - ar, ay - ar, ax + ar, ay + ar], start=180, end=360, fill=ARCH, width=20)
d.ellipse([ax - 7, ay - ar - 7, ax + 7, ay - ar + 7], fill=GOLD)

# ---------- full moon with a soft halo (drawn last in the sky) ----------
mx, my, mr = 798, 152, 46
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(halo)
hd.ellipse([mx - 92, my - 92, mx + 92, my + 92], fill=(240, 238, 210, 26))
hd.ellipse([mx - 66, my - 66, mx + 66, my + 66], fill=(240, 238, 210, 30))
img.paste(Image.alpha_composite(img.convert("RGBA"), halo).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img)
d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=MOON)
d.ellipse([mx - 18, my - 10, mx - 6, my + 2], fill=(226, 224, 204))
d.ellipse([mx + 10, my + 14, mx + 22, my + 26], fill=(226, 224, 204))

# moon path on the water (broken, widening dashes)
for i in range(13):
    yy = HOR + 16 + i * 19
    half = 18 + i * 6
    jitter = rng.randint(-18, 18)
    seg = rng.randint(16, 28)
    d.line([(mx - half + jitter, yy), (mx - half + jitter + seg, yy)], fill=(222, 228, 202), width=3)
    d.line([(mx + half + jitter - seg, yy), (mx + half + jitter, yy)], fill=(222, 228, 202), width=3)
    if i % 2 == 0:
        d.line([(mx - 11 + jitter, yy), (mx + 11 + jitter, yy)], fill=(238, 240, 216), width=3)
# gentle ripple dashes
for _ in range(70):
    x = rng.randint(X0 + 20, X1 - 60)
    y = rng.randint(HOR + 14, BAND - 18)
    d.line([(x, y), (x + rng.randint(12, 30), y)], fill=LAKE_L, width=2)

# crescent boats with lanterns (the boats of Miralune are shaped like moons)
def crescent_boat(bx, by, s):
    import math
    pts = []
    for i in range(13):
        a = math.pi * i / 12
        pts.append((bx - 42 * s * math.cos(a), by + 16 * s * math.sin(a)))
    for i in range(12, -1, -1):
        a = math.pi * i / 12
        pts.append((bx - 42 * s * math.cos(a), by - 4 * s + 10 * s * math.sin(a)))
    d.polygon(pts, fill=INK)
    d.line([(bx, by - 2 * s), (bx, by - 30 * s)], fill=INK, width=2)
    d.ellipse([bx - 6 * s, by - 40 * s, bx + 6 * s, by - 28 * s], fill=GOLD)
    d.line([(bx - 24 * s, by + 24 * s), (bx + 24 * s, by + 24 * s)], fill=(244, 200, 110), width=2)
    d.line([(bx - 14 * s, by + 32 * s), (bx + 14 * s, by + 32 * s)], fill=(244, 200, 110), width=2)

crescent_boat(300, 706, 1.15)
crescent_boat(668, 782, 0.9)
crescent_boat(856, 692, 0.72)

# ---------- name band: the only text ----------
d.rectangle([X0, BAND, X1, Y1], fill=NAVY)
d.line([(X0 + 40, BAND + 22), (X1 - 40, BAND + 22)], fill=GOLD, width=2)
name = "MIRALUNE"
f = SERIF_B(72)
spacing = 30
widths = [d.textlength(ch, font=f) for ch in name]
total = sum(widths) + spacing * (len(name) - 1)
x = (W - total) / 2
for ch, wch in zip(name, widths):
    d.text((x, BAND + 34), ch, font=f, fill=CREAM)
    x += wch + spacing

# ---------- print grain (deterministic) ----------
grain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(grain)
for _ in range(2600):
    x = rng.randint(0, W - 1)
    y = rng.randint(0, H - 1)
    a = rng.randint(4, 13)
    gd.point((x, y), fill=(24, 22, 18, a) if rng.random() < 0.5 else (255, 252, 238, a))
img = Image.alpha_composite(img.convert("RGBA"), grain).convert("RGB")
d = ImageDraw.Draw(img)

# ---------- frame ----------
d.rectangle([X0, Y0, X1, Y1], outline=INK, width=3)
d.rectangle([18, 18, W - 18, H - 18], outline=INK, width=1)

os.makedirs("/output", exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT}: {os.path.getsize(OUT)} bytes, {img.size}")
