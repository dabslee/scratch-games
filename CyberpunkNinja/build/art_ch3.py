"""
Chapter 3 (The Server Gardens) art. The pack ships the gardens tileset,
backgrounds, server racks and Mukuro himself; this adds the Garden Warden
palette swap, the cooling-mist columns, the mind pods and stone lanterns,
all in the pack's palette.

All functions return 1x art-pixel images unless noted.
"""
import math
import random

from PIL import Image, ImageDraw

from assets import PALETTE as P
from art_ch2 import recolor, st  # noqa: F401  (re-exported for build.py)


def C(name, a=255):
    return P[name] + (a,)


# Mukuro's black-and-red livery -> a white robe with a jade blade.
WARDEN_MAP = {
    'night1': 'slate2', 'night2': 'slate3', 'night3': 'steel', 'indigo': 'white',
    'red1': 'green1', 'red2': 'green2', 'red3': 'lime', 'slate1': 'night2', 'slate2': 'night3',
}

MIST_FRAMES = 8


def mist(frame):
    """16x16 tileable column of rising coolant mist; frames scroll upward."""
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    rng = random.Random(3)
    wisps = [(rng.uniform(1, 14), rng.uniform(0, 16), rng.choice(['cyan4', 'white', 'cyan3']),
              rng.randint(2, 5)) for _ in range(14)]
    shift = frame * 16 / MIST_FRAMES
    px = im.load()
    for x0, y0, col, ln in wisps:
        y = (y0 - shift) % 16
        sway = math.sin((y0 + frame) * 0.8) * 0.8
        for k in range(ln):
            yy = int(y + k) % 16
            xx = int(x0 + sway) % 16
            a = 150 if k == 0 else 90
            px[xx, yy] = C(col, a)
    # faint body of the column
    for y in range(16):
        for x in (2, 13):
            if (x + y + frame) % 3 == 0:
                px[x, y] = C('cyan2', 50)
    return im


def mist_cap():
    """Soft top of a mist column."""
    im = Image.new('RGBA', (16, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (x, y) in enumerate(((3, 5), (7, 3), (11, 5), (5, 1), (10, 2))):
        d.point((x, y), fill=C('cyan4', 120 - i * 15))
    return im


def pod(frame):
    """A mind pod: a glass cylinder holding a glowing engram, 14x30."""
    im = Image.new('RGBA', (14, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([1, 26, 12, 29], fill=C('slate1'), outline=C('slate2'))
    d.rectangle([2, 0, 11, 2], fill=C('slate1'), outline=C('slate2'))
    d.rectangle([2, 3, 11, 25], fill=C('green1', 200))
    d.line([2, 3, 2, 25], fill=C('cyan2', 220))
    d.line([11, 3, 11, 25], fill=C('slate3', 220))
    d.line([4, 4, 4, 22], fill=C('cyan4', 120))
    glow = ['purple2', 'purple3'][frame % 2]
    d.ellipse([4, 10, 9, 15], fill=C(glow))
    d.point([(6, 12), (7, 11)], fill=C('white'))
    for bx, by in ((5, 20 - 4 * frame), (8, 7 + 3 * frame), (6, 23)):
        d.point((bx, by), fill=C('cyan4', 200))
    d.point([(4, 27), (7, 27), (10, 27)], fill=C('green2' if frame else 'lime'))
    return im


def toro(frame):
    """Stone garden lantern (toro), 12x22, with a flickering light."""
    im = Image.new('RGBA', (12, 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(0, 6), (6, 1), (11, 6)], fill=C('slate3'), outline=C('slate2'))
    d.rectangle([2, 7, 9, 12], fill=C('slate2'))
    d.rectangle([4, 8, 7, 11], fill=C(['yellow', 'orange'][frame % 2]))
    d.rectangle([1, 13, 10, 14], fill=C('slate3'))
    d.rectangle([4, 15, 7, 19], fill=C('slate2'))
    d.rectangle([2, 20, 9, 21], fill=C('slate3'))
    d.point((6, 0), fill=C('slate3'))
    return im


def bonsai():
    """Small potted bonsai on a server plinth, 14x18."""
    im = Image.new('RGBA', (14, 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([3, 13, 10, 17], fill=C('slate1'), outline=C('slate2'))
    d.point([(5, 15), (8, 15)], fill=C('cyan3'))
    d.line([7, 13, 6, 9], fill=C('brown'))
    d.line([6, 9, 9, 6], fill=C('brown'))
    d.ellipse([1, 5, 7, 9], fill=C('green1'))
    d.ellipse([7, 2, 13, 6], fill=C('green1'))
    d.point([(3, 6), (9, 3), (11, 4)], fill=C('green2'))
    return im
