"""
Shared helpers for the generated art: the asset pack's starter project, palette
colors by name, palette swaps, ordered-dither gradients and hand-placed pixel grids.

Everything the build draws uses the pack's 34-color palette (assets.PALETTE), so a
recolor is just a swap of palette names.
"""
from PIL import Image

import assets
from assets import PALETTE as P


ST = None


def st():
    global ST
    if ST is None:
        ST = assets.starter()
    return ST


def C(name, a=255):
    return P[name] + (a,)


# ------------------------------------------------------------------ recolors
def recolor(im, mapping):
    """Swap palette colors by name: {'night1': 'purple1', ...}."""
    lut = {P[a]: P[b] for a, b in mapping.items()}
    im = im.convert('RGBA').copy()
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in lut:
                nr, ng, nb = lut[(r, g, b)]
                px[x, y] = (nr, ng, nb, a)
    return im


def recolor_costumes(sprite, mapping, prefix=''):
    """[(name, 4x image, rcx, rcy)] for every costume of a pack sprite, recolored."""
    out = []
    for c in st().costumes(sprite):
        im = recolor(st().image(sprite, c['name']), mapping)
        out.append((prefix + c['name'], im, c['rotationCenterX'], c['rotationCenterY']))
    return out


# ------------------------------------------------------------------ backgrounds
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def gradient(im, y0, y1, c0, c1):
    """Two-color ordered-dither gradient between rows y0..y1."""
    px = im.load()
    for y in range(y0, y1):
        f = (y - y0) / max(1, (y1 - y0 - 1))
        for x in range(im.width):
            px[x, y] = C(c1) if f * 16 > BAYER[y % 4][x % 4] else C(c0)


# ------------------------------------------------------------------ hand-placed pixel grids
KEY = {'k': 'ink', 'n': 'night1', 'N': 'night2', 'w': 'white', 's': 'steel', 'S': 'slate3', 'D': 'slate2',
       '1': 'skin3', '2': 'skin2', '3': 'skin1', 'b': 'brown', 'l': 'lime', 'm': 'mag3', 'g': 'green2', 'G': 'green1',
       'r': 'red2', 'R': 'red1', 'o': 'gold', 'c': 'cyan4', 'p': 'purple3', 'P': 'purple2', 'y': 'yellow'}


def pix_grid(rows, w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    top = h - len(rows)
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != '.':
                im.putpixel((i, top + j), C(KEY[ch]))
    return im
