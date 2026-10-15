"""
Chapter 8 (The Tenshu) art: the Daimyo in all three forms (the mech's procedural
fallback, the castle defense eye, the engram and the man himself), his slash
wave, the hollowed soldiers and the Tenshu's cables. The castle itself (tiles,
sky, fake moon) comes straight from the pack.


All functions return 1x art-pixel images unless noted.
"""
import math
import random

from PIL import Image, ImageDraw

from gfx.util import C, pix_grid


# ------------------------------------------------------------------ the exoskeleton
EXO_W, EXO_H = 84, 92
EXO_ANCHOR = (42, 91)       # feet centre

POSES = {
    # hands (x, y), sword angle in degrees (0 = forward, 90 = up), body dy, front knee raised, flame, kneel
    'idle': ((54, 52), -55, 0, False, False, False),
    'walk': ((54, 52), -50, 1, False, False, False),
    'wind': ((40, 26), 150, 0, False, False, False),
    'slash': ((66, 44), 0, 2, False, False, False),
    'low': ((60, 54), -20, 3, False, False, False),
    'stomp': ((52, 40), 100, -4, True, False, False),
    'dash': ((46, 38), 200, 2, False, True, False),
    'hurt': ((50, 54), -70, 2, False, False, False),
    'broken': ((58, 74), -80, 16, False, False, True),
}


def exo(pose='idle', frame=0):
    """The Daimyo's samurai exoskeleton, facing right."""
    hands, ang, dy, knee, flame, kneel = POSES[pose]
    dy += frame % 2 if pose in ('idle', 'walk') else 0
    im = Image.new('RGBA', (EXO_W, EXO_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lac, red, gold, steel = C('night1'), C('red2'), C('gold'), C('slate3')
    # legs
    if kneel:
        d.rectangle([28, 78, 40, 90], fill=lac, outline=C('ink'))
        d.rectangle([44, 82, 62, 90], fill=lac, outline=C('ink'))
    else:
        d.rectangle([30, 62 + dy, 38, 88], fill=lac, outline=C('ink'))
        if knee:
            d.rectangle([44, 56, 54, 66], fill=lac, outline=C('ink'))
            d.rectangle([50, 66, 58, 76], fill=lac, outline=C('ink'))
        else:
            d.rectangle([46, 62 + dy, 54, 88], fill=lac, outline=C('ink'))
        for x0 in (29, 45):
            if knee and x0 == 45:
                continue
            d.line([x0 + 1, 72, x0 + 1, 86], fill=gold)
        d.rectangle([27, 87, 40, 91], fill=steel)
        if not knee:
            d.rectangle([43, 87, 57, 91], fill=steel)
    # skirt plates (kusazuri)
    for i in range(4):
        y = 50 + dy + i * 4
        d.rectangle([22 + i, y, 60 - i, y + 3], fill=lac, outline=C('ink'))
        d.line([24 + i, y + 1, 58 - i, y + 1], fill=red if i % 2 == 0 else gold)
    # back thruster
    d.rectangle([16, 30 + dy, 22, 44 + dy], fill=steel, outline=C('ink'))
    if flame:
        for k, col in enumerate(('white', 'cyan3', 'cyan2')):
            d.polygon([(16, 32 + dy + k), (4 - k * 3, 37 + dy), (16, 42 + dy - k)], fill=C(col))
    # torso (do) with lacing
    d.rectangle([26, 28 + dy, 56, 52 + dy], fill=lac, outline=C('ink'))
    for y in range(31 + dy, 50 + dy, 3):
        d.line([28, y, 54, y], fill=red)
    d.line([26, 28 + dy, 56, 28 + dy], fill=gold)
    if kneel:
        # cracked open: the core shows through
        d.polygon([(38, 30 + dy), (44, 38 + dy), (40, 46 + dy), (46, 52 + dy)], outline=C('cyan3'))
        d.ellipse([36, 36 + dy, 46, 46 + dy], fill=C('cyan3'))
        d.ellipse([39, 39 + dy, 43, 43 + dy], fill=C('white'))
    # back shoulder guard
    d.rectangle([16, 26 + dy, 28, 44 + dy], fill=red, outline=C('ink'))
    for y in range(29 + dy, 44 + dy, 4):
        d.line([17, y, 27, y], fill=gold)
    # helmet, crest and mask
    hy = 10 + dy
    d.pieslice([28, hy, 54, hy + 26], 180, 360, fill=lac, outline=C('ink'))
    d.rectangle([28, hy + 12, 54, hy + 15], fill=lac)
    d.polygon([(26, hy + 12), (30, hy + 6), (32, hy + 14)], fill=red)
    d.polygon([(56, hy + 12), (52, hy + 6), (50, hy + 14)], fill=red)
    d.arc([26, hy - 8, 56, hy + 8], 200, 340, fill=gold, width=2)
    d.polygon([(40, hy - 2), (44, hy - 2), (42, hy + 2)], fill=gold)
    d.rectangle([36, hy + 15, 50, hy + 25], fill=C('red1'), outline=C('ink'))
    eye = C('yellow') if not kneel else C('slate3')
    d.line([39, hy + 18, 42, hy + 18], fill=eye)
    d.line([45, hy + 18, 48, hy + 18], fill=eye)
    d.line([38, hy + 22, 48, hy + 22], fill=C('white'))
    # sword (nodachi) and front arm
    hx, hyy = hands
    hyy += dy if not kneel else 0
    a = math.radians(ang)
    tip = (hx + math.cos(a) * 48, hyy - math.sin(a) * 48)
    pommel = (hx - math.cos(a) * 9, hyy + math.sin(a) * 9)
    d.line([pommel, (hx, hyy)], fill=C('red1'), width=3)
    d.line([(hx, hyy), tip], fill=C('white'), width=2)
    d.line([(hx + math.cos(a) * 3, hyy - math.sin(a) * 3), tip], fill=C('steel'))
    d.line([(52, 34 + dy), (hx, hyy)], fill=lac, width=6)
    d.ellipse([hx - 3, hyy - 3, hx + 3, hyy + 3], fill=steel)
    # front shoulder guard
    d.rectangle([48, 26 + dy, 60, 42 + dy], fill=red, outline=C('ink'))
    for y in range(29 + dy, 42 + dy, 4):
        d.line([49, y, 59, y], fill=gold)
    return im


# ------------------------------------------------------------------ the castle defense AI
def eye(state='idle', frame=0):
    """A floating crest (mon) with a single eye, 48x48."""
    im = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([2, 2, 45, 45], fill=C('night1'), outline=C('gold'))
    d.ellipse([5, 5, 42, 42], outline=C('gold'))
    for k in range(8):
        a = math.radians(k * 45 + frame * 11)
        d.line([24 + math.cos(a) * 12, 24 + math.sin(a) * 12, 24 + math.cos(a) * 19, 24 + math.sin(a) * 19],
               fill=C('gold'), width=2)
    if state == 'open':
        for k in range(4):
            a = math.radians(k * 90 + 45)
            d.pieslice([4, 4, 43, 43], k * 90 + 20, k * 90 + 70, fill=C('night2'))
        d.ellipse([13, 13, 34, 34], fill=C('cyan3'), outline=C('white'))
        d.ellipse([20, 20, 27, 27], fill=C('white'))
    elif state == 'dead':
        d.ellipse([14, 14, 33, 33], fill=C('slate2'))
        d.line([10, 12, 36, 38], fill=C('ink'), width=2)
    else:
        iris = {'idle': 'red2', 'charge': 'yellow'}.get(state, 'red2')
        d.ellipse([12, 16, 35, 31], fill=C('white'))
        d.ellipse([18, 17, 29, 30], fill=C(iris))
        d.ellipse([22, 21, 25, 26], fill=C('ink'))
    return im


# ------------------------------------------------------------------ the engram
def mask(state='idle', frame=0):
    """The Daimyo's ghost: a floating kabuto and menpo with trailing static, 48x48."""
    im = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(frame + (9 if state == 'pin' else 0))
    for k in range(10):
        x = 10 + k * 3 + rng.randint(-1, 1)
        ln = rng.randint(6, 14)
        d.line([x, 32, x + rng.randint(-3, 3), 32 + ln], fill=C('purple2', 160))
    d.pieslice([8, 4, 40, 34], 180, 360, fill=C('purple1', 220), outline=C('purple3'))
    d.arc([4, -10, 44, 12], 200, 340, fill=C('gold'), width=2)
    d.rectangle([14, 18, 34, 32], fill=C('red1', 230), outline=C('purple3'))
    eyes = C('slate3') if state == 'pin' else C(['red3', 'white'][frame % 2])
    d.line([17, 22, 22, 22], fill=eyes, width=2)
    d.line([26, 22, 31, 22], fill=eyes, width=2)
    d.line([17, 28, 31, 28], fill=C('white', 200))
    if state == 'pin':
        for (x0, y0, x1, y1) in ((2, 10, 14, 22), (46, 12, 34, 24), (6, 40, 16, 30)):
            d.line([x0, y0, x1, y1], fill=C('mag3'), width=2)
    return im


def orb(frame):
    im = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 7, 7], fill=C('purple2'))
    d.ellipse([2, 2, 5, 5], fill=C('mag4' if frame % 2 else 'white'))
    return im


# ------------------------------------------------------------------ hollowed soldiers (Mukuro's rig)
# The Tenshu's guard in lacquered armor, eyes blank white.
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


SOLDIER_MAP = {'night3': 'indigo', 'indigo': 'slate3', 'red2': 'white', 'red3': 'red2',
               'slate2': 'slate1', 'slate3': 'slate2', 'yellow': 'gold'}


# ------------------------------------------------------------------ the Daimyo, in person
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
