"""
Write the dialogue portrait sheet (art/portraits.png): every portrait the game uses,
at native size (40x40 art pixels) on a 4-column grid with no gutters, in the order
listed in art/portraits.json. build.py reads portraits back from this sheet, so an
edited sheet dropped in its place changes the game. Also writes a labeled, enlarged
preview (art/portraits_preview.png) that shows which speaker uses which portrait.

Run with CN_PACK set:  python3 build/export_portraits.py
The sheet is the source of truth once it exists (it holds hand-made art), so this
only refreshes portraits.json and the preview from it. Pass --reset to rebuild the
sheet from the original art, or --hotaru PNG to install a new Hotaru set (an 80x40
image: neutral on the left, visor up on the right; the angry face is derived).
"""
import json
import os
import random
import sys
from collections import Counter

from PIL import Image, ImageDraw

import art_ch2
import art_v2
import assets
import dialogue

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, '..', 'art')
CELL, COLS = 40, 4
ORDER = ['hotaru_neutral', 'hotaru_angry', 'hotaru_visor_up', 'kuro_neutral',
         'kuro_smirk', 'tetsu_neutral', 'daicam_neutral', 'mukuro_neutral',
         'daimyo_neutral', 'luck_neutral', 'sys_boot', 'oni_neutral',
         'harm_neutral']
DRAWN = {'luck_neutral': art_ch2.luck_portrait, 'sys_boot': art_ch2.system_portrait,
         'oni_neutral': art_v2.oni_portrait, 'harm_neutral': art_v2.harm_portrait}


def source_portraits():
    st = assets.starter()
    out = {}
    for name in ORDER:
        out[name] = DRAWN[name]() if name in DRAWN else st.image_1x('Portraits', name)
    return out


def framed(figure, tones=('night2', 'cyan1', 'slate2')):
    """A figure on a dithered gradient backdrop (top, bottom and fleck colors; Hotaru's
    blue by default), inside the cyan portrait border."""
    base = art_v2.portrait_base(*tones)
    out = base.copy()
    out.alpha_composite(figure.convert('RGBA'))
    bp, op = base.load(), out.load()
    for y in range(CELL):
        for x in range(CELL):
            if bp[x, y][3] and bp[x, y][:3] == art_v2.P['cyan2'] and (x in (0, CELL - 1) or y in (0, CELL - 1)):
                op[x, y] = bp[x, y]
            elif not bp[x, y][3]:
                op[x, y] = (0, 0, 0, 0)
    return out


def angry_from(neutral):
    """Hotaru's angry face, derived from her neutral portrait: the visor glass turns deep
    red with narrowed slits glowing through it, and her brows pull down into a V."""
    im = neutral.convert('RGBA').copy()
    px = im.load()
    visor = {(17, 250, 255): (190, 32, 48), (16, 219, 238): (170, 28, 44), (18, 203, 227): (160, 26, 42),
             (12, 166, 184): (120, 18, 34), (11, 148, 170): (110, 15, 31), (10, 129, 138): (92, 14, 28),
             (9, 120, 150): (86, 12, 28), (8, 96, 112): (70, 10, 24), (11, 79, 96): (58, 8, 20)}
    for y in range(15, 22):
        for x in range(10, 32):
            if px[x, y][3] and px[x, y][:3] in visor:
                px[x, y] = visor[px[x, y][:3]] + (255,)
    hot, core = (255, 90, 74, 255), (255, 224, 102, 255)
    for (x, y), c in {(15, 17): hot, (16, 17): core, (17, 18): core, (18, 18): hot}.items():
        px[x, y] = c
        px[42 - x, y] = c
    brow, brow_d = (100, 108, 140, 255), (61, 64, 92, 255)
    for (x, y), c in {(15, 13): brow, (16, 13): brow, (17, 14): brow_d, (18, 14): brow_d}.items():
        px[x, y] = c
        px[39 - x, y] = c
    return im


def from_upscale(path, grid=40):
    """Recover a grid x grid pixel portrait from an enlarged copy (such as an AI upscale):
    take the dominant color in the middle of each cell, ignoring soft edges."""
    im = Image.open(path).convert('RGB')
    if im.size == (grid, grid):
        return im
    px = im.load()
    pw, ph = im.width / grid, im.height / grid
    out = Image.new('RGB', (grid, grid))
    op = out.load()
    for r in range(grid):
        for c in range(grid):
            x0, x1 = int((c + 0.3) * pw), int((c + 0.7) * pw)
            y0, y1 = int((r + 0.3) * ph), int((r + 0.7) * ph)
            groups = {}
            for y in range(y0, y1):
                for x in range(x0, x1):
                    p = px[x, y]
                    groups.setdefault(tuple(v // 12 for v in p), []).append(p)
            g = max(groups.values(), key=len)
            op[c, r] = tuple(sum(p[i] for p in g) // len(g) for i in range(3))
    return out


def snap_palette(images, radius=26):
    """Merge near-identical shades shared by a set of portraits into one clean palette
    (frequency-weighted means of each group) and snap every pixel to it."""
    counts = Counter()
    for im in images:
        for y in range(1, im.height - 1):
            for x in range(1, im.width - 1):
                counts[im.getpixel((x, y))] += 1
    groups = []
    for c, n in counts.most_common():
        for seed, mem in groups:
            if sum((p - q) ** 2 for p, q in zip(c, seed)) < radius * radius:
                mem.append((c, n))
                break
        else:
            groups.append((c, [(c, n)]))
    pal = [tuple(round(sum(c[i] * n for c, n in mem) / sum(n for _, n in mem)) for i in range(3))
           for _, mem in groups]
    out = []
    for im in images:
        im = im.copy()
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                px[x, y] = min(pal, key=lambda c: sum((u - v) ** 2 for u, v in zip(px[x, y], c)))
        out.append(im)
    return out


def bordered(im):
    """The cyan portrait border (rounded corners) over a full-bleed portrait."""
    base = art_v2.portrait_base('night2', 'cyan1', 'slate2')
    out = im.convert('RGBA').copy()
    bp, op = base.load(), out.load()
    for y in range(CELL):
        for x in range(CELL):
            if not bp[x, y][3]:
                op[x, y] = (0, 0, 0, 0)
            elif bp[x, y][:3] == art_v2.P['cyan2'] and (x in (0, CELL - 1) or y in (0, CELL - 1)):
                op[x, y] = bp[x, y]
    return out


# Kuro is a ghost in the machine: his portraits are muted and cooled (all but his eyes),
# set against a dark purple backdrop, with holographic scanlines and a little static.
KURO_EYES = {(222, 250, 247), (173, 208, 209)}
KURO_BACK = ((14, 10, 30), (40, 28, 72))      # dark and light purple, replacing his greens
KURO_MOUTH = (128, 96, 168)


def kuro_ghost(im, smirk=False):
    im = im.convert('RGB').copy()
    px = im.load()
    rng = random.Random(77)
    for y in range(CELL):
        for x in range(CELL):
            r, g, b = px[x, y]
            if (r, g, b) in KURO_EYES:
                continue
            if g > r + 12 and g > b:
                # backdrop: his green dither becomes a purple one, same pattern
                c = KURO_BACK[1] if g > 60 else KURO_BACK[0]
                if rng.random() < 0.03:
                    c = (78, 62, 120)          # a fleck of static
            else:
                lum = 0.3 * r + 0.59 * g + 0.11 * b
                c = tuple(int((0.45 * v + 0.55 * lum) * 0.82) for v in (r, g, b))
                c = (int(c[0] * 0.92), int(c[1] * 0.9), min(255, int(c[2] * 1.08 + 4)))
            if y % 2 == 1:
                c = tuple(int(v * 0.8) for v in c)   # holographic scanlines
            px[x, y] = c
    # a clearer mouth (it was nearly black on black); the smirk curls up at one end
    for x in range(18, 22):
        px[x, 25] = KURO_MOUTH
    if smirk:
        px[17, 24] = KURO_MOUTH
    return im


def kuro_glitch(cell, k):
    """An in-game glitch frame for a framed Kuro portrait: a few row bands tear sideways,
    with a magenta/cyan split along the figure's edges, and the static thickens."""
    im = cell.convert('RGBA').copy()
    src = cell.convert('RGBA')
    px, sp = im.load(), src.load()
    rng = random.Random(500 + k)
    back = {KURO_BACK[0], KURO_BACK[1], (78, 62, 120)}

    def is_back(p):
        return p[:3] in back or p[:3] in {tuple(int(v * 0.8) for v in c) for c in back}
    for _ in range(k):
        y0, h, dx = rng.randint(6, 30), rng.randint(1, 2), rng.choice((-2, -1, 1, 2))
        for y in range(y0, min(CELL - 1, y0 + h)):
            row = [sp[min(max(x - dx, 1), CELL - 2), y] for x in range(CELL)]
            for x in range(1, CELL - 1):
                px[x, y] = row[x]
            for x in range(2, CELL - 2):
                if y != y0:
                    break
                if not is_back(row[x]) and is_back(row[x - 1]):
                    px[x - 1, y] = (255, 61, 184, 255)
                if not is_back(row[x]) and is_back(row[x + 1]):
                    px[x + 1, y] = (62, 240, 255, 255)
    for _ in range(4 + 4 * k):
        x, y = rng.randint(1, CELL - 2), rng.randint(1, CELL - 2)
        if px[x, y][:3] not in KURO_EYES:
            px[x, y] = rng.choice(((110, 90, 160, 255), (78, 62, 120, 255)))
    return im


def install_kuro(sheet, neutral_src, smirk_src):
    """Kuro's portraits are full 40x40 paintings with their own dark green backdrop
    (enlarged copies are fine; they're sampled back down to the grid). Both are snapped
    to one shared palette so edges stay crisp, then framed with the cyan border."""
    ims = snap_palette([from_upscale(neutral_src), from_upscale(smirk_src)])
    for name, im in zip(('kuro_neutral', 'kuro_smirk'), ims):
        i = ORDER.index(name)
        x, y = (i % COLS) * CELL, (i // COLS) * CELL
        sheet.paste((0, 0, 0, 0), (x, y, x + CELL, y + CELL))
        sheet.alpha_composite(bordered(kuro_ghost(im, smirk=name == 'kuro_smirk')), (x, y))
    return ims


def install_hotaru(sheet, src):
    pair = Image.open(src).convert('RGBA')
    assert pair.size == (2 * CELL, CELL), 'expected an 80x40 image, got %s' % (pair.size,)
    neutral, up = pair.crop((0, 0, CELL, CELL)), pair.crop((CELL, 0, 2 * CELL, CELL))
    for name, fig in (('hotaru_neutral', neutral), ('hotaru_angry', angry_from(neutral)), ('hotaru_visor_up', up)):
        i = ORDER.index(name)
        x, y = (i % COLS) * CELL, (i // COLS) * CELL
        sheet.paste((0, 0, 0, 0), (x, y, x + CELL, y + CELL))
        sheet.alpha_composite(framed(fig), (x, y))


def main():
    os.makedirs(ART, exist_ok=True)
    path = os.path.join(ART, 'portraits.png')
    rows = (len(ORDER) + COLS - 1) // COLS
    if '--reset' in sys.argv or not os.path.exists(path):
        ports = source_portraits()
        sheet = Image.new('RGBA', (COLS * CELL, rows * CELL), (0, 0, 0, 0))
        for i, name in enumerate(ORDER):
            sheet.alpha_composite(ports[name].convert('RGBA'), ((i % COLS) * CELL, (i // COLS) * CELL))
    else:
        sheet = Image.open(path).convert('RGBA')
    if '--hotaru' in sys.argv:
        install_hotaru(sheet, sys.argv[sys.argv.index('--hotaru') + 1])
    if '--kuro' in sys.argv:
        k = sys.argv.index('--kuro')
        clean = install_kuro(sheet, sys.argv[k + 1], sys.argv[k + 2])
        # keep the cleaned 40x40 sources next to the sheet
        for name, im in zip(('kuro_neutral', 'kuro_smirk'), clean):
            im.save(os.path.join(ART, 'src', name + '.png'))
    sheet.save(path)
    ports = {n: sheet.crop(((i % COLS) * CELL, (i // COLS) * CELL, (i % COLS + 1) * CELL, (i // COLS + 1) * CELL))
             for i, n in enumerate(ORDER)}

    # which lines show each portrait
    use = Counter()
    who = {}
    for lines in dialogue.CONVERSATIONS.values():
        for spk, real, port, text in lines:
            use[port] += 1
            who.setdefault(port, set()).add(real)
    manifest = {'cell': CELL, 'columns': COLS,
                'note': 'Cells are read left to right, top to bottom. Keep each portrait inside its 40x40 cell.',
                'portraits': [{'name': n, 'row': i // COLS, 'col': i % COLS, 'speakers': sorted(who.get(n, [])),
                               'lines': use.get(n, 0)} for i, n in enumerate(ORDER)]}
    json.dump(manifest, open(os.path.join(ART, 'portraits.json'), 'w'), indent=2)

    # enlarged, labeled preview
    k, lab = 6, 54
    font = assets.Font(False)
    W, H = COLS * (CELL * k + 12) + 12, rows * (CELL * k + lab + 12) + 12
    prev = Image.new('RGBA', (W, H), assets.PALETTE['night1'] + (255,))
    for i, name in enumerate(ORDER):
        x = 12 + (i % COLS) * (CELL * k + 12)
        y = 12 + (i // COLS) * (CELL * k + lab + 12)
        big = ports[name].convert('RGBA').resize((CELL * k, CELL * k), Image.NEAREST)
        prev.alpha_composite(big, (x, y))
        for j, (label, col) in enumerate(((name, 'white'), ('%d lines' % use.get(name, 0), 'steel'))):
            t = Image.new('RGBA', (font.width(label) + 1, 11), (0, 0, 0, 0))
            font.draw(t, 0, 0, label, assets.PALETTE[col])
            prev.alpha_composite(t.resize((t.width * 2, t.height * 2), Image.NEAREST), (x, y + CELL * k + 6 + j * 24))
    prev.save(os.path.join(ART, 'portraits_preview.png'))
    print('wrote art/portraits.png', sheet.size, 'and art/portraits_preview.png', prev.size)


if __name__ == '__main__':
    main()
