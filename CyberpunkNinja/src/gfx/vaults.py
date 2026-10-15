"""
Chapter 2 (The Pachinko Vaults) art. The asset pack stops at Chapter 1, so
everything here is generated: palette swaps of existing pack art (the pack's
sprites are drawn from one 34-color palette precisely so they can be
recolored) plus new pixel art drawn in that same palette.


All functions return 1x art-pixel images unless noted.
"""
from PIL import Image, ImageDraw

import assets
from assets import PALETTE as P
from gfx.portraits import luck_portrait
from gfx.ui import nameplate
from gfx.util import C, gradient, recolor, recolor_costumes


LUCK_MAP = {
    'night1': 'purple1', 'night2': 'mag1', 'night3': 'mag2', 'indigo': 'mag3',
    'red1': 'brown', 'red2': 'gold', 'red3': 'yellow', 'yellow': 'white',
    'slate2': 'steel', 'slate3': 'white', 'cyan3': 'mag3', 'cyan4': 'mag4', 'mag3': 'yellow',
}
CROUPIER_MAP = {
    'red1': 'slate3', 'red2': 'steel', 'red3': 'white', 'white': 'ink',
    'mag1': 'red2', 'mag3': 'red3', 'slate1': 'night2', 'slate2': 'night3', 'slate3': 'indigo',
    'steel': 'gold', 'yellow': 'gold', 'gold': 'yellow', 'night3': 'red1',
}
SLOT_TURRET_MAP = {
    'slate1': 'brown', 'slate2': 'gold', 'slate3': 'yellow', 'steel': 'white',
    'red2': 'mag3', 'red3': 'mag4', 'ink': 'ink',
}
TILE_MAP = {
    'slate1': 'purple1', 'slate2': 'mag1', 'slate3': 'mag2', 'steel': 'gold',
    'cyan1': 'brown', 'cyan3': 'yellow', 'cyan4': 'white', 'night2': 'night2', 'white': 'yellow',
}


# ------------------------------------------------------------------ tiles
def vaults_atlas():
    atlas = Image.open(assets.pack_path('tilesets', 'alley_atlas_8x8.png')).convert('RGBA')
    return recolor(atlas, TILE_MAP)


def sky():
    im = Image.new('RGBA', (240, 180), C('ink'))
    gradient(im, 0, 60, 'ink', 'night1')
    gradient(im, 60, 120, 'night1', 'night2')
    gradient(im, 120, 180, 'night2', 'purple1')
    d = ImageDraw.Draw(im)
    # chandeliers hanging from the vault ceiling (period 120 so the layer tiles)
    for cx in (30, 150):
        d.line([cx, 0, cx, 14], fill=C('brown'))
        d.polygon([(cx - 12, 16), (cx + 12, 16), (cx + 6, 24), (cx - 6, 24)], fill=C('gold'))
        d.line([cx - 12, 16, cx + 12, 16], fill=C('yellow'))
        for i, dx in enumerate(range(-10, 11, 4)):
            d.line([cx + dx, 24, cx + dx, 28 + (i % 2) * 3], fill=C('yellow'))
            im.putpixel((cx + dx, 29 + (i % 2) * 3), C('white'))
    # warm bokeh lights
    import random
    rng = random.Random(22)
    for _ in range(70):
        x, y = rng.randrange(240), rng.randrange(30, 170)
        im.putpixel((x, y), C(rng.choice(['gold', 'mag3', 'yellow', 'mag2'])))
    return im


def pachinko_cabinet(d, x, y, w, h, lit, dim=False):
    body = 'night2' if dim else 'night3'
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=C(body))
    d.rectangle([x, y, x + w - 1, y + 3], fill=C('mag1' if dim else 'mag2'))
    d.line([x, y + h - 1, x + w - 1, y + h - 1], fill=C('ink'))
    glass = (x + 2, y + 6, x + w - 3, y + h - 8)
    d.rectangle(glass, fill=C('night1'))
    cols = ['yellow', 'mag3', 'cyan3', 'gold'] if not dim else ['gold', 'mag2', 'cyan2', 'brown']
    k = 0
    for yy in range(glass[1] + 2, glass[3], 4):
        for xx in range(glass[0] + 1 + (yy // 4) % 2, glass[2], 3):
            if (k + lit) % 5 != 0:
                d.point((xx, yy), fill=C(cols[k % len(cols)]))
            k += 1
    d.rectangle([x + 2, y + h - 6, x + w - 3, y + h - 4], fill=C('gold' if not dim else 'brown'))


def far():
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # back row: small dim cabinets
    for i, x in enumerate(range(0, 240, 12)):
        pachinko_cabinet(d, x + 1, 104, 10, 34, i, dim=True)
    # front row: taller cabinets on a carpet floor
    d.rectangle([0, 160, 239, 179], fill=C('night1'))
    for x in range(0, 240, 8):
        d.line([x, 162, x + 4, 162], fill=C('mag1'))
    for i, x in enumerate(range(0, 240, 16)):
        pachinko_cabinet(d, x + 1, 114, 14, 46, i * 3)
    return im


def mid():
    im = Image.new('RGBA', (240, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bold = assets.Font(True)
    for cx in (60, 180):
        # gold-trimmed marble pillars
        d.rectangle([cx - 7, 0, cx + 7, 179], fill=C('purple1'))
        d.line([cx - 7, 0, cx - 7, 179], fill=C('gold'))
        d.line([cx + 7, 0, cx + 7, 179], fill=C('brown'))
        for y in range(10, 180, 24):
            d.rectangle([cx - 8, y, cx + 8, y + 2], fill=C('gold'))
            d.point((cx - 4, y + 1), fill=C('yellow'))
    # neon signs between the pillars
    for cx, text, col in ((0, '777', 'red3'), (240, '777', 'red3')):
        w = bold.width(text)
        x = cx - w // 2
        d.rectangle([x - 4, 44, x + w + 3, 56], fill=C('ink', 200), outline=C('mag2'))
        bold.draw(im, x, 46, text, P[col])
    # balcony railing
    d.line([0, 92, 239, 92], fill=C('gold'))
    for x in range(0, 240, 6):
        d.line([x, 93, x, 99], fill=C('brown'))
    d.line([0, 100, 239, 100], fill=C('gold'))
    return im


# ------------------------------------------------------------------ props
def card_frames():
    """Spinning card-blade (4 frames, 9x9)."""
    frames = []
    for i in range(4):
        im = Image.new('RGBA', (9, 9), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if i in (0, 2):
            face = 'white' if i == 0 else 'mag2'
            d.rectangle([1, 0, 7, 8], fill=C(face), outline=C('gold'))
            if i == 0:
                d.point([(4, 3), (3, 4), (4, 4), (5, 4), (4, 5)], fill=C('red2'))
            else:
                d.point([(3, 3), (5, 5), (5, 3), (3, 5)], fill=C('mag4'))
        else:
            d.line([4, 0, 4, 8], fill=C('yellow'))
            d.line([3, 1, 3, 7], fill=C('gold'))
        frames.append(im)
    return frames


SYMBOLS = {
    'seven': ['.RRRRRRRR.', '.RRRRRRRR.', '......RR..', '.....RR...', '....RR....', '...RR.....', '...RR.....', '..RR......', '..RR......', '..RR......'],
    'cherry': ['......GG..', '.....G.G..', '....G...G.', '...G....G.', '..RR...RR.', '.RRRR.RRRR', '.RWRR.RWRR', '.RRRR.RRRR', '..RR...RR.', '..........'],
    'spade': ['....KK....', '...KKKK...', '..KKKKKK..', '.KKKKKKKK.', 'KKKKKKKKKK', 'KKKKKKKKKK', '.KKK.KKK..', '....KK....', '...KKKK...', '..........'],
    'skull': ['..WWWWWW..', '.WWWWWWWW.', 'WWWWWWWWWW', 'WKKWWWKKWW', 'WKKWWWKKWW', 'WWWWKWWWWW', '.WWWWWWWW.', '..WKWKWK..', '..WWWWWW..', '..........'],
    'jackpot': ['....YY....', '...YWWY...', '..YYWWYY..', 'YYYYYYYYYY', '.YYYYYYYY.', '..YYYYYY..', '..YY..YY..', '.YY....YY.', 'YY......YY', '..........'],
}
SYM_COL = {'R': 'red2', 'G': 'green2', 'W': 'white', 'K': 'ink', 'Y': 'yellow'}


def symbol(name):
    im = Image.new('RGBA', (12, 14), C('white'))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 11, 13], outline=C('steel'))
    for r, row in enumerate(SYMBOLS[name]):
        for c, ch in enumerate(row):
            if ch in SYM_COL:
                im.putpixel((1 + c, 2 + r), C(SYM_COL[ch]))
    return im


def reel_blur(n):
    im = Image.new('RGBA', (12, 14), C('white'))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 11, 13], outline=C('steel'))
    for y in range(1, 13):
        if (y + n * 2) % 5 in (0, 1):
            d.line([2, y, 9, y], fill=C(['red2', 'mag3', 'gold'][(y + n) % 3]))
        elif (y + n * 2) % 5 == 3:
            d.line([3, y, 8, y], fill=C('steel'))
    return im


def slot_machine(frame):
    """Giant slot machine behind Lady Luck (80x76). Reel windows at x=14,34,54 / y=30."""
    w, h = 80, 76
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 8, w - 9, h - 1], radius=6, fill=C('red1'), outline=C('gold'))
    d.rounded_rectangle([8, 0, w - 13, 20], radius=5, fill=C('red2'), outline=C('yellow'))
    bold = assets.Font(True)
    t = 'LUCK'
    bold.draw(im, (w - 4) // 2 - bold.width(t) // 2 - 2, 6, t, P['yellow'] if frame == 0 else P['white'])
    d.rectangle([10, 26, w - 15, 49], fill=C('ink'), outline=C('gold'))
    for i, x in enumerate((12, 32, 52)):
        d.rectangle([x, 28, x + 13, 47], fill=C('night1'))
    # payout tray, coin slot and buttons
    d.rectangle([14, 56, w - 19, 62], fill=C('night2'), outline=C('gold'))
    for i, col in enumerate(('mag3', 'cyan3', 'yellow')):
        d.rectangle([16 + i * 14, 66, 24 + i * 14, 69], fill=C(col))
    # marquee bulbs, alternating each frame
    for i, (bx, by) in enumerate([(x, 22) for x in range(8, w - 10, 5)] + [(5, y) for y in range(26, h - 4, 6)] + [(w - 10, y) for y in range(26, h - 4, 6)]):
        im.putpixel((bx, by), C('yellow' if (i + frame) % 2 else 'white'))
    # lever
    d.line([w - 6, 30, w - 6, 50], fill=C('steel'))
    d.line([w - 9, 50, w - 6, 50], fill=C('steel'))
    d.ellipse([w - 9, 25, w - 3, 31], fill=C('red3'), outline=C('red1'))
    return im


def jackpot_sign(on):
    bold = assets.Font(True)
    t = 'JACKPOT'
    w = bold.width(t) + 10
    im = Image.new('RGBA', (w, 15), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, 14], fill=C('ink', 220), outline=C('mag2' if on else 'mag1'))
    if on:
        bold.draw(im, 5, 3, t, P['yellow'], P['red2'])
    else:
        bold.draw(im, 5, 3, t, P['brown'])
    return im


def pachinko_prop(n):
    im = Image.new('RGBA', (16, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pachinko_cabinet(d, 0, 0, 16, 30, n * 2)
    d.rectangle([0, 0, 15, 29], outline=C('ink'))
    return im


def preview(path):
    """Contact sheet of the generated art, for eyeballing."""
    sheet = Image.new('RGBA', (240 * 3 + 20, 400), C('slate1'))
    for i, layer in enumerate((sky(), far(), mid())):
        sheet.alpha_composite(layer, (i * 245, 0))
    comp = sky()
    comp.alpha_composite(far())
    comp.alpha_composite(mid())
    sheet.alpha_composite(comp, (0, 185))
    x = 250
    for name in ('idle_0', 'attack1_1', 'attack2_2', 'heavy_3', 'dash_1', 'deflect_0', 'hurt_0'):
        c = [r for r in recolor_costumes('Mukuro', LUCK_MAP) if r[0] == name][0]
        im = c[1].resize((c[1].width // 4, c[1].height // 4), Image.NEAREST)
        sheet.alpha_composite(im, (x, 190))
        x += 50
    x = 250
    for name in ('idle_0', 'attack_2', 'attack_4', 'walk_2'):
        c = [r for r in recolor_costumes('HannyaBoy', CROUPIER_MAP) if r[0] == name][0]
        im = c[1].resize((c[1].width // 4, c[1].height // 4), Image.NEAREST)
        sheet.alpha_composite(im, (x, 235))
        x += 50
    for i, c in enumerate(recolor_costumes('Turret', SLOT_TURRET_MAP)[:3]):
        im = c[1].resize((c[1].width // 4, c[1].height // 4), Image.NEAREST)
        sheet.alpha_composite(im, (450 + i * 24, 240))
    sheet.alpha_composite(slot_machine(0), (250, 280))
    for i, s in enumerate(SYMBOLS):
        sheet.alpha_composite(symbol(s), (262 + i * 14, 362))
    sheet.alpha_composite(luck_portrait(), (340, 280))
    sheet.alpha_composite(nameplate('LADY LUCK'), (340, 325))
    for i, f in enumerate(card_frames()):
        sheet.alpha_composite(f, (390 + i * 12, 280))
    sheet.alpha_composite(jackpot_sign(True), (390, 300))
    sheet.alpha_composite(pachinko_prop(0), (390, 320))
    atlas = vaults_atlas()
    sheet.alpha_composite(atlas, (480, 280))
    sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
    sheet.save(path)


def cage(stage):
    """Cashier's cage around DaiCam: 0 intact, 1 dented, 2 broken (28x40)."""
    w, h = 28, 40
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if stage < 2:
        d.rectangle([0, 0, w - 1, 3], fill=C('gold'), outline=C('brown'))
        d.rectangle([0, h - 4, w - 1, h - 1], fill=C('gold'), outline=C('brown'))
        for i, x in enumerate(range(1, w, 4)):
            bend = 1 if (stage == 1 and i in (3, 4)) else 0
            d.line([x, 4, x + bend, h // 2], fill=C('yellow'))
            d.line([x + bend, h // 2, x, h - 5], fill=C('gold'))
        bold = assets.Font(True)
        d.rectangle([7, 14, 20, 22], fill=C('red2'), outline=C('yellow'))
        bold.draw(im, 9, 14, '$', P['yellow'])
    else:
        d.rectangle([0, h - 4, w - 1, h - 1], fill=C('gold'), outline=C('brown'))
        for x in (1, 5, 22, 26):
            d.line([x, h - 5, x + (2 if x < 14 else -2), h - 14], fill=C('gold'))
    return im
