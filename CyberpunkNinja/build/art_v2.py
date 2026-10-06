"""
Art for the 8-chapter story: new portraits, chapter cards, the Sewers chapter,
Dobunushi, the Harmacist, the Physic Gardens props, hollowed soldiers and the
Daimyo in person. Everything is drawn in the pack's 34-color palette.

All functions return 1x art-pixel images unless noted.
"""
import math
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
    'red2': 'green1', 'mag1': 'night2', 'skin2': 'green2', 'skin1': 'green1', 'red1': 'slate1',
    'white': 'lime', 'yellow': 'lime', 'gold': 'green2', 'steel': 'slate3', 'night3': 'slate1',
    'mag3': 'lime', 'slate3': 'slate2',
}


def drainling_frame(im1x, seed):
    """A Hannya Boy re-dyed as a sewer mutant, with runoff dripping off him."""
    from art_ch2 import recolor
    im = recolor(im1x, DRAIN_MAP)
    px = im.load()
    rng = random.Random(seed)
    w, h = im.size
    greens = {P['green1'], P['green2']}
    spots = [(x, y) for y in range(h - 1) for x in range(w)
             if px[x, y][3] and px[x, y][:3] in greens and not px[x, y + 1][3]]
    for x, y in rng.sample(spots, min(5, len(spots))):
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
    """The fused mass, 104x72, anchored bottom-center. state: idle, open, spew, dead."""
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
    for _ in range(14):
        x, y = rng.randrange(8, 96), rng.randrange(20, 70)
        if im.getpixel((x, y))[3]:
            im.putpixel((x, y), C('lime' if rng.random() < 0.3 else 'green2'))
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
