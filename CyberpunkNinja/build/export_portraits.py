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


def framed(figure):
    """A figure on Hotaru's dithered blue backdrop, inside the cyan portrait border."""
    base = art_v2.portrait_base('night2', 'cyan1', 'slate2')
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
