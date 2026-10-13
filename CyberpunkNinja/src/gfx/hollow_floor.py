"""
Chapter 5 (Hollow Floor) art. Hollow Floor is built from Kuro's memories, so
most of it is pack art re-toned into a violet "memory" ramp by luminance, with
glitches flickering behind the rooms. The phasing block is shared with the
Academy (glitch blocks here, training holograms there).


All functions return 1x art-pixel images unless noted.
"""
import random

from PIL import Image, ImageDraw

import assets
from assets import PALETTE as P
from gfx.util import C, gradient, st


MEMORY_RAMP = ['ink', 'night1', 'night2', 'purple1', 'purple2', 'purple3', 'white']


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


# ------------------------------------------------------------------ tiles and backdrops
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


# ------------------------------------------------------------------ phasing blocks (shared with the Academy)
def phase_block(state, holo=False):
    """8x8 block: state 'on', 'warn' (about to vanish), 'soon' (about to appear) or 'off'.
    Glitch (violet) or hologram (cyan). 'off' is only a faint dotted outline so it reads as empty."""
    edge, fill, hi = ('cyan2', 'cyan1', 'cyan4') if holo else ('purple3', 'purple1', 'white')
    im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if state == 'off':
        for i in range(0, 8, 3):
            for p in ((i, 0), (i, 7), (0, i), (7, i)):
                im.putpixel(p, C(edge, 90))
        return im
    if state == 'soon':
        d.rectangle([0, 0, 7, 7], fill=C(fill, 50), outline=C(hi, 230))
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


# ------------------------------------------------------------------ background glitches
def glitch_piece(i):
    """Torn scanlines, RGB-split blocks and corrupted glyph rows that flicker behind
    Hollow Floor's rooms. Returns a 1x image (center anchored)."""
    rng = random.Random(900 + i)
    kind = i % 4
    if kind == 0:
        # a horizontal tear: stacked scanlines sliding apart
        w, h = rng.randint(90, 160), rng.randint(6, 12)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for y in range(0, h, 2):
            x0 = rng.randint(0, w // 4)
            x1 = rng.randint(w * 3 // 4, w - 1)
            d.line([x0, y, x1, y], fill=C(rng.choice(('cyan2', 'purple2', 'mag2', 'indigo')), 200))
    elif kind == 1:
        # an RGB-split block
        w, h = rng.randint(20, 46), rng.randint(14, 30)
        im = Image.new('RGBA', (w + 6, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w - 1, h - 1], fill=C('mag2', 150))
        d.rectangle([6, 0, w + 5, h - 1], fill=C('cyan2', 150))
        d.rectangle([6, 0, w - 1, h - 1], fill=C('purple3', 170))
        for y in range(1, h, 3):
            d.line([0, y, w + 5, y], fill=C('night1', 120))
    elif kind == 2:
        # a row of corrupted glyph blocks
        w, h = rng.randint(60, 110), 7
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        px = im.load()
        x = 0
        while x < w - 4:
            col = C(rng.choice(('cyan3', 'purple3', 'mag3', 'white')), 220)
            for yy in range(5):
                for xx in range(3):
                    if rng.random() < 0.55:
                        px[x + xx, 1 + yy] = col
            x += rng.randint(4, 7)
    else:
        # a dithered dead-pixel patch
        w, h = rng.randint(30, 60), rng.randint(20, 40)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        px = im.load()
        for y in range(h):
            for x in range(w):
                if (x + y) % 2 == 0 and rng.random() < 0.6 - abs(y - h / 2) / h:
                    px[x, y] = C(rng.choice(('purple1', 'purple2', 'indigo', 'cyan1')), 190)
    return im
