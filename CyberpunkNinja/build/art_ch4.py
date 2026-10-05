"""
Chapter 4 (Monorail Ascent) art. The pack has nothing for the monorail, so
this draws it in the pack's palette: a train-livery recolor of the alley
tiles, a dusk sky above the cloud layer, rail pylons that rush past, wind
streaks, trackside signal posts, and Raijin, the armored locomotive.

All functions return 1x art-pixel images unless noted.
"""
import math
import random

from PIL import Image, ImageDraw

import assets
from assets import PALETTE as P
from art_ch2 import recolor, gradient, st  # noqa: F401


def C(name, a=255):
    return P[name] + (a,)


# Kanshi rail livery: pale steel cars with an orange stripe.
TRAIN_MAP = {
    'slate1': 'slate2', 'slate2': 'slate3', 'slate3': 'steel', 'steel': 'white',
    'cyan1': 'red1', 'cyan3': 'orange', 'cyan4': 'yellow', 'mag3': 'orange', 'yellow': 'orange',
}
# Rail Guards (Hannya Boy) and Rail Gunners (Croupier) in Kanshi security colors.
GUARD_MAP = {
    'red1': 'slate1', 'red2': 'slate2', 'red3': 'steel', 'mag1': 'red1', 'mag2': 'orange', 'mag3': 'yellow',
    'night3': 'slate2', 'indigo': 'slate3',
}
GUNNER_MAP = {
    'red1': 'night2', 'red2': 'indigo', 'red3': 'slate3', 'white': 'orange',
    'mag1': 'night2', 'mag3': 'orange', 'slate1': 'slate1', 'gold': 'yellow',
}


def rail_atlas():
    atlas = Image.open(assets.pack_path('tilesets', 'alley_atlas_8x8.png')).convert('RGBA')
    return recolor(atlas, TRAIN_MAP)


# ------------------------------------------------------------------ backgrounds
def sky():
    """Dusk above the cloud layer, 240x180."""
    im = Image.new('RGBA', (240, 180), C('ink'))
    gradient(im, 0, 50, 'ink', 'night2')
    gradient(im, 50, 100, 'night2', 'purple1')
    gradient(im, 100, 140, 'purple1', 'mag1')
    gradient(im, 140, 180, 'mag1', 'red2')
    rng = random.Random(41)
    for _ in range(40):
        x, y = rng.randrange(240), rng.randrange(0, 70)
        im.putpixel((x, y), C(rng.choice(['white', 'steel', 'purple3'])))
    # a low, hazy sun sinking into the clouds (tiles every 240 px)
    d = ImageDraw.Draw(im)
    d.ellipse([150, 128, 190, 168], fill=C('orange'))
    for y in range(132, 168, 4):
        d.line([148, y, 192, y], fill=C('red2'))
    return im


def far():
    """Cloud sea below with distant tower tops poking through, 240x180."""
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(8)
    for x0, w, h in ((10, 10, 40), (60, 6, 24), (96, 14, 52), (170, 8, 30), (210, 12, 44)):
        d.rectangle([x0, 150 - h, x0 + w, 160], fill=C('night2'))
        d.line([x0 + w // 2, 150 - h - 6, x0 + w // 2, 150 - h], fill=C('night2'))
        im.putpixel((x0 + w // 2, 150 - h - 6), C('red3'))
        for k in range(3):
            im.putpixel((x0 + 2 + rng.randrange(max(1, w - 3)), 150 - h + 4 + rng.randrange(h - 6)), C('orange'))
    # cloud banks, drawn as overlapping ellipses that wrap at 240
    for row, (yc, col, n) in enumerate(((150, 'purple2', 14), (160, 'purple3', 16), (170, 'mag4', 18))):
        for i in range(n):
            cx = (i * 240 // n + row * 7) % 240
            r = 10 + (i * 7 + row * 3) % 8
            for dx in (-240, 0, 240):
                d.ellipse([cx + dx - r, yc - r // 2, cx + dx + r, yc + r // 2 + 12], fill=C(col))
    d.rectangle([0, 172, 239, 179], fill=C('mag4'))
    return im


def mid():
    """Rail pylons and catenary, repeating every 80 px so they rush past."""
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x0 in (20, 100, 180):
        d.rectangle([x0, 60, x0 + 4, 180], fill=C('night1'))
        d.line([x0 + 5, 60, x0 + 5, 180], fill=C('night3'))
        d.rectangle([x0 - 14, 58, x0 + 18, 62], fill=C('night1'))
        d.point([(x0 - 12, 63), (x0 + 16, 63)], fill=C('red3'))
        for y in range(70, 180, 14):
            d.line([x0, y, x0 + 4, y + 10], fill=C('night2'))
    for y, sag in ((64, 4), (70, 5)):
        for x in range(240):
            k = (x - 22) % 80
            yy = y + int(sag * math.sin(math.pi * k / 80))
            im.putpixel((x, yy), C('night2'))
    return im


def wind(frame):
    """Full-screen wind streaks, 4 frames sliding left."""
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    rng = random.Random(5)
    for _ in range(26):
        x0, y = rng.randrange(240), rng.randrange(180)
        ln = rng.randint(8, 22)
        col = rng.choice(['white', 'steel', 'purple3'])
        x0 = (x0 - frame * 15) % 240
        for k in range(ln):
            a = 140 if k < ln // 2 else 80
            im.putpixel(((x0 + k) % 240, y), C(col, a))
    return im


# ------------------------------------------------------------------ hazards and props
def post():
    """Trackside signal post: a steel mast with a red lamp, 10x22."""
    im = Image.new('RGBA', (10, 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 6, 21], fill=C('slate3'))
    d.line([4, 4, 4, 21], fill=C('steel'))
    d.rectangle([1, 0, 9, 6], fill=C('slate1'), outline=C('slate3'))
    d.ellipse([3, 1, 7, 5], fill=C('red3'))
    im.putpixel((4, 2), C('white'))
    d.rectangle([2, 19, 8, 21], fill=C('orange'))
    return im


def warn(frame):
    """Incoming-post warning chevron for the right screen edge, 14x14."""
    im = Image.new('RGBA', (14, 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = 'yellow' if frame % 2 == 0 else 'orange'
    d.polygon([(7, 0), (14, 13), (0, 13)], fill=C(col), outline=C('ink'))
    d.rectangle([6, 4, 7, 9], fill=C('ink'))
    d.rectangle([6, 11, 7, 12], fill=C('ink'))
    return im


def shell(frame, returned=False):
    im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    outer, inner = ('cyan2', 'cyan4') if returned else ('red2', 'yellow')
    d.ellipse([1, 1, 6, 6], fill=C(outer))
    d.ellipse([2, 2, 4 + frame % 2, 4 + frame % 2], fill=C(inner))
    return im


def seat():
    """Dining-car bench, 18x12."""
    im = Image.new('RGBA', (18, 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([1, 0, 4, 9], fill=C('red1'), outline=C('red2'))
    d.rectangle([1, 6, 16, 9], fill=C('red1'), outline=C('red2'))
    d.line([3, 10, 3, 11], fill=C('slate3'))
    d.line([14, 10, 14, 11], fill=C('slate3'))
    return im


def zap(live, frame):
    """Electrified roof section, 60x10 (warning sparks or a live arc)."""
    im = Image.new('RGBA', (60, 10), (0, 0, 0, 0))
    rng = random.Random(frame * 7 + (31 if live else 3))
    px = im.load()
    if not live:
        for _ in range(12):
            x, y = rng.randrange(60), rng.randrange(6, 10)
            px[x, y] = C(rng.choice(['yellow', 'orange']))
        for x in range(0, 60, 4):
            px[x, 9] = C('orange', 180)
        return im
    y = 7
    for x in range(60):
        y = max(1, min(9, y + rng.choice([-2, -1, 0, 1, 2])))
        px[x, y] = C('white')
        if y + 1 < 10:
            px[x, y + 1] = C('cyan3')
        if rng.random() < 0.15:
            px[x, max(0, y - 1)] = C('yellow')
    for x in range(60):
        px[x, 9] = C('cyan2')
    return im


def wreck_box():
    """Raijin's black box, 12x10."""
    im = Image.new('RGBA', (12, 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1, 11, 9], fill=C('orange'), outline=C('red1'))
    d.rectangle([3, 3, 8, 6], fill=C('ink'))
    d.point([(4, 4), (6, 4)], fill=C('cyan3'))
    return im


# ------------------------------------------------------------------ Raijin
RJ_W, RJ_H = 104, 96
RJ_CORE = (24, 70)      # reactor core centre (the costume anchor)
RJ_CUT = 81             # rows below this are hidden behind Hotaru's car


def raijin(state='idle', frame=0):
    """The armored locomotive, nose facing left. state: idle, fire, vent, hurt, dead."""
    im = Image.new('RGBA', (RJ_W, RJ_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    dark, body, hi = C('night1'), C('slate2'), C('slate3')
    # body and sloped nose
    d.polygon([(14, 46), (34, 22), (103, 22), (103, 92), (6, 92), (6, 60)], fill=body, outline=C('ink'))
    d.polygon([(16, 47), (34, 26), (40, 26), (22, 50)], fill=hi)
    d.rectangle([40, 30, 103, 34], fill=C('red2'))
    d.rectangle([40, 35, 103, 36], fill=C('orange'))
    # cab windows: the oni's eyes
    eye = C('red3') if (state != 'dead' and frame % 6 != 5) else C('red1')
    d.polygon([(26, 38), (36, 32), (40, 34), (30, 42)], fill=eye)
    d.polygon([(44, 32), (56, 32), (54, 38), (44, 38)], fill=eye)
    # brows / horns
    d.line([24, 34, 38, 26], fill=C('ink'), width=2)
    d.polygon([(46, 22), (50, 10), (54, 22)], fill=C('gold'))
    d.polygon([(66, 22), (72, 6), (76, 22)], fill=C('gold'))
    # turret cannon on the roof
    d.rectangle([60, 14, 84, 22], fill=dark, outline=C('slate3'))
    d.rectangle([44, 15, 60, 19], fill=dark)
    d.rectangle([42, 16, 44, 18], fill=C('slate3'))
    if state == 'fire':
        d.ellipse([34, 12, 44, 22], fill=C('yellow'))
        d.ellipse([37, 14, 42, 20], fill=C('white'))
    # pantograph frame
    d.line([88, 22, 82, 8], fill=C('steel'))
    d.line([82, 8, 96, 4], fill=C('steel'))
    d.line([96, 4, 100, 22], fill=C('steel'))
    # side panels, rivets and kanji-like plate
    for x in range(48, 100, 10):
        d.rectangle([x, 42, x + 7, 58], outline=hi)
    for x in range(44, 103, 6):
        d.point((x, 63), fill=hi)
    d.rectangle([70, 66, 92, 76], fill=dark, outline=C('gold'))
    d.line([74, 71, 88, 71], fill=C('gold'))
    d.line([81, 68, 81, 74], fill=C('gold'))
    # fanged grille below the nose
    d.rectangle([6, 78, 44, 92], fill=dark)
    for x in range(8, 44, 5):
        d.polygon([(x, 78), (x + 2, 84), (x + 4, 78)], fill=C('steel'))
    # wheels / bogie
    for wx in (52, 74, 94):
        d.ellipse([wx - 7, 84, wx + 7, 98], fill=C('ink'), outline=C('slate3'))
        d.point((wx, 91), fill=C('orange' if frame % 2 else 'yellow'))
    # the reactor core
    cx, cy = RJ_CORE
    if state in ('vent', 'hurt') or state == 'dead':
        glow = ['cyan3', 'cyan4'][frame % 2] if state != 'dead' else 'slate3'
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=C('ink'), outline=C('orange'))
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=C(glow))
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=C('white'))
        if state == 'vent':
            for k, (sx, sy) in enumerate(((cx - 12, cy - 14), (cx - 4, cy - 18), (cx + 6, cy - 15))):
                yy = sy - (frame % 3) * 2
                d.ellipse([sx - 3, yy - 3, sx + 3, yy + 3], fill=C('white', 150))
    else:
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=C('slate1'), outline=C('orange'))
        d.line([cx - 9, cy, cx + 9, cy], fill=C('ink'))
        d.line([cx, cy - 9, cx, cy + 9], fill=C('ink'))
        d.point([(cx - 4, cy - 4), (cx + 4, cy + 4)], fill=C('cyan2'))
    if state == 'dead':
        rng = random.Random(frame)
        for _ in range(30):
            x, y = rng.randrange(6, 103), rng.randrange(22, 92)
            if im.getpixel((x, y))[3]:
                im.putpixel((x, y), C(rng.choice(['ink', 'red1', 'orange'])))
    return im


def arm(frame):
    """Pantograph arm swung across the roof; anchored at the claw tip (left)."""
    im = Image.new('RGBA', (130, 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([10, 5, 129, 8], fill=C('slate3'), outline=C('slate1'))
    for x in range(14, 129, 10):
        d.line([x, 5, x + 5, 8], fill=C('slate1'))
    d.polygon([(0, 6), (10, 1), (12, 12), (2, 10)], fill=C('steel'), outline=C('ink'))
    d.point([(1, 7), (3, 4)], fill=C('white'))
    if frame % 2:
        d.point([(5, 0), (8, 13), (0, 3)], fill=C('cyan3'))
    else:
        d.point([(6, 13), (2, 1), (9, 0)], fill=C('yellow'))
    return im


def plow(frame):
    """Spiked rail plow Raijin drags across the roof in its ram, 44x14."""
    im = Image.new('RGBA', (44, 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(0, 13), (14, 2), (43, 2), (43, 13)], fill=C('slate2'), outline=C('ink'))
    d.rectangle([18, 4, 43, 6], fill=C('red2'))
    for x in range(4, 42, 6):
        d.polygon([(x, 13), (x + 3, 8), (x + 6, 13)], fill=C('steel'))
    for x in (8, 26, 40):
        d.point((x, 12), fill=C('yellow' if frame % 2 else 'orange'))
    return im
