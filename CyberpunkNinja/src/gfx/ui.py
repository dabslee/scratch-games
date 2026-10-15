"""
Interface art in the asset pack's style: character name plates, chapter cards,
the boss name plate, big banner words and a 3x5 pixel face for small print.


All functions return 1x art-pixel images unless noted.
"""
from PIL import Image, ImageDraw

import assets
from assets import PALETTE as P
from gfx.util import C, st


def nameplate(text, border='gold'):
    """Dialogue name tag in the style of the pack's NamePlates."""
    base = st().image_1x('NamePlates', 'name_mukuro')
    bg = (20, 15, 45, 235)
    red = P['red2'] + (255,)
    tw = assets.Font(True).width(text)
    w = tw + 12
    im = Image.new('RGBA', (w, base.height), (0, 0, 0, 0))
    left = base.crop((0, 0, 4, base.height))
    right = base.crop((base.width - 5, 0, base.width, base.height))
    mid = base.crop((5, 0, 6, base.height))
    im.paste(left, (0, 0))
    for x in range(4, w - 5):
        im.paste(mid, (x, 0))
    im.paste(right, (w - 5, 0))
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            p = px[x, y]
            if p[3] and p[:3] == P['white']:
                px[x, y] = bg
            elif p[3] and p == red:
                px[x, y] = C(border)
    assets.Font(True).draw(im, 5, 1, text, P['white'])
    return im


# ------------------------------------------------------------------ chapter cards
CARDS = [
    ('PROLOGUE', 'THE SLUMS', '貧民街'), ('CHAPTER 1', 'NEON ALLEY', 'ネオン横丁'),
    ('CHAPTER 2', 'PACHINKO', '金庫'), ('CHAPTER 3', 'THE SEWERS', '下水道'),
    ('CHAPTER 4', 'MONORAIL', '登り線'), ('CHAPTER 5', 'HOLLOW FLOOR', '虚ろ'),
    ('CHAPTER 6', 'THE GARDENS', '薬草園'), ('CHAPTER 7', 'THE ACADEMY', '忍道場'),
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


# a 3x5 pixel face for small print (case-insensitive)
TINY = {
    'a': '010101111101101', 'b': '110101110101110', 'c': '011100100100011', 'd': '110101101101110',
    'e': '111100110100111', 'f': '111100110100100', 'g': '011100101101011', 'h': '101101111101101',
    'i': '111010010010111', 'j': '001001001101010', 'k': '101101110101101', 'l': '100100100100111',
    'm': '101111111101101', 'n': '110101101101101', 'o': '010101101101010', 'p': '110101110100100',
    'q': '010101101110011', 'r': '110101110101101', 's': '011100010001110', 't': '111010010010010',
    'u': '101101101101111', 'v': '101101101101010', 'w': '101101111111101', 'x': '101101010101101',
    'y': '101101010010010', 'z': '111001010100111', ' ': '000000000000000', '-': '000000111000000',
    '.': '000000000000010', "'": '010010000000000',
}


def tiny_width(text):
    return len(text) * 4 - 1


def tiny_text(im, x, y, text, col):
    """Draw `text` in the 3x5 face with its top-left at (x, y)."""
    for i, ch in enumerate(text.lower()):
        g = TINY[ch]
        for k, bit in enumerate(g):
            if bit == '1':
                im.putpixel((x + i * 4 + k % 3, y + k // 3), col)


def banner_word(word):
    """A big gold banner word in the style of the pack's SEVERANCE banner (2x pixel text)."""
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
