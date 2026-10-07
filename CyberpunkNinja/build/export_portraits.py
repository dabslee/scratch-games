"""
Write the dialogue portrait sheet (art/portraits.png): every portrait the game uses,
at native size (40x40 art pixels) on a 4-column grid with no gutters, in the order
listed in art/portraits.json. build.py reads portraits back from this sheet, so an
edited sheet dropped in its place changes the game. Also writes a labeled, enlarged
preview (art/portraits_preview.png) that shows which speaker uses which portrait.

Run with CN_PACK set:  python3 build/export_portraits.py
"""
import json
import os
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


def main():
    os.makedirs(ART, exist_ok=True)
    ports = source_portraits()
    rows = (len(ORDER) + COLS - 1) // COLS
    sheet = Image.new('RGBA', (COLS * CELL, rows * CELL), (0, 0, 0, 0))
    for i, name in enumerate(ORDER):
        sheet.alpha_composite(ports[name].convert('RGBA'), ((i % COLS) * CELL, (i // COLS) * CELL))
    sheet.save(os.path.join(ART, 'portraits.png'))

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
