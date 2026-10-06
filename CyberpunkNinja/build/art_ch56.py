"""
Chapter 5 (Hollow Floor) and Chapter 6 (The Academy) art.

Hollow Floor is built from Kuro's memories, so most of it is pack art
re-toned into a violet "memory" ramp by luminance. The Academy re-tones the
Tenshu tileset into red lacquer and draws a training-hall backdrop. Both
chapters share the phasing block (glitch blocks in Ch5, training holograms
in Ch6).

All functions return 1x art-pixel images unless noted.
"""
import random

from PIL import Image, ImageDraw

import assets
from assets import PALETTE as P
from art_ch2 import recolor, gradient, st  # noqa: F401


def C(name, a=255):
    return P[name] + (a,)


MEMORY_RAMP = ['ink', 'night1', 'night2', 'purple1', 'purple2', 'purple3', 'white']
ACADEMY_RAMP = ['ink', 'night1', 'brown', 'red1', 'red2', 'orange', 'yellow']


def tone(im, ramp, keep=(), stretch=False):
    """Map every pixel onto a color ramp by luminance (palette names in `keep` survive).
    With stretch, the image's own darkest..brightest range spans the whole ramp."""
    im = im.convert('RGBA').copy()
    px = im.load()
    keepset = {P[k] for k in keep}
    cols = [P[c] for c in ramp]
    lo, hi = 0.0, 1.0
    if stretch:
        lums = [(0.3 * r + 0.59 * g + 0.11 * b) / 255 for r, g, b, a in im.getdata() if a]
        if lums:
            lo, hi = min(lums), max(lums) + 1e-6
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a or (r, g, b) in keepset:
                continue
            lum = ((0.3 * r + 0.59 * g + 0.11 * b) / 255 - lo) / (hi - lo)
            c = cols[max(0, min(len(cols) - 1, int(lum * len(cols))))]
            px[x, y] = c + (a,)
    return im


def tone_costumes(sprite, ramp, prefix, keep=(), names=None, suffix=''):
    """[(name, 4x image, rcx, rcy)] for a pack sprite's costumes, re-toned."""
    out = []
    for c in st().costumes(sprite):
        n = c['name']
        if names is not None and not any(n.startswith(k) for k in names):
            continue
        if suffix:
            if not n.endswith(suffix):
                continue
            n = n[:-len(suffix)]
        elif n.endswith('_m') or n.endswith('_g'):
            continue
        im = tone(st().image(sprite, c['name']), ramp, keep, stretch=True)
        out.append((prefix + n, im, c['rotationCenterX'], c['rotationCenterY']))
    return out


def glitch_rows(im, seed, n=10, shift=6):
    """Offset a few random horizontal bands, like a corrupted scanline."""
    rng = random.Random(seed)
    out = im.copy()
    for _ in range(n):
        y = rng.randrange(im.height - 4)
        h = rng.randint(1, 4)
        dx = rng.randint(-shift, shift)
        band = im.crop((0, y, im.width, y + h))
        out.paste((0, 0, 0, 0), (0, y, im.width, y + h))
        out.paste(band, (dx, y))
        out.paste(band, (dx - im.width if dx > 0 else dx + im.width, y))
    return out


# ------------------------------------------------------------------ Chapter 5
def memory_atlas():
    atlas = Image.open(assets.pack_path('tilesets', 'sump_atlas_8x8.png')).convert('RGBA')
    return tone(atlas, ['purple1', 'purple2', 'purple3', 'white'], keep=('mag3', 'mag2'), stretch=True)


def hollow_sky():
    im = Image.new('RGBA', (240, 180), C('ink'))
    gradient(im, 0, 90, 'ink', 'night1')
    gradient(im, 90, 180, 'night1', 'night2')
    d = ImageDraw.Draw(im)
    rng = random.Random(55)
    for _ in range(26):
        x, y, s = rng.randrange(240), rng.randrange(170), rng.randint(2, 6)
        d.rectangle([x, y, x + s, y + s], outline=C(rng.choice(['purple2', 'purple3', 'mag2'])))
    for y in range(0, 180, 3):
        for x in range(0, 240, 2):
            if (x + y) % 7 == 0:
                im.putpixel((x, y), C('night2'))
    return im


def hollow_far():
    far = Image.open(assets.pack_path('backgrounds', 'neon_alley', 'far.png')).convert('RGBA')
    return glitch_rows(tone(far, ['ink', 'night1', 'night2', 'purple1'], stretch=True), 3, 12, 8)


def hollow_mid():
    mid = Image.open(assets.pack_path('backgrounds', 'sump', 'mid.png')).convert('RGBA')
    return glitch_rows(tone(mid, ['ink', 'night1', 'night2', 'purple1'], stretch=True), 9, 8, 5)


def possess():
    """Full-screen purple vignette for when Kuro has the controls."""
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    px = im.load()
    for y in range(180):
        for x in range(240):
            e = min(x, 239 - x, y, 179 - y)
            if e < 22 and (x + y) % (1 + e // 6) == 0:
                px[x, y] = C('purple2', 200 - e * 8)
            elif y % 4 == 0 and x % 3 == 0:
                px[x, y] = C('purple3', 40)
    return im


# ------------------------------------------------------------------ shared phasing blocks
def phase_block(state, holo=False):
    """8x8 block: state 'on', 'warn' or 'off'. Glitch (violet) or hologram (cyan)."""
    edge, fill, hi = ('cyan2', 'cyan1', 'cyan4') if holo else ('purple3', 'purple1', 'white')
    im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if state == 'off':
        for i in range(0, 8, 2):
            im.putpixel((i, 0), C(edge, 120))
            im.putpixel((i, 7), C(edge, 120))
        return im
    a = 255 if state == 'on' else 150
    d.rectangle([0, 0, 7, 7], fill=C(fill, a), outline=C(edge, a))
    d.line([1, 1, 6, 1], fill=C(hi, a))
    for y in (3, 5):
        d.line([1, y, 6, y], fill=C(edge, a // 2))
    if state == 'warn':
        for (x, y) in ((2, 2), (5, 4), (3, 6)):
            im.putpixel((x, y), (0, 0, 0, 0))
    return im


# ------------------------------------------------------------------ Chapter 6
SHELL_MAP = {'cyan1': 'red1', 'cyan2': 'red2', 'cyan3': 'red3', 'cyan4': 'orange'}


def academy_atlas():
    atlas = Image.open(assets.pack_path('tilesets', 'tenshu_atlas_8x8.png')).convert('RGBA')
    return tone(atlas, ['night1', 'brown', 'red1', 'red2', 'orange', 'yellow'], keep=('gold',), stretch=True)


def academy_sky():
    im = Image.new('RGBA', (240, 180), C('ink'))
    gradient(im, 0, 80, 'ink', 'night1')
    gradient(im, 80, 180, 'night1', 'red1')
    d = ImageDraw.Draw(im)
    for x in (20, 80, 140, 200):
        d.line([x, 0, x, 10], fill=C('brown'))
        d.ellipse([x - 5, 10, x + 5, 22], fill=C('red2'), outline=C('red1'))
        d.line([x - 4, 16, x + 4, 16], fill=C('orange'))
    return im


def academy_far():
    """A shoji screen wall with trainee silhouettes behind the paper."""
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 70, 239, 160], fill=C('brown'))
    for x in range(0, 240, 30):
        d.rectangle([x + 2, 74, x + 27, 156], fill=C('orange', 60))
        for gx in range(x + 2, x + 28, 8):
            d.line([gx, 74, gx, 156], fill=C('brown'))
        for gy in range(74, 157, 12):
            d.line([x + 2, gy, x + 27, gy], fill=C('brown'))
    rng = random.Random(14)
    for x in range(15, 240, 60):
        h = rng.randint(30, 38)
        top = 150 - h
        d.ellipse([x - 3, top, x + 3, top + 6], fill=C('red1', 200))
        d.rectangle([x - 3, top + 6, x + 3, 150], fill=C('red1', 200))
        d.line([x + 3, top + 10, x + 14, top + 2], fill=C('red1', 200))
    d.rectangle([0, 160, 239, 179], fill=C('night1'))
    return im


def academy_mid():
    """Lacquered pillars with hanging banners, every 120 px."""
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in (30, 150):
        d.rectangle([x, 0, x + 8, 179], fill=C('red1'))
        d.line([x + 1, 0, x + 1, 179], fill=C('red2'))
        d.rectangle([x - 2, 40, x + 10, 44], fill=C('gold'))
        bx = x + 30
        d.rectangle([bx, 6, bx + 16, 70], fill=C('night2'), outline=C('gold'))
        d.line([bx + 8, 14, bx + 8, 40], fill=C('white'), width=2)
        d.line([bx + 3, 24, bx + 13, 24], fill=C('white'))
        d.line([bx + 4, 48, bx + 12, 58], fill=C('red3'), width=2)
        d.line([bx + 12, 48, bx + 4, 58], fill=C('red3'), width=2)
        d.polygon([(bx, 70), (bx + 8, 64), (bx + 16, 70)], fill=C('ink'))
    return im


def dummy():
    """Training dummy, 14x26."""
    im = Image.new('RGBA', (14, 26), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([6, 8, 7, 25], fill=C('brown'))
    d.rectangle([1, 10, 12, 12], fill=C('brown'))
    d.ellipse([3, 0, 10, 8], fill=C('gold'), outline=C('brown'))
    d.rectangle([4, 13, 9, 20], fill=C('gold'), outline=C('brown'))
    d.line([4, 16, 9, 16], fill=C('red2'))
    d.rectangle([3, 24, 10, 25], fill=C('slate2'))
    return im
