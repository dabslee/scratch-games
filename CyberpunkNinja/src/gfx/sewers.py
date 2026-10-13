"""
Chapter 3 (The Sewers) art: the stained tileset, glowing runoff, the tunnel
backdrops, falling sludge and the rising tide, the Drainlings and Dobunushi
(built on the hand-edited base in art/characters/ when it's there).


All functions return 1x art-pixel images unless noted.
"""
import math
import os
import random

from PIL import Image, ImageDraw

import assets
from assets import PALETTE as P
from gfx.util import C, recolor


# ------------------------------------------------------------------ tiles and backdrops
def gradient(im, y0, y1, a, b):
    """Vertical dithered blend between two palette colors over rows y0..y1."""
    px = im.load()
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        for x in range(im.width):
            px[x, y] = C(b) if ((x * 5 + y * 3) % 8) / 8 < t else C(a)


def sewer_atlas():
    """The Sump's tiles, stained: violet stone to wet slate, moss and runoff for the accents."""
    atlas = Image.open(assets.pack_path('tilesets', 'sump_atlas_8x8.png')).convert('RGBA')
    return recolor(atlas, {'night2': 'slate1', 'night1': 'night2', 'slate1': 'slate2', 'slate3': 'green2',
                           'cyan1': 'green1', 'cyan3': 'lime', 'cyan4': 'lime', 'mag3': 'lime'})


def toxic_tile(surface, frame=0, col=0):
    """8x8 cell of glowing Kanshi runoff; `surface` draws the bright top edge. The two
    frames bubble: specks drift up and bubbles swell and pop along the surface."""
    im = Image.new('RGBA', (8, 8), C('green1'))
    d = ImageDraw.Draw(im)
    for y in range(8):
        for x in range(8):
            if (x * 3 + (y + frame) * 5) % 9 == 0:
                im.putpixel((x, y), C('green2'))
    if surface:
        d.line([0, 0, 7, 0], fill=C('lime'))
        d.line([0, 1, 7, 1], fill=C('green2'))
        for x in ((1 + frame * 3) % 8, (5 + frame * 3) % 8):
            im.putpixel((x, 0), C('white'))
        # a bubble every few cells, swelling on one frame and bursting on the other
        bx = (col * 5 + 2) % 6 + 1
        if (col + frame) % 3 == 0:
            for q in ((bx, 1), (bx - 1, 2), (bx + 1, 2), (bx, 3)):
                im.putpixel(q, C('lime'))
            im.putpixel((bx, 2), C('green1'))
        elif (col + frame) % 3 == 1:
            im.putpixel((bx, 2), C('lime'))
    im.putpixel(((2 + frame * 5) % 8, 4 - frame), C('lime'))
    return im


def sewer_sky():
    """Back wall of the tunnel: dark brick, grime streaks, a faint green glow below."""
    im = Image.new('RGBA', (240, 180), C('ink'))
    gradient(im, 0, 120, 'ink', 'night1')
    gradient(im, 120, 180, 'night1', 'green1')
    d = ImageDraw.Draw(im)
    for y in range(4, 170, 7):
        off = 0 if (y // 7) % 2 else 6
        d.line([0, y, 239, y], fill=C('slate1'))
        for x in range(off, 240, 12):
            d.line([x, y, x, y + 6], fill=C('slate1'))
    rng = random.Random(21)
    for _ in range(18):
        x = rng.randrange(240)
        y = rng.randrange(20, 120)
        ln = rng.randint(10, 40)
        d.line([x, y, x, y + ln], fill=C('green1'))
    return im


def sewer_far():
    """Receding stone arches of the main culvert, with the runoff channel below."""
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in (0, 80, 160):
        d.rectangle([x, 26, x + 9, 179], fill=C('night2'))
        d.line([x + 9, 26, x + 9, 179], fill=C('slate1'))
        for w, col in ((5, 'night2'), (1, 'slate2')):
            d.arc([x + 6, 40, x + 86, 150], 180, 360, fill=C(col), width=w)
        for y in range(30, 170, 9):
            d.line([x, y, x + 8, y], fill=C('night1'))
    d.rectangle([0, 0, 239, 26], fill=C('night1'))
    d.line([0, 26, 239, 26], fill=C('slate2'))
    d.rectangle([0, 160, 239, 179], fill=C('green1'))
    for k in range(0, 240, 7):
        d.point((k, 160), fill=C('green2'))
    return im


def sewer_mid():
    """Big outflow pipes, valve wheels and dripping sludge, every 120 px."""
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in (10, 130):
        # vertical pipe with bands
        d.rectangle([x, 0, x + 12, 179], fill=C('slate1'))
        d.line([x + 2, 0, x + 2, 179], fill=C('slate2'))
        for y in range(10, 180, 34):
            d.rectangle([x - 1, y, x + 13, y + 3], fill=C('slate2'))
        # a horizontal outflow pipe with a broken mouth leaking runoff
        d.rectangle([x + 12, 60, x + 70, 72], fill=C('slate1'))
        d.line([x + 12, 62, x + 70, 62], fill=C('slate2'))
        d.ellipse([x + 64, 58, x + 76, 74], fill=C('ink'), outline=C('slate2'))
        for k, col in ((0, 'green2'), (2, 'lime'), (4, 'green2')):
            d.line([x + 68 + k, 70, x + 68 + k, 179], fill=C(col, 150))
        # valve wheel
        cx0, cy0 = x + 40, 110
        d.ellipse([cx0 - 7, cy0 - 7, cx0 + 7, cy0 + 7], outline=C('red1'))
        d.line([cx0 - 7, cy0, cx0 + 7, cy0], fill=C('red1'))
        d.line([cx0, cy0 - 7, cx0, cy0 + 7], fill=C('red1'))
    return im


def sludge_fall(frame):
    """16x16 tileable column of falling runoff; frames scroll downward."""
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = im.load()
    for x in range(4, 12):
        for y in range(16):
            yy = (y - frame * 2) % 16
            edge = x in (4, 11)
            col = 'green1' if edge else ('lime' if (x * 7 + yy * 3) % 11 == 0 else 'green2')
            px[x, y] = C(col, 170 if edge else 220)
    for y in range(16):
        if (y + frame * 2) % 5 == 0:
            px[3 if y % 2 else 12, y] = C('green2', 160)
    return im


def tide_surface(frame):
    """The rising sludge: a wavy lit surface over a deep body (top-center anchored)."""
    w, h = 244, 200
    im = Image.new('RGBA', (w, h), C('green1', 215))
    px = im.load()
    for x in range(w):
        top = int(2 + 2 * math.sin((x + frame * 3) * 0.12) + 1.2 * math.sin((x - frame * 2) * 0.31))
        for y in range(0, top + 1):
            px[x, y] = (0, 0, 0, 0)
        px[x, top + 1] = C('lime')
        px[x, top + 2] = C('green2')
        for y in range(top + 3, h):
            if (x * 3 + y * 7 + frame) % 23 == 0:
                px[x, y] = C('green2', 215)
    for k in range(6):
        bx = (k * 41 + frame * 9) % w
        by = 10 + (k * 13 + frame * 5) % 40
        px[bx, by] = C('lime')
    return im


# ------------------------------------------------------------------ Drainlings
DRAIN_MAP = {
    # a rotting, irradiated body: ashen gray skin, rags, a rusted pipe
    'red2': 'slate3', 'red1': 'lime', 'yellow': 'slate3', 'skin2': 'slate3', 'skin1': 'slate2',
    'night3': 'night2', 'mag1': 'slate1', 'gold': 'brown', 'slate1': 'night1', 'slate2': 'slate1',
    'steel': 'skin1', 'slate3': 'brown', 'mag2': 'green2', 'mag3': 'lime',
}


def drainling_frame(im1x, seed):
    """A Hannya Boy turned sewer zombie: no mask or horns, ashen skin, radioactive pustules."""
    src = im1x.convert('RGBA')
    sp = src.load()
    w, h = src.size
    white, ink = P['white'], P['ink']

    def colored(p):
        return p[3] and p[:3] not in (white, ink)
    # the mask's horns are white pixels touching nothing but outline: cut them and their outline
    horn = set()
    for y in range(h):
        for x in range(w):
            if sp[x, y][3] and sp[x, y][:3] == white:
                nb = [sp[x + dx, y + dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                      if 0 <= x + dx < w and 0 <= y + dy < h and (dx or dy)]
                if not any(colored(p) for p in nb):
                    horn.add((x, y))
    for x, y in horn:
        sp[x, y] = (0, 0, 0, 0)
    for y in range(h):
        for x in range(w):
            if sp[x, y][3] and sp[x, y][:3] == ink:
                nb = [sp[x + dx, y + dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                      if 0 <= x + dx < w and 0 <= y + dy < h and (dx or dy)]
                if not any(colored(p) or (p[3] and p[:3] == white) for p in nb):
                    sp[x, y] = (0, 0, 0, 0)
    im = recolor(src, dict(DRAIN_MAP, white='slate1'))
    px = im.load()
    rng = random.Random(11)
    skin, rag = P['slate3'], P['night2']

    def inside(x, y):
        return all(0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3] and px[x + dx, y + dy][:3] != ink
                   for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)))
    cand = [(x, y) for y in range(h - 1) for x in range(w - 1)
            if px[x, y][3] and px[x, y][:3] in (skin, rag, P['slate1'], P['night1']) and inside(x, y)]
    # pustules: glowing lime and yellow bulbs scattered over skin and rags
    taken = []
    for x, y in rng.sample(cand, len(cand)):
        if len(taken) >= 9:
            break
        if any(abs(x - tx) < 3 and abs(y - ty) < 3 for tx, ty in taken):
            continue
        taken.append((x, y))
        big = len(taken) % 3 != 0
        px[x, y] = C('yellow') if len(taken) % 4 == 1 else C('lime')
        if big:
            for dx, dy, col in ((1, 0, 'lime'), (0, 1, 'green2'), (1, 1, 'green1')):
                if inside(x + dx, y + dy) or px[x + dx, y + dy][3]:
                    px[x + dx, y + dy] = C(col)
    # runoff dripping off the lower edges
    greens = {P['lime'], P['green2'], P['night2'], P['slate1']}
    spots = [(x, y) for y in range(h - 1) for x in range(w)
             if px[x, y][3] and px[x, y][:3] in greens and not px[x, y + 1][3]]
    rng = random.Random(seed)
    for x, y in rng.sample(spots, min(3, len(spots))):
        for k in range(1, rng.randint(2, 4)):
            if y + k < h and not px[x, y + k][3]:
                px[x, y + k] = C('green2' if k < 2 else 'lime')
    return im


def spit(frame):
    im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([1, 1, 6, 6], fill=C('green2'), outline=C('green1'))
    d.point([(3 + frame, 2), (2, 4)], fill=C('lime'))
    return im


# ------------------------------------------------------------------ Dobunushi
DOBU_W, DOBU_H = 104, 72


def dobu_body(state='idle', frame=0):
    """The fused mass, 104x72, anchored bottom-center. state: idle, open, spew, dead.
    Built on the hand-edited base in art/characters/ when it's there."""
    if os.path.exists(DOBU_BASE):
        return dobu_states(Image.open(DOBU_BASE).convert('RGBA'), state, frame)
    im = Image.new('RGBA', (DOBU_W, DOBU_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(7)
    breathe = (frame % 2)
    # the mound: overlapping lumps of fused bodies
    lumps = [(52, 46, 46, 30), (30, 52, 26, 22), (76, 52, 26, 22), (52, 30, 32, 22), (16, 62, 18, 12), (88, 62, 18, 12)]
    for cx0, cy0, rx, ry in lumps:
        ry2 = ry + (breathe if cy0 < 40 else 0)
        d.ellipse([cx0 - rx, cy0 - ry2, cx0 + rx, cy0 + ry], fill=C('green1'), outline=C('ink'))
    for cx0, cy0, rx, ry in lumps:
        d.arc([cx0 - rx + 3, cy0 - ry + 3, cx0 + rx - 3, cy0 + ry - 3], 200, 320, fill=C('green2'))
    # fused faces: old Hannya masks and Drainling heads half sunk into the flesh
    for (fx, fy, mask) in ((26, 46, True), (78, 44, False), (40, 62, False), (66, 60, True), (52, 24, False)):
        if mask:
            d.rectangle([fx - 5, fy - 4, fx + 5, fy + 5], fill=C('red1'), outline=C('ink'))
            d.polygon([(fx - 5, fy - 4), (fx - 7, fy - 9), (fx - 3, fy - 4)], fill=C('steel'))
            d.polygon([(fx + 5, fy - 4), (fx + 7, fy - 9), (fx + 3, fy - 4)], fill=C('steel'))
            d.line([fx - 3, fy - 1, fx - 1, fy - 1], fill=C('yellow'))
            d.line([fx + 1, fy - 1, fx + 3, fy - 1], fill=C('yellow'))
            d.line([fx - 3, fy + 3, fx + 3, fy + 3], fill=C('white'))
        else:
            d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=C('green2'), outline=C('ink'))
            d.point([(fx - 2, fy - 1), (fx + 2, fy - 1)], fill=C('lime'))
            d.line([fx - 2, fy + 2, fx + 2, fy + 2], fill=C('ink'))
    # extra eyes that blink in turn
    for i, (ex, ey) in enumerate(((36, 34), (68, 32), (18, 56), (86, 56), (58, 50))):
        if (i + frame) % 4:
            d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=C('lime'))
            d.point((ex, ey), fill=C('ink'))
    # the broken Kanshi outflow pipe it grew around
    d.rectangle([44, 0, 60, 18], fill=C('slate2'), outline=C('ink'))
    d.line([46, 2, 46, 16], fill=C('slate3'))
    d.rectangle([42, 0, 62, 4], fill=C('slate3'), outline=C('ink'))
    d.text((47, 7), 'K', fill=C('red2'))
    for k in range(3):
        d.line([50 + k * 2, 18, 50 + k * 2, 22 + (k + frame) % 3], fill=C('lime'))
    dobu_states(im, state, frame, base=False)
    for _ in range(14):
        x, y = rng.randrange(8, 96), rng.randrange(20, 70)
        if im.getpixel((x, y))[3]:
            im.putpixel((x, y), C('lime' if rng.random() < 0.3 else 'green2'))
    return im


DOBU_BASE = assets.art_path('characters', 'dobunushi_base.png')
DOBU_BLINK = (86, 56)  # the eye that closes on the second idle frame


def dobu_states(im, state, frame, base=True):
    """The open core, spew mouth and death dissolve, drawn over a finished body."""
    im = im.copy() if base else im
    d = ImageDraw.Draw(im)
    if base and frame % 2:
        ex, ey = DOBU_BLINK
        px = im.load()
        for y in range(ey - 2, ey + 3):
            for x in range(ex - 2, ex + 3):
                if px[x, y][3] and px[x, y][:3] in (C('lime'), C('ink')):
                    px[x, y] = C('green1')
        d.line([ex - 1, ey, ex + 1, ey], fill=C('ink'))
    if state == 'open':
        # the mass parts around a glowing core
        d.ellipse([34, 30, 70, 64], fill=C('night1'), outline=C('green1'))
        d.ellipse([42, 36, 62, 58], fill=C('green2'))
        d.ellipse([46, 40, 58, 54], fill=C('lime'))
        d.ellipse([49, 43, 55, 51], fill=C('white'))
        for k in range(6):
            a = math.radians(k * 60 + frame * 20)
            d.line([52 + math.cos(a) * 12, 47 + math.sin(a) * 12, 52 + math.cos(a) * 18, 47 + math.sin(a) * 18],
                   fill=C('green1'), width=2)
    elif state == 'spew':
        d.ellipse([40, 40, 64, 62], fill=C('ink'), outline=C('green1'))
        d.ellipse([44, 46, 60, 62], fill=C('green2'))
        for x in range(42, 64, 3):
            d.polygon([(x, 40), (x + 2, 40), (x + 1, 44)], fill=C('white'))
    if state == 'dead':
        px = im.load()
        for y in range(DOBU_H):
            for x in range(DOBU_W):
                if px[x, y][3] and (x + y * 3 + frame) % (5 - min(4, frame)) == 0:
                    px[x, y] = (0, 0, 0, 0)
    return im


ARM_L = 76


def dobu_arm(frame=0, stump=False):
    """A long, clawed limb pointing right; the shoulder (rotation center) is the left end."""
    w = 20 if stump else ARM_L + 10
    im = Image.new('RGBA', (w, 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    end = w - 4 if stump else ARM_L - 4
    pts_top, pts_bot = [], []
    for x in range(0, end + 1):
        wob = 1.5 * math.sin((x + frame * 7) * 0.25)
        th = 5.5 - x / 26
        pts_top.append((x, 11 - th + wob))
        pts_bot.append((x, 11 + th + wob))
    d.polygon(pts_top + pts_bot[::-1], fill=C('green1'), outline=C('ink'))
    d.line(pts_top[2:-2], fill=C('green2'))
    for x in range(5, end - 2, 8):
        wob = 1.5 * math.sin((x + frame * 7) * 0.25)
        d.line([x, 9 + wob, x + 1, 13 + wob], fill=C('ink'))
        d.point((x + 3, 12 + wob), fill=C('lime'))
    if stump:
        d.ellipse([end - 4, 6, end + 3, 16], fill=C('red1'), outline=C('ink'))
        d.point([(end, 10), (end - 1, 12)], fill=C('lime'))
        return im
    # the hand: a fused fist of fingers and an old pipe clamp
    hx = ARM_L
    d.ellipse([hx - 8, 3, hx + 6, 19], fill=C('green1'), outline=C('ink'))
    d.rectangle([hx - 9, 7, hx - 6, 15], fill=C('slate2'), outline=C('ink'))
    for k, dy in enumerate((-6, -1, 4)):
        d.polygon([(hx + 3, 11 + dy), (hx + 9, 9 + dy + k), (hx + 4, 13 + dy)], fill=C('steel'), outline=C('ink'))
    d.point([(hx - 2, 8), (hx - 1, 14)], fill=C('lime'))
    return im
