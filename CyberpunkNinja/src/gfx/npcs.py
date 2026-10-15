"""
Townspeople and the Spire Lobby: the hand-drawn civilians and receptionist from
art/characters/ (given a breathing idle and a run), the reception desk and the
lobby sign.


All functions return 1x art-pixel images unless noted.
"""
import os

from PIL import Image, ImageDraw

import assets
from assets import PALETTE as P
from gfx.ui import tiny_text, tiny_width
from gfx.util import C


SRC = assets.art_path('characters')
CIVILIANS = 4                           # art/characters/civilians.png: four 14x28 townsfolk, facing right


def breathe(im, waist):
    """An idle breath: everything above the waist row settles one pixel."""
    out = im.copy()
    top = im.crop((0, 0, im.width, waist))
    out.paste((0, 0, 0, 0), (0, 0, im.width, waist + 1))
    out.alpha_composite(top, (0, 1))
    return out


def civilian(i, frame):
    """Townsperson i (debtors, captives) from art/characters/civilians.png, centered on a 14x28
    canvas (bottom-center). The figures sit wherever they were drawn on the strip, split on
    their empty columns. Frame 1 is the out-breath."""
    sheet = Image.open(os.path.join(SRC, 'civilians.png')).convert('RGBA')
    alpha = sheet.getchannel('A')
    filled = [any(alpha.getpixel((x, y)) for y in range(sheet.height)) for x in range(sheet.width)]
    spans, x = [], 0
    while x < sheet.width:
        if filled[x]:
            x0 = x
            while x < sheet.width and filled[x]:
                x += 1
            spans.append((x0, x))
        x += 1
    assert len(spans) == CIVILIANS, 'expected %d figures in civilians.png, found %d' % (CIVILIANS, len(spans))
    x0, x1 = spans[i]
    im = Image.new('RGBA', (14, 28), (0, 0, 0, 0))
    im.alpha_composite(sheet.crop((x0, 0, x1, 28)), ((14 - (x1 - x0)) // 2, 0))
    return breathe(im, 15) if frame else im


def stride(im, k, top=19):
    """A running step from a standing figure: below the hips the legs part (k = 1) or cross
    (k = -1) by a pixel each side of their middle, and the body above lifts a pixel."""
    w, h = im.size
    px = im.load()
    cols = [x for x in range(w) for y in range(top, h) if px[x, y][3]]
    mid = (min(cols) + max(cols)) / 2
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.alpha_composite(im.crop((0, 0, w, top)), (0, -1))
    op = out.load()
    for y in range(top, h):
        for x in range(w):
            if px[x, y][3]:
                nx = x + (k if x > mid else -k)
                if 0 <= nx < w:
                    op[nx, y - (1 if y < top + 2 else 0)] = px[x, y]
    for x in range(w):
        if px[x, top][3] and not op[x, top - 1][3]:
            op[x, top - 1] = px[x, top]
    return out


def civilian_run(i, frame):
    """Townsperson i running (four frames: legs apart, passing, crossed, passing), facing right."""
    base = civilian(i, 0)
    return (stride(base, 1), base, stride(base, -1), base)[frame]


def receptionist(frame):
    """The Spire Lobby's receptionist (art/characters/receptionist.png), turned to face the door, 18x29."""
    im = Image.open(os.path.join(SRC, 'receptionist.png')).convert('RGBA').transpose(Image.FLIP_LEFT_RIGHT)
    return breathe(im, 16) if frame else im


def desk(frame=0, staffed=True):
    """The Spire Lobby's reception desk, with the receptionist behind it until he jumps it, 72x30 (bottom-center)."""
    im = Image.new('RGBA', (72, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if staffed:
        im.alpha_composite(receptionist(frame), (37, -2))
    # a terminal on the counter
    d.rectangle([12, 6, 24, 14], fill=C('ink'), outline=C('slate2'))
    d.rectangle([14, 8, 22, 12], fill=C('cyan1'))
    d.line([15, 9, 20, 9], fill=C('cyan3'))
    d.line([15, 11, 18, 11], fill=C('cyan2'))
    # the counter: a glossy top, a dark front with the Kanshi diamond, a lit kick strip
    d.rectangle([0, 15, 71, 29], fill=C('night2'), outline=C('ink'))
    d.line([0, 15, 71, 15], fill=C('steel'))
    d.line([1, 16, 70, 16], fill=C('slate2'))
    d.line([1, 27, 70, 27], fill=C('cyan2'))
    d.polygon([(36, 18), (40, 22), (36, 26), (32, 22)], fill=C('red2'), outline=C('red3'))
    d.point([(36, 22)], fill=C('white'))
    return im


def directory():
    """The Spire Lobby's sign over the desk: the welcome over two lines, and Kanshi's motto
    in small grey type. 72 px wide at most, to sit inside the dark panel behind the desk."""
    f = assets.Font(False)
    lines = ['Welcome to', 'Kanshi Spire']
    motto = 'Invent the Future'
    w = max(max(f.width(t) for t in lines), tiny_width(motto)) + 4
    assert w <= 72, ('lobby sign too wide', w)
    im = Image.new('RGBA', (w, 30), C('ink'))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, 29], outline=C('cyan2'))
    for k, t in enumerate(lines):
        f.draw(im, (w - f.width(t)) // 2, 2 + k * 9, t, P['white'])
    tiny_text(im, (w - tiny_width(motto)) // 2, 22, motto, C('steel'))
    return im
