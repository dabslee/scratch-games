"""
Dialogue portraits drawn in code: Lady Luck, the Kanshi system log, Big Oni and
the Harmacist, plus the dithered backdrop the hand-drawn ones are set on.

The game reads its portraits from the sheet in art/portraits/, which is the
source of truth; export_portraits.py only redraws these on --reset.


All functions return 1x art-pixel images unless noted.
"""
import random

from PIL import Image, ImageDraw

from assets import PALETTE as P
from gfx.util import C, recolor, st


PORTRAIT_MAP = {
    'night1': 'purple1', 'night2': 'mag1', 'red1': 'brown', 'red2': 'gold', 'red3': 'yellow',
    'cyan2': 'mag3', 'slate1': 'slate3', 'slate2': 'steel', 'slate3': 'white',
}


def luck_portrait():
    im = recolor(st().image_1x('Portraits', 'mukuro_neutral'), PORTRAIT_MAP)
    d = ImageDraw.Draw(im)
    # a gold card held up at the left edge of the frame
    d.rectangle([4, 24, 11, 34], fill=C('white'), outline=C('gold'))
    d.point([(7, 28), (8, 28), (7, 29), (8, 29), (6, 29), (9, 29), (7, 30), (8, 30)], fill=C('red2'))
    return im


def system_portrait():
    """Boot-screen portrait for the Kanshi system log."""
    im = Image.new('RGBA', (40, 40), C('ink'))
    d = ImageDraw.Draw(im)
    for y in range(0, 40, 2):
        d.line([0, y, 39, y], fill=C('night1'))
    d.ellipse([12, 6, 27, 21], outline=C('cyan2'))
    d.line([19, 4, 19, 13], fill=C('cyan3'))
    d.line([20, 4, 20, 13], fill=C('cyan3'))
    for i, (w, col) in enumerate(((30, 'cyan2'), (22, 'cyan1'), (26, 'red2'), (14, 'cyan2'))):
        d.line([5, 26 + i * 3, 5 + w, 26 + i * 3], fill=C(col))
    d.rectangle([0, 0, 39, 39], outline=C('cyan1'))
    return im


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
