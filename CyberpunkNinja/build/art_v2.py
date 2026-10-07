"""
Art for the 8-chapter story: new portraits, chapter cards, the Sewers chapter,
Dobunushi, the Harmacist, the Physic Gardens props, hollowed soldiers and the
Daimyo in person. Everything is drawn in the pack's 34-color palette.

All functions return 1x art-pixel images unless noted.
"""
import math
import os
import random

from PIL import Image, ImageDraw

from assets import PALETTE as P
from art_ch2 import st


def C(name, a=255):
    return P[name] + (a,)


# ------------------------------------------------------------------ portraits
def portrait_base(top, bottom, dot):
    """40x40 frame in the pack's portrait style: cyan border, dithered backdrop."""
    frame = st().image_1x('Portraits', 'tetsu_neutral')
    im = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
    fp, px = frame.load(), im.load()
    rng = random.Random(len(top) * 7 + len(dot))
    for y in range(40):
        for x in range(40):
            p = fp[x, y]
            if not p[3]:
                continue
            if p[:3] == P['cyan2'] and (x in (0, 1, 38, 39) or y in (0, 1, 38, 39)):
                px[x, y] = p
            else:
                t = y / 39
                px[x, y] = C(bottom) if (x * 3 + y * 5) % 7 < t * 7 else C(top)
                if rng.random() < 0.06:
                    px[x, y] = C(dot)
    return im


def oni_portrait():
    im = portrait_base('night1', 'red1', 'orange')
    d = ImageDraw.Draw(im)
    # shoulders and jacket
    d.rectangle([6, 30, 33, 37], fill=C('red2'))
    d.rectangle([17, 30, 22, 37], fill=C('night1'))
    d.line([6, 30, 33, 30], fill=C('red3'))
    d.point([(25, 33), (25, 34)], fill=C('cyan3'))
    # horns
    d.polygon([(11, 9), (8, 2), (14, 8)], fill=C('white'))
    d.polygon([(28, 9), (31, 2), (25, 8)], fill=C('white'))
    # mask
    d.rectangle([11, 8, 28, 28], fill=C('red2'), outline=C('ink'))
    d.rectangle([12, 9, 27, 11], fill=C('red3'))
    d.line([12, 14, 18, 16], fill=C('ink'), width=2)
    d.line([27, 14, 21, 16], fill=C('ink'), width=2)
    d.rectangle([14, 16, 16, 17], fill=C('yellow'))
    d.rectangle([23, 16, 25, 17], fill=C('yellow'))
    d.line([19, 18, 20, 18], fill=C('red1'))
    d.rectangle([13, 21, 26, 26], fill=C('ink'))
    for x in range(14, 26, 2):
        d.rectangle([x, 21, x, 23], fill=C('white'))
    d.polygon([(14, 26), (15, 23), (16, 26)], fill=C('white'))
    d.polygon([(23, 26), (24, 23), (25, 26)], fill=C('white'))
    return im


def harm_portrait():
    im = portrait_base('night1', 'green1', 'lime')
    d = ImageDraw.Draw(im)
    # lab coat, collar and the vial bandolier
    d.polygon([(5, 38), (8, 29), (31, 29), (34, 38)], fill=C('white'))
    d.polygon([(15, 29), (19, 36), (20, 36), (24, 29)], fill=C('slate2'))
    d.line([8, 31, 31, 37], fill=C('brown'), width=2)
    for i, col in enumerate(('lime', 'green2', 'mag3', 'lime')):
        x = 11 + i * 5
        y = 32 + i
        d.rectangle([x, y - 2, x + 1, y], fill=C(col))
    # neck, face
    d.rectangle([17, 25, 22, 29], fill=C('skin2'))
    d.ellipse([12, 10, 27, 27], fill=C('skin3'), outline=C('skin1'))
    # dark hair in a tight bun, with a stick through it
    d.pieslice([11, 7, 28, 24], 180, 360, fill=C('night2'))
    d.rectangle([11, 14, 13, 22], fill=C('night2'))
    d.ellipse([16, 3, 23, 9], fill=C('night2'))
    d.line([13, 4, 26, 8], fill=C('gold'))
    # green lens goggles pushed down over the eyes
    d.rectangle([12, 16, 27, 19], fill=C('slate1'))
    d.rectangle([13, 17, 18, 18], fill=C('lime'))
    d.rectangle([21, 17, 26, 18], fill=C('lime'))
    d.point([(14, 17), (22, 17)], fill=C('white'))
    # thin smile, painted lips
    d.line([17, 23, 22, 23], fill=C('red2'))
    d.point([(16, 22), (23, 22)], fill=C('red2'))
    return im


# ------------------------------------------------------------------ Chapter 2: the Sewers
def gradient(im, y0, y1, a, b):
    """Vertical dithered blend between two palette colors over rows y0..y1."""
    px = im.load()
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        for x in range(im.width):
            px[x, y] = C(b) if ((x * 5 + y * 3) % 8) / 8 < t else C(a)


def sewer_atlas():
    """The Sump's tiles, stained: violet stone to wet slate, moss and runoff for the accents."""
    import assets
    from art_ch2 import recolor
    atlas = Image.open(assets.pack_path('tilesets', 'sump_atlas_8x8.png')).convert('RGBA')
    return recolor(atlas, {'night2': 'slate1', 'night1': 'night2', 'slate1': 'slate2', 'slate3': 'green2',
                           'cyan1': 'green1', 'cyan3': 'lime', 'cyan4': 'lime', 'mag3': 'lime'})


def toxic_tile(surface, frame=0):
    """8x8 cell of glowing Kanshi runoff; `surface` draws the bright top edge."""
    im = Image.new('RGBA', (8, 8), C('green1'))
    d = ImageDraw.Draw(im)
    for y in range(8):
        for x in range(8):
            if (x * 3 + y * 5 + frame) % 9 == 0:
                im.putpixel((x, y), C('green2'))
    if surface:
        d.line([0, 0, 7, 0], fill=C('lime'))
        d.line([0, 1, 7, 1], fill=C('green2'))
        for x in ((1 + frame * 3) % 8, (5 + frame * 3) % 8):
            im.putpixel((x, 0), C('white'))
    im.putpixel(((2 + frame * 5) % 8, 4), C('lime'))
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


def heat_vent(frame):
    """The Physic Gardens' greenhouse heat: warm shimmer instead of coolant mist."""
    import art_ch3
    from art_ch2 import recolor
    return recolor(art_ch3.mist(frame), {'cyan4': 'yellow', 'white': 'white', 'cyan3': 'orange', 'cyan2': 'red3'})


# ------------------------------------------------------------------ chapter cards
CARDS = [
    ('PROLOGUE', 'THE SUMP', '沈殿'), ('CHAPTER 1', 'NEON ALLEY', 'ネオン横丁'),
    ('CHAPTER 2', 'THE SEWERS', '下水道'), ('CHAPTER 3', 'PACHINKO VAULTS', '金庫'),
    ('CHAPTER 4', 'PHYSIC GARDENS', '薬草園'), ('CHAPTER 5', 'MONORAIL ASCENT', '登り線'),
    ('CHAPTER 6', 'HOLLOW FLOOR', '虚ろ'), ('CHAPTER 7', 'THE ACADEMY', '忍道場'),
    ('CHAPTER 8', 'THE TENSHU', '天守'),
]


def _kanji(text):
    from PIL import ImageFont
    font = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 12, index=1)
    w = int(font.getlength(text)) + 2
    im = Image.new('L', (w, 14), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    d.text((0, 0), text, fill=255, font=font)
    return im


def chapter_card(i):
    """200x44 card in the pack's ChapterCards style for chapter i (0 = prologue)."""
    import assets
    label, title, kanji = CARDS[i]
    base = st().image_1x('ChapterCards', 'ch0')
    im = base.copy()
    px = im.load()
    for y in range(1, 43):
        bg = px[194, y]
        for x in range(1, 196):
            if px[x, y][3] and px[x, y][:3] != P['mag2']:
                px[x, y] = bg
    reg, bold = assets.Font(False), assets.Font(True)
    reg.draw(im, 10, 6, label, P['mag3'])
    lx = 10 + reg.width(label) + 6
    ImageDraw.Draw(im).line([lx, 9, 188, 9], fill=C('mag1'))
    # kanji watermark, bottom right
    kj = _kanji(kanji)
    kx = 192 - kj.width
    for y in range(kj.height):
        for x in range(kj.width):
            if kj.getpixel((x, y)) > 128 and 0 < kx + x < 196:
                px[kx + x, 26 + y] = C('mag1')
    # title: white over cyan, with an ink outline and a dark cyan drop shadow, at 2x
    # (the regular face when the bold one is too wide)
    font = bold if (bold.width(title) + 8) * 2 <= 188 else reg
    tw = font.width(title) + 4
    t = Image.new('RGBA', (tw, 12), (0, 0, 0, 0))
    font.draw(t, 1, 1, title, P['white'])
    tp = t.load()
    for y in range(t.height):
        for x in range(t.width):
            if tp[x, y][3] and y > 4:
                tp[x, y] = C('cyan3')
    out = Image.new('RGBA', (tw + 2, 14), (0, 0, 0, 0))
    mask = t.split()[3]
    out.paste(Image.new('RGBA', t.size, C('cyan1')), (2, 2), mask)
    ink = Image.new('RGBA', t.size, C('ink'))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.paste(ink, (1 + dx, 1 + dy), mask)
    out.alpha_composite(t, (1, 1))
    out = out.resize((out.width * 2, out.height * 2), Image.NEAREST)
    im.alpha_composite(out, (6, 15))
    return im


def boss_plate(text):
    """96x11 boss name plate in the style of the pack's NamePlates."""
    import assets
    im = st().image_1x('NamePlates', 'boss_big_oni').copy()
    px = im.load()
    bg = px[48, 1]
    for y in range(1, im.height - 1):
        for x in range(2, im.width - 2):
            if px[x, y][3] and px[x, y][:3] != P['red2']:
                px[x, y] = bg
    font = assets.Font(True)
    if font.width(text) > im.width - 8:
        font = assets.Font(False)
    font.draw(im, (im.width - font.width(text)) // 2, 2, text, P['white'])
    return im


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
    import assets
    im = Image.new('RGBA', (76, 30), C('ink'))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 75, 29], outline=C('green2'))
    d.line([0, 9, 75, 9], fill=C('green1'))
    f = assets.Font(False)
    f.draw(im, 3, 1, 'KANSHI CLEAR', P['lime'])
    f.draw(im, 3, 11, 'COST    4 CR', P['steel'])
    f.draw(im, 3, 20, 'PRICE 2400 CR', P['red3'] if frame else P['red2'])
    return im


def debtor(frame):
    """A debtor in line, head down, 10x30 (bottom-center)."""
    im = Image.new('RGBA', (10, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([3, 22, 4, 29], fill=C('slate1'))
    d.rectangle([6, 22, 7, 29], fill=C('slate1'))
    d.rectangle([2, 11 + frame, 8, 23], fill=C('slate2'), outline=C('slate1'))
    d.ellipse([3, 5 + frame, 8, 11 + frame], fill=C('skin1'))
    d.line([3, 6 + frame, 8, 6 + frame], fill=C('night2'))
    d.line([1, 13 + frame, 1, 20], fill=C('slate2'))
    d.line([9, 13 + frame, 9, 20], fill=C('slate2'))
    d.rectangle([2, 15, 8, 16], fill=C('red1'))
    return im


def soldier():
    """A hollowed soldier at attention: Kanshi armor, an empty white visor, 14x36 (bottom-center)."""
    im = Image.new('RGBA', (14, 36), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([3, 26, 5, 35], fill=C('night2'))
    d.rectangle([8, 26, 10, 35], fill=C('night2'))
    d.rectangle([2, 34, 5, 35], fill=C('slate2'))
    d.rectangle([8, 34, 11, 35], fill=C('slate2'))
    d.rectangle([2, 12, 11, 26], fill=C('night2'), outline=C('ink'))
    d.line([2, 12, 11, 12], fill=C('red2'))
    d.rectangle([5, 16, 8, 22], fill=C('slate1'))
    d.line([1, 13, 1, 24], fill=C('night2'))
    d.line([12, 13, 12, 24], fill=C('night2'))
    d.rectangle([0, 12, 2, 15], fill=C('red1'))
    d.rectangle([11, 12, 13, 15], fill=C('red1'))
    d.ellipse([3, 2, 10, 11], fill=C('night1'), outline=C('ink'))
    d.rectangle([4, 6, 9, 7], fill=C('white'))
    d.line([2, 2, 11, 2], fill=C('slate2'))
    return im


def banner_word(word):
    """A big gold banner word in the style of the pack's SEVERANCE banner (2x pixel text)."""
    import assets
    bold = assets.Font(True)
    tw = bold.width(word) + 4
    t = Image.new('RGBA', (tw, 12), (0, 0, 0, 0))
    bold.draw(t, 1, 1, word, P['yellow'])
    tp = t.load()
    for y in range(t.height):
        for x in range(t.width):
            if tp[x, y][3] and y > 4:
                tp[x, y] = C('gold')
    mask = t.split()[3]
    out = Image.new('RGBA', (tw + 3, 15), (0, 0, 0, 0))
    out.paste(Image.new('RGBA', t.size, C('red1')), (2, 3), mask)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.paste(Image.new('RGBA', t.size, C('ink')), (1 + dx, 1 + dy), mask)
    out.alpha_composite(t, (1, 1))
    return out.resize((out.width * 2, out.height * 2), Image.NEAREST)


# ------------------------------------------------------------------ Drainlings
DRAIN_MAP = {
    # a rotting, irradiated body: ashen gray skin, rags, a rusted pipe
    'red2': 'slate3', 'red1': 'lime', 'yellow': 'slate3', 'skin2': 'slate3', 'skin1': 'slate2',
    'night3': 'night2', 'mag1': 'slate1', 'gold': 'brown', 'slate1': 'night1', 'slate2': 'slate1',
    'steel': 'skin1', 'slate3': 'brown', 'mag2': 'green2', 'mag3': 'lime',
}


def drainling_frame(im1x, seed):
    """A Hannya Boy turned sewer zombie: no mask or horns, ashen skin, radioactive pustules."""
    from art_ch2 import recolor
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
    Built on the hand-edited base in art/src when it's there."""
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


DOBU_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'src', 'dobunushi_base.png')
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
DM_DEAD = [
"...............................................p",
".......................................p........",
"...........................................p....",
"....................................kk..........",
"..................................kk22k.........",
"................................kk222222kk......",
"...............................kS2kk222222kss...",
"..........................kkkkkSS2222222222ksss.",
"...........kkkkkkkkkkkkkkNNNNrrkSS2222222kkssk..",
".....kk...knnnnnnnnnnnnkNNNNNNNrkkk22222k.kk....",
"....kbbk.knnnknnnnnnnkkoooNNoNNNNNkkkkkk........",
"....kbbkknnnnnknnnnnnnkoooNoNoNNNNk.............",
"....kbbknnnnnnnknnnnnnkoooNNoNNNNk22k...........",
".....kkknnnnnnnnnnnnnnkoooNNNNNNk.k22k..........",
".......kkkkkkkkkkkkkkkkkkkkkkkkkk..k22kobkDDSSSc",
"...........................RRRRRRRRRRRRRR.......",
]


# ------------------------------------------------------------------ The Harmacist
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


HARM_FRAMES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'art', 'src', 'harmacist_frames')
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
    return out


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


# ------------------------------------------------------------------ hollowed fighters (Mukuro's rig)
# Kuro's former students in their training gi; the Tenshu's hollowed soldiers in lacquered armor.
# Either way the eyes are blank white.
TRAINEE_MAP = {'night1': 'slate1', 'night2': 'slate2', 'night3': 'slate3', 'indigo': 'steel',
               'red2': 'white', 'red3': 'red2', 'slate2': 'steel', 'slate3': 'white'}
SOLDIER_MAP = {'night3': 'indigo', 'indigo': 'slate3', 'red2': 'white', 'red3': 'red2',
               'slate2': 'slate1', 'slate3': 'slate2', 'yellow': 'gold'}


# ------------------------------------------------------------------ the Daimyo, in person
MAN_W, MAN_H = 40, 36
MAN_FOOT = (17, 35)
MAN_POSES = {
    # blade (hilt x, y, angle), lean, stride, hand open (soul grab)
    'idle': ((22, 22, -40), 0, 2, False),
    'walk': ((22, 22, -35), 1, 4, False),
    'wind': ((10, 22, 200), -1, 3, False),
    'cut': ((24, 18, 5), 3, 7, False),
    'feint': ((12, 20, 150), 0, 3, False),
    'grab0': ((10, 24, 210), -1, 3, True),
    'grab1': ((10, 24, 210), 3, 8, True),
    'hurt': ((20, 26, -70), -2, 1, False),
}


def daimyo_man(pose='idle', frame=0):
    """The Daimyo out of his armor: an old man in black and gold with Tamakiri. Faces right."""
    if pose == 'dead':
        return pix_grid(DM_DEAD, 48, 16)
    im = Image.new('RGBA', (MAN_W, MAN_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    (hx, hy, ang), lean, step, grab = MAN_POSES[pose]
    bob = frame % 2 if pose in ('idle', 'walk') else 0
    cx0 = 17 + lean
    top = 10 + bob
    # hakama (wide trousers) and sandals
    d.polygon([(cx0 - 5, 24), (cx0 + 5, 24), (cx0 + 5 + step // 2, 34), (cx0 - 6 - step // 2, 34)],
              fill=C('night1'), outline=C('ink'))
    d.line([cx0, 25, cx0, 33], fill=C('ink'))
    d.point([(cx0 - 6 - step // 2, 35), (cx0 + 5 + step // 2, 35)], fill=C('brown'))
    # black kimono with a gold mon and red under-collar
    d.polygon([(cx0 - 5, top + 3), (cx0 + 5, top + 3), (cx0 + 6, 25), (cx0 - 6, 25)], fill=C('night2'),
              outline=C('ink'))
    d.line([cx0 - 2, top + 3, cx0 + 2, top + 9], fill=C('red2'))
    d.rectangle([cx0 - 5, 22, cx0 + 6, 23], fill=C('gold'))
    d.ellipse([cx0 - 3, top + 8, cx0, top + 11], outline=C('gold'))
    # head: shaved, gray topknot, hard eyes, a thin beard
    d.ellipse([cx0 - 3, top - 7, cx0 + 4, top + 2], fill=C('skin2'), outline=C('ink'))
    d.rectangle([cx0 - 2, top - 9, cx0, top - 7], fill=C('steel'))
    d.line([cx0 + 1, top - 3, cx0 + 3, top - 3], fill=C('ink'))
    d.line([cx0 + 1, top + 1, cx0 + 3, top + 2], fill=C('slate3'))
    # Tamakiri: a long blade that glows like a cut in the air
    a = math.radians(ang)
    tip = (hx + math.cos(a) * 17, hy - math.sin(a) * 17)
    d.line([cx0 + 2, top + 5, hx, hy], fill=C('night2'), width=2)
    d.line([(hx, hy), (hx - math.cos(a) * 3, hy + math.sin(a) * 3)], fill=C('gold'), width=2)
    d.line([(hx, hy), tip], fill=C('cyan4'))
    d.line([(hx + math.cos(a) * 3, hy - math.sin(a) * 3), tip], fill=C('purple3'))
    if grab:
        # the free hand reaches out, glowing: the soul grab
        gx = cx0 + 8 + (6 if pose == 'grab1' else 0)
        d.line([cx0 + 3, top + 5, gx, top + 6], fill=C('night2'), width=2)
        for k in range(3):
            d.point((gx + 1, top + 4 + k * 2), fill=C('skin2'))
        d.ellipse([gx - 1, top + 2, gx + 5, top + 10], outline=C('purple3'))
    return im


def cable():
    """A bundle of Tenshu cables, 6x110 (bottom-center), hanging from the ceiling."""
    im = Image.new('RGBA', (6, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x, col in ((1, 'night2'), (3, 'slate1'), (4, 'night2')):
        d.line([x, 0, x, 109], fill=C(col))
    for y in range(4, 110, 13):
        d.point((2, y), fill=C('red3'))
    return im


# ------------------------------------------------------------------ Physic Gardens: front parallax
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


# ------------------------------------------------------------------ monorail: robotic crows
CROW = [[
"..........kkk...........",
".........kSSSk..........",
"........kSssSSk.........",
"..kkk..kSsssSSSk........",
".kSSDk.kSsssSSSSk.......",
"kDSDDDkkkSsSSSSSSk......",
".kkDDDDDSSDDDDDDDSkk....",
"kyrkDDDDDDDDDDDDDDDDkkk.",
"kkkkkDDDDDDDDDDDDDDkDDDk",
"...kkkkDDDDDDDDDkkkk.kkk",
"......kkkkkDkkkkk.......",
"..........kok...........",
"..........k.k...........",
"........................",
], [
"........................",
"........................",
"........................",
"..kkk...................",
".kSSDk..................",
"kDSDDDk.................",
".kkDDDDkkkkkkkkkkkk.....",
"kyrkDDDDDDDDDDDDDDDkkkk.",
"kkkkkDDDDSSSDDDDDDDkDDDk",
"...kkkkDDSsssSDDDkkk.kkk",
"......kkkSsssSSkkk......",
".........kSssSk.........",
"..........kSSk..........",
"...........kk...........",
]]


def robo_crow(frame):
    """A Kanshi surveillance crow, 24x14, flying left, red eye and a signal light."""
    return pix_grid(CROW[frame % 2], 24, 14)


# ------------------------------------------------------------------ Hollow Floor: background glitches
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


# ------------------------------------------------------------------ the Daimyo's slash wave
def crescent(frame):
    """A crescent of Tamakiri's red edge flung through the air, 14x20, travelling right."""
    im = Image.new('RGBA', (14, 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 13, 19], fill=C('red2'))
    d.ellipse([-5 + frame, 2, 9 + frame, 17], fill=(0, 0, 0, 0))
    px = im.load()
    for y in range(20):
        row = [x for x in range(14) if px[x, y][3]]
        if row:
            px[row[-1], y] = C('white')          # the hot outer edge
            if len(row) > 2:
                px[row[0], y] = C('red3')
    return im
