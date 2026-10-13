"""
Chapter 6 (The Physic Gardens) art. The pack ships the gardens tileset and
backgrounds; this adds the Garden Warden palette swap, the updraft columns and
greenhouse heat vents, the mind pods, stone lanterns and herb props, the
cloud-pruned trees, and the Harmacist (hand-drawn frames from art/characters/)
with her vials and poison clouds.


All functions return 1x art-pixel images unless noted.
"""
import math
import os
import random

from PIL import Image, ImageDraw

import assets
from assets import PALETTE as P
from gfx.util import C, pix_grid, recolor


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


def heat_vent(frame):
    """The Physic Gardens' greenhouse heat: warm shimmer instead of coolant mist."""
    return recolor(mist(frame), {'cyan4': 'yellow', 'white': 'white', 'cyan3': 'orange', 'cyan2': 'red3'})


# ------------------------------------------------------------------ props
def planter(frame):
    """Physic Gardens herb planter: a raised bed of medicinal plants, 16x24 (bottom-center)."""
    im = Image.new('RGBA', (16, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([1, 15, 14, 23], fill=C('brown'), outline=C('ink'))
    d.line([2, 16, 13, 16], fill=C('gold'))
    d.rectangle([3, 19, 12, 21], fill=C('night1'))
    sway = frame % 2
    for i, x in enumerate((3, 6, 9, 12)):
        top = 4 + (i * 5) % 6
        d.line([x, 15, x + (sway if i % 2 else -sway), top], fill=C('green2'))
        d.point([(x - 1, top + 3), (x + 1, top + 5), (x + (sway if i % 2 else -sway), top)], fill=C('lime'))
    d.point([(5, 7), (10, 9)], fill=C('mag4'))
    return im


def herbs():
    """A drying rack of herb bundles and jars, 14x30 (bottom-center)."""
    im = Image.new('RGBA', (14, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1, 29], fill=C('brown'))
    d.rectangle([12, 0, 13, 29], fill=C('brown'))
    for y in (2, 12):
        d.line([0, y, 13, y], fill=C('brown'))
        for x in (3, 7, 10):
            d.line([x, y + 1, x, y + 2], fill=C('gold'))
            d.polygon([(x - 1, y + 3), (x + 1, y + 3), (x, y + 8)], fill=C('green1' if x != 7 else 'green2'))
    d.line([0, 22, 13, 22], fill=C('brown'))
    for x, col in ((2, 'lime'), (6, 'mag3'), (10, 'green2')):
        d.rectangle([x, 23, x + 2, 28], fill=C(col), outline=C('slate2'))
    return im


def price_board(frame):
    """The Dispensary's price board, 76x30 (top-center)."""
    im = Image.new('RGBA', (76, 30), C('ink'))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 75, 29], outline=C('green2'))
    d.line([0, 9, 75, 9], fill=C('green1'))
    f = assets.Font(False)
    f.draw(im, 3, 1, 'KANSHI CLEAR', P['lime'])
    f.draw(im, 3, 11, 'COST    4 CR', P['steel'])
    f.draw(im, 3, 20, 'PRICE 2400 CR', P['red3'] if frame else P['red2'])
    return im


# ------------------------------------------------------------------ The Harmacist
HARM_DOWN = [
"...........o......................",
"............okk...................",
"...........kNNNkk.................",
"...........kNNNNNk................",
"............kNNNNNk...............",
".............kN111lk..............",
".............k1111lk..............",
"..............k111k...............",
"...............k1rk...............",
"...........kkkkk11kk..............",
"..........kwwwwbwwwwk.............",
".........kwwwwwwbwwwwk............",
".........kwswwwwwlbwwwk...........",
"........kwwswwwwwwmbwwwk..........",
"........kwwsww11wwwwgbkwk.........",
"........kwwswww11wwwwwkwwk........",
".......kwwwwswwwwwwwwk..kwk.......",
".......kwwwwswwwwwwwnk...kwk......",
"......kwwwwwwswwwwnnnnk...kwk.....",
"......kwwwwwwswwwnnnnnnk...kwk....",
".....kwwwwwwwwswwkknnnnk...k1k....",
".....kwwwwwwwwswk..knnnk..k111k...",
"....kwwwwwwwwwswk...knnk..k111k.kl",
"....kkkkkkkkkkkkk...kbbk...kkk.lgl",
]


HARM_W, HARM_H = 34, 36
HARM_FOOT = (15, 35)
HARM_POSES = {
    # front hand (x, y), back hand (x, y), lean, stride, held item
    'idle': ((20, 20), (10, 21), 0, 2, None),
    'walk': ((19, 20), (11, 20), 1, 4, None),
    'throw0': ((10, 9), (9, 21), -1, 3, 'vial'),
    'throw1': ((25, 14), (9, 21), 1, 4, None),
    'slash0': ((9, 17), (10, 21), -1, 2, 'scalpel'),
    'slash1': ((27, 19), (9, 20), 2, 5, 'scalpel'),
    'stim0': ((18, 12), (11, 21), 0, 2, 'stim'),
    'stim1': ((14, 15), (16, 15), 1, 2, 'stim'),
    'burst': ((23, 24), (7, 24), 0, 5, 'vial'),
    'hurt': ((19, 23), (9, 23), -2, 1, None),
    'limp': ((18, 25), (14, 21), -1, 3, None),
}


HARM_FRAMES = assets.art_path('characters', 'harmacist')
HARM_ANCHOR = (40, 61)  # her feet in each 80x64 cell


def _components(im):
    px = im.load()
    seen, comps = set(), []
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][3] and (x, y) not in seen:
                stack, comp = [(x, y)], []
                seen.add((x, y))
                while stack:
                    a, b = stack.pop()
                    comp.append((a, b))
                    for q in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1), (a + 1, b + 1), (a - 1, b - 1), (a + 1, b - 1), (a - 1, b + 1)):
                        if 0 <= q[0] < im.width and 0 <= q[1] < im.height and q not in seen and px[q][3]:
                            seen.add(q)
                            stack.append(q)
                comps.append(comp)
    return comps


def harm_frames():
    """The hand-drawn Harmacist animations: {anim: [80x64 frames]}, facing right. The
    vial already in flight is taken out of the throw frames, since the game throws
    its own."""
    out = {}
    for folder in sorted(os.listdir(HARM_FRAMES)):
        if not os.path.isdir(os.path.join(HARM_FRAMES, folder)):
            continue
        anim = folder.split('_', 1)[1]
        files = sorted(os.listdir(os.path.join(HARM_FRAMES, folder)))
        out[anim] = [Image.open(os.path.join(HARM_FRAMES, folder, f)).convert('RGBA') for f in files]
    for i in (4, 5, 6):
        im = out['throw'][i]
        comps = sorted(_components(im), key=len)
        px = im.load()
        for comp in comps[:-1]:
            for q in comp:
                px[q] = (0, 0, 0, 0)
    out['slash'] = [harm_sword(im) for im in out['slash']]
    return out


# the sword's greens, light to dark (kept off the visor's lime so harm_juiced leaves them alone)
SWORD_GREENS = [(232, 255, 204), (170, 250, 104), (66, 210, 120), (30, 110, 70)]


def harm_sword(im):
    """Her scalpel, made a sword: the blade (or the swoosh of the cut) doubled in length
    out from her hand, and green instead of cyan."""
    im = im.copy()
    px = im.load()
    blade, hand = [], []
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            if (b - r > 35 and g - r > 30 and b >= g - 6) or ((r, g, b) == (255, 255, 255) and a < 255):
                blade.append((x, y))
            elif (r, g, b) in ((242, 196, 160), (206, 150, 122)) and y > 36:
                hand.append((x, y))
    if not blade:
        return im
    if hand:
        hx = sum(q[0] for q in hand) / len(hand)
        hy = sum(q[1] for q in hand) / len(hand)
    else:
        hx, hy = min(blade, key=lambda q: (q[0] - 40) ** 2 + (q[1] - 44) ** 2)

    def green(p):
        r, g, b, a = p
        lum = (r + g + b) / 3
        k = 0 if lum > 225 else 1 if lum > 170 else 2 if lum > 90 else 3
        return SWORD_GREENS[k] + (a,)

    cols = {q: green(px[q]) for q in blade}
    for q, c in cols.items():
        px[q] = c
    out = {}
    if len(blade) > 25:
        # the swoosh of the cut: the same arc at twice the size
        for (x, y), c in cols.items():
            sx, sy = hx + (x - hx) * 2, hy + (y - hy) * 2
            for dx in (0, 1):
                for dy in (0, 1):
                    out[(int(round(sx)) + dx, int(round(sy)) + dy)] = c
    else:
        # the blade itself, raised in the windup: a long sword, two pixels wide with a dark
        # edge so it reads against her white coat
        solid = [q for q in blade if im.getpixel(q)[3] == 255 and sum(im.getpixel(q)[:3]) > 360] or blade
        tx, ty = max(solid, key=lambda q: (q[0] - hx) ** 2 + (q[1] - hy) ** 2)
        L = ((tx - hx) ** 2 + (ty - hy) ** 2) ** 0.5 or 1
        ux, uy = (tx - hx) / L, (ty - hy) / L
        length = L * 2.8
        edge, core, shine = SWORD_GREENS[3] + (255,), SWORD_GREENS[1] + (255,), SWORD_GREENS[0] + (255,)
        line = []
        k = 1.5
        while k <= length:
            line.append((hx + ux * k, hy + uy * k))
            k += 0.5
        for lx, ly in line:
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    q = (int(round(lx + ox)), int(round(ly + oy)))
                    out.setdefault(q, edge)
        for lx, ly in line:
            out[(int(round(lx)), int(round(ly)))] = core
            out[(int(round(lx - uy * 0.7)), int(round(ly + ux * 0.7)))] = shine
    for (x, y), c in out.items():
        if 0 <= x < im.width and 0 <= y < im.height and (not px[x, y][3] or (x, y) in cols or px[x, y][3] < c[3]):
            px[x, y] = c
    return im


def harm_juiced(im, frame=0):
    """After her stim: the visor burns red and red flecks crawl over the coat."""
    im = im.copy()
    px = im.load()
    box = im.getbbox()
    if not box:
        return im
    solid = {}
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if px[x, y][3]:
                solid[px[x, y][:3]] = solid.get(px[x, y][:3], 0) + 1
    if max(solid.values()) > 0.6 * sum(solid.values()):
        return im  # a flash frame (all white or all red): leave it
    lime, glow = C('lime'), (236, 255, 196)
    top = box[1]
    for y in range(top, min(top + 10, box[3])):
        x = box[0]
        while x < box[2]:
            if px[x, y][:3] in (lime, glow):
                x2 = x
                while x2 < box[2] and px[x2, y][3] and px[x2, y][:3] in (lime, glow):
                    x2 += 1
                if x2 - x >= 3:  # a visor, not a vial
                    for k in range(x, x2):
                        px[k, y] = C('red3') + (255,) if px[k, y][:3] == lime else (255, 200, 180, 255)
                x = x2
            x += 1
    coat = C('white')
    cx = (box[0] + box[2]) // 2
    for k in range(3):
        fx, fy = cx - 4 + k * 4, top + 13 + (frame + k * 2) % 7
        if 0 <= fx < im.width and 0 <= fy < im.height and px[fx, fy][:3] == coat:
            px[fx, fy] = C('red3') + (255,)
    return im


def harmacist(pose='idle', frame=0, juiced=False):
    """The Harmacist, facing right, 34x36, feet at HARM_FOOT."""
    im = Image.new('RGBA', (HARM_W, HARM_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if pose == 'dead':
        return pix_grid(HARM_DOWN, HARM_W, HARM_H)
    arm, back, lean, step, item = HARM_POSES[pose]
    bob = frame % 2 if pose in ('idle', 'walk', 'limp') else 0
    hx0 = 15 + lean
    top = 9 + bob
    # legs and heels
    d.line([13, 27, 13 - (step if pose in ('walk', 'limp') and frame % 2 else 0), 34], fill=C('night1'), width=2)
    d.line([17, 27, 17 + step, 34], fill=C('night1'), width=2)
    d.point([(12 - (step if pose in ('walk', 'limp') and frame % 2 else 0), 34), (18 + step, 34)], fill=C('ink'))
    # back arm
    d.line([hx0 - 3, top + 4, back[0], back[1]], fill=C('steel'), width=2)
    # long lab coat, split at the back
    d.polygon([(hx0 - 5, top + 2), (hx0 + 5, top + 2), (hx0 + 6, 29), (hx0 + 1, 28), (hx0 - 1, 30), (hx0 - 7, 29)],
              fill=C('white'), outline=C('ink'))
    d.line([hx0, top + 3, hx0 + 1, 28], fill=C('steel'))
    # vial bandolier
    d.line([hx0 - 4, top + 3, hx0 + 5, top + 13], fill=C('brown'))
    for k, col in enumerate(('lime', 'mag3', 'green2')):
        d.point((hx0 - 2 + k * 3, top + 6 + k * 3), fill=C(col))
        d.point((hx0 - 2 + k * 3, top + 5 + k * 3), fill=C(col))
    # head: skin, dark bun with a gold pin, green goggles
    d.ellipse([hx0 - 3, top - 7, hx0 + 4, top + 1], fill=C('skin3'), outline=C('ink'))
    d.pieslice([hx0 - 4, top - 8, hx0 + 4, top], 170, 350, fill=C('night2'))
    d.ellipse([hx0 - 7, top - 9, hx0 - 2, top - 4], fill=C('night2'), outline=C('ink'))
    d.line([hx0 - 8, top - 9, hx0 - 2, top - 5], fill=C('gold'))
    d.line([hx0 + 1, top - 4, hx0 + 4, top - 4], fill=C('red3') if juiced else C('lime'))
    d.point((hx0 + 2, top - 1), fill=C('red2'))
    # front arm (coat sleeve) and whatever she holds
    d.line([hx0 + 2, top + 4, arm[0], arm[1]], fill=C('white'), width=2)
    d.point(arm, fill=C('skin3'))
    if item == 'vial':
        d.rectangle([arm[0] - 1, arm[1] - 3, arm[0], arm[1] - 1], fill=C('lime'))
    elif item == 'scalpel':
        d.line([arm[0], arm[1], arm[0] + 5, arm[1] - 2], fill=C('cyan4'))
    elif item == 'stim':
        d.line([arm[0] - 2, arm[1] + 2, arm[0] + 3, arm[1] - 2], fill=C('steel'))
        d.point((arm[0] + 1, arm[1]), fill=C('mag3'))
    if juiced:
        for k in range(3):
            d.point((hx0 - 6 + k * 6, top + 2 + (frame + k) % 5), fill=C('red3'))
    return im


def vial(frame):
    im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([3, 1, 4, 6], fill=C('lime'), outline=C('green1'))
    d.point((3 + frame, 0), fill=C('steel'))
    return im


def cloud(frame, big=False):
    """A lingering poison cloud, 32x24 (bottom-center)."""
    w, h = (48, 32) if big else (32, 24)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(frame * 3 + big)
    for _ in range(9 if big else 6):
        rx = rng.randint(6, 10)
        cx0 = rng.randint(rx, w - rx)
        cy0 = rng.randint(h // 2, h - rx)
        d.ellipse([cx0 - rx, cy0 - rx, cx0 + rx, cy0 + rx], fill=C('green2', 120), outline=C('green1', 150))
    for _ in range(5):
        im.putpixel((rng.randrange(w), rng.randrange(h // 2, h)), C('lime'))
    return im


# ------------------------------------------------------------------ front parallax
def garden_trees(base):
    """Paint a thick band of cloud-pruned Japanese trees, dotted with blossoms, over the
    gardens' mid parallax layer (240x180, wraps horizontally)."""
    im = base.copy().convert('RGBA')
    W, H = im.size
    rng = random.Random(44)
    layer = Image.new('RGBA', (W * 3, H), (0, 0, 0, 0))   # draw 3 tiles wide, fold back to wrap
    d = ImageDraw.Draw(layer)

    def tree(x0, ground, height, back):
        trunk = C('night1') if back else C('ink')
        bark = C('night2') if back else C('brown')
        leaf, lit = (C('night1'), C('night2')) if back else (C('slate1'), C('green1'))
        # a leaning, slightly crooked trunk
        lean = rng.choice((-1, 1)) * rng.uniform(0.15, 0.4)
        pts = []
        for k in range(0, height + 1, 4):
            pts.append((x0 + lean * k + math.sin(k * 0.21 + x0) * 2, ground - k))
        for wdt, col in ((5 if not back else 4, trunk), (2, bark)):
            d.line(pts, fill=col, width=wdt)
        top = pts[-1]
        pads = [top]
        # branches sweep out sideways and end in flat foliage pads
        for b in range(rng.randint(2, 4)):
            k = rng.randint(len(pts) // 3, len(pts) - 1)
            sx, sy = pts[k]
            side = rng.choice((-1, 1))
            ex, ey = sx + side * rng.randint(12, 24), sy - rng.randint(2, 10)
            d.line([(sx, sy), ((sx + ex) / 2, sy - 1), (ex, ey)], fill=trunk, width=2)
            pads.append((ex, ey))
        for (px0, py0) in pads:
            for c in range(rng.randint(2, 3)):
                rx, ry = rng.randint(9, 16), rng.randint(4, 7)
                cx0, cy0 = px0 + rng.randint(-6, 6), py0 - rng.randint(0, 5)
                d.ellipse([cx0 - rx, cy0 - ry, cx0 + rx, cy0 + ry], fill=leaf)
                d.chord([cx0 - rx + 2, cy0 - ry, cx0 + rx - 2, cy0 + ry - 3], 180, 360, fill=lit)

    for back in (True, False):
        n = 9 if back else 7
        for i in range(n):
            x0 = W + i * W / n + rng.uniform(-8, 8) + (14 if back else 0)
            ground = H + 4
            height = rng.randint(70, 100) if back else rng.randint(45, 80)
            tree(x0, ground, height, back)
            for extra in (-W, W):
                pass
    # fold the 3-wide canvas into one wrapping tile
    tile = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for k in range(3):
        tile.alpha_composite(layer.crop((k * W, 0, (k + 1) * W, H)))
    # blossoms: pink dots over the foliage, a few petals drifting below
    tp = tile.load()
    for _ in range(900):
        x, y = rng.randrange(W - 2), rng.randrange(H - 2)
        if tp[x, y][3] and tp[x, y][:3] in (P['slate1'], P['green1'], P['night1'], P['night2']):
            back = tp[x, y][:3] in (P['night1'], P['night2'])
            col, hi = (C('mag1'), C('mag2')) if back else (C('mag3'), C('mag4'))
            for dx, dy in ((0, 0), (1, 0), (0, 1)):
                if tp[x + dx, y + dy][3]:
                    tp[x + dx, y + dy] = col
            tp[x, y] = hi
    for _ in range(30):
        x, y = rng.randrange(W), rng.randrange(60, H)
        if not tp[x, y][3]:
            tp[x, y] = C('mag4' if rng.random() < 0.5 else 'mag3')
    im.alpha_composite(tile)
    return im
